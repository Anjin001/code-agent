"""一键演示脚本：自动运行 Agent，展示「输入 -> 推理 -> 工具调用 -> 输出」全过程。

用法：
    python demo.py                              # 离线 Mock 演示（无需 API Key，适合录视频）
    python demo.py --real                       # 真实调用 DeepSeek（需先在 .env 配好密钥）
    python demo.py --prompt "写一个快速排序"      # 自定义演示需求
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from codegen.agent import CodeGenAgent
from codegen.config import load_config
from codegen.tools import list_files, read_file

DEFAULT_PROMPT = "写一个计算斐波那契数列第 n 项的函数"


def main() -> None:
    parser = argparse.ArgumentParser(description="Code Gen Agent 演示脚本")
    parser.add_argument("--real", action="store_true", help="真实调用 DeepSeek（需配置 .env）")
    parser.add_argument("--prompt", type=str, default=DEFAULT_PROMPT, help="演示用需求描述")
    args = parser.parse_args()

    llm_cfg, agent_cfg = load_config()
    agent = CodeGenAgent(llm_cfg, agent_cfg, mock=not args.real)
    mode = "真实 DeepSeek" if args.real else "离线 Mock（无需 API Key）"

    bar = "=" * 58
    print(bar)
    print(f"  Code Gen Agent 演示 | 模式：{mode}")
    print(bar)

    print(f"\n[你] {args.prompt}")
    print("[Agent] 推理中：LLM -> 工具调用 -> 生成结果 ...\n")
    answer = agent.chat(args.prompt)
    print(f"[Agent] {answer}")

    time.sleep(0.5)
    print(f"\n{bar}")
    print("  workspace 目录文件：")
    files = list_files.invoke({"path": "."})
    print("  " + (files.replace("\n", "\n  ") if files else "(空)"))

    ws = Path(agent.agent_cfg.workspace)
    py_files = sorted(ws.glob("*.py"), key=lambda p: p.stat().st_mtime)
    if py_files:
        newest = py_files[-1]
        print(f"\n{bar}")
        print(f"  最新生成文件 {newest.name} 内容：")
        print(bar)
        print(read_file.invoke({"path": newest.name}))
        print(bar)

    print("演示结束。")


if __name__ == "__main__":
    main()
