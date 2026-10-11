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
    """把生成的代码保存到 workspace 目录下的文件。

    适用场景：生成了一段完整代码、需要持久化保存到文件时调用；生成代码后通常都应保存。
    参数 filename：str，要保存的文件名（相对路径），例如 "fibonacci.py" 或 "src/hello.cpp"。
    参数 code：str，要写入的完整代码内容，例如 "def add(a, b): return a + b"。
    返回：字符串，成功返回已保存的字符数与相对路径；失败返回错误原因。
    不适用：只想在回复中展示代码而不落盘时不要用；读取文件内容请用 read_file。
    """
    target = _resolve_safely(filename)
    if target is None:
        return f"错误：文件名 {filename} 试图写到工作目录之外，已拒绝。"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(code, encoding="utf-8")
    return f"已保存 {len(code)} 字符到 {target.relative_to(_workspace().resolve())}"


@tool
def read_file(path: str) -> str:
    """读取 workspace 目录内的文件内容。

    适用场景：需要查看已生成文件的内容、获取上下文，或确认文件是否已保存时调用。
    参数 path：str，文件相对路径，例如 "fibonacci.py"。
    返回：字符串，文件内容；文件不存在或路径越界时返回错误提示。
    不适用：要写文件用 save_code_to_file，要执行代码用 run_python，要列目录用 list_files。
    """
    target = _resolve_safely(path)
    if target is None:
        return f"错误：{path} 在工作目录之外，已拒绝读取。"
    if not target.exists():
        return f"错误：文件 {path} 不存在。"
    return target.read_text(encoding="utf-8")


@tool
def run_python(code: str) -> str:
    """在子进程中执行一段 Python 代码并返回输出。

    适用场景：生成代码后想运行验证正确性，或需要实际执行一段 Python 时调用。
    参数 code：str，要执行的 Python 代码，例如 "print(sum(range(10)))"。
    返回：字符串，标准输出与标准错误的合并内容；超时或空输出时有对应提示。
    不适用：只想生成代码而不运行；或代码不是 Python（如 C++ 需编译）时不要用。
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
    """列出 workspace 目录下的文件。

    适用场景：想确认已生成了哪些文件、或查看目录结构时调用。
    参数 path：str，目录相对路径，默认 "." 表示根目录，例如 "."。
    返回：字符串，文件名列表（每行一个）；空目录返回 "(空)"。
    不适用：要读文件内容用 read_file，要写文件用 save_code_to_file。
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
