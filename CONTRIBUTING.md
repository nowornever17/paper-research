# ✨ 贡献指南

感谢你对 CaseForge 的兴趣！无论你的技术背景如何，都有你可以贡献的地方。

## 我能贡献什么？

| 门槛 | 贡献类型 | 时间 | 例子 |
|------|---------|------|------|
| 🟢 最低 | Prompt 模板 | 30 分钟 | 为你的学科写一个提取模板 |
| 🟡 中等 | AI Provider | 1 小时 | 接入新的 LLM API |
| 🔴 高级 | Reader / Exporter | 2 小时 | 支持新文件格式或输出格式 |
| 📚 文档 | 翻译、示例 | 1 小时 | 翻译 README，提供使用案例 |

## 🟢 最快上手：贡献一个 Prompt 模板（30 分钟）

不需要懂 Python！只需在你熟悉的领域写好提取模板即可。

### 步骤

1. **Fork** 本仓库
2. 在 `prompts/` 下创建你的学科文件，如 `prompts/psychology.md`
3. 参考已有模板（`prompts/urban_design.md`）的格式
4. 用 3-5 篇真实论文测试你的模板
5. 提交 PR，标题格式：`feat: add psychology prompt template`

### 模板格式

```markdown
你是一位[学科]研究助手。请严格基于论文内容提取信息，不要编造。

请对以下论文进行结构化拆解：

【论文标题】
{title}

【论文正文】
{content}

═══════════════════════════════════════════════
请按以下格式输出：

【研究背景】（2-4 句话）
【研究对象/目的】（1-2 句话）
【研究方法】（3-5 句话）
【核心发现/成果】（要点列表）
【创新点】（1-2 句话）
【优势与局限】（各 1-2 句话）
【一句话总结】
═══════════════════════════════════════════════
```

### PR 描述模板

```
## 学科背景
[你的学科]

## 适用场景
[这个模板适合什么类型的论文]

## 测试论文
- [论文 1 标题/链接]
- [论文 2 标题/链接]
- [论文 3 标题/链接]
```

## 🟡 新增 AI Provider

在 `config.example.py` 的 `API_REGISTRY` 中新增一个条目：

```python
"your_provider": {
    "key":      YOUR_API_KEY,
    "base_url": "https://api.example.com",
    "model":    "model-name",
    "label":    "Provider Name",
},
```

确认 `base_url` 兼容 OpenAI 接口格式后提交 PR。

## 🔴 新增 Reader / Exporter

- **Reader**：实现 `read_file()` 接口，支持新格式（EPUB、HTML 等）
- **Exporter**：实现 `save` 接口，支持新输出格式（CSV、BibTeX 等）

## 开发规范

```bash
pip install -r requirements.txt
pip install pytest ruff

# 测试
python -m pytest tests/ -v

# Lint
ruff check .
```

## Commit 规范

```
feat: 新增 xxx
fix: 修复 xxx
docs: 更新文档
test: 新增测试
```

## 行为准则

- 保持友善和尊重
- 欢迎不同学科背景的贡献者
- 提问前先搜索已有 Issue
