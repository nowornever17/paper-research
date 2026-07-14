"""格式化与保存模块"""
import os
import json
from datetime import datetime


def format_result(result: dict, title: str = "") -> str:
    """在终端美观地打印提取结果（8 字段深度拆解版）"""
    sep = "─" * 52
    fields = [
        ("🌍 研究背景", "background"),
        ("🎯 研究对象/目的", "objective"),
        ("🧪 研究方法", "methods"),
        ("🔬 实验/实证", "experiment"),
        ("📈 核心发现/成果", "findings"),
        ("💡 创新点", "innovation"),
        ("⚖️ 优势与局限", "pros_cons"),
        ("✨ 一句话总结", "summary"),
    ]
    lines = [
        "",
        "=" * 52,
        f"  {title or '论文拆解'}",
        f"  模型：{result.get('model', '未知')} | 方法：{result.get('method', '')}",
        "=" * 52,
    ]
    for label, key in fields:
        val = result.get(key)
        if val:
            lines += ["", f"{label}", val]
    lines += ["", sep]
    return "\n".join(lines)


def save_results(results: list, output_dir: str, prefix: str = "analysis"):
    """保存为 Markdown + JSON 双格式（向后兼容，推荐使用 exporters.save_all）"""
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    md_path   = os.path.join(output_dir, f"{prefix}_{ts}.md")
    json_path = os.path.join(output_dir, f"{prefix}_{ts}.json")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 论文拆解报告\n\n")
        f.write(f"_生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}，")
        f.write(f"共 {len(results)} 篇_\n\n")
        for r in results:
            t = r.get("title", "未知案例")
            f.write(f"## {t}\n\n")
            for label, key in [
                ("研究背景", "background"), ("研究对象/目的", "objective"),
                ("研究方法", "methods"), ("实验/实证", "experiment"),
                ("核心发现/成果", "findings"), ("创新点", "innovation"),
                ("优势与局限", "pros_cons"), ("一句话总结", "summary"),
            ]:
                f.write(f"**{label}**\n\n{r.get(key,'未提取到')}\n\n")
            f.write("---\n\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n  💾  结果已保存：")
    print(f"      Markdown → {md_path}")
    print(f"      JSON     → {json_path}")
    return md_path, json_path
