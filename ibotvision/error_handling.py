class IBOTVisionErrorHandling(Exception):
    """Base error for all IBOTVision SDK failures."""


class AuthErrorHandling(IBOTVisionErrorHandling):
    """Raised when authentication fails — invalid, expired, or revoked API key."""


class PublishErrorHandling(IBOTVisionErrorHandling):
    """Raised when a signal publish request is rejected by the gateway."""
