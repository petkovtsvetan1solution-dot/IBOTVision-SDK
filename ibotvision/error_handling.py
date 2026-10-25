"""
IBOTVision SDK — exception taxonomy.

New code should catch:
    IbotvisionError            (base)
    AuthError, PublishError, RateLimitError

Old code that catches IBOTVisionErrorHandling / AuthErrorHandling /
PublishErrorHandling still works — those are aliases at the bottom.
"""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Mapping, Optional


def parse_retry_after(header_value: Optional[str]) -> Optional[float]:
    """Parse Retry-After as either integer seconds or HTTP-date. Returns seconds."""
    if not header_value:
        return None
    header_value = header_value.strip()
    try:
        return float(header_value)
    except ValueError:
        pass
    try:
        dt = parsedate_to_datetime(header_value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = (dt - datetime.now(timezone.utc)).total_seconds()
        return max(0.0, delta)
    except (TypeError, ValueError):
        return None


class IbotvisionError(Exception):
    """
    Base exception for all IBOTVision SDK failures.

    Attributes:
        status_code:  HTTP status code if the error came from a gateway response.
        raw_response: The underlying httpx.Response, if available.
        retry_after:  Seconds to wait before retrying (from Retry-After header).
        payload:      Parsed JSON body if the gateway returned one.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        raw_response: Any = None,
        retry_after: Optional[float] = None,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.raw_response = raw_response
        self.retry_after = retry_after
        self.payload = payload

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({str(self)!r}, "
            f"status_code={self.status_code!r})"
        )


class AuthError(IbotvisionError):
    """Authentication failed — invalid, expired, or revoked API key."""


class PublishError(IbotvisionError):
    """Signal publish was rejected by the gateway."""


class RateLimitError(PublishError):
    """
    HTTP 429. Carries `.retry_after` (seconds) parsed from the Retry-After header.

    Example:
        try:
            await client.publish(...)
        except RateLimitError as e:
            wait = e.retry_after or 5.0
            await asyncio.sleep(wait)
    """

    def should_retry(self, attempt: int, max_retries: int = 3) -> bool:
        """True if a retry is worth attempting at this attempt number."""
        if self.retry_after is not None and self.retry_after > 60:
            return False
        return attempt < max_retries


# ── Backwards-compatible aliases (v0.1.0 names) ──────────────────────────────
IBOTVisionErrorHandling = IbotvisionError
AuthErrorHandling = AuthError
PublishErrorHandling = PublishError
