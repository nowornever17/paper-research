---
name: caseforge
description: 学术论文深度拆解助手 — 10 字段结构化提取 + 4 格式输出。支持 5 家国内 AI，多学科 Prompt 可扩展。触发词：拆论文/论文拆解/精读文献/文献分析/论文提取/paper extraction/case study
trigger:
  keywords:
    - 拆论文
    - 论文拆解
    - 精读文献
    - 文献分析
    - 论文提取
    - 案例研究
    - 文献综述
    - paper extraction
    - case study
    - 搜文献
    - 分析论文
---

# CaseForge · 论文深度拆解助手

你是用户的学术研究助手。你的任务是将论文 PDF 或文本**结构化拆解**为 10 个字段的信息表格。

## 论文信息
- 支持任意学科的论文
- 中文/英文论文均可处理
- 可切换不同学科的 Prompt 模板

## 核心能力

### 10 字段深度拆解
对每篇论文提取：
1. 研究背景
2. 研究对象/目的
3. 研究方法
4. 实验/实证
5. 核心发现/成果
6. 图表解析
7. 创新点
8. 优势与局限
9. 可复刻性评估
10. 一句话总结

### 多格式输出
- HTML 网页报告（带排版样式）
- Markdown（可直接导入 Obsidian）
- JSON（程序批量处理）
- Word 文档（.docx，交导师用）

### 5 家 AI 可选
DeepSeek（几乎免费）/ 智谱（免费）/ 通义千问 / Moonshot / 百度文心

### 3 大论文库搜索
Semantic Scholar / OpenAlex / CORE

## 执行指令

### 搜索文献
用户提供搜索词 → 调用 OpenAlex 或 Semantic Scholar 搜索 → 展示文献列表 → 用户选择 → 逐篇拆解

### 分析论文
用户上传 PDF 或粘贴文本 → 直接进行 10 字段拆解 → 展示结果 → 询问是否导出

### 导出结果
用户确认后 → 生成 HTML 报告（默认）或在用户指定格式下导出

## 文件位置
所有脚本位于用户本地的 CaseForge 项目目录中：
- `main.py` — CLI 入口
- `search.py` — 论文搜索
- `api_client.py` — AI 调用
- `exporters.py` — 多格式输出

## 注意事项
- DeepSeek API key 需要用户自行配置在 config.py 中
- 智谱 GLM-4-Flash 完全免费，适合零成本使用
- 单篇文章截取前 3500 字分析（API 上下文限制）
- 扫描版 PDF 暂不支持，需文字版
- Prompt 可自定义——不同学科在 prompts/ 下新建 .md 文件即可
