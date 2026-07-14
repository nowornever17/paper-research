"""
城市设计案例研究助手 — 主程序
==============================
功能：对输入的城市设计案例文章，提取三个维度的精华内容：
      ① 背景与冲突  ② 关键决策或方案  ③ 经验与教训

使用方式：
  python case_extractor.py          # 交互式菜单
  python case_extractor.py --demo   # 运行西溪湿地演示
  python case_extractor.py --tfidf  # 强制使用 TF-IDF 本地方案（不调 API）

首次运行前安装依赖：
  pip install openai requests beautifulsoup4 jieba scikit-learn numpy
"""

# ╔══════════════════════════════════════════════════════╗
# ║         SECTION 1  导入与依赖检查                    ║
# ╚══════════════════════════════════════════════════════╝
import os, sys, json, time, hashlib, re, argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# --- 可选依赖：缺失时对应功能降级，不直接崩溃 ---
def _try_import(mod):
    try:
        return __import__(mod), True
    except ImportError:
        return None, False

_, HAS_OPENAI   = _try_import("openai")
_, HAS_REQUESTS = _try_import("requests")
_, HAS_BS4      = _try_import("bs4")
_, HAS_JIEBA    = _try_import("jieba")
_, HAS_SKLEARN  = _try_import("sklearn")

if HAS_OPENAI:
    from openai import OpenAI
if HAS_REQUESTS:
    import requests
    import urllib3
    urllib3.disable_warnings()          # 屏蔽部分国内站点的 SSL 证书警告
if HAS_BS4:
    from bs4 import BeautifulSoup

# --- 加载配置 ---
try:
    from config import ACTIVE_API, API_REGISTRY, OUTPUT_DIR
except ImportError:
    print("⚠  找不到 config.py，请确保它与本文件在同一目录下。")
    sys.exit(1)

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
CACHE_FILE = os.path.join(OUTPUT_DIR, ".extraction_cache.json")


# ╔══════════════════════════════════════════════════════╗
# ║         SECTION 2  提取 Prompt（核心）               ║
# ╚══════════════════════════════════════════════════════╝
#
# 设计原则：
#   ① 格式严格固定 → 方便程序解析
#   ② 低温度(0.2) → 结果忠于原文，减少"幻觉"
#   ③ 明确说明不足时如实填写 → 避免模型编造内容
#   ④ 结合毕设方向（城市湿地公园）定制"经验与教训"维度

SYSTEM_PROMPT = (
    "你是一位专注于城市设计与公共政策的学术研究助手，"
    "帮助本科毕业生快速理解案例文献的核心价值。\n"
    "请严格基于文章内容进行分析，不要添加原文中不存在的信息。\n"
    "若某维度信息不足，请如实写「文章未明确说明」，不要编造。"
)

USER_PROMPT_TEMPLATE = """\
请对以下案例文章进行结构化精华提取。

【文章标题】
{title}

【文章正文】
{content}

═══════════════════════════════════════════════
请严格按以下格式输出，不要输出任何其他内容：

【背景与冲突】
（该案例的起因、核心矛盾或争议点、涉及的主要利益相关方，2-4句话）

【关键决策或方案】
（最终采用的解决方案、关键规划或政策决策、具体实施举措，2-4句话）

【经验与教训】
启示：（一句话总结，对城市湿地公园开发或城市设计实践的具体启示）
═══════════════════════════════════════════════"""


# ╔══════════════════════════════════════════════════════╗
# ║         SECTION 3  AI API 提取模块                   ║
# ╚══════════════════════════════════════════════════════╝

