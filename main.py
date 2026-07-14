"""
城市设计案例研究助手 v1.7 — 插件化版
==========================================
用法:
  python main.py                    # 交互式菜单
  python main.py --demo             # 西溪湿地演示
  python main.py --file paper.pdf   # 直接分析 PDF/TXT/MD 文件
  python main.py --api zhipu        # 切换 API
  python main.py --list-apis        # 列出 API
  python main.py --tfidf            # 强制本地 TF-IDF

首次使用: pip install -r requirements.txt
"""

import os
import sys
import argparse
from pathlib import Path

# 确保能找到同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ACTIVE_API, API_REGISTRY, OUTPUT_DIR
from api_client import call_ai_api
from search import search_semantic_scholar, fetch_url_content
from formatter import format_result, save_results
from cache import get_cached_or_none, save_cache, _fingerprint
from pdf_reader import read_file as read_pdf_file

CACHE_FILE = os.path.join(OUTPUT_DIR, ".extraction_cache.json")
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


def extract_case_insights(text: str, title: str = "", force_tfidf: bool = False, use_cache: bool = True) -> dict:
    """
    主函数：对一篇文章提取三维度精华
    """
    text = text.strip()
    if not text:
        return {"background": "【输入文本为空】", "decisions": "", "lessons": "",
                "model": "N/A", "method": "empty", "raw": ""}

    if use_cache:
        cached = get_cached_or_none(CACHE_FILE, text)
        if cached:
            return cached

    if force_tfidf:
        from case_extractor import tfidf_fallback
        return tfidf_fallback(text, title)

    try:
        result = call_ai_api(text, title, API_REGISTRY[ACTIVE_API])
        if use_cache:
            save_cache(CACHE_FILE, _fingerprint(text), result)
        return result
    except Exception as e:
        print(f"\n  ⚠  API 调用失败：{e}\n  →  自动降级到 TF-IDF 方案\n")
        from case_extractor import tfidf_fallback
        return tfidf_fallback(text, title)


# ── 交互式模式 ──

def mode_paste(force_tfidf=False):
    """模式一：手动粘贴单篇文章"""
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
    print(f"\n  ⏳  正在分析...\n")
    result = extract_case_insights(text, title=title, force_tfidf=force_tfidf)
    print(format_result(result, title))
    if input("\n是否保存到文件？(y/n): ").strip().lower() == "y":
        save_results([{**result, "title": title}], OUTPUT_DIR, prefix="single")


def mode_search(force_tfidf=False):
    """模式二：学术搜索 + 批量摘要"""
    print("\n┌──────────────────────────────────────────┐")
    print("│  模式二：学术搜索（Semantic Scholar）      │")
    print("│  建议用英文搜索词，效果更好                │")
    print("└──────────────────────────────────────────┘\n")
    query = input("请输入搜索词：").strip()
    if not query:
        return
    print("\n  🔍  正在搜索...")
    papers = search_semantic_scholar(query, max_results=8)
    if not papers:
        print("⚠  未找到结果。")
        return
    print(f"\n  找到 {len(papers)} 篇文献：\n")
    for i, p in enumerate(papers, 1):
        print(f"  [{i}] {p['title']} ({p['year']})")
        print(f"      {p['authors']}\n")
    choice = input("输入编号提取精华（逗号分隔，回车跳过）：").strip()
    if not choice:
        return
    collected = []
    for part in choice.split(","):
        try:
            idx = int(part.strip()) - 1
            if 0 <= idx < len(papers):
                p = papers[idx]
                text = f"Title: {p['title']}\n\nAbstract: {p['abstract']}"
                print(f"\n  ⏳  正在分析：{p['title'][:50]}...")
                r = extract_case_insights(text, title=p["title"], force_tfidf=force_tfidf)
                r["title"] = p["title"]
                collected.append(r)
                print(format_result(r, p["title"]))
        except ValueError:
            pass
    if collected and input("\n是否保存？(y/n): ").strip().lower() == "y":
        save_results(collected, OUTPUT_DIR, prefix="search")


