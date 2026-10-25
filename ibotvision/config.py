"""
IBOTVision SDK — configuration.

Resolution order (highest priority first):
  1. Explicit kwargs passed to Config(...)
  2. OS environment variables (IBOTVISION_*)
  3. Module defaults

White-label partners override gateway_url, user_agent, extra_headers, and
auth_header_name to point at their own infrastructure.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional


DEFAULT_GATEWAY = "https://api.ibotvision.com"
DEFAULT_USER_AGENT = "ibotvision-sdk/1.0.0"


@dataclass
class Config:
    """SDK configuration container."""

    api_key: str
    gateway_url: str = DEFAULT_GATEWAY
    timeout: float = 10.0
    max_retries: int = 3
    user_agent: str = DEFAULT_USER_AGENT
    extra_headers: Optional[Dict[str, str]] = None
    auth_header_name: str = "X-API-Key"

    def __post_init__(self) -> None:
        if not self.api_key:
            raise ValueError(
                "api_key is required — pass explicitly or set IBOTVISION_API_KEY"
            )
        if not self.api_key.startswith("vow_pub_"):
            raise ValueError("api_key must start with 'vow_pub_'")
        self.gateway_url = self.gateway_url.rstrip("/")

    @classmethod
    def from_env(cls, **overrides: Any) -> "Config":
        """Build a Config from env vars, with optional kwargs to override."""
        api_key = overrides.pop("api_key", None) or os.environ.get(
            "IBOTVISION_API_KEY", ""
        )
        gateway_url = overrides.pop("gateway_url", None) or os.environ.get(
            "IBOTVISION_GATEWAY_URL", DEFAULT_GATEWAY
        )
        timeout = overrides.pop("timeout", None)
        if timeout is None:
            timeout = float(os.environ.get("IBOTVISION_TIMEOUT", "10"))
        max_retries = overrides.pop("max_retries", None)
        if max_retries is None:
            max_retries = int(os.environ.get("IBOTVISION_MAX_RETRIES", "3"))
        user_agent = overrides.pop("user_agent", None) or os.environ.get(
            "IBOTVISION_USER_AGENT", DEFAULT_USER_AGENT
        )
        return cls(
            api_key=api_key,
            gateway_url=gateway_url,
            timeout=timeout,
            max_retries=max_retries,
            user_agent=user_agent,
            **overrides,
        )

    def headers(self) -> Dict[str, str]:
        """Request headers including auth + white-label extras."""
        h: Dict[str, str] = {
            "User-Agent": self.user_agent,
            self.auth_header_name: self.api_key,
        }
        if self.extra_headers:
            h.update(self.extra_headers)
        return h
