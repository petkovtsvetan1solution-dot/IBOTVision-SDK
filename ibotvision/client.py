"""
IBOTVision SDK — publisher clients.

Two classes:
  AsyncPublisherClient — primary, uses httpx.AsyncClient, connection-pooled.
  SyncPublisherClient  — legacy wrapper using asyncio.run() per call.

Backwards-compat: PublisherClient is an alias for SyncPublisherClient.
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import httpx

from ibotvision.config import DEFAULT_GATEWAY, Config
from ibotvision.error_handling import (
    AuthError,
    IbotvisionError,
    PublishError,
    RateLimitError,
    parse_retry_after,
)
from ibotvision.models import PublishPayload, PublishResponse, RegisterResponse


async def _register_async(
    display_name: str,
    email: str,
    gateway_url: str,
    referral_code: Optional[str],
    timeout: float,
) -> RegisterResponse:
    """Register without requiring a client instance (used by module-level register)."""
    body: Dict[str, Any] = {"display_name": display_name, "email": email}
    if referral_code:
        body["referral_code"] = referral_code
    async with httpx.AsyncClient(
        base_url=gateway_url.rstrip("/"), timeout=timeout
    ) as http:
        try:
            resp = await http.post("/api/v1/publisher/register", json=body)
        except httpx.RequestError as exc:
            raise IbotvisionError(f"connection error: {exc}") from exc
        if not resp.is_success:
            raise IbotvisionError(
                f"registration failed ({resp.status_code}): {resp.text[:200]}",
                status_code=resp.status_code,
                raw_response=resp,
            )
        return resp.json()  # type: ignore[no-any-return]


def register(
    display_name: str,
    email: str,
    gateway_url: str = DEFAULT_GATEWAY,
    referral_code: Optional[str] = None,
) -> RegisterResponse:
    """
    Register a new publisher account. No auth required.

    Backwards-compat module-level function — same behavior as v0.1.0
    PublisherClient.register() static method.

    Args:
        display_name:  Your bot or strategy name.
        email:         Address to receive the publisher key.
        gateway_url:   Override for enterprise self-hosted deployments.
        referral_code: Optional referral code from an existing publisher.
    """
    return asyncio.run(
        _register_async(display_name, email, gateway_url, referral_code, 10.0)
    )


class AsyncPublisherClient:
    """Async, connection-pooled IBOTVision publisher."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        gateway_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        user_agent: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        config: Optional[Config] = None,
    ) -> None:
        if config is not None:
            self._config = config
        else:
            overrides: Dict[str, Any] = {}
            if api_key is not None:
                overrides["api_key"] = api_key
            if gateway_url is not None:
                overrides["gateway_url"] = gateway_url
            if timeout is not None:
                overrides["timeout"] = timeout
            if max_retries is not None:
                overrides["max_retries"] = max_retries
            if user_agent is not None:
                overrides["user_agent"] = user_agent
            if extra_headers is not None:
                overrides["extra_headers"] = extra_headers
            self._config = Config.from_env(**overrides)

        self._client: Optional[httpx.AsyncClient] = None

    @property
    def config(self) -> Config:
        return self._config

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._config.gateway_url,
                timeout=self._config.timeout,
                headers=self._config.headers(),
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "AsyncPublisherClient":
        await self._get_client()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def publish(
        self,
        symbol: str,
        action: str,
        lots: float,
        price: float,
        comment: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PublishResponse:
        """Publish a symbol to all subscribers. Non-blocking."""
        action = action.upper()
        if action not in ("BUY", "SELL"):
            raise PublishError(f"action must be 'BUY' or 'SELL', got '{action}'")
        if lots <= 0:
            raise PublishError("lots must be greater than 0")
        if price <= 0:
            raise PublishError("price must be greater than 0")

        payload: PublishPayload = {
            "symbol": symbol.upper(),
            "action": action,
            "lots": lots,
            "price": price,
        }
        if comment:
            payload["comment"] = comment
        if metadata:
            payload["metadata"] = metadata

        client = await self._get_client()
        last_error: Optional[IbotvisionError] = None

        for attempt in range(self._config.max_retries + 1):
            try:
                resp = await client.post("/api/v1/publish", json=payload)
            except httpx.RequestError as exc:
                last_error = IbotvisionError(f"connection error: {exc}")
                if attempt == self._config.max_retries:
                    raise last_error from exc
                await asyncio.sleep(2 ** attempt)
                continue

            if resp.status_code == 401:
                raise AuthError(
                    "invalid or revoked API key",
                    status_code=401,
                    raw_response=resp,
                )

            if resp.status_code == 429:
                retry_after = parse_retry_after(resp.headers.get("Retry-After"))
                error = RateLimitError(
                    "rate limit exceeded"
                    + (f" (retry after {retry_after:.0f}s)" if retry_after else ""),
                    status_code=429,
                    raw_response=resp,
                    retry_after=retry_after,
                    payload=self._safe_json(resp),
                )
                if error.should_retry(attempt, self._config.max_retries):
                    await asyncio.sleep(retry_after or (2 ** attempt))
                    last_error = error
                    continue
                raise error

            if not resp.is_success:
                raise PublishError(
                    f"publish failed ({resp.status_code}): {resp.text[:200]}",
                    status_code=resp.status_code,
                    raw_response=resp,
                    payload=self._safe_json(resp),
                )

            try:
                return resp.json()  # type: ignore[no-any-return]
            except ValueError as exc:
                raise IbotvisionError(
                    f"gateway returned non-JSON: {resp.text[:200]}",
                    status_code=resp.status_code,
                    raw_response=resp,
                ) from exc

        if last_error is not None:
            raise last_error
        raise IbotvisionError("publish failed for unknown reason")

    async def register(
        self,
        display_name: str,
        email: str,
        referral_code: Optional[str] = None,
    ) -> RegisterResponse:
        """Register a new publisher account. No auth required."""
        client = await self._get_client()
        body: Dict[str, Any] = {"display_name": display_name, "email": email}
        if referral_code:
            body["referral_code"] = referral_code
        try:
            resp = await client.post("/api/v1/publisher/register", json=body)
        except httpx.RequestError as exc:
            raise IbotvisionError(f"connection error: {exc}") from exc

        if not resp.is_success:
            raise IbotvisionError(
                f"registration failed ({resp.status_code}): {resp.text[:200]}",
                status_code=resp.status_code,
                raw_response=resp,
            )
        return resp.json()  # type: ignore[no-any-return]

    @staticmethod
    def _safe_json(resp: httpx.Response) -> Optional[Any]:
        try:
            return resp.json()
        except Exception:
            return None


class SyncPublisherClient:
    """Thread-safe synchronous wrapper around AsyncPublisherClient."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._init_args = args
        self._init_kwargs = kwargs

    def _run_sync(self, coro: Any) -> Any:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        raise RuntimeError(
            "SyncPublisherClient cannot be used from async context. "
            "Use AsyncPublisherClient instead."
        )

    async def _do_publish(self, *args: Any, **kwargs: Any) -> PublishResponse:
        async with AsyncPublisherClient(
            *self._init_args, **self._init_kwargs
        ) as client:
            return await client.publish(*args, **kwargs)

    async def _do_register(self, *args: Any, **kwargs: Any) -> RegisterResponse:
        async with AsyncPublisherClient(
            *self._init_args, **self._init_kwargs
        ) as client:
            return await client.register(*args, **kwargs)

    def publish(self, *args: Any, **kwargs: Any) -> PublishResponse:
        return self._run_sync(self._do_publish(*args, **kwargs))

    def register(self, *args: Any, **kwargs: Any) -> RegisterResponse:
        return self._run_sync(self._do_register(*args, **kwargs))

    def close(self) -> None:
        """No-op — clients are per-call."""


# Backwards-compat: v0.1.0 name was sync
PublisherClient = SyncPublisherClient
