"""Code Gen Agent —— 基于 LangChain + DeepSeek 的代码生成助手。"""
from .agent import CodeGenAgent
from .config import load_config

__all__ = ["CodeGenAgent", "load_config"]
__version__ = "1.0.0"
