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
        "name": "2026 iThome 臺灣雲端大會（Cloud Summit 2026）",
        "short": "臺灣雲端大會",
        "color": "#0f9d8e",
    },
}

# Ordered topic taxonomy used to group talks on the index page.
CATEGORIES = [
    ("agentic-arch", "🤖", "Agentic AI 架構與導入"),
    ("observability-data", "📊", "可觀測性、評測與資料治理"),
    ("spec-driven", "🛠️", "規格驅動開發與 AI 協作"),
    ("security", "🛡️", "企業資安與威脅防禦"),
    ("cloud-infra", "☁️", "雲端基礎設施與維運"),
    ("industry", "🏭", "產業應用案例"),
    ("transformation", "🚀", "企業 AI 轉型策略與領導"),
]

# (summit, order) -> category id. Every talk must appear exactly once.
ORDER_CATEGORY = {
    ("ai-enterprise", 1): "spec-driven",
    ("ai-enterprise", 2): "agentic-arch",
    ("ai-enterprise", 3): "agentic-arch",
    ("ai-enterprise", 4): "industry",
    ("ai-enterprise", 5): "industry",
    ("ai-enterprise", 6): "agentic-arch",
    ("ai-enterprise", 7): "observability-data",
    ("ai-enterprise", 8): "observability-data",
    ("ai-enterprise", 9): "agentic-arch",
    ("ai-enterprise", 10): "cloud-infra",
    ("ai-enterprise", 11): "agentic-arch",
    ("ai-enterprise", 12): "security",
    ("ai-enterprise", 13): "agentic-arch",
    ("ai-enterprise", 14): "agentic-arch",
    ("ai-enterprise", 15): "spec-driven",
    ("ai-enterprise", 16): "spec-driven",
    ("ai-enterprise", 17): "transformation",
    ("ai-enterprise", 18): "observability-data",
    ("ai-enterprise", 19): "observability-data",
    ("ai-enterprise", 20): "spec-driven",
    ("ai-enterprise", 21): "agentic-arch",
    ("ai-enterprise", 22): "spec-driven",
    ("ai-enterprise", 23): "industry",
    ("ai-enterprise", 24): "agentic-arch",
    ("ai-enterprise", 25): "observability-data",
    ("ai-enterprise", 26): "transformation",
    ("ai-enterprise", 27): "spec-driven",
    ("ai-enterprise", 28): "industry",
    ("ai-enterprise", 29): "cloud-infra",
    ("ai-enterprise", 30): "observability-data",
    ("ai-enterprise", 31): "industry",
    ("cloud-edge", 1): "security",
    ("cloud-edge", 2): "security",
    ("cloud-edge", 3): "transformation",
    ("cloud-edge", 4): "agentic-arch",
    ("cloud-edge", 5): "security",
    ("cloud-edge", 6): "transformation",
    ("cloud-edge", 7): "spec-driven",
    ("cloud-edge", 8): "security",
    ("cloud-edge", 9): "spec-driven",
    ("cloud-edge", 10): "transformation",
    ("cloud-edge", 11): "cloud-infra",
    ("cloud-edge", 12): "cloud-infra",
    ("cloud-edge", 13): "spec-driven",
    ("cloud-edge", 14): "industry",
    ("cloud-edge", 15): "observability-data",
    ("cloud-edge", 16): "agentic-arch",
    ("cloud-edge", 17): "security",
    ("cloud-edge", 18): "cloud-infra",
    ("cloud-edge", 19): "security",
    ("cloud-edge", 20): "agentic-arch",
    ("cloud-edge", 21): "spec-driven",
    ("cloud-edge", 22): "security",
    ("cloud-edge", 23): "cloud-infra",
    ("cloud-edge", 24): "transformation",
    ("cloud-edge", 25): "security",
    ("cloud-edge", 26): "industry",
    ("cloud-edge", 27): "industry",
    ("cloud-edge", 28): "agentic-arch",
    ("cloud-edge", 29): "cloud-infra",
    ("cloud-edge", 30): "cloud-infra",
    ("cloud-edge", 31): "industry",
    ("cloud-edge", 32): "security",
    ("cloud-edge", 33): "cloud-infra",
    ("cloud-edge", 34): "industry",
    ("cloud-edge", 35): "cloud-infra",
    ("cloud-edge", 36): "agentic-arch",
    ("cloud-edge", 37): "agentic-arch",
}

