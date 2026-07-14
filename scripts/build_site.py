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
        "highlights": [
            "<strong>金融級代理架構</strong>：第 24 場提出「Agentic OS」完整金融級治理與狀態管理框架。",
            "<strong>多模型路由戰略</strong>：第 3 場以半導體 CoWoS/Interposer 巧妙比擬多模型路由，實現高性價比與彈性。",
            "<strong>生產級可觀測性</strong>：第 8 場介紹 OpenTelemetry 與 OpenInference 可觀測性標準在 Agentic 工作流中的實踐。",
            "<strong>對話式 Retail 分析</strong>：第 14 場探討 Config-Driven 架構讓對話產出配置的設計思路與避坑指南。",
            "<strong>極致隱私保護</strong>：第 30 場揭秘「Schema-Only」零資料接觸架構，平衡大模型檢索與敏感數據隱私阻絕。"
        ],
        "summary": "企業級 AI 應用正在朝向「高安全、低耦合、多模型路由與標準化觀測」的自主代理（Agentic）系統演進，傳統的單體 Prompt chat 已被更複雜的狀態機與流程編排取代。"
    },
    "featured-cloud-edge": {
        "title": "臺灣雲端大會精選導讀",
        "highlights": [
            "<strong>金融平台工程</strong>：第 36 場以 MCP 協議、動態狀態機與 Agent Trace 打造可擴展 AI 中樞，突破效能生死線。",
            "<strong>人機協同哲學</strong>：第 10 場反思「共智時代」下的理解債，探討 AI 與軟體工程師角色的深刻轉變。",
            "<strong>自主零日利用</strong>：第 19 場揭露前沿 AI 模型發現並自主利用零日漏洞的威脅實例，點出防禦體系升級的緊迫性。",
            "<strong>自主 Kubernetes 維運</strong>：第 20 場探討以 kagent 及 A2A 協議在 K8s 運行時的自動偵測與協作防禦。",
            "<strong>城市主權 AI 案例</strong>：第 27 場展示高雄以視覺語言模型（VLM）與數位孿生技術打造智慧城市防汛與治理平台。"
        ],
        "summary": "AI 已正式深入企業作業系統、K8s 底層基礎設施與雲端防禦，推動雲端架構從靜態配置向「自適應、自愈、自主協同防禦」的典範轉移。"
    },
    "agentic-arch": {
        "title": "Agentic AI 架構與導入專區導讀",
        "highlights": [
            "<strong>多 Agent 協作協議</strong>：探討 Microsoft Orleans virtual actors 與 A2A 自主協作框架，解決多模代理狀態同步難題。",
            "<strong>低摩擦 API 整合</strong>：解讀 Model Context Protocol (MCP) 與 OAuth 授權治理在既有 API 與微服務中的實踐。",
            "<strong>企業 AI 智能工作流</strong>：IBM Bob 的實戰設計，以及 Config-Driven 讓 Agent 用對話動態產出零售分析的配置技術。",
            "<strong>雲地協同工作流</strong>：Orleans 與微軟 Agent 框架結合，建構高可靠的分散式 AI 運行環境。"
        ],
        "summary": "本專區的核心在於「狀態管理與協同協議」，透過 MCP 協議與虛擬 Actor 模型，將多個獨立 Agent 連接成低耦合、高可擴展的網格系統。"
    },
    "observability-data": {
        "title": "可觀測性、評測與資料治理專區導讀",
        "highlights": [
            "<strong>LLM 生產監控</strong>：結合 OpenTelemetry 與 OpenInference 進行 LLM 決策鏈（Trace）追蹤與異常告警。",
            "<strong>決策系統評估</strong>：引進 Decision System 工作坊機制，動態評估 Agent 行為與業務產出指標的對齊。",
            "<strong>非結構化數據提取</strong>：利用 LangGraph 自癒（Self-healing）機制，優化 FDA 大量法規文件的非結構化提取精準度。",
            "<strong>知識增值工程</strong>：透過會議逐字稿數據化，以 AI 重建培訓驗證模型與企業能力數據庫。"
        ],
        "summary": "「無法量測就無法改善」。建立標準化的可觀測性 Trace、自癒式的檢索架構與客觀評測基準，是將 AI 應用推向生產環境、確保可稽核性的前提。"
    },
    "spec-driven": {
        "title": "規格驅動開發與 AI 協作專區導讀",
        "highlights": [
            "<strong>規格導向開發 (SDD)</strong>：解密 Spec-kit 開發流程，利用 AI 結合定義好的 Specifications 自動生成程式碼與進行單元測試。",
            "<strong>反思 Vibe Coding</strong>：探討如何利用 Vibe Coding 進行快速 PoC，並在落地生產時迅速轉換為 Spec-driven 工程以控制品質。",
            "<strong>代碼生成安全與信任</strong>：Black Duck 介紹對 AI 生成程式碼的信任工程與安全分析，防範潛在安全與智財風險。",
            "<strong>自研 AI 工程師實踐</strong>：電商平台基於 SDD 架構與 AI 自動化軟體交付、重構經典舊系統的避坑實戰。"
        ],
        "summary": "AI 協作軟體開發已從早期的「盲寫 (Vibe Coding)」走向「規格驅動 (Spec-Driven)」。將規格書視為人機協同的單一真理源，是發揮 AI 極致吞吐量與高可靠性的黃金法則。"
    },
    "security": {
        "title": "企業資安與威脅防禦專區導讀",
        "highlights": [
            "<strong>授權漏洞與間接注入</strong>：防範 AI 主動呼叫外部 API 時，面臨的影子 IT、惡意輸入污染與權限越軌新型攻擊面。",
            "<strong>影子 AI 與惡意爬蟲防禦</strong>：Cloudflare 實戰演示如何利用邊緣網路防禦惡意 Agent 爬蟲並進行 SASE 安全轉型。",
            "<strong>合規治理與機密運算</strong>：結合 ISO 42001 / ISO 27001、TIPS 資料加密治理，以及保護敏感數據的雲端機密運算實踐。",
            "<strong>Runtime 安全偵測</strong>：利用 AI 增強 Kubernetes 運行時的威脅偵測，超越傳統基於規則的防禦瓶頸。"
        ],
        "summary": "AI 既是防禦者的武器，也為攻擊者帶來全新通道。企業必須從代碼生成源頭、員工使用行為、API 調用鏈路及雲端運行時，建立全方位的立體防禦架構。"
    },
    "cloud-infra": {
        "title": "雲端基礎設施與維運專區導讀",
        "highlights": [
            "<strong>主權算力雲調度</strong>：hicloud 算力雲基礎設施建置，以及面對大模型推理的混合式與多雲 AI 網路架構。",
            "<strong>自主自治維運實務</strong>：Foundry Local 驅動 Windows Server 2025 自主維運，以及 AI 作為維運同事（Infra Copilot）的真實痛點與落地實作。",
            "<strong>資料庫雲端自治</strong>：超大型 MS SQL 資料庫雲端遷移與自治管理，釋放 DBA 繁瑣維運負擔。",
            "<strong>AI 雲成本治理</strong>：如何結合 FinOps 理念，建立大模型調用與訓練算力的成本可觀測性、預測與成本分攤機制。"
        ],
        "summary": "AI 計算的高度波動性使基礎設施面臨巨大挑戰。透過混合雲彈性架構、AI 自主維運與 FinOps 成本治理，是控制算力支出並保持高可用性的關鍵。"
    },
    "industry": {
        "title": "產業應用案例專區導讀",
        "highlights": [
            "<strong>智慧醫療</strong>：SMART on FHIR 標準與 LINE Bot 對接，實現去識別化、符合醫療法規的個人 AI 健康助理。",
            "<strong>綠色金融碳管理</strong>：國泰雲端碳管理平台實戰，展示如何利用碳金融工具賦能供應鏈實現減碳治理。",
            "<strong>智慧旅宿與房貸顧問</strong>：AI 賦能旅宿客服及自動導覽，以及金融業基於 Agent 構建的智慧房貸顧問實例。",
            "<strong>營造與建築合規檢索</strong>：自研 On-prem 本地端 AI Agent 搭配企業知識庫，解決營建圖紙複雜規範的精準檢索與審查。"
        ],
        "summary": "AI 必須與產業的專業知識 and 法規標準（如醫療 FHIR、金融合規）高度融合。結合本地端資料加值，才能在垂直領域實現具備商業變現價值的應用。"
    },
    "transformation": {
        "title": "企業 AI 轉型策略與領導專區導讀",
        "highlights": [
            "<strong>轉型組織 POD 設計</strong>：打造跨國跨部門的 AI 敏捷 POD 原生組織架構，突破傳統 silo 隔閡。",
            "<strong>中小型企業生存指南</strong>：撕開轉型中華麗的包裝，探討中小型企業在預算有限下從煉獄爬回現實的 AI 落地心法。",
            "<strong>決策現場的智能轉型</strong>：陳泳睿分享 AI 驅動管理者決策現場的數據分析、動態預測與商業智慧實戰。",
            "<strong>員工 AI 使用與治理</strong>：防範員工盲目使用 AI 造成的專利及合規漏洞，建立良性引導的 AI 使用規範。"
        ],
        "summary": "企業 AI 轉型本質上是「組織變革管理」。除技術導入外，更涉及人機協同文化的建立、權責重塑以及業務流程的端到端重構，需要高層的持續戰略支持。"
    }
}

def render_guide_card(key: str) -> str:
    g = GUIDE_CARDS.get(key)
    if not g:
        return ''
    highlights_li = ''.join(f'<li>{h}</li>' for h in g.get('highlights', []))
    return f'''<div class="section-guide-card">
  <div class="section-guide-title">📖 {esc(g["title"])}</div>
  <div class="section-guide-content">
    <div class="section-guide-block">
      <h4>🔍 閱讀與觀看重點</h4>
      <ul class="guide-list">
        {highlights_li}
      </ul>
    </div>
    <div class="section-guide-block">
      <h4>💡 專區總結 / Takeaway</h4>
      <p>{esc(g["summary"])}</p>
    </div>
  </div>
</div>'''


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
<link rel="stylesheet" href="{prefix}assets/css/style.css?v=1.0.9">
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
