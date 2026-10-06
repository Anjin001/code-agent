"""命令行入口：启动交互式代码生成 Agent。

用法：
    python main.py                              # 交互模式（需配置 DEEPSEEK_API_KEY）
    python main.py --mock                       # 离线演示（无需密钥）
    python main.py --prompt "写一个快速排序"      # 单条需求，直接返回结果
"""
from __future__ import annotations

import argparse

from codegen.agent import CodeGenAgent
from codegen.config import load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Code Gen Agent - 自然语言生成代码")
    parser.add_argument("--mock", action="store_true", help="离线假模型演示（无需 API Key）")
    parser.add_argument("--prompt", type=str, help="直接传入一条需求并退出（非交互）")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    llm_cfg, agent_cfg = load_config()
    agent = CodeGenAgent(llm_cfg, agent_cfg, mock=args.mock)

    if args.prompt:
        print(agent.chat(args.prompt))
        return

    print("Code Gen Agent 已启动（输入 exit / quit 退出）。")
    while True:
        try:
            text = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break
        if not text:
            continue
        if text.lower() in {"exit", "quit", "退出"}:
            print("再见！")
            break
        try:
            print("\nAgent：" + agent.chat(text))
        except Exception as exc:  # noqa: BLE001
            print(f"\n[错误] {exc}")


if __name__ == "__main__":
    main()
