# Constant mappings for known API providers
from typing import Final
from pydantic import BaseModel, Field
from .providers import Provider

PROVIDER_MODELS: Final[dict[Provider, list[str]]] = {
    "anthropic": [
        "claude-3-5-haiku-20241015",  #Latest Haiku (3.5)
        "claude-sonnet-4-6", #Latest Sonnet (3.5)
        "claude-opus-4-6",     #Latest Opus (3.0)
    ],
    "glm": [
        "glm-4.6", #Haiku model
        "glm-4.7", #Sonnet model
        "glm-5.0", #Opus model
    ],
    "kimi": [
        "kimi-k2.5", #Haiku model
        "kimi-k2.5", #Sonnet model
        "kimi-k2-thinking", #Opus model
    ],
}


class Model(BaseModel):
    """Default model configurations for each provider."""

    provider: Provider
    anthropic_default_haiku_model: str = Field(
        default=PROVIDER_MODELS["anthropic"][0], description="Default Haiku model identifier"
    )
    anthropic_default_sonnet_model: str = Field(
        default=PROVIDER_MODELS["anthropic"][1], description="Default Sonnet model identifier"
    )
    anthropic_default_opus_model: str = Field(
        default=PROVIDER_MODELS["anthropic"][2], description="Default Opus model identifier"
    )

    @classmethod
    def create_provider_models(cls, provider: Provider) -> "Model":
        """Create a Model instance with defaults for the specified provider."""
        defaults = {
            "anthropic": {
                "anthropic_default_haiku_model": "claude-3-haiku-20240307",
                "anthropic_default_sonnet_model": "claude-3-5-sonnet-20241022",
                "anthropic_default_opus_model": "claude-3-opus-20240229",
            }
        }
        return cls(provider=provider, **defaults.get(provider, {}))

    def to_values(self) -> list[str]:
        """Return list of available model names for this provider."""
        return PROVIDER_MODELS.get(self.provider, [])
