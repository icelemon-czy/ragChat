# Tongyi RAG Desktop Application

这是一个基于 **Python**, **Qt5 (PyQt5)**, **LangChain** 和 **ChromaDB** 构建的本地桌面 RAG (检索增强生成) 应用程序。它集成了阿里云的 **通义千问 (Qwen)** 大模型，允许用户构建本地知识库（支持本地文件上传）并基于该知识库进行智能问答。

## ✨ 核心特性

*   **⚡️ 全异步无阻塞 UI**: 采用 `qasync` 深度集成 `asyncio` 与 Qt 事件循环，确保在文件解析、生成回答或处理向量数据时界面保持流畅响应。
*   **🤖 通义千问集成**: 内置阿里云 DashScope SDK，支持流式 (Streaming) 输出，提供打字机式的对话体验。
*   **📚 本地向量知识库**: 
    *   使用 **ChromaDB** 进行本地数据存储与检索。
    *   支持 **直接上传本地文件** (PDF, DOCX, TXT, MD)，自动提取文本内容。
    *   自动文本切分 (Chunking) 与去重展示。
*   **🎨 现代 UI 设计**: 
    *   **聊天界面**: 气泡式对话，支持 Markdown 渲染。
    *   **知识库面板**: 列表式文档管理，支持**平滑滚动 (Pixel-perfect scrolling)**，淡紫色标题与优雅的分割线设计。
    *   **Dark Mode 适配**: 强制适配浅色主题，解决 macOS Dark Mode 下的显示问题。
*   **💾 数据持久化**: 数据库文件自动存储于系统应用数据目录，重启后数据不丢失。

## 🛠️ 技术栈

*   **GUI 框架**: PyQt5
*   **异步运行库**: qasync
*   **LLM 编排**: LangChain
*   **大模型 API**: Alibaba Tongyi (Qwen-Plus)
*   **向量数据库**: ChromaDB
*   **文件解析**: Unstructured (支持 PDF, DOCX 等)

## 📂 项目结构

```text
RagDataBase/
├── main.py                 # 程序入口，负责 API Key 检查和 qasync 事件循环启动
├── requirements.txt        # Python 依赖列表
├── services/
│   └── rag_service.py      # 核心服务层：封装 ChromaDB读写、文解析及 LLM 调用
└── ui/
    ├── mainwindow.py       # 主窗口布局
    ├── chat_widget.py      # 左侧：聊天主要逻辑与视图
    ├── chat_model.py       # 聊天数据模型
    └── knowledge_widget.py # 右侧：知识库管理，支持文件上传与预览
```

## 🚀 快速开始

### 1. 环境准备
确保您的系统安装了 Python 3.8+。
**macOS 用户** 如果需要处理 PDF 文件，建议安装以下系统库：
```bash
brew install libmagic poppler tesseract
```

### 2. 安装依赖
在项目根目录下运行：
```bash
pip install -r requirements.txt
```

### 3. 配置 API Key
您需要一个阿里云 DashScope 的 API Key。
*   可以在 `main.py` 中设置 `DEFAULT_API_KEY` 以免去每次输入。
*   或者在程序启动弹窗中输入。

### 4. 运行应用
```bash
python main.py
```

## 📖 使用指南

1.  **添加知识库**:
    *   **方式一**: 点击 "📂 Upload Local File" 选择本地 PDF 或 Word 文档，系统会自动解析并填充内容。
    *   **方式二**: 手动输入文档标题和正文内容。
    *   点击 "Save to Knowledge Base" 保存。上方列表会显示文档摘要预览。

2.  **开始对话**:
    *   在左侧聊天框输入与知识库相关的问题。
    *   AI 将检索相关片段，并生成基于文档的回答。

## ⚠️ 注意事项

*   **ChromaDB 兼容性**: 在某些 Windows/Mac 环境下，ChromaDB 可能需要安装 SQLite3 的特定版本。
*   **Token 消耗**: 使用通义千问 API 会产生相应的 Token 费用。
