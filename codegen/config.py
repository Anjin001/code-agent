"""配置加载：从环境变量 / .env 读取 LLM 与 Agent 参数。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# 加载项目根目录下的 .env（若存在）
load_dotenv()


@dataclass
class LLMConfig:
    """LLM 相关配置。"""

    model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com"
    api_key: str = ""
    temperature: float = 0.2
    max_retries: int = 3


@dataclass
class AgentConfig:
    """Agent 行为配置。"""

    max_steps: int = 8          # 单次请求最多允许的推理/工具调用轮数
    memory_size: int = 20       # 上下文记忆保留的消息条数
    workspace: Path = field(default_factory=lambda: Path.cwd() / "workspace")


def load_config() -> tuple[LLMConfig, AgentConfig]:
    """从环境变量读取配置，未设置时使用默认值。"""
    llm = LLMConfig(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        api_key=os.getenv("DEEPSEEK_API_KEY", ""),
        temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.2")),
        max_retries=int(os.getenv("DEEPSEEK_MAX_RETRIES", "3")),
    )
    agent = AgentConfig(
        max_steps=int(os.getenv("AGENT_MAX_STEPS", "8")),
        memory_size=int(os.getenv("AGENT_MEMORY_SIZE", "20")),
        workspace=Path(os.getenv("AGENT_WORKSPACE", "workspace")),
    )
    return llm, agent
