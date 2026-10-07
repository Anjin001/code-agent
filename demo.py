"""一键演示脚本：自动运行 Agent，展示「输入 -> 推理 -> 工具调用 -> 输出」全过程。

用法：
    python demo.py                              # 自动判断：有 Key 真实调用，无 Key 离线 Mock
    python demo.py --real                       # 强制真实调用 DeepSeek（需 .env 配置密钥）
    python demo.py --mock                       # 强制离线 Mock
    python demo.py --prompt "写一个快速排序"      # 自定义演示需求
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from codegen.agent import CodeGenAgent
from codegen.config import load_config
from codegen.tools import list_files, read_file

DEFAULT_PROMPT = "写一个hello world的C++程序"


def main() -> None:
    parser = argparse.ArgumentParser(description="Code Gen Agent 演示脚本")
    parser.add_argument("--real", action="store_true", help="强制真实调用 DeepSeek（需配置 .env）")
    parser.add_argument("--mock", action="store_true", help="强制离线 Mock 模式")
    parser.add_argument("--prompt", type=str, default=DEFAULT_PROMPT, help="演示用需求描述")
    args = parser.parse_args()

    llm_cfg, agent_cfg = load_config()

    # 模式判定：--real 强制真实；--mock 强制离线；否则有 Key 真实、无 Key 自动降级离线
    if args.real:
        use_mock = False
    elif args.mock:
        use_mock = True
    else:
        use_mock = not llm_cfg.api_key

    if use_mock and not args.mock:
        print("⚠️  未检测到 DEEPSEEK_API_KEY，已自动使用离线 Mock 模式。")
        print("   在 .env 中配置密钥后即可真实调用 DeepSeek。\n")

    agent = CodeGenAgent(llm_cfg, agent_cfg, mock=use_mock)
    mode = "真实 DeepSeek (deepseek-chat)" if not use_mock else "离线 Mock（未检测到 API Key）"

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
    generated = sorted([p for p in ws.iterdir() if p.is_file()], key=lambda p: p.stat().st_mtime)
    if generated:
        newest = generated[-1]
        print(f"\n{bar}")
        print(f"  最新生成文件 {newest.name} 内容：")
        print(bar)
        print(read_file.invoke({"path": newest.name}))
        print(bar)

    print("演示结束。")


if __name__ == "__main__":
    main()