# (summit, order) -> one-sentence "why this is featured" blurb (zh-TW).
FEATURED = {
    ("ai-enterprise", 24): "提出『Agentic Operating System』完整治理框架，回應金融級場景對可稽核、可信任 AI 的嚴苛要求。",
    ("cloud-edge", 36): "以 MCP、Agentic RAG 動態狀態機與 Agent Trace 打通金融業 AI 落地三條生死線，並用真實 Benchmark 數據驗證成效。",
    ("ai-enterprise", 3): "以半導體 CoWoS／Interposer 封裝技術類比企業多模型 AI 整合，視角新穎少見。",
    ("ai-enterprise", 8): "把 OWASP Top 10 for Agentic AI、OpenTelemetry／OpenInference 系統化整理成企業可落地的可觀測性架構。",
    ("ai-enterprise", 14): "從『Workflow Agent』的失敗經驗，提煉出『Config-Driven』新架構模式，實戰教訓具體可借鏡。",
    ("ai-enterprise", 30): "『零資料接觸架構（ZDTA）』以 Schema-Only 查詢代理解決 LLM 資料外洩兩難，設計巧妙。",
    ("cloud-edge", 10): "跳脫工具面，從『共智』與『理解債』重新定義 AI 時代工程師的角色，觀點少見。",
    ("cloud-edge", 19): "揭露前沿模型自主發現零日漏洞的實例，點出漏洞管理典範轉移的緊迫性。",
    ("cloud-edge", 20): "以開源 kagent 與 A2A 協議打造 Kubernetes 自主協作生態系，技術含金量高且可實作。",
    ("cloud-edge", 27): "高雄以主權 AI VLM 與數位孿生打造國家級智慧城市旗艦案例，規模與縱深少見。",
}

# Explicit display order for the featured section (dict insertion order above is
# authoritative — Python dicts preserve insertion order). Kept as a separate name
# for clarity at call sites.
FEATURED_ORDER = list(FEATURED.keys())

CATEGORY_LABEL = {cid: (emoji, label) for cid, emoji, label in CATEGORIES}


GUIDE_CARDS = {
    "featured-ai-enterprise": {
        "title": "AI Enterprise 精選導讀",
        "highlights": "主要涵蓋金融級 AI 治理（Agentic OS）、多模型整合（MixRoute 路由）、生產環境可觀測性（OpenTelemetry 監控）、架構演進（Config-Driven 模式）與極致隱私保護（零資料接觸 ZDTA）五大議題。",
        "summary": "企業在導入 AI 時已不再滿足於簡單的問答，而是朝向「可稽核、低耦合、可控且安全」的自主代理（Agentic）系統演進。"
    },
    "featured-cloud-edge": {
        "title": "臺灣雲端大會精選導讀",
        "highlights": "主要涵蓋金融平台工程（MCP 與狀態機實踐）、共智時代的人機協作哲學（李智樺）、漏洞管理移轉（自主發現零日漏洞）、Kubernetes 自主運作（kagent A2A 協議）與國家級智慧城市（高雄主權 AI 案例）。",
        "summary": "本組精選著重於 AI 如何深入企業底層基礎設施（K8s 與雲端平台）與開發實務，推動系統架構與人機協同的雙重典範轉移。"
    },
    "agentic-arch": {
        "title": "Agentic AI 架構專區導讀",
        "highlights": "精選 12 場議程，涵蓋 IBM Bob、Orleans virtual actors 虛擬角色、kagent 協作、自癒（Self-healing）機制，以及透過 MCP (Model Context Protocol) 進行低摩擦 API 整合等前沿實務。",
        "summary": "本專區的核心在於「如何建構能獨立思考、自主修正並與外部系統對話的 Agent 網路」，開發焦點正式從 Prompt 轉向狀態機、事件驅動與人機協作協議。"
    },
    "dev-engineering": {
        "title": "AI 輔助軟體工程導讀",
        "highlights": "精選 10 場議程，深度拆解 SDD (Spec-Driven Development) 規格導向開發實戰、Vibe Coding 的利弊反思（何時該 Vibe，何時該寫 Spec）、工程師角色從寫代碼轉為設計驗證的改變，以及即時語音串流在 DevOps 中的應用。",
        "summary": "AI 正在重構軟體交付的生命週期，促使開發團隊從無規格的「盲寫」走向以規格驅動（Spec-Driven）與自動驗收的現代化軟體交付閉環。"
    },
    "data-infra": {
        "title": "現代數據底座與算力導讀",
        "highlights": "精選 8 場議程，包括金融業 AI 數據底座構建、hicloud AI 算力雲與 GPU 調度、MS SQL 超大型資料庫的雲地自治遷移、以及為 AI 智能體設計的向量檢索（pgvector）與 RAG 檢索增強實務。",
        "summary": "高階 AI 的表現高度依賴數據品質與算力彈性，本專區展示了如何將傳統數據資產與資料庫升級，為 Agent 打造高效、安全且低延遲的智能數據中樞。"
    },
    "sec-compliance": {
        "title": "資安、合規與 AI 治理導讀",
        "highlights": "精選 17 場議程，全面探討 AI 安全防禦，包括 Web/MDM 三層治理框架、Black Duck 生成代碼信任工程（5層安全檢驗）、防禦爬蟲 Agent 的 SASE 安全轉型、ISO 42001 與 TIPS 敏感資料治理、以及 Fortinet 的 AISOC 威脅防禦。",
        "summary": "AI 在釋放生產力的同時也擴大了企業攻擊面，本專區為企業提供了從代碼產出、員工日常使用到雲端邊緣安全防禦的全方位合規治理與信任架構藍圖。"
    },
    "transformation": {
        "title": "組織轉型與產業應用導讀",
        "highlights": "精選 21 場議程，包含跨國 IT 大廠轉型組織 POD 藍圖、中小型企業導入 AI 的落地生存指南、安東尼（陳泳睿）的管理者決策現場的智能轉型實戰、Hahow for Business 逐字稿能力數據化，以及旅遊與醫療（SMART on FHIR）的 AI 落地案例。",
        "summary": "AI 的最終價值在於解決真實商業問題，本專區從組織變革、流程重塑和多個垂直產業實例，指明了從個人工具點狀應用到面狀企業進化的智慧轉型路線。"
    }
}


