"""学术搜索模块 — Semantic Scholar / OpenAlex / CORE + 网页抓取"""
import os
import re
from typing import Optional

try:
    import requests
    import urllib3
    urllib3.disable_warnings()
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


def search_semantic_scholar(query: str, max_results: int = 8) -> list:
    """通过 Semantic Scholar API 搜索英文学术文献。免费、无需 Key。"""
    if not HAS_REQUESTS:
        print("⚠  缺少 requests 包")
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


def search_openalex(query: str, max_results: int = 8) -> list:
    """通过 OpenAlex API 搜索学术作品。免费、无需 Key，多语言。"""
    if not HAS_REQUESTS:
        return []

    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per_page": min(max_results, 25),
        "sort": "cited_by_count:desc",
    }
    headers = {"User-Agent": "mailto:caseforge@github.io"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"⚠  OpenAlex 搜索失败: {e}")
        return []

    results = []
    for w in data.get("results", []):
        authors = [a.get("author", {}).get("display_name", "Unknown")
                    for a in w.get("authorships", [])[:3]]

        # 解析 OpenAlex 倒排索引摘要
        abstract = w.get("abstract")  # 可能直接有
        if not abstract:
            inv = w.get("abstract_inverted_index")
            if inv:
                # 倒排索引: {word: [positions]} → 按位置重建文本
                words = sorted(
                    [(pos, word) for word, positions in inv.items() for pos in positions],
                    key=lambda x: x[0]
                )
                abstract = " ".join(w for _, w in words)

        results.append({
            "title":    w.get("title", "Unknown"),
            "abstract": abstract or "No abstract.",
            "year":     w.get("publication_year", "N/A"),
            "authors":  ", ".join(authors),
            "url":      w.get("doi", ""),
            "pdf_url":  w.get("open_access", {}).get("oa_url", ""),
            "source":   "OpenAlex",
        })
    return results


def search_core(query: str, max_results: int = 8) -> list:
    """通过 CORE API 搜索开放获取文献。免费，但需要 API Key。"""
    if not HAS_REQUESTS:
        return []

    # CORE 需要 API Key，没有 Key 时返回空
    # 申请: https://core.ac.uk/services/api
    api_key = os.environ.get("CORE_API_KEY", "")
    if not api_key:
        print("⚠  CORE 需要 API Key（免费申请: https://core.ac.uk/services/api）")
        return []

    params = {
        "q": query,
        "limit": min(max_results, 10),
        "apiKey": api_key,
    }
    try:
        resp = requests.get(
            "https://api.core.ac.uk/v3/search/works",
            params=params, timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"⚠  CORE 搜索失败: {e}")
        return []

    results = []
    for w in data.get("results", []):
        results.append({
            "title":    w.get("title", "Unknown"),
            "abstract": w.get("abstract") or "No abstract.",
            "year":     w.get("yearPublished", "N/A"),
            "authors":  ", ".join(a["name"] for a in w.get("authors", [])[:3]),
            "url":      w.get("downloadUrl", ""),
            "pdf_url":  w.get("downloadUrl", ""),
            "source":   "CORE",
        })
    return results


def search_all(query: str, max_results: int = 5) -> list:
    """聚合搜索所有可用数据库"""
    all_results = []
    for engine, fn in [
        ("Semantic Scholar", search_semantic_scholar),
        ("OpenAlex", search_openalex),
        ("CORE", search_core),
    ]:
        try:
            results = fn(query, max_results)
            print(f"  {engine}: {len(results)} 篇")
            all_results.extend(results)
        except Exception:
            pass
    # 去重（按标题相似度）
    seen = set()
    unique = []
    for r in all_results:
        key = r["title"].lower().strip()[:50]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique[:max_results * 3]


def fetch_url_content(url: str) -> Optional[str]:
    """从 URL 抓取文章正文。CNKI/万方等需登录页面请手动复制。"""
    if not (HAS_REQUESTS and HAS_BS4):
        print("⚠  缺少 requests 或 beautifulsoup4")
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        resp.encoding = resp.apparent_encoding

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