def _load_cache() -> dict:
    """读本地缓存 —— 避免对相同文章重复调用 API"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_cache(key: str, result: dict):
    """写缓存到本地 JSON"""
    cache = _load_cache()
    cache[key] = result
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def _fingerprint(text: str) -> str:
    """取文章前 500 字的 MD5 作为缓存键"""
    return hashlib.md5(text.strip()[:500].encode("utf-8")).hexdigest()

def _parse_response(raw: str) -> dict:
    """
    解析 AI 返回的结构化文本，提取三个维度。
    采用状态机逐行扫描，兼容模型输出格式略有偏差的情况。
    """
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
                if current_key and buf:          # 保存上一段
                    result[current_key] = "\n".join(buf).strip()
                current_key, buf = key, []
                matched = True
                break
        if not matched and current_key and s:
            buf.append(s)

    if current_key and buf:                      # 保存最后一段
        result[current_key] = "\n".join(buf).strip()

    return result

def call_ai_api(text: str, title: str = "") -> dict:
    """
    调用 AI API 提取三维度精华。

    DeepSeek / 智谱 GLM / 通义千问 三者均实现了 OpenAI 兼容接口，
    所以这里只用 openai 包，改 config.py 中 ACTIVE_API 即可无缝切换。

    参数：
        text   文章正文
        title  文章标题（可选，提高提取质量）
    返回：
        dict { background, decisions, lessons, model, method, raw }
    """
    if not HAS_OPENAI:
        raise ImportError("请先安装 openai 包：pip install openai")

    cfg = API_REGISTRY[ACTIVE_API]
    if not cfg["key"]:
        raise ValueError(
            f"config.py 中 {ACTIVE_API.upper()}_API_KEY 未填写。\n"
            f"请填写密钥，或将 ACTIVE_API 改为已配置的供应商。"
        )

    client = OpenAI(api_key=cfg["key"], base_url=cfg["base_url"])

    # 截断过长文章（避免超出上下文窗口，中文约 3500 字 = ~2000 tokens）
    content = text.strip()[:3500]
    if len(text.strip()) > 3500:
        content += "\n\n（原文较长，已截取前段用于分析）"

    prompt = USER_PROMPT_TEMPLATE.format(
        title=title or "（未提供标题）",
        content=content,
    )

    resp = client.chat.completions.create(
        model=cfg["model"],
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=800,
        temperature=0.2,    # 低温度 = 更忠于原文，减少发挥
    )

    raw = resp.choices[0].message.content.strip()
    parsed = _parse_response(raw)
    return {**parsed, "model": cfg["label"], "method": "ai_api", "raw": raw}


# ╔══════════════════════════════════════════════════════╗
# ║         SECTION 4  TF-IDF 降级方案（完全本地）       ║
# ╚══════════════════════════════════════════════════════╝

def tfidf_fallback(text: str, title: str = "") -> dict:
    """
    TF-IDF 降级方案：不需要任何 API，完全离线运行。

    原理：
      ① jieba 分句并分词
      ② sklearn TF-IDF 计算各句"全局重要性"
      ③ 结合城市设计领域关键词，为每个维度打分
      ④ 返回得分最高的原文句子（注意：是抽取，不是生成）

    优缺点：
      ✓ 免费、快速、完全离线
      ✗ 无法理解语义，句子可能不连贯
      ✗ "经验与教训"维度效果最差（作者不一定直接写这些词）
      → 适合快速过滤，找出值得精读的篇目
    """
    if not HAS_JIEBA:
        return {
            "background": "【需安装 jieba：pip install jieba】",
            "decisions":  "", "lessons": "",
            "model": "TF-IDF（缺少依赖）", "method": "tfidf_error", "raw": "",
        }

    # ── ① 分句 ──
    segs = re.split(r'[。！？；\n]+', text)
    sents = [s.strip() for s in segs if len(s.strip()) >= 12]

    if len(sents) < 3:
        return {
            "background": text.strip()[:300],
            "decisions": "（文章过短，无法提取）",
            "lessons":   "（文章过短，无法提取）",
            "model": "TF-IDF（文章过短）", "method": "tfidf_short", "raw": text,
        }

    # ── ② TF-IDF 打分 ──
    import jieba as _jieba
    def tok(s):
        return " ".join(_jieba.cut(s, cut_all=False))

    scores = [1.0] * len(sents)   # 默认均等权重
    if HAS_SKLEARN:
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            import numpy as np
            vect = TfidfVectorizer(max_features=300, token_pattern=r"(?u)\b\w+\b")
            mat  = vect.fit_transform([tok(s) for s in sents])
            scores = np.array(mat.sum(axis=1)).flatten().tolist()
        except Exception:
            pass   # sklearn 出错时退回均等权重

    # ── ③ 城市设计专项关键词词表 ──
    kw = {
        "background": [
            "冲突", "争议", "矛盾", "问题", "困境", "危机", "压力",
            "批评", "反对", "投诉", "上访", "抗议", "质疑", "纠纷",
            "背景", "起因", "拆迁", "搬迁", "居民", "原住民", "补偿",
            "湿地", "生态", "破坏", "污染", "威胁", "开发商", "利益",
        ],
        "decisions": [
            "方案", "决策", "政策", "规划", "措施", "办法", "计划",
            "实施", "推进", "建立", "设立", "制定", "颁布", "批准",
            "修复", "改造", "整改", "整治", "调整", "优化", "协商",
            "委员会", "机制", "平台", "基金", "标准", "评估", "共治",
        ],
        "lessons": [
            "经验", "教训", "启示", "借鉴", "总结", "反思", "值得",
            "应当", "需要", "建议", "重要", "关键", "必须", "不足",
            "模式", "路径", "意义", "创新", "改进", "提升", "未来",
        ],
    }

    # ── ④ 综合评分，取最相关的句子 ──
    def best(kw_list: list, n: int = 2) -> str:
        ranked = []
        for i, s in enumerate(sents):
            kw_score = sum(1 for w in kw_list if w in s)
            ranked.append((kw_score * 2.0 + scores[i] * 0.5, i, s))
        ranked.sort(reverse=True)
        idxs = sorted(item[1] for item in ranked[:n])
        return "。".join(sents[i] for i in idxs) + "。"

    return {
        "background": best(kw["background"], 2),
        "decisions":  best(kw["decisions"],  2),
        "lessons":    best(kw["lessons"],    1),
        "model":  "TF-IDF 降级方案（本地，无需 API）",
        "method": "tfidf",
        "raw":    text[:300] + "...",
    }


# ╔══════════════════════════════════════════════════════╗
# ║         SECTION 5  统一提取入口                      ║
# ╚══════════════════════════════════════════════════════╝

def extract_case_insights(
    text: str,
    title: str = "",
    force_tfidf: bool = False,
    use_cache: bool = True,
) -> dict:
    """
    ============================================================
    主函数：对一篇文章提取三维度精华（对外暴露的唯一接口）
    ============================================================

    参数：
        text        文章正文（直接粘贴即可，支持任意格式）
        title       文章标题（可选）
        force_tfidf 是否强制使用本地 TF-IDF，不调用 API
        use_cache   是否启用缓存（同一文章不会重复调 API）

    返回：
        {
          "background": "背景与冲突...",
          "decisions":  "关键决策或方案...",
          "lessons":    "启示：...",
          "model":      "使用的模型名称",
          "method":     "ai_api" 或 "tfidf",
          "raw":        "AI 原始输出（调试用）"
        }
    """
    text = text.strip()
    if not text:
        return {
            "background": "【输入文本为空】",
            "decisions": "", "lessons": "",
            "model": "N/A", "method": "empty", "raw": "",
        }

    # ── 查缓存 ──
    cache_key = _fingerprint(text)
    if use_cache:
        cached = _load_cache().get(cache_key)
        if cached:
            print("  ↩  命中缓存，跳过 API 调用")
            return cached

    # ── 强制 TF-IDF ──
    if force_tfidf:
        return tfidf_fallback(text, title)

    # ── 尝试调用 API，失败则自动降级 ──
    try:
        result = call_ai_api(text, title)
        if use_cache:
            _save_cache(cache_key, result)
        return result

    except ValueError as e:
        # 密钥未配置
        print(f"\n  ⚠  API 配置问题：{e}")
        print("  →  自动降级到 TF-IDF 方案\n")
        return tfidf_fallback(text, title)

    except Exception as e:
        print(f"\n  ✗  API 调用失败：{e}")
        print("  →  自动降级到 TF-IDF 方案\n")
        return tfidf_fallback(text, title)


# ╔══════════════════════════════════════════════════════╗
# ║         SECTION 6  学术搜索模块                      ║
# ╚══════════════════════════════════════════════════════╝

def search_semantic_scholar(query: str, max_results: int = 8) -> list:
    """
    通过 Semantic Scholar API 搜索英文学术文献。

    完全免费，无需 API Key，国内可直接访问（偶尔需要重试）。
    适合：搜索 urban wetland / ecological compensation / community participation
    局限：以英文文献为主，中文期刊基本搜不到。

    参数：query 建议用英文，如 "urban wetland park development conflict governance"
    """
    if not HAS_REQUESTS:
        print("⚠  缺少 requests 包：pip install requests")
        return []

    params = {
        "query":  query,
        "limit":  min(max_results, 20),
        "fields": "title,abstract,year,authors,url,openAccessPdf",
    }
    headers = {"User-Agent": "Mozilla/5.0 (academic research tool)"}

    try:
        resp = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params=params, headers=headers, timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"⚠  Semantic Scholar 搜索失败: {e}")
        return []

    results = []
    for p in data.get("data", []):
        results.append({
            "title":    p.get("title", "Unknown"),
            "abstract": p.get("abstract") or "No abstract.",
            "year":     p.get("year", "N/A"),
            "authors":  ", ".join(a["name"] for a in p.get("authors", [])[:3]),
            "url":      p.get("url", ""),
            "pdf_url":  (p.get("openAccessPdf") or {}).get("url"),
            "source":   "Semantic Scholar",
        })
    return results

def fetch_url_content(url: str) -> Optional[str]:
    """
    从 URL 抓取文章正文（适合新闻报道、政府公告、研究院报告）。
    CNKI / 万方等需登录的页面请手动复制，不要用此函数。
    """
    if not (HAS_REQUESTS and HAS_BS4):
        print("⚠  缺少 requests 或 beautifulsoup4")
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        resp.encoding = resp.apparent_encoding   # 自动处理编码，避免乱码

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script","style","nav","header","footer","aside","iframe"]):
            tag.decompose()

        body = (
            soup.find("article") or
            soup.find(class_=re.compile(r"article|content|main|body", re.I)) or
            soup.find("main") or
            soup.body
        )
        if not body:
            return None

        text = body.get_text(separator="\n")
        text = re.sub(r'\n{3,}', '\n\n', text).strip()
        return text if len(text) > 200 else None

    except Exception as e:
        print(f"⚠  抓取失败 ({url[:60]}): {e}")
        return None


# ╔══════════════════════════════════════════════════════╗
# ║         SECTION 7  格式化与保存                      ║
# ╚══════════════════════════════════════════════════════╝

def format_result(result: dict, title: str = "") -> str:
    """在终端美观地打印提取结果"""
    sep = "─" * 52
    return "\n".join([
        "",
        "=" * 52,
        f"  {title or '案例分析'}",
        f"  来源：{result.get('model', '未知')}",
        "=" * 52,
        "",
        "【背景与冲突】",
        result.get("background") or "（未提取到）",
        "",
        "【关键决策或方案】",
        result.get("decisions") or "（未提取到）",
        "",
        "【经验与教训】",
        result.get("lessons") or "（未提取到）",
        "",
        sep,
    ])

def save_results(results: list, prefix: str = "analysis"):
    """
    将提取结果保存为两种格式：
      - Markdown (.md)：可直接插入论文附录，可读性好
      - JSON (.json)：便于后续用 Python 或 Excel 批量处理
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    md_path   = os.path.join(OUTPUT_DIR, f"{prefix}_{ts}.md")
    json_path = os.path.join(OUTPUT_DIR, f"{prefix}_{ts}.json")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 城市设计案例精华摘录\n\n")
        f.write(f"_生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}，")
        f.write(f"共 {len(results)} 篇，模型：{results[0].get('model','') if results else ''}_ \n\n")
        for r in results:
            t = r.get("title", "未知案例")
            f.write(f"## {t}\n\n")
            f.write(f"**背景与冲突**\n\n{r.get('background','未提取到')}\n\n")
            f.write(f"**关键决策或方案**\n\n{r.get('decisions','未提取到')}\n\n")
            f.write(f"**经验与教训**\n\n{r.get('lessons','未提取到')}\n\n")
            f.write("---\n\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n  💾  结果已保存：")
    print(f"      Markdown → {md_path}")
    print(f"      JSON     → {json_path}")
    return md_path, json_path


