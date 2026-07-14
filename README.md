# CaseForge

> Turn papers into structured knowledge. · v2.0

[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://python.org)
[![API](https://img.shields.io/badge/API-5%20providers-green)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)](./LICENSE)
[![CI](https://img.shields.io/badge/CI-passing-brightgreen)]()

## ✨ What is CaseForge?

CaseForge 将学术论文转换为结构化的知识报告。

```
  📄 论文 PDF / 粘贴文本
        │
        ▼
  CaseForge Pipeline
        │
        ▼
  📊 结构化知识报告（HTML / MD / JSON / Word）
```

不是"AI 帮你读论文"，而是"AI 帮你把论文拆成一张信息表格"。

## 🔬 8 字段深度拆解

| 字段 | 说明 |
|------|------|
| 🌍 研究背景 | 社会/学术背景，要解决什么问题 |
| 🎯 研究对象/目的 | 研究对象是什么，研究目标 |
| 🧪 研究方法 | 定量/定性？数据来源？分析框架？ |
| 🔬 实验/实证 | 实验设计、数据收集、分析方法 |
| 📈 核心发现/成果 | 最重要的研究结论 |
| 💡 创新点 | 相比已有研究的创新之处 |
| ⚖️ 优势与局限 | 长处 + 不足或适用范围 |
| ✨ 一句话总结 | 核心贡献一句话 |

## 🚀 快速开始

```bash
git clone https://github.com/nowornever17/CaseForge.git
cd CaseForge
pip install -r requirements.txt
cp config.example.py config.py    # 填入任意一家 API Key
python main.py --demo             # 西溪湿地案例演示
python main.py --file paper.pdf   # 直接分析 PDF
python main.py --api zhipu        # 切换到免费智谱 API
```

## 🌐 3 大论文库 + 5 家 AI

| 搜索 | API | 特点 |
|------|-----|------|
| Semantic Scholar | — | 免费，英文为主 |
| OpenAlex | — | 免费，2.5 亿篇，多语言 |
| CORE | 免费 Key | 全球开放获取仓库 |
| DeepSeek | ¥0.15/100篇 | 几乎免费 |
| 智谱 GLM | **免费** | 每天 10 万 tokens |
| 通义千问 | ¥300 试用金 | 阿里云 |
| Moonshot | 按量付费 | 长文本强 |
| 百度文心 | 免费额度 | 中文优化 |

## 🛠 CLI

```bash
python main.py --help           # 帮助
python main.py --demo           # 演示
python main.py --file <路径>    # 分析文件
python main.py --api <name>     # 切换 API
python main.py --list-apis      # 列出 API
python main.py --tfidf          # 强制本地方案
```

## 📁 项目结构

```
├── main.py              # CLI 入口
├── api_client.py        # AI 调用 + Prompt 加载
├── search.py            # Semantic Scholar / OpenAlex / CORE
├── pdf_reader.py        # PDF / TXT / MD 解析
├── exporters.py         # MD / JSON / Word / HTML 输出
├── formatter.py         # 终端格式化
├── cache.py             # 去重缓存
├── case_extractor.py    # TF-IDF 降级 + 向后兼容
├── prompts/             # Prompt 插件（多学科可扩展）
└── tests/               # 测试
```

## 🔌 插件化架构

新增学科不需要改代码，只需在 `prompts/` 下新建一个 `.md` 文件：

```
prompts/
├── urban_design.md    ← 城市设计（默认）
├── education.md       ← 教育学（示例）
└── medicine.md        ← 任何人都可以加
```

详见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## ⚠️ 已知限制

- PDF 仅支持文本型，纯扫描图片 PDF 需 OCR（未来版本）
- 单篇文章截取前 3500 字分析（受 API 上下文窗口限制）
- CNKI / 万方等需登录的学术数据库无法直接抓取

## 🤝 贡献

欢迎提 Issue 和 PR — 特别是贡献新的学科 Prompt！

详见 [CONTRIBUTING.md](./CONTRIBUTING.md) · [CHANGELOG.md](./CHANGELOG.md)
