"""输出格式模块 — Markdown / JSON / Word"""
import os
import json
from datetime import datetime


def save_markdown(results: list, output_dir: str, prefix: str = "analysis") -> str:
    """保存为 Markdown"""
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    path = os.path.join(output_dir, f"{prefix}_{ts}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# 案例精华摘录\n\n")
        f.write(f"_生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}，")
        f.write(f"共 {len(results)} 篇_\n\n")
        for r in results:
            t = r.get("title", "未知案例")
            f.write(f"## {t}\n\n")
            f.write(f"**背景与冲突**\n\n{r.get('background','未提取到')}\n\n")
            f.write(f"**关键决策或方案**\n\n{r.get('decisions','未提取到')}\n\n")
            f.write(f"**经验与教训**\n\n{r.get('lessons','未提取到')}\n\n")
            f.write("---\n\n")
    return path


def save_json(results: list, output_dir: str, prefix: str = "analysis") -> str:
    """保存为 JSON"""
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    path = os.path.join(output_dir, f"{prefix}_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return path


def save_docx(results: list, output_dir: str, prefix: str = "analysis") -> str:
    """保存为 Word 文档 (.docx)

    需要: pip install python-docx
    """
    try:
        from docx import Document
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        print("⚠  需要安装 python-docx: pip install python-docx")
        return ""

    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    path = os.path.join(output_dir, f"{prefix}_{ts}.docx")

    doc = Document()

    # 标题
    title = doc.add_heading('案例精华摘录', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 元信息
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_run = meta.add_run(
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}　共 {len(results)} 篇"
    )
    meta_run.font.size = Pt(10)
    meta_run.font.color.rgb = RGBColor(128, 128, 128)

    for r in results:
        doc.add_heading(r.get("title", "未知案例"), level=1)

        doc.add_heading("背景与冲突", level=2)
        doc.add_paragraph(r.get("background", "未提取到"))

        doc.add_heading("关键决策或方案", level=2)
        doc.add_paragraph(r.get("decisions", "未提取到"))

        doc.add_heading("经验与教训", level=2)
        doc.add_paragraph(r.get("lessons", "未提取到"))

        doc.add_paragraph("—" * 30)

    doc.save(path)
    return path


def save_all(results: list, output_dir: str, prefix: str = "analysis") -> dict:
    """保存为所有支持格式"""
    paths = {
        "md": save_markdown(results, output_dir, prefix),
        "json": save_json(results, output_dir, prefix),
    }
    docx_path = save_docx(results, output_dir, prefix)
    if docx_path:
        paths["docx"] = docx_path

    print(f"\n  💾  结果已保存：")
    for fmt, p in paths.items():
        print(f"      {fmt.upper():6s} → {p}")
    return paths