def render_guide_card(key: str) -> str:
    g = GUIDE_CARDS.get(key)
    if not g:
        return ""
    return f"""<div class="section-guide-card">
  <div class="section-guide-title">📖 {esc(g['title'])}</div>
  <div class="section-guide-content">
    <div class="section-guide-block">
      <h4>🔍 閱讀與觀看重點</h4>
      <p>{esc(g['highlights'])}</p>
    </div>
    <div class="section-guide-block">
      <h4>💡 專區總結 / Takeaway</h4>
      <p>{esc(g['summary'])}</p>
    </div>
  </div>
</div>"""


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def get_category(c: dict) -> str:
    return ORDER_CATEGORY[(c["summit"], c["order"])]


def get_featured_reason(c: dict):
    return FEATURED.get((c["summit"], c["order"]))


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
<meta name="description" content="AI Enterprise Summit 2026 與 2026 iThome 臺灣雲端大會（Cloud Summit 2026）議程摘要與詳細內容整理">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/css/style.css?v=1.0.8">
</head>
"""


def render_card(c: dict, featured: bool = False) -> str:
    meta = SUMMIT_META[c["summit"]]
    cover_html = ""
    if c.get("cover"):
        cover_html = f'<div class="card-cover"><img src="{esc(c["cover"])}" loading="lazy" alt=""></div>'
    tags_html = "".join(f'<span class="tag">{esc(t)}</span>' for t in c.get("tags", [])[:4])
    speaker = ""
    if c.get("speaker"):
        speaker_title = f'（{esc(c["speaker_title"])}）' if c.get("speaker_title") else ""
        speaker = f'<div class="card-speaker">🎤 {esc(c["speaker"])}{speaker_title}</div>'
    featured_html = ""
    card_class = "card"
    if featured:
        card_class += " card-featured"
        reason = get_featured_reason(c) or ""
        if reason:
            featured_html = f'<p class="card-featured-reason">✨ {esc(reason)}</p>'
    category = get_category(c)
    return f"""<a class="{card_class}" href="talks/{esc(c['slug'])}.html" data-summit="{esc(c['summit'])}" data-category="{esc(category)}" data-tags="{esc(' '.join(c.get('tags', [])))}" data-title="{esc(c['title'])}" data-speaker="{esc(c.get('speaker',''))}">
  {cover_html}
  <div class="card-body">
    <span class="badge" style="--badge-color:{meta['color']}">{esc(meta['short'])} · #{c['order']:02d}</span>
    <h3>{esc(c['title'])}</h3>
    {speaker}
    {featured_html}
    <p class="card-summary">{esc(c['summary'])}</p>
    <div class="tags">{tags_html}</div>
  </div>
