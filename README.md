# Code Gen Agent（代码生成助手）

> 软件工程 Homework 1 —— 基于 **LangChain + DeepSeek** 的代码生成 Agent
>
> 学号 · 姓名：**2412190129 陈林赟**

## 一、项目简介

Code Gen Agent 是一个命令行交互的代码生成助手：用户用自然语言描述需求，Agent 通过
「输入 → 推理 → 工具调用 → 输出」的循环，生成规范、可直接运行的代码，并自动保存到
`workspace/` 目录；必要时还会执行代码做验证。

项目覆盖了 Agent 开发的核心能力：

| 能力 | 实现方式 |
|------|----------|
| LLM 调用 | LangChain `ChatOpenAI` 对接 DeepSeek（OpenAI 兼容接口） |
| Prompt 设计 | 结构化系统提示 + 少样本（few-shot）示例 |
| 工具集成 | 保存代码 / 读取文件 / 执行 Python / 列举文件 4 个工具 |
| Agent 循环 | ReAct 风格：推理 → 工具调用 → 观察 → 最终回答 |
| 上下文记忆 | 滚动窗口记忆（`ConversationMemory`） |
| 错误处理 | LLM 调用指数退避重试、工具执行异常回填 |

## 二、环境要求

- Python 3.10+（开发环境为 3.11）
- 一个 DeepSeek API Key（也可用 `--mock` 离线演示，无需密钥）

## 三、快速开始

### 1. 安装依赖

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# Windows
copy .env.example .env
# macOS / Linux
cp .env.example .env
```

编辑 `.env`，填入你的 DeepSeek 密钥：

```
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

### 3. 运行

```bash
# 交互模式
python main.py

# 单条需求（非交互，适合脚本/演示）
python main.py --prompt "写一个计算斐波那契第 n 项的函数"

# 离线演示（无需 API Key）
python main.py --mock --prompt "写一个斐波那契函数"
```

生成的代码默认保存在 `workspace/` 目录。

## 四、使用示例

```
你：写一个快速排序函数，要求处理空数组
Agent：已调用 save_code_to_file 保存 quicksort.py ...
      - 文件：workspace/quicksort.py
      - 思路：...
      - 复杂度：...
```

## 五、一键演示与录屏

```bash
python demo.py                       # 自动判断：有 Key 真实调用，无 Key 离线 Mock
python demo.py --real                # 强制真实调用 DeepSeek
python demo.py --mock                # 强制离线 Mock
python demo.py --prompt "写一个快速排序"   # 自定义需求
```

配置好 `.env` 里的 `DEEPSEEK_API_KEY` 后，`python demo.py` 会真实调用 DeepSeek；
未配置 Key 时自动降级为离线 Mock（会打印提示）。1 分钟视频讲解稿见
[demo-script.md](./demo-script.md)。

## 六、测试

```bash
pytest -v
```

测试使用离线 Mock 模型，无需 API Key。

## 七、目录结构

```
code-agent/
├── main.py                 # 命令行入口
├── demo.py                 # 一键演示脚本（录屏用）
├── codegen/                # 核心包
│   ├── config.py           # 配置加载（环境变量/.env）
│   ├── llm.py              # LLM 构建（DeepSeek / Mock）
│   ├── tools.py            # 工具定义
│   ├── prompts.py          # 系统提示 + 少样本
│   ├── memory.py           # 上下文记忆
│   └── agent.py            # Agent 主循环
├── tests/                  # 单元测试
├── workspace/              # 生成代码的输出目录（运行时创建，已 gitignore）
├── requirements.txt
├── .env.example
├── demo-script.md          # 演示视频讲解稿
└── Design.md               # 设计文档
```

## 八、技术栈

- **语言**：Python 3.11
- **Agent 框架**：LangChain（`langchain-core` + `langchain-openai`）
- **LLM**：DeepSeek `deepseek-chat`（OpenAI 兼容 API，可替换为任意兼容服务）

详细设计见 [Design.md](./Design.md)。
