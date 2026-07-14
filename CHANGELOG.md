# Changelog

## v1.5 (2026-07-14)
- 新增 `pdf_reader.py` — 支持 PDF/TXT/MD 文件直接分析
- `--file` CLI 参数
- 修复 skill 文件中的个人信息泄露

## v1.2 (2026-07-14)
- 模块化重构：拆分为 api_client / cache / search / formatter
- Prompt 外置到 `prompts/extract.md`
- 移除硬编码路径
- 新增 Moonshot (Kimi) + 百度文心 ERNIE API
- CLI: `--help` / `--list-apis` / `--api`

## v1.1 (2026-07-09)
- 初始版本
- DeepSeek + 智谱 + 通义 三 API 支持
- TF-IDF 降级方案
- 西溪湿地 demo
- 交互式三模式菜单