</a>"""


def render_index(talks: list) -> str:
    n_ai = sum(1 for c in talks if c["summit"] == "ai-enterprise")
    n_ce = sum(1 for c in talks if c["summit"] == "cloud-edge")

    featured_by_key = {(c["summit"], c["order"]): c for c in talks}
    featured_talks = [featured_by_key[key] for key in FEATURED_ORDER if key in featured_by_key]

    featured_groups_html = []
    for summit in ("ai-enterprise", "cloud-edge"):
        group = [c for c in featured_talks if c["summit"] == summit]
        if not group:
            continue
        meta = SUMMIT_META[summit]
        cards = "\n".join(render_card(c, featured=True) for c in group)
        featured_groups_html.append(f"""<div class="featured-group" data-summit="{summit}">
  <h3 class="featured-group-heading"><span class="dot" style="--dot:{meta['color']}"></span>{esc(meta['name'])}</h3>
  {render_guide_card("featured-" + summit)}
  <div class="grid featured-grid">
    {cards}
  </div>
</div>""")
    featured_groups = "\n".join(featured_groups_html)

    by_category = {cid: [] for cid, _, _ in CATEGORIES}
    for c in talks:
        by_category[get_category(c)].append(c)

    nav_pills = "\n".join(
        f'<a class="cat-pill" href="#cat-{cid}">{emoji} {esc(label)}<span class="cat-count">{len(by_category[cid])}</span></a>'
        for cid, emoji, label in CATEGORIES
    )

    sections_html = []
    for cid, emoji, label in CATEGORIES:
        items = by_category[cid]
        cards = "\n".join(render_card(c) for c in items)
        sections_html.append(f"""<section class="category-section" id="cat-{cid}" data-category="{cid}">
  <h2 class="category-heading">{emoji} {esc(label)} <span class="category-heading-count">{len(items)} 場</span></h2>
  {render_guide_card(cid)}
  <div class="grid">
    {cards}
  </div>
</section>""")
    categories_html = "\n".join(sections_html)

    return render_head("Summit 2026 議程摘要總覽") + f"""<body>
<div class="bg-glow" aria-hidden="true"></div>
<header class="site-header">
  <div class="container">
    <p class="eyebrow">2026 台灣科技雙峰會 · 議程精讀</p>
    <h1>Summit 2026 議程摘要</h1>
    <p class="subtitle">AI Enterprise Summit 2026（{n_ai} 場）＋ 2026 iThome 臺灣雲端大會（{n_ce} 場）議程重點整理，含架構圖與關鍵投影片</p>
    <div class="header-links">
      <a href="https://aienterprise.ithome.com.tw/2026/agenda" class="header-link-btn" target="_blank">
        🔗 AI Enterprise Summit 官方議程
      </a>
      <a href="https://cloudsummit.ithome.com.tw/2026/agenda" class="header-link-btn" target="_blank">
        🔗 臺灣雲端大會 官方議程
      </a>
    </div>
  </div>
</header>
<main class="container">
  <div class="toolbar">
    <input type="search" id="search" placeholder="搜尋標題、講者、關鍵字…">
    <div class="filters" id="filters">
      <button class="filter-btn active" data-filter="all">全部</button>
      <button class="filter-btn" data-filter="ai-enterprise">AI Enterprise Summit</button>
      <button class="filter-btn" data-filter="cloud-edge">2026 臺灣雲端大會</button>
    </div>
  </div>
  <p id="result-count" class="result-count"></p>

  <section class="featured-section" id="featured-section">
    <div class="section-heading-block">
      <p class="eyebrow eyebrow-gold">✨ Editor's Pick</p>
      <h2 class="featured-heading">精選議程</h2>
      <p class="featured-sub">分別從兩場大會中，挑選出視角新穎、架構完整或具代表性的議程</p>
    </div>
    {featured_groups}
  </section>

  <nav class="cat-nav">
    {nav_pills}
  </nav>

  <div id="categories">
    {categories_html}
  </div>

  <p id="empty-state" class="empty-state" hidden>沒有符合條件的議程。</p>
</main>
<footer class="site-footer">
  <div class="container">
    <p>資料來源：AI Enterprise Summit 2026 / 2026 iThome 臺灣雲端大會（Cloud Summit 2026）官方議程投影片（PDF／Markdown）。本站內容為 AI 輔助整理之摘要，僅供參考，正確內容請以原始投影片為準。</p>
  </div>
</footer>
<script src="assets/js/app.js?v=1.0.3"></script>
</body>
</html>
"""


def render_sections(sections: list) -> str:
    out = []
    for idx, s in enumerate(sections):
        body = esc(s.get("body", "")).replace("\n\n", "</p><p>").replace("\n", "<br>")
        out.append(f'<section class="detail-section" id="section-{idx}"><h2>{esc(s.get("heading",""))}</h2><p>{body}</p></section>')
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
    return f"""<section class="detail-section plain-section" id="section-images">
  <h2>重點圖片／架構圖</h2>
  <div class="diagram-grid">
    {''.join(figs)}
  </div>
</section>"""


def render_talk(c: dict, prev_c: dict | None, next_c: dict | None) -> str:
    meta = SUMMIT_META[c["summit"]]
    emoji, label = CATEGORY_LABEL[get_category(c)]
    highlights = "".join(f"<li>{esc(h)}</li>" for h in c.get("highlights", []))
    speaker_block = ""
    if c.get("speaker"):
        speaker_title = f'　·　{esc(c["speaker_title"])}' if c.get("speaker_title") else ""
        speaker_block = f'<p class="detail-speaker">🎤 {esc(c["speaker"])}{speaker_title}</p>'
    tags_html = "".join(f'<span class="tag">{esc(t)}</span>' for t in c.get("tags", []))
    featured_reason = get_featured_reason(c)
    featured_block = f'<p class="detail-featured">✨ 精選理由：{esc(featured_reason)}</p>' if featured_reason else ""

    download_btn = ""
    if c.get("source_file"):
        file_kind = c.get("kind", "pdf").upper()
        download_btn = f"""<div class="action-row">
      <a href="../slides/{c['summit']}/{esc(c['source_file'])}" class="download-btn" target="_blank">
        📥 下載原始 {file_kind} 投影片
      </a>
    </div>"""

    nav_links = []
    if prev_c:
        nav_links.append(f'<a class="nav-link" href="{esc(prev_c["slug"])}.html"><span class="nav-dir">← 上一場議程</span><span class="nav-title">{esc(prev_c["title"])}</span></a>')
    else:
        nav_links.append('<div class="nav-placeholder"></div>')
    if next_c:
        nav_links.append(f'<a class="nav-link nav-next" href="{esc(next_c["slug"])}.html"><span class="nav-dir">下一場議程 →</span><span class="nav-title">{esc(next_c["title"])}</span></a>')
    else:
        nav_links.append('<div class="nav-placeholder"></div>')

    # Generate Table of Contents (TOC)
    toc_links = []
    toc_links.append(f'<a href="#section-summary" class="toc-link">議程摘要</a>')
    toc_links.append(f'<a href="#section-highlights" class="toc-link">重點整理</a>')
    if c.get("key_images"):
        toc_links.append(f'<a href="#section-images" class="toc-link">重點圖片</a>')
    for idx, s in enumerate(c.get("sections", [])):
        toc_links.append(f'<a href="#section-{idx}" class="toc-link">{esc(s.get("heading", ""))}</a>')
    
    toc_html = "\n".join(toc_links)

    return render_head(f"{c['title']} - Summit 2026 議程摘要", depth=1) + f"""<body>
<div class="bg-glow" aria-hidden="true"></div>
<header class="site-header detail-header">
  <div class="container">
    <a class="back-link" href="../index.html">← 回議程總覽</a>
    <div class="badge-row">
      <span class="badge" style="--badge-color:{meta['color']}">{esc(meta['name'])} · #{c['order']:02d}</span>
      <span class="badge category-badge">{emoji} {esc(label)}</span>
    </div>
    <h1>{esc(c['title'])}</h1>
    {speaker_block}
    {featured_block}
    <div class="tags">{tags_html}</div>
    {download_btn}
  </div>
</header>
<main class="container detail-main">
  <div class="detail-grid">
    <div class="detail-content">
      <section class="detail-section summary-box" id="section-summary">
        <h2>摘要</h2>
        <p>{esc(c['summary'])}</p>
      </section>
      <section class="detail-section highlights-card" id="section-highlights">
        <h2>重點整理</h2>
        <ul class="highlights">{highlights}</ul>
      </section>
      {render_images(c.get('key_images', []))}
      {render_sections(c.get('sections', []))}
    </div>
    <aside class="detail-sidebar">
      <div class="toc-card">
        <h3>📍 本頁導覽</h3>
        <nav class="toc-nav-list">
          {toc_html}
        </nav>
      </div>
    </aside>
  </div>
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
<script src="../assets/js/app.js?v=1.0.3"></script>
</body>
</html>
"""


def main():
    talks = load_content()
    TALKS_OUT.mkdir(parents=True, exist_ok=True)

    missing = [(c["summit"], c["order"], c["slug"]) for c in talks if (c["summit"], c["order"]) not in ORDER_CATEGORY]
    if missing:
        raise SystemExit(f"Missing category mapping for: {missing}")

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
