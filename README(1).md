# 城市设计案例研究助手

> AI 驱动的学术案例文献精华提取工具 · v1.6

[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://python.org)
[![API](https://img.shields.io/badge/API-5%20providers-green)]()

## ✨ 功能

- 🔍 **自动提取三维度精华** — 背景与冲突 / 关键决策 / 经验教训
- 🌐 **学术搜索** — Semantic Scholar 英文文献搜索 + AI 批量摘要
- 🤖 **5 家 AI API** — DeepSeek / 智谱(免费) / 通义 / Moonshot(Kimi) / 文心
- 📦 **降级保护** — API 失败自动切本地 TF-IDF，不中断工作流
- 💾 **双格式输出** — Markdown + JSON
- ⚡ **去重缓存** — 同一篇文章不重复调用 API
- 🎬 **Demo 开箱即用** — `demo_xixi.py` 西溪湿地案例一秒体验

## 🚀 快速开始

```bash
pip install -r requirements.txt
cp config.example.py config.py    # 填入任意一家 API Key
python main.py                    # 交互式菜单
python main.py --demo             # 演示模式
python main.py --file paper.pdf   # 直接分析 PDF/TXT/MD 文件
python main.py --api zhipu        # 切换免费智谱
```

## 🏗 工作流程

```
  PDF / TXT / MD / 粘贴
        │
        ▼
  pdf_reader.py (v1.5+)
        │
        ▼
  api_client.py  ←── prompts/extract.md
        │
        ├─✅ 成功 → formatter.py → .md + .json
        │
        └─❌ 失败 → case_extractor.py (TF-IDF 降级)
                     │
                     └─ formatter.py → .md + .json
```

## 📁 项目结构

```
├── main.py              # 入口 + CLI
├── api_client.py        # AI API 调用（可切换 5 家供应商）
├── pdf_reader.py        # PDF/TXT/MD 文件解析（pdfplumber + markitdown）
├── search.py            # Semantic Scholar + 网页抓取
├── cache.py             # 去重缓存
├── formatter.py         # 格式化 + 保存
├── case_extractor.py    # TF-IDF 降级方案 + 向后兼容
├── config.example.py    # 配置模板（不含真实 Key）
├── demo_xixi.py         # 西溪湿地演示
├── prompts/
│   └── extract.md       # AI Prompt 模板（可独立编辑）
└── requirements.txt     # Python 依赖
```

## 🛠 CLI 命令

```bash
python main.py --help           # 帮助
python main.py --file <路径>     # 直接分析文件（PDF/TXT/MD）
python main.py --list-apis      # 列出所有 API
python main.py --api <name>     # 切换 API 供应商
python main.py --tfidf          # 强制本地 TF-IDF
python main.py --demo           # 西溪湿地演示
```

## ⚠️ 已知限制

- PDF 仅支持文本型，纯扫描图片 PDF 需 OCR（未来版本）
- Semantic Scholar 以英文文献为主，中文文献需手动粘贴
- 单篇文章截取前 3500 字分析（受 API 上下文窗口限制）
- CNKI / 万方等需登录的学术数据库无法直接抓取

## 🤝 贡献

欢迎提 Issue 和 PR。详见 [CHANGELOG.md](./CHANGELOG.md)。
