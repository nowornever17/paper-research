# 城市设计案例研究助手

> AI 驱动的学术案例文献精华提取工具

## 功能

输入一篇城市设计/公共政策案例文章 → DeepSeek AI 自动提取三个维度的结构化精华：

- 🔍 **背景与冲突** — 核心矛盾、争议点、利益相关方
- 🏗️ **关键决策或方案** — 政策措施、规划方案、实施举措
- 💡 **经验与教训** — 一句话启示

## 两种模式

| 模式 | 方案 | 特点 |
|------|------|------|
| AI API | DeepSeek / 智谱 / 通义千问 | 理解语义，生成连贯结论 |
| TF-IDF | 本地 jieba + sklearn | 免费、离线、应急备用 |

API 失败时自动降级到 TF-IDF，不会中断工作流。

## 快速开始

```bash
pip install -r requirements.txt
cp config.example.py config.py  # 填入你的 API Key
python case_extractor.py        # 交互式菜单
python demo_xixi.py             # 西溪湿地演示对比
```

## 论文选题

《基于空间公平理念的万丰湖片区滨湖核心地段城市设计》
—— 株洲市天元区万丰湖片区 · 空间公平 · 可达性分析

## 文件结构

```
├── case_extractor.py    # 主程序
├── config.example.py    # 配置模板（不含真实 Key）
├── demo_xixi.py         # 西溪湿地演示案例
├── requirements.txt     # Python 依赖
└── research_output/     # 提取结果输出（MD + JSON）
```
