"""LLM 构建：默认调用 DeepSeek（OpenAI 兼容接口），并提供离线 Mock 模型。"""
from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, ToolMessage

from .config import LLMConfig


def build_llm(config: LLMConfig, mock: bool = False):
    """构建底层聊天模型。

    mock=True 时返回 MockChatModel（离线演示 / 测试用）；
    否则返回指向 DeepSeek 的 ChatOpenAI 实例。
    """
    if mock:
        return MockChatModel()

    if not config.api_key:
        raise RuntimeError(
            "未检测到 DEEPSEEK_API_KEY。请复制 .env.example 为 .env 并填入密钥，"
            "或使用 --mock 以离线模式演示。"
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=config.model,
        api_key=config.api_key,
        base_url=config.base_url,
        temperature=config.temperature,
        max_retries=config.max_retries,
        timeout=60,
    )


class MockChatModel:
    """离线假模型：完整走一遍「推理 -> 工具调用 -> 最终回答」的 Agent 循环。

    不依赖网络与 API Key，便于在无密钥环境下演示架构、跑通测试。
    行为约定：首轮返回一次 save_code_to_file 的工具调用；
    收到工具执行结果（ToolMessage）后返回最终回答。
    """

    _SAMPLE = (
        "def fibonacci(n: int) -> int:\n"
        "    \"\"\"返回第 n 个斐波那契数（0 <= n）。\"\"\"\n"
        "    if n < 0:\n"
        "        raise ValueError('n 必须为非负整数')\n"
        "    if n <= 1:\n"
        "        return n\n"
        "    a, b = 0, 1\n"
        "    for _ in range(2, n + 1):\n"
        "        a, b = b, a + b\n"
        "    return b\n"
    )

    def __init__(self) -> None:
        self._tools: dict[str, Any] = {}

    def bind_tools(self, tools: list[Any], **kwargs: Any) -> "MockChatModel":
        self._tools = {t.name: t for t in tools}
        return self

    def invoke(self, messages: list[Any], **kwargs: Any) -> AIMessage:
        last = messages[-1] if messages else None
        if isinstance(last, ToolMessage):
            return AIMessage(
                content="已完成代码生成并保存到 workspace 目录（Mock 演示模式，未调用真实大模型）。"
            )

        if "save_code_to_file" in self._tools:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "save_code_to_file",
                        "args": {
                            "filename": "generated_fibonacci.py",
                            "code": self._SAMPLE,
                        },
                        "id": "call_mock_1",
                        "type": "tool_call",
                    }
                ],
            )

        return AIMessage(content=self._SAMPLE)
