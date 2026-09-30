import httpx

from ibotvision.error_handling import (
    AuthErrorHandling,
    IBOTVisionErrorHandling,
    PublishErrorHandling,
)

DEFAULT_GATEWAY = "https://api.ibotvision.com"


class PublisherClient:
    """
    IBOTVision signal publisher.

    Wraps POST /api/v1/publish — sends trading signals to all subscribers
    of your bot channel via the IBOTVision NATS mesh.

    Args:
        api_key:     Your vow_pub_ publisher key from ibotvision.com
        gateway_url: Override for enterprise self-hosted deployments
        timeout:     HTTP request timeout in seconds (default 10)
    """

    def __init__(
        self,
        api_key: str,
        gateway_url: str = DEFAULT_GATEWAY,
        timeout: int = 10,
    ):
        if not api_key.startswith("vow_pub_"):
            raise AuthErrorHandling("api_key must start with 'vow_pub_'")
        self._api_key = api_key
        self._base = gateway_url.rstrip("/")
        self._timeout = timeout

    def publish(
        self,
        symbol: str,
        action: str,
        lots: float,
        price: float,
        comment: str = "",
    ) -> dict:
        """
        Publish a symbol to all subscribers.

        Args:
            symbol:  Ticker symbol (e.g. "AAPL")
            action:  "BUY" or "SELL"
            lots:    Share count or contract size
            price:   Reference price at publish time
            comment: Optional note — logged, not executed

        Returns:
            Gateway response dict on success.

        Raises:
            AuthErrorHandling:       Invalid or revoked API key.
            PublishErrorHandling:    Gateway rejected the publish.
            IBOTVisionErrorHandling: Connection or unexpected error.
        """
        action = action.upper()
        if action not in ("BUY", "SELL"):
            raise PublishErrorHandling(
                f"action must be 'BUY' or 'SELL', got '{action}'"
            )
        if lots <= 0:
            raise PublishErrorHandling("lots must be greater than 0")
        if price <= 0:
            raise PublishErrorHandling("price must be greater than 0")

        payload: dict = {
            "symbol": symbol.upper(),
            "action": action,
            "lots":   lots,
            "price":  price,
        }
        if comment:
            payload["comment"] = comment

        try:
            resp = httpx.post(
                f"{self._base}/api/v1/publish",
                json=payload,
                headers={"X-API-Key": self._api_key},
                timeout=self._timeout,
            )
        except httpx.RequestError as exc:
            raise IBOTVisionErrorHandling(f"connection error: {exc}") from exc

        if resp.status_code == 401:
            raise AuthErrorHandling("invalid or revoked API key")
        if resp.status_code == 429:
            raise PublishErrorHandling("rate limit exceeded — slow down requests")
        if not resp.is_success:
            raise PublishErrorHandling(
                f"publish failed ({resp.status_code}): {resp.text}"
            )

        try:
            return resp.json()
        except ValueError as exc:
            raise IBOTVisionErrorHandling(f"gateway returned non-JSON response: {resp.text[:200]}") from exc

    @staticmethod
    def register(
        display_name: str,
        email: str,
        gateway_url: str = DEFAULT_GATEWAY,
    ) -> dict:
        """
        Register a new publisher account.

        No authentication required. The gateway creates a Firebase account
        and emails a vow_pub_ key to the provided address.

        Args:
            display_name: Your bot or strategy name
            email:        Address to receive the publisher key

        Returns:
            Gateway response dict. The key is delivered by email.

        Raises:
            IBOTVisionErrorHandling: Registration failed or connection error.
        """
        try:
            resp = httpx.post(
                f"{gateway_url.rstrip('/')}/api/v1/publisher/register",
                json={"display_name": display_name, "email": email},
                timeout=10,
            )
        except httpx.RequestError as exc:
            raise IBOTVisionErrorHandling(f"connection error: {exc}") from exc

        if not resp.is_success:
            raise IBOTVisionErrorHandling(
                f"registration failed ({resp.status_code}): {resp.text}"
            )

        return resp.json()
