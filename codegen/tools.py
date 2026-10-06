"""Agent 工具集：保存代码、读取文件、执行 Python、列举文件。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from langchain_core.tools import tool

# 工作目录：所有文件读写都被限制在 WORKSPACE 之内，避免越权访问。
WORKSPACE: Path = Path.cwd() / "workspace"


def set_workspace(path: Path) -> None:
    """设置工具使用的工作目录（Agent 初始化时调用）。"""
    global WORKSPACE
    WORKSPACE = Path(path)
    WORKSPACE.mkdir(parents=True, exist_ok=True)


def _workspace() -> Path:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    return WORKSPACE


def _resolve_safely(path: str) -> Path | None:
    """把相对路径解析到 WORKSPACE 内；越界返回 None。"""
    base = _workspace().resolve()
    target = (base / path).resolve()
    if not str(target).startswith(str(base)):
        return None
    return target


@tool
def save_code_to_file(filename: str, code: str) -> str:
    """把生成的代码保存到工作目录（workspace）下的文件。

    Args:
        filename: 文件名（相对路径，例如 utils.py 或 src/hello.py）。
        code: 要写入的完整代码内容。
    """
    target = _resolve_safely(filename)
    if target is None:
        return f"错误：文件名 {filename} 试图写到工作目录之外，已拒绝。"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(code, encoding="utf-8")
    return f"已保存 {len(code)} 字符到 {target.relative_to(_workspace().resolve())}"


@tool
def read_file(path: str) -> str:
    """读取工作目录（workspace）内的文件内容，用于获取上下文。

    Args:
        path: 文件相对路径。
    """
    target = _resolve_safely(path)
    if target is None:
        return f"错误：{path} 在工作目录之外，已拒绝读取。"
    if not target.exists():
        return f"错误：文件 {path} 不存在。"
    return target.read_text(encoding="utf-8")


@tool
def run_python(code: str) -> str:
    """在受限子进程中执行一段 Python 代码并返回输出，用于验证生成的代码。

    Args:
        code: 要执行的 Python 代码。
    """
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=str(_workspace()),
        )
    except subprocess.TimeoutExpired:
        return "错误：代码执行超时（超过 15 秒）。"
    output = (proc.stdout or "") + (proc.stderr or "")
    return output.strip() or "(无输出)"


@tool
def list_files(path: str = ".") -> str:
    """列出工作目录（workspace）下的文件。

    Args:
        path: 目录相对路径，默认 "." 表示根目录。
    """
    target = _resolve_safely(path)
    if target is None:
        return f"错误：{path} 在工作目录之外。"
    if not target.exists():
        return f"错误：目录 {path} 不存在。"
    names = sorted(p.name for p in target.iterdir())
    return "\n".join(names) if names else "(空)"


# 暴露给 Agent 的工具列表
TOOLS = [save_code_to_file, read_file, run_python, list_files]
