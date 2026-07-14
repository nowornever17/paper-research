# 贡献指南

感谢你对 Paper Research 的兴趣！

## 如何贡献

### 最低门槛：贡献 Prompt

不需要懂 Python！只需要在你熟悉的领域写好一个 Prompt 模板即可：

1. 在 `prompts/<你的学科>/` 下新建 `extract.md`
2. 参考 `prompts/urban_design/extract.md` 的格式
3. 提交 PR

示例：如果你是教育学背景，创建 `prompts/education/extract.md`，设计适合教育案例研究的三维度提取模板。

### 中等门槛：新增 AI Provider

1. 在 `config.example.py` 的 `API_REGISTRY` 中新增一个条目
2. 确认 base_url 和 model 参数正确
3. 测试通过后提交 PR

### 高级门槛：新增 Reader / Exporter

- **Reader**: 实现 read_file() 接口，支持新文件格式
- **Exporter**: 实现 save 接口，支持新输出格式（CSV/BibTeX 等）

## 开发规范

```bash
pip install -r requirements.txt
pip install pytest ruff

# 运行测试
python -m pytest tests/ -v

# 代码检查
ruff check .
```

## Commit 规范

```
feat: 新增 xxx 功能
fix: 修复 xxx 问题
docs: 更新文档
test: 新增测试
refactor: 重构 xxx
```

## 分支策略

- `main` — 稳定版本
- `feat/xxx` — 新功能分支
- 提交 PR 到 `main`

## 行为准则

- 保持友善和尊重
- 欢迎不同学科背景的贡献者
- 提问前先搜索已有 Issue