# ╔══════════════════════════════════════════════════════╗
# ║         SECTION 8  交互式主程序                      ║
# ╚══════════════════════════════════════════════════════╝

def mode_paste(force_tfidf=False):
    """
    模式一：手动粘贴单篇文章（推荐）
    从知网/万方/PDF复制文章内容，粘贴后输入 END 回车结束。
    """
    print("\n┌──────────────────────────────────────────┐")
    print("│  模式一：单篇精华提取                      │")
    print("│  粘贴文章内容，粘贴完毕后输入 END 并回车   │")
    print("└──────────────────────────────────────────┘\n")

    title = input("文章标题（可选，回车跳过）：").strip()
    print('\n粘贴文章内容，完成后另起一行输入 END：')

    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        except EOFError:
            break

    text = "\n".join(lines).strip()
    if not text:
        print("⚠  未检测到输入，已退出。")
        return

    print(f"\n  ⏳  正在分析，约需 5–15 秒...\n")
    result = extract_case_insights(text, title=title, force_tfidf=force_tfidf)
    print(format_result(result, title))

    if input("\n是否保存到文件？(y/n，默认 n): ").strip().lower() == "y":
        save_results([{**result, "title": title}], prefix="single")


def mode_search(force_tfidf=False):
    """
    模式二：Semantic Scholar 学术搜索 + 批量摘要
    先搜索英文文献列表，再对感兴趣的篇目提取三维度精华。
    """
    print("\n┌──────────────────────────────────────────┐")
    print("│  模式二：学术搜索（Semantic Scholar）      │")
    print("│  建议用英文搜索词，效果更好                │")
    print("└──────────────────────────────────────────┘\n")
    print("示例：urban wetland park development conflict community participation\n")

    query = input("请输入搜索词：").strip()
    if not query:
        return

    print("\n  🔍  正在搜索...")
    papers = search_semantic_scholar(query, max_results=8)

    if not papers:
        print("⚠  未找到结果，请换关键词或检查网络。")
        return

    print(f"\n  找到 {len(papers)} 篇相关文献：\n")
    for i, p in enumerate(papers, 1):
        print(f"  [{i}] {p['title']} ({p['year']})")
        print(f"      {p['authors']}")
        if p.get("pdf_url"):
            print(f"      PDF: {p['pdf_url']}")
        print(f"      {p['url']}\n")

    choice = input("输入编号提取精华（多篇用逗号，如 1,3；回车跳过）：").strip()
    if not choice:
        return

    indices = []
    for part in choice.split(","):
        try:
            idx = int(part.strip()) - 1
            if 0 <= idx < len(papers):
                indices.append(idx)
        except ValueError:
            pass

    collected = []
    for idx in indices:
        p = papers[idx]
        text = f"Title: {p['title']}\n\nAbstract: {p['abstract']}"
        print(f"\n  ⏳  正在分析：{p['title'][:50]}...")
        r = extract_case_insights(text, title=p["title"], force_tfidf=force_tfidf)
        r["title"] = p["title"]
        collected.append(r)
        print(format_result(r, p["title"]))

    if collected and input("\n是否保存所有结果？(y/n): ").strip().lower() == "y":
        save_results(collected, prefix="search")