def mode_demo():
    """模式三：西溪湿地演示"""
    try:
        from demo_xixi import XIXI_TITLE, XIXI_TEXT
    except ImportError:
        print("⚠  找不到 demo_xixi.py")
        return
    print(f"\n  演示案例：{XIXI_TITLE} ({len(XIXI_TEXT)} 字)\n")
    print("━━━  AI API ━━━")
    r_ai = extract_case_insights(XIXI_TEXT, title=XIXI_TITLE)
    print(format_result(r_ai, XIXI_TITLE))
    print("\n━━━  TF-IDF 对比 ━━━")
    r_tf = extract_case_insights(XIXI_TEXT, title=XIXI_TITLE, force_tfidf=True, use_cache=False)
    print(format_result(r_tf, XIXI_TITLE + "（TF-IDF）"))
    save_results(
        [{**r_ai, "title": XIXI_TITLE}, {**r_tf, "title": XIXI_TITLE + "（TF-IDF对比）"}],
        OUTPUT_DIR, prefix="demo_xixi"
    )


def main():
    global ACTIVE_API
    parser = argparse.ArgumentParser(
        description="城市设计案例研究助手 v1.7 — AI 学术案例精华提取",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                  # 交互式菜单
  python main.py --demo           # 西溪湿地演示
  python main.py --api zhipu      # 切换智谱（免费）
  python main.py --list-apis      # 列出 API
        """
    )
    parser.add_argument("--demo",      action="store_true", help="运行西溪湿地演示")
    parser.add_argument("--tfidf",     action="store_true", help="强制 TF-IDF 本地方案")
    parser.add_argument("--api",       type=str, metavar="NAME", help="切换 API 供应商")
    parser.add_argument("--list-apis", action="store_true", help="列出所有 API")
    parser.add_argument("--file",      type=str, metavar="PATH", help="直接分析文件 (PDF/TXT/MD)")
    args = parser.parse_args()

    if args.list_apis:
        print("\n📡 支持的 AI API：\n")
        for k, v in API_REGISTRY.items():
            marker = " ← 当前" if k == ACTIVE_API else ""
            print(f"  {k:12s}  {v['label']:30s}  [{('已配置' if v['key'] else '未配置')}]{marker}")
        return

    if args.api:
        if args.api not in API_REGISTRY:
            print(f"❌ 未知 API: {args.api} | 可用: {', '.join(API_REGISTRY.keys())}")
            return
        ACTIVE_API = args.api
        print(f"✅ 已切换至: {API_REGISTRY[ACTIVE_API]['label']}")

    bar = "═" * 50
    print(f"\n╔{bar}╗")
    print(f"║  城市设计案例研究助手 v1.7{' ' * 23}║")
    print(f"║  当前 API：{API_REGISTRY[ACTIVE_API]['label']:<38}║")
    print(f"╚{bar}╝")

    # --file: 直接分析文件
    if args.file:
        filepath = args.file
        print(f"\n  📄  读取文件: {filepath}")
        file_result = read_pdf_file(filepath)
        if file_result.get("error"):
            print(f"  ❌  {file_result['error']}")
            return
        text = file_result["text"]
        print(f"  ✅  提取成功 ({file_result['method']}, {len(text)} 字符)")
        title = os.path.splitext(os.path.basename(filepath))[0]
        print(f"\n  ⏳  正在分析...\n")
        result = extract_case_insights(text, title=title, force_tfidf=args.tfidf)
        print(format_result(result, title))
        if input("\n是否保存？(y/n): ").strip().lower() == "y":
            save_results([{**result, "title": title}], OUTPUT_DIR, prefix="file")
        return

    if args.demo:
        mode_demo()
        return

    print("\n  1  手动粘贴文章 → 提取精华")
    print("  2  学术搜索 → 批量摘要")
    print("  3  西溪湿地演示")
    print("  4  查看 API 列表")
    ch = input("\n选项（1/2/3/4）：").strip()
    if   ch == "1": mode_paste(force_tfidf=args.tfidf)
    elif ch == "2": mode_search(force_tfidf=args.tfidf)
    elif ch == "3": mode_demo()
    elif ch == "4":
        for k, v in API_REGISTRY.items():
            print(f"  {k:12s}  {v['label']}")
    else: print("无效选项")


if __name__ == "__main__":
    main()
