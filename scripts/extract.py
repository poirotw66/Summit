#!/usr/bin/env python3
"""
Extract text + candidate diagram/architecture images from the summit slide decks.

For every PDF:
  - dump full per-page text to data/text/<slug>.txt (for later summarization)
  - score each page for "diagram likelihood" (embedded image count + keyword hits)
  - render the best-scoring pages (and always page 1 as a cover) to JPEG images
    under site/assets/images/<slug>/

For every Markdown talk (no PDF available):
  - just copy the raw text to data/text/<slug>.txt

Writes an aggregated manifest to data/talks.json.
"""
import json
import re
import unicodedata
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
import io

ROOT = Path(__file__).resolve().parent.parent
SUMMITS = {
    "ai-enterprise": ROOT / "AI-Enterprise-Summit-2026-slides",
    "cloud-edge": ROOT / "Cloud-Edge-Summit-2026-slides",
}
DATA_DIR = ROOT / "data"
TEXT_DIR = DATA_DIR / "text"
IMG_DIR = ROOT / "site" / "assets" / "images"

DIAGRAM_KEYWORDS = [
    "architecture", "arch.", "diagram", "pipeline", "workflow", "topology",
    "sequence", "system design", "flow chart", "flowchart", "roadmap",
    "架構", "流程", "拓撲", "藍圖", "框架", "全景圖", "系統圖", "示意圖",
    "部署圖", "架構圖", "時序圖", "全流程", "資料流",
]

MAX_IMAGES_PER_TALK = 4
RENDER_ZOOM = 2.0  # ~144 dpi from 72 base
COVER_ZOOM = 1.3
MAX_WIDTH = 1600
JPEG_QUALITY = 82


def slugify(name: str) -> str:
    """Turn '08-Observability Architecture....pdf' stem into a URL slug."""
    stem = name
    m = re.match(r"^(\d+)-(.*)$", stem)
    num, rest = (m.group(1), m.group(2)) if m else ("00", stem)
    rest = unicodedata.normalize("NFKC", rest)
    # keep CJK + alnum, replace everything else with '-'
    rest = re.sub(r"[^\w\u4e00-\u9fff]+", "-", rest, flags=re.UNICODE)
    rest = re.sub(r"-+", "-", rest).strip("-")
    return f"{num}-{rest}"


def save_pixmap(pix: fitz.Pixmap, path: Path):
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > MAX_WIDTH:
        h = int(img.height * MAX_WIDTH / img.width)
        img = img.resize((MAX_WIDTH, h), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True)


def score_page(page) -> tuple[int, int]:
    """Return (score, n_images) for diagram-likelihood ranking."""
    text = page.get_text() or ""
    lower = text.lower()
    n_imgs = len(page.get_images(full=True))
    score = n_imgs * 2
    for kw in DIAGRAM_KEYWORDS:
        if kw.lower() in lower:
            score += 5
            break
    # dense drawings (vector diagrams) also count
    try:
        n_draw = len(page.get_drawings())
    except Exception:
        n_draw = 0
    if n_draw > 40:
        score += 3
    return score, n_imgs


def process_pdf(pdf_path: Path, slug: str) -> dict:
    doc = fitz.open(pdf_path)
    n_pages = len(doc)
    page_texts = []
    scores = []
    for i, page in enumerate(doc):
        txt = page.get_text()
        page_texts.append(txt)
        s, n_imgs = score_page(page)
        scores.append(s)

    # dump text
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    with open(TEXT_DIR / f"{slug}.txt", "w", encoding="utf-8") as f:
        for i, txt in enumerate(page_texts):
            f.write(f"\n===== PAGE {i + 1} =====\n")
            f.write(txt.strip() + "\n")

    # cover = page 1
    out_dir = IMG_DIR / slug
    images = []
    cover_page = doc[0]
    cover_pix = cover_page.get_pixmap(matrix=fitz.Matrix(COVER_ZOOM, COVER_ZOOM))
    cover_rel = f"assets/images/{slug}/cover.jpg"
    save_pixmap(cover_pix, ROOT / "site" / cover_rel)
    images.append({"file": cover_rel, "page": 1, "role": "cover"})

    # candidate diagram pages (excluding page 1, need score > 0)
    ranked = sorted(
        [(i, s) for i, s in enumerate(scores) if i != 0 and s >= 5],
        key=lambda t: -t[1],
    )[:MAX_IMAGES_PER_TALK]
    ranked.sort(key=lambda t: t[0])  # keep original page order in output
    for i, s in ranked:
        page = doc[i]
        pix = page.get_pixmap(matrix=fitz.Matrix(RENDER_ZOOM, RENDER_ZOOM))
        rel = f"assets/images/{slug}/p{i + 1}.jpg"
        save_pixmap(pix, ROOT / "site" / rel)
        images.append({"file": rel, "page": i + 1, "role": "diagram", "score": s})

    full_text = "\n".join(page_texts)
    return {
        "slug": slug,
        "kind": "pdf",
        "num_pages": n_pages,
        "text_file": str((TEXT_DIR / f"{slug}.txt").relative_to(ROOT)),
        "word_count": len(full_text),
        "images": images,
    }


def process_md(md_path: Path, slug: str) -> dict:
    text = md_path.read_text(encoding="utf-8")
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    (TEXT_DIR / f"{slug}.txt").write_text(text, encoding="utf-8")
    return {
        "slug": slug,
        "kind": "md",
        "num_pages": None,
        "text_file": str((TEXT_DIR / f"{slug}.txt").relative_to(ROOT)),
        "word_count": len(text),
        "images": [],
    }


def main():
    talks = []
    for summit_key, folder in SUMMITS.items():
        for path in sorted(folder.iterdir()):
            if path.name == "manifest.json" or path.name == "web-slides.md":
                continue
            if path.suffix.lower() not in (".pdf", ".md"):
                continue
            m = re.match(r"^(\d+)-(.*)$", path.stem)
            num = int(m.group(1)) if m else 0
            title = m.group(2) if m else path.stem
            slug = f"{summit_key}-{slugify(path.name).rsplit('.', 1)[0]}" if False else f"{summit_key}-{slugify(path.stem)}"
            print(f"Processing [{summit_key}] {path.name} -> {slug}")
            if path.suffix.lower() == ".pdf":
                info = process_pdf(path, slug)
            else:
                info = process_md(path, slug)
            info.update({
                "summit": summit_key,
                "order": num,
                "title": title,
                "source_file": path.name,
            })
            talks.append(info)

    talks.sort(key=lambda t: (t["summit"], t["order"]))
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "talks.json", "w", encoding="utf-8") as f:
        json.dump(talks, f, ensure_ascii=False, indent=2)
    print(f"\nWrote {len(talks)} talks to data/talks.json")


if __name__ == "__main__":
    main()
