# Summit 2026 議程摘要網站

彙整 **AI Enterprise Summit 2026** 與 **Cloud & Edge Summit 2026** 兩場研討會共 68 場議程的
投影片（PDF／Markdown），自動擷取文字與重點架構圖／示意圖，並整理成可瀏覽、可搜尋的靜態網站。

## 網站內容

- `site/index.html`：議程總覽首頁，可依 Summit 篩選、依標題／講者／關鍵字搜尋
- `site/talks/<slug>.html`：每場議程的詳細頁，包含：
  - 摘要（2–4 句話）
  - 重點整理（條列式 highlights）
  - 重點圖片／架構圖（自動從投影片中挑選並嵌入）
  - 詳細內容分段說明（背景、架構、技術重點、案例、結論等）

## 專案結構

```
AI-Enterprise-Summit-2026-slides/   原始投影片（PDF/MD，不納入版控，見 .gitignore）
Cloud-Edge-Summit-2026-slides/      原始投影片（PDF/MD，不納入版控）
scripts/
  extract.py       擷取每份 PDF 的文字與候選架構圖，輸出到 data/ 與 site/assets/images/
  build_site.py    讀取 content/*.json + data/talks.json，產生 site/ 底下的靜態網頁
data/
  talks.json       所有議程的中繼資料（標題、講者頁碼、圖片清單等）
  text/*.txt       每場議程擷取出的純文字（供人工／AI 撰寫摘要參考）
content/*.json     每場議程人工／AI 撰寫的摘要、重點、詳細內容與圖片說明（網站真正的內容來源）
site/              產生的靜態網站（實際部署的內容）
.github/workflows/deploy.yml   GitHub Actions：推送到 main 分支後自動部署 site/ 到 GitHub Pages
```

## 重新產生網站

若修改了 `content/*.json` 或 `data/talks.json`，重新產生 `site/`：

```bash
python3 scripts/build_site.py
```

若要重新從原始 PDF 擷取文字與圖片（需要原始投影片資料夾存在）：

```bash
pip install pymupdf pillow
python3 scripts/extract.py
```

## 部署到 GitHub Pages

1. 將此專案推送到 GitHub repository（分支 `main`）。
2. 到 repository 的 **Settings → Pages**，將 **Source** 設定為 **GitHub Actions**。
3. 推送後，`.github/workflows/deploy.yml` 會自動建置並部署 `site/` 資料夾內容到 GitHub Pages。

## 內容免責聲明

網站內容為 AI 輔助整理之摘要，僅供快速瀏覽參考，正確與完整內容請以各議程原始投影片為準。部分投影片
PDF 缺乏可擷取文字層（整頁皆為圖片），此類議程之內容改依提供之補充資訊整理，並於頁面中標註。
