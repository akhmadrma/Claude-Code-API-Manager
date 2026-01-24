# Constant mappings for known API providers
from typing import Final, Literal, TypeAlias

from pydantic import BaseModel, Field, field_validator

Provider: TypeAlias = Literal["anthropic", "glm"]

PROVIDERS: Final[tuple[Provider, ...]] = ("anthropic", "glm")

PROVIDER_URLS: Final[dict[Provider, str]] = {
    "anthropic": "https://api.anthropic.com",
    "glm": "https://api.z.ai/api/anthropic",
}


# TODO : Refactor BaseURL Return onlu string url
class BaseURL(BaseModel):
    """
    Base URL configuration for different API providers.

    This model manages API endpoint URLs for various services, providing
    a centralized way to handle different API providers and their endpoints.
    """
    provider : Provider
    value: str = Field(
        default=PROVIDER_URLS["anthropic"], description="The base URL for the API endpoint"
    )

    @field_validator("value")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """
        Validate that the base URL is properly formatted.

        Args:
            v: The base URL to validate

        Returns:
            The validated base URL with trailing slash
        """
        v = cls._normalize_url(v)
        if not v.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return f"{v}/"

    @classmethod
    def get_provider_url(cls, provider: Provider) -> str:
        """
        Get the base URL for a specific provider.

        Args:
            provider: The provider name (e.g., "anthropic", "glm")

        Returns:
            The base URL for the specified provider

        Raises:
            ValueError: If the provider is not supported
        """
        if provider not in PROVIDER_URLS:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: {PROVIDERS}")
        return PROVIDER_URLS[provider]

    @classmethod
    def create_for_provider(cls, provider: Provider) -> "BaseURL":
        """
        Create a BaseURL instance for a specific provider.

        Args:
            provider: The provider name (e.g., "anthropic", "glm")

        Returns:
            BaseURL instance configured for the specified provider
        """
        base_url = cls.get_provider_url(provider)
        return cls(provider=provider, value=base_url)

    @staticmethod
    def _normalize_url(url: str) -> str:
        """
        Normalize URL by removing trailing slash for comparison.

        Args:
            url: URL to normalize

        Returns:
            Normalized URL without trailing slash
        """
        return url.rstrip("/")

    def to_values(self) -> str:
        """
        Return the base URL value as a string.

        Returns:
            str: The base URL value
        """
        return PROVIDER_URLS.get(self.provider, self.value)
