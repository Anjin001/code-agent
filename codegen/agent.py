"""核心 Agent 循环：输入 -> 推理 -> 工具调用 -> 输出，含记忆与错误重试。"""
from __future__ import annotations

import time
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, ToolMessage

from .config import AgentConfig, LLMConfig
from .llm import build_llm
from .memory import ConversationMemory
from .prompts import SYSTEM_PROMPT
from .tools import TOOLS, set_workspace


class CodeGenAgent:
    """基于 ReAct 思想的代码生成 Agent。

    一次 chat() 内部的执行循环：
        构造消息（系统提示 + 历史记忆 + 当前问题）
        -> 调用 LLM（已绑定工具）
        -> 若模型返回工具调用：执行工具，把结果作为 ToolMessage 回填，继续循环
        -> 若模型直接返回文本：结束，作为最终回答
    """

    def __init__(self, llm_cfg: LLMConfig, agent_cfg: AgentConfig, mock: bool = False) -> None:
        self.llm_cfg = llm_cfg
        self.agent_cfg = agent_cfg
        self.memory = ConversationMemory(size=agent_cfg.memory_size)

        set_workspace(agent_cfg.workspace)
        self.llm = build_llm(llm_cfg, mock=mock)
        self.llm_with_tools = self.llm.bind_tools(TOOLS)

    def chat(self, user_input: str) -> str:
        """处理一条用户输入，返回最终回答。"""
        self.memory.add_user(user_input)
        answer = self._run_loop()
        self.memory.add_ai(answer)
        return answer

    def _run_loop(self) -> str:
        messages: list[BaseMessage] = [
            SystemMessage(content=SYSTEM_PROMPT),
            *self.memory.messages(),
        ]

        for _ in range(self.agent_cfg.max_steps):
            response = self._invoke_with_retry(messages)
            if not response.tool_calls:
                return response.content or "(模型未返回内容)"

            # 记录模型的这一步（含工具调用），并执行工具
            messages.append(response)
            for call in response.tool_calls:
                tool_msg = self._execute_tool(call)
                messages.append(tool_msg)

        return "已达最大推理步数，任务未完成。请简化需求或稍后重试。"

    def _invoke_with_retry(self, messages: list[BaseMessage]) -> AIMessage:
        """带指数退避的 LLM 调用，容忍网络抖动、限流等瞬时错误。"""
        last_err: Exception | None = None
        for attempt in range(self.llm_cfg.max_retries + 1):
            try:
                return self.llm_with_tools.invoke(messages)
            except Exception as exc:  # noqa: BLE001 - 统一兜底后重试
                last_err = exc
                if attempt < self.llm_cfg.max_retries:
                    time.sleep(2 ** attempt)
        raise RuntimeError(f"LLM 调用失败（已重试 {self.llm_cfg.max_retries} 次）：{last_err}")

    def _execute_tool(self, call: dict[str, Any]) -> ToolMessage:
        name = call.get("name", "")
        args = call.get("args", {})
        tool = next((t for t in TOOLS if t.name == name), None)
        if tool is None:
            content = f"错误：未知工具 {name}"
        else:
            try:
                content = str(tool.invoke(args))
            except Exception as exc:  # noqa: BLE001 - 工具失败反馈给模型，让其纠正
                content = f"工具 {name} 执行出错：{exc}"
        return ToolMessage(content=content, tool_call_id=call.get("id"), name=name)
