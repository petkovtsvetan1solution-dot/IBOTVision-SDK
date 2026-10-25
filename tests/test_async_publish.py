"""Minimal verification of the refactored client — run before deploy."""
import pytest
from unittest.mock import AsyncMock, patch

import httpx

from ibotvision import (
    AsyncPublisherClient,
    AuthError,
    Config,
    RateLimitError,
)


def _config():
    return Config(api_key="vow_pub_test", gateway_url="https://test.invalid")


@pytest.mark.asyncio
async def test_successful_publish():
    mock_resp = httpx.Response(200, json={"ok": True, "message_id": "m1"})
    with patch.object(httpx.AsyncClient, "post", AsyncMock(return_value=mock_resp)):
        async with AsyncPublisherClient(config=_config()) as c:
            result = await c.publish(symbol="AAPL", action="BUY", lots=1, price=100.0)
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_429_raises_rate_limit_with_retry_after():
    mock_resp = httpx.Response(
        429,
        headers={"Retry-After": "30"},
        json={"error": "slow down"},
    )
    with patch.object(httpx.AsyncClient, "post", AsyncMock(return_value=mock_resp)):
        async with AsyncPublisherClient(
            config=Config(
                api_key="vow_pub_test",
                gateway_url="https://test.invalid",
                max_retries=0,
            )
        ) as c:
            with pytest.raises(RateLimitError) as exc_info:
                await c.publish(symbol="AAPL", action="BUY", lots=1, price=100.0)
    assert exc_info.value.retry_after == 30.0
    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_401_raises_auth_error():
    mock_resp = httpx.Response(401, json={"error": "bad key"})
    with patch.object(httpx.AsyncClient, "post", AsyncMock(return_value=mock_resp)):
        async with AsyncPublisherClient(config=_config()) as c:
            with pytest.raises(AuthError):
                await c.publish(symbol="AAPL", action="BUY", lots=1, price=100.0)


def test_sync_client_basic():
    mock_resp = httpx.Response(200, json={"ok": True})
    with patch.object(httpx.AsyncClient, "post", AsyncMock(return_value=mock_resp)):
        from ibotvision import PublisherClient
        client = PublisherClient(
            api_key="vow_pub_test", gateway_url="https://test.invalid"
        )
        result = client.publish(symbol="AAPL", action="BUY", lots=1, price=100.0)
    assert result["ok"] is True


def test_backwards_compat_static_register():
    """v0.1.0 allowed PublisherClient.register(...) as a static call."""
    mock_resp = httpx.Response(200, json={"ok": True, "message": "check email"})
    with patch.object(httpx.AsyncClient, "post", AsyncMock(return_value=mock_resp)):
        from ibotvision import register
        result = register(
            "My Bot", "me@example.com", gateway_url="https://test.invalid"
        )
    assert result["ok"] is True


def test_register_with_referral_code():
    mock_resp = httpx.Response(
        200, json={"ok": True, "referral_credited_to": "ref123"}
    )
    captured = {}

    async def capture_post(self, url, **kwargs):
        captured["json"] = kwargs.get("json", {})
        return mock_resp

    with patch.object(httpx.AsyncClient, "post", capture_post):
        from ibotvision import register
        result = register(
            "My Bot",
            "me@example.com",
            gateway_url="https://test.invalid",
            referral_code="REF123",
        )
    assert captured["json"].get("referral_code") == "REF123"
    assert result["referral_credited_to"] == "ref123"
