from typing import TypedDict, Literal

class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str