#!/usr/bin/env python3
"""
Build the static site from content/*.json + data/talks.json into site/.

Generates:
  site/index.html                 - landing page with filterable talk cards
  site/talks/<slug>.html           - one detail page per talk
  site/assets/css/style.css        - shared styles (hand-written, not generated here)
  site/assets/js/app.js            - client-side filter/search (hand-written)
  site/assets/data/talks.json      - copy of talk metadata for client-side search
"""
import json
import html
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
DATA_DIR = ROOT / "data"
SITE_DIR = ROOT / "site"
TALKS_OUT = SITE_DIR / "talks"

SUMMIT_META = {
    "ai-enterprise": {
        "name": "AI Enterprise Summit 2026",
        "short": "AI Enterprise",
        "color": "#6d5bd0",
    },
    "cloud-edge": {
        "name": "Cloud & Edge Summit 2026",
        "short": "Cloud & Edge",
        "color": "#0f9d8e",
    },
}


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def load_content():
    talks = json.load(open(DATA_DIR / "talks.json", encoding="utf-8"))
    by_slug = {t["slug"]: t for t in talks}
    merged = []
    for f in sorted(CONTENT_DIR.glob("*.json")):
        c = json.load(open(f, encoding="utf-8"))
        meta = by_slug.get(c["slug"], {})
        c["order"] = meta.get("order", 0)
        c["source_file"] = meta.get("source_file", "")
        c["kind"] = meta.get("kind", "pdf")
        cover = None
        for img in meta.get("images", []):
            if img.get("role") == "cover":
                cover = img["file"]
                break
        c["cover"] = cover
        merged.append(c)
    merged.sort(key=lambda c: (c["summit"], c["order"]))
    return merged


def render_head(title: str, depth: int = 0) -> str:
    prefix = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="AI Enterprise Summit 2026 與 Cloud &amp; Edge Summit 2026 議程摘要與詳細內容整理">
<link rel="stylesheet" href="{prefix}assets/css/style.css">
</head>
"""


def render_card(c: dict) -> str:
    meta = SUMMIT_META[c["summit"]]
    cover_html = ""
    if c.get("cover"):
        cover_html = f'<div class="card-cover"><img src="{esc(c["cover"])}" loading="lazy" alt=""></div>'
    tags_html = "".join(f'<span class="tag">{esc(t)}</span>' for t in c.get("tags", [])[:4])
    speaker = ""
    if c.get("speaker"):
        speaker_title = f'（{esc(c["speaker_title"])}）' if c.get("speaker_title") else ""
        speaker = f'<div class="card-speaker">🎤 {esc(c["speaker"])}{speaker_title}</div>'
    return f"""<a class="card" href="talks/{esc(c['slug'])}.html" data-summit="{esc(c['summit'])}" data-tags="{esc(' '.join(c.get('tags', [])))}" data-title="{esc(c['title'])}" data-speaker="{esc(c.get('speaker',''))}">
  {cover_html}
  <div class="card-body">
    <span class="badge" style="--badge-color:{meta['color']}">{esc(meta['short'])} · #{c['order']:02d}</span>
    <h3>{esc(c['title'])}</h3>
    {speaker}
    <p class="card-summary">{esc(c['summary'])}</p>
    <div class="tags">{tags_html}</div>
  </div>
</a>"""


def render_index(talks: list) -> str:
    cards = "\n".join(render_card(c) for c in talks)
    n_ai = sum(1 for c in talks if c["summit"] == "ai-enterprise")
    n_ce = sum(1 for c in talks if c["summit"] == "cloud-edge")
    return render_head("Summit 2026 議程摘要總覽") + f"""<body>
<header class="site-header">
  <div class="container">
    <h1>Summit 2026 議程摘要</h1>
    <p class="subtitle">AI Enterprise Summit 2026（{n_ai} 場）＋ Cloud &amp; Edge Summit 2026（{n_ce} 場）議程重點整理，含架構圖與關鍵投影片</p>
  </div>
</header>
<main class="container">
  <div class="toolbar">
    <input type="search" id="search" placeholder="搜尋標題、講者、關鍵字…">
    <div class="filters" id="filters">
      <button class="filter-btn active" data-filter="all">全部</button>
      <button class="filter-btn" data-filter="ai-enterprise">AI Enterprise Summit</button>
      <button class="filter-btn" data-filter="cloud-edge">Cloud &amp; Edge Summit</button>
    </div>
  </div>
  <p id="result-count" class="result-count"></p>
  <div class="grid" id="grid">
    {cards}
  </div>
  <p id="empty-state" class="empty-state" hidden>沒有符合條件的議程。</p>
