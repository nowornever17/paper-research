"""AI API 调用模块 — 支持 DeepSeek / 智谱 / 通义 / Moonshot / 文心"""
import os
from typing import Optional

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def _load_prompt(discipline: str = "urban_design") -> str:
    """从 prompts/ 目录加载对应学科的 prompt 模板。

    支持学科: urban_design (城市设计), education (教育学)
    自定义: 在 prompts/ 下新建 <discipline>.md 即可
    """
    prompt_dir = os.path.join(os.path.dirname(__file__), "prompts")

    # 先尝试加载指定学科的 prompt
    prompt_path = os.path.join(prompt_dir, f"{discipline}.md")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    # Fallback: 默认 prompt (extract.md)
    default_path = os.path.join(prompt_dir, "extract.md")
    if os.path.exists(default_path):
        with open(default_path, "r", encoding="utf-8") as f:
            return f.read()
    return """你是一位专注于城市设计与公共政策的学术研究助手。
请严格基于文章内容进行分析，不要添加原文中不存在的信息。
若某维度信息不足，请如实写「文章未明确说明」，不要编造。

请对以下案例文章进行结构化精华提取。

【文章标题】
{title}

【文章正文】
{content}

═══════════════════════════════════════════════
请严格按以下格式输出：

【背景与冲突】
（2-4句话）

【关键决策或方案】
（2-4句话）

【经验与教训】
启示：（一句话总结）
═══════════════════════════════════════════════"""


def _parse_response(raw: str) -> dict:
    """状态机解析 AI 返回的结构化文本"""
    result = {"background": "", "decisions": "", "lessons": ""}
    markers = {
        "【背景与冲突】":    "background",
        "【关键决策或方案】": "decisions",
        "【经验与教训】":    "lessons",
    }
    current_key, buf = None, []

    for line in raw.split("\n"):
        s = line.strip()
        matched = False
        for marker, key in markers.items():
            if marker in s:
                if current_key and buf:
                    result[current_key] = "\n".join(buf).strip()
                current_key, buf = key, []
                matched = True
                break
        if not matched and current_key and s:
            buf.append(s)

    if current_key and buf:
        result[current_key] = "\n".join(buf).strip()

    return result


def call_ai_api(text: str, title: str = "", api_config: Optional[dict] = None) -> dict:
    """
    调用 AI API 提取三维度精华。

    参数：
        text       文章正文
        title      文章标题（可选）
        api_config API 配置字典，包含 key/base_url/model/label
    返回：
        dict { background, decisions, lessons, model, method, raw }
    """
    if not HAS_OPENAI:
        raise ImportError("请先安装 openai 包：pip install openai")

    if not api_config or not api_config.get("key"):
        raise ValueError("API 密钥未配置，请在 config.py 中填写对应 API_KEY")

    client = OpenAI(api_key=api_config["key"], base_url=api_config["base_url"])

    # 截断过长文章（中文约 3500 字）
    content = text.strip()[:3500]
    if len(text.strip()) > 3500:
        content += "\n\n（原文较长，已截取前段用于分析）"

    prompt_template = _load_prompt()
    prompt = prompt_template.format(
        title=title or "（未提供标题）",
        content=content,
    )

    resp = client.chat.completions.create(
        model=api_config["model"],
        messages=[
            {"role": "system", "content": prompt_template.split("---")[0].strip()},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=800,
        temperature=0.2,
    )

    raw = resp.choices[0].message.content.strip()
    parsed = _parse_response(raw)
    return {**parsed, "model": api_config["label"], "method": "ai_api", "raw": raw}
