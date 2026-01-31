from typing import Final, Literal, TypeAlias


Provider: TypeAlias = Literal["anthropic", "glm","kimi"]

PROVIDERS: Final[tuple[Provider, ...]] = ("anthropic", "glm", "kimi")
