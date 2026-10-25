"""IBOTVision SDK — typed payload and response shapes."""
from __future__ import annotations

from typing import Any, Dict, TypedDict


class PublishPayload(TypedDict, total=False):
    """Request body for POST /api/v1/publish."""
    symbol: str
    action: str
    lots: float
    price: float
    comment: str
    metadata: Dict[str, Any]


class PublishResponse(TypedDict, total=False):
    """Gateway response on successful publish."""
    ok: bool
    message: str
    message_id: str
    delivered_to: int


class RegisterResponse(TypedDict, total=False):
    """Response from POST /api/v1/publisher/register."""
    ok: bool
    message: str
    display_name: str
    email: str
    referral_code: str
    referral_credited_to: str
