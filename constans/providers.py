from typing import Final, Literal, TypeAlias


Provider: TypeAlias = Literal["anthropic", "glm"]

PROVIDERS: Final[tuple[Provider, ...]] = ("anthropic", "glm")
