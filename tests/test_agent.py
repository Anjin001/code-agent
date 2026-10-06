"""Agent 冒烟测试（使用离线 Mock 模型，无需 API Key）。"""
from __future__ import annotations

from codegen.agent import CodeGenAgent
from codegen.config import AgentConfig, LLMConfig


def _make_agent(tmp_path) -> CodeGenAgent:
    llm_cfg = LLMConfig(api_key="")
    agent_cfg = AgentConfig(max_steps=8, memory_size=20, workspace=tmp_path / "workspace")
    return CodeGenAgent(llm_cfg, agent_cfg, mock=True)


def test_agent_generates_and_saves_code(tmp_path):
    agent = _make_agent(tmp_path)
    answer = agent.chat("写一个斐波那契函数")
    assert answer, "Agent 应返回非空回答"
    files = list((tmp_path / "workspace").glob("*.py"))
    assert files, "Mock 应调用 save_code_to_file 生成代码文件"


def test_memory_records_conversation(tmp_path):
    agent = _make_agent(tmp_path)
    agent.chat("写一个斐波那契函数")
    assert len(agent.memory) == 2  # 一条 user + 一条 assistant


def test_tool_rejects_path_escape(tmp_path):
    from codegen.tools import read_file, set_workspace

    set_workspace(tmp_path / "ws")
    result = read_file.invoke({"path": "../secret.txt"})
    assert "拒绝" in result
