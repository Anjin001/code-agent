"""上下文记忆：基于滚动窗口的对话记忆。"""
from __future__ import annotations

from collections import deque

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class ConversationMemory:
    """保留最近 N 条消息的简单记忆。

    超过容量时自动丢弃最旧的消息（FIFO），避免上下文无限增长、
    超出模型上下文窗口或增加调用成本。
    """

    def __init__(self, size: int = 20) -> None:
        self._size = size
        self._messages: deque[BaseMessage] = deque(maxlen=size)

    def add_user(self, text: str) -> None:
        self._messages.append(HumanMessage(content=text))

    def add_ai(self, text: str) -> None:
        self._messages.append(AIMessage(content=text))

    def messages(self) -> list[BaseMessage]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)