</main>
<footer class="site-footer">
  <div class="container">
    <p>資料來源：AI Enterprise Summit 2026 / Cloud &amp; Edge Summit 2026 官方議程投影片（PDF／Markdown）。本站內容為 AI 輔助整理之摘要，僅供參考，正確內容請以原始投影片為準。</p>
  </div>
</footer>
<script src="assets/js/app.js"></script>
</body>
</html>
"""


def render_sections(sections: list) -> str:
    out = []
    for s in sections:
        body = esc(s.get("body", "")).replace("\n\n", "</p><p>").replace("\n", "<br>")
        out.append(f'<section class="detail-section"><h2>{esc(s.get("heading",""))}</h2><p>{body}</p></section>')
    return "\n".join(out)


def render_images(images: list) -> str:
    if not images:
        return ""
    figs = []
    for img in images:
        figs.append(f"""<figure class="diagram">
  <img src="../{esc(img['file'])}" loading="lazy" alt="{esc(img.get('caption',''))}">
  <figcaption>{esc(img.get('caption',''))}</figcaption>
</figure>""")
    return f"""<section class="detail-section">
  <h2>重點圖片／架構圖</h2>
  <div class="diagram-grid">
    {''.join(figs)}
  </div>
</section>"""


def render_talk(c: dict, prev_c: dict | None, next_c: dict | None) -> str:
    meta = SUMMIT_META[c["summit"]]
    highlights = "".join(f"<li>{esc(h)}</li>" for h in c.get("highlights", []))
    speaker_block = ""
    if c.get("speaker"):
        speaker_title = f'　·　{esc(c["speaker_title"])}' if c.get("speaker_title") else ""
        speaker_block = f'<p class="detail-speaker">🎤 {esc(c["speaker"])}{speaker_title}</p>'
    tags_html = "".join(f'<span class="tag">{esc(t)}</span>' for t in c.get("tags", []))

    nav_links = []
    if prev_c:
        nav_links.append(f'<a class="nav-link" href="{esc(prev_c["slug"])}.html">← {esc(prev_c["title"])}</a>')
    else:
        nav_links.append('<span></span>')
    if next_c:
        nav_links.append(f'<a class="nav-link nav-next" href="{esc(next_c["slug"])}.html">{esc(next_c["title"])} →</a>')
    else:
        nav_links.append('<span></span>')

    return render_head(f"{c['title']} - Summit 2026 議程摘要", depth=1) + f"""<body>
<header class="site-header detail-header">
  <div class="container">
    <a class="back-link" href="../index.html">← 回議程總覽</a>
    <span class="badge" style="--badge-color:{meta['color']}">{esc(meta['name'])} · #{c['order']:02d}</span>
    <h1>{esc(c['title'])}</h1>
    {speaker_block}
    <div class="tags">{tags_html}</div>
  </div>
</header>
<main class="container detail-main">
  <section class="detail-section summary-box">
    <h2>摘要</h2>
    <p>{esc(c['summary'])}</p>
  </section>
  <section class="detail-section">
    <h2>重點整理</h2>
    <ul class="highlights">{highlights}</ul>
  </section>
  {render_images(c.get('key_images', []))}
  {render_sections(c.get('sections', []))}
  <nav class="talk-nav">
    {nav_links[0]}
    {nav_links[1]}
  </nav>
</main>
<footer class="site-footer">
  <div class="container">
    <p>本頁內容為 AI 輔助整理之摘要，原始檔案：{esc(c.get('source_file',''))}。正確內容請以原始投影片為準。</p>
  </div>
</footer>
</body>
</html>
"""


def main():
    talks = load_content()
    TALKS_OUT.mkdir(parents=True, exist_ok=True)

    # index
    (SITE_DIR / "index.html").write_text(render_index(talks), encoding="utf-8")

    # per-summit ordered list for prev/next navigation
    by_summit = {}
    for c in talks:
        by_summit.setdefault(c["summit"], []).append(c)

    for summit, lst in by_summit.items():
        for i, c in enumerate(lst):
            prev_c = lst[i - 1] if i > 0 else None
            next_c = lst[i + 1] if i < len(lst) - 1 else None
            html_out = render_talk(c, prev_c, next_c)
            (TALKS_OUT / f"{c['slug']}.html").write_text(html_out, encoding="utf-8")

    # data for client-side search
    data_dir = SITE_DIR / "assets" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    slim = [
        {
            "slug": c["slug"], "title": c["title"], "summit": c["summit"],
            "speaker": c.get("speaker", ""), "tags": c.get("tags", []),
            "summary": c.get("summary", ""),
        }
        for c in talks
    ]
    (data_dir / "talks.json").write_text(json.dumps(slim, ensure_ascii=False), encoding="utf-8")

    print(f"Built site: {len(talks)} talks -> {SITE_DIR}")


if __name__ == "__main__":
    main()