def mode_demo():
    """
    模式三：演示模式（西溪湿地案例）
    同时运行 AI API 和 TF-IDF 两种方案，对比效果。
    """
    try:
        from demo_xixi import XIXI_TITLE, XIXI_TEXT
    except ImportError:
        print("⚠  找不到 demo_xixi.py，请确保它与本文件在同一目录。")
        return

    print(f"\n  演示案例：{XIXI_TITLE}")
    print(f"  文章字数：{len(XIXI_TEXT)} 字\n")

    print("━━━  方案一：AI API  ━━━")
    r_ai = extract_case_insights(XIXI_TEXT, title=XIXI_TITLE)
    print(format_result(r_ai, XIXI_TITLE))

    print("\n━━━  方案二：TF-IDF 本地对比  ━━━")
    r_tf = extract_case_insights(XIXI_TEXT, title=XIXI_TITLE,
                                 force_tfidf=True, use_cache=False)
    print(format_result(r_tf, XIXI_TITLE + "（TF-IDF）"))

    save_results(
        [{**r_ai, "title": XIXI_TITLE},
         {**r_tf, "title": XIXI_TITLE + "（TF-IDF对比）"}],
        prefix="demo_xixi"
    )


def main():
    parser = argparse.ArgumentParser(description="城市设计案例研究助手")
    parser.add_argument("--demo",  action="store_true", help="运行西溪湿地演示")
    parser.add_argument("--tfidf", action="store_true", help="强制 TF-IDF，不调 API")
    args = parser.parse_args()

    bar = "═" * 50
    print(f"\n╔{bar}╗")
    print(f"║  城市设计案例研究助手 v1.0{' ' * 23}║")
    print(f"║  当前 API：{API_REGISTRY[ACTIVE_API]['label']:<38}║")
    print(f"╚{bar}╝")

    if args.demo:
        mode_demo()
        return

    print("\n  请选择工作模式：")
    print("  1  手动粘贴文章 → 三维度精华提取（推荐）")
    print("  2  关键词搜索英文学术文献 → 批量摘要")
    print("  3  演示模式（西溪湿地案例）")

    ch = input("\n请输入选项（1/2/3）：").strip()
    if   ch == "1": mode_paste(force_tfidf=args.tfidf)
    elif ch == "2": mode_search(force_tfidf=args.tfidf)
    elif ch == "3": mode_demo()
    else:           print("无效选项")


if __name__ == "__main__":
    main()
