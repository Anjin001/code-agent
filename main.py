"""命令行入口：启动交互式代码生成 Agent。

用法：
    python main.py                              # 交互模式（有 Key 真实调用，无 Key 自动离线）
    python main.py --mock                       # 强制离线假模型演示
    python main.py --real                       # 强制真实调用 DeepSeek（需配置 .env）
    python main.py --prompt "写一个快速排序"      # 单条需求，直接返回结果
"""
from __future__ import annotations

import argparse

from codegen.agent import CodeGenAgent
from codegen.config import load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Code Gen Agent - 自然语言生成代码")
    parser.add_argument("--mock", action="store_true", help="强制离线假模型演示")
    parser.add_argument("--real", action="store_true", help="强制真实调用 DeepSeek（需配置 .env）")
    parser.add_argument("--prompt", type=str, help="直接传入一条需求并退出（非交互）")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    llm_cfg, agent_cfg = load_config()

    # 模式判定：--real 强制真实；--mock 强制离线；否则有 Key 真实、无 Key 自动降级离线
    if args.real:
        use_mock = False
    elif args.mock:
        use_mock = True
    else:
        use_mock = not llm_cfg.api_key
        if use_mock:
            print("⚠️  未检测到 DEEPSEEK_API_KEY，自动使用离线 Mock 模式。")
            print("   在 .env 中配置密钥后即可真实调用 DeepSeek。")

    agent = CodeGenAgent(llm_cfg, agent_cfg, mock=use_mock)

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
