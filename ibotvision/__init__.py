"""
IBOTVision SDK — connect your bots to institutional-grade P2P symbol routing.
"""
from ibotvision.client import (
    AsyncPublisherClient,
    PublisherClient,
    SyncPublisherClient,
    register,
)
from ibotvision.config import (
    DEFAULT_GATEWAY,
    DEFAULT_USER_AGENT,
    Config,
)
from ibotvision.error_handling import (
    AuthError,
    IbotvisionError,
    PublishError,
    RateLimitError,
    AuthErrorHandling,
    IBOTVisionErrorHandling,
    PublishErrorHandling,
)
from ibotvision.models import (
    PublishPayload,
    PublishResponse,
    RegisterResponse,
)

__version__ = "1.0.0"

__all__ = [
    "AsyncPublisherClient",
    "SyncPublisherClient",
    "PublisherClient",
    "register",
    "Config",
    "DEFAULT_GATEWAY",
    "DEFAULT_USER_AGENT",
    "IbotvisionError",
    "AuthError",
    "PublishError",
    "RateLimitError",
    "IBOTVisionErrorHandling",
    "AuthErrorHandling",
    "PublishErrorHandling",
    "PublishPayload",
    "PublishResponse",
    "RegisterResponse",
]
