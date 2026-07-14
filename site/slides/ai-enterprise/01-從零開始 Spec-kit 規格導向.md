# 從零開始 Spec-kit 規格導向

- **來源（議程介紹）**: https://chechia.net/posts/2026-07-01-ws-speckit-ai-ent/
- **來源（Workshop 投影片）**: https://chechia.net/slides/2026-07-01-ws-speckit-ai-ent/
- **活動**: AI Enterprise Summit 2026 · Workshop
- **時間**: 2026-07-02 09:00–10:30（約 90 分鐘）
- **講者**: Che-Chia Chang（SRE @ Maicoin / Microsoft MVP）

## Workshop 目標

使用 Spec-kit 實際體驗 Spec-driven Development（SDD）：撰寫可執行規格、善用範本與自動化腳本，並把規格整合進日常開發流程。

### 為何會有幫助：避免 Spec drift

多數團隊導入 AI 寫程式後，常見痛點是需求、規格、實作與測試不同步，最後演變成 Spec drift，導致返工與品質不穩定。本工作坊聚焦用 Spec-kit / SDD 建立「規格先行、可執行驗證、持續對齊」的流程，讓 AI 與工程團隊使用同一份契約協作。

### 學員學習目標

- 理解 Spec-driven development (SDD) 的概念與實踐流程
- 使用 Spec-kit 建立、維護與驗證規格
- 將 SDD 套用至開發任務，提升一致性與品質
- 以 AI Agent 自動化重複流程，減少手動錯誤並加速開發週期

---

## Workshop 行前準備

- 攜帶筆電，可上網
- 安裝 VS Code
- 安裝 Spec-kit CLI
- 下載 workshop 範例程式碼
- 講師提供 Azure OpenAI API Key（也可自帶習慣的 LLM）
- 會用 VS Code + GitHub Copilot Chat 亦可自有方式參加

### 環境設定

```bash
git clone https://github.com/chechiachang/speckit-playground.git
```

安裝 Spec-kit CLI：

```bash
uv --version
# 沒有的話：
curl -LsSf https://astral.sh/uv/install.sh | sh

uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v0.8.9
```

VS Code Chat 設定 Azure OpenAI model（`chatLanguageModels.json`），並先用可用模型做連線測試。

### Mindset

- 先自己思考，再問 ChatGPT
- Workshop 重點在累積動手經驗

---

## 大綱

本次 workshop 以 hands-on 為主、講解為輔：

1. LAB1：第一個 Spec-kit 專案
2. 講解：什麼是 Spec-kit
3. 講解：什麼時候 SDD 會優於 Vibe Coding
4. 講解：Spec-kit 經驗分享（適合／不適合的 use case）
5. 驗收、回顧、Q&A

---

## LAB1：第一個 Spec-kit 專案

核心流程：

```text
/specify -> /plan -> /tasks -> /implement
```

重點：

- SDD：先把需求寫成 Spec，Spec 是唯一 source of truth
- Spec-kit：把 SDD 變成可執行流程，降低 drift 與返工
- 改需求先改 Spec，不先改 code

### 初始化

```bash
specify init --here --integration copilot
specify check
```

會建立 `.specify` 等檔案，並整合 Copilot Chat prompts。

### 建立 Constitution

```text
/speckit.constitution 用zh-tw 專案建立憲法：規格從簡，程式簡潔，及早執行。
```

Constitution 是 agent 行為準則，每次行動都會被參考。

### 建立 Spec（YouBike 範例）

```text
/clear

/speckit.specify 建立一個單頁 Web 應用：台北市 YouBike 2.0 即時站點查詢器。
核心需求：
- 用 python + uv
- 自動從政府 API 抓取 JSON 站點資訊
- 搜尋框：可依「站點地址」或「名稱」過濾
- 列表呈現：站點名稱、可用車輛、剩餘空位

/speckit.clarify
```

### Auto-approve 注意安全

頻繁 approve 會卡住開發；可允許 session 內 auto-approve，但應限制：

- readonly：git / bash / grep 等
- write：只允許特定工具與參數

### Plan / Tasks / Implement

```text
/clear
/speckit.plan
/speckit.tasks
/speckit.analyze
# 依建議修復後再 analyze
/speckit.implement
```

實作過程中可回覆「繼續」「繼續直到完成可執行」，完成後問「如何執行」。

### Interruption & Error Handling

- Agent 卡在 feature branch 規則時，可用 `/speckit.git.feature`
- Spec / Plan / Tasks 未滿足時無法 implement：請 agent 用 zh-tw 說明卡點
- 錯誤若來自 Spec：回頭改 Spec；無關 Spec：直接貼錯誤給 agent 修正

### 驗收

- 先手動驗收：執行、error、功能是否符合 Spec
- 實務上把測試覆蓋率、lint、style 寫進 Spec，讓 agent 自動驗收

```text
/speckit.specify 需要測試覆蓋率達到 80%，並且所有 lint 與 style 都必須通過
```

---

## 什麼是 Spec-kit

- Spec-driven Development toolkit
- 定義 script / template / checklist，讓 agent 可預測地產生 Spec
- 把 workflow 拆成 spec → plan → tasks → implement
- 每步都有 checkpoint，才進入下一步
- 支援長任務、多輪對話 session

> Chat 是聊天，產出 Spec 是工程。SDD 是方法；Spec-kit 是把方法落地成可重複 workflow 的工具。

---

## 為何比 Vibe Coding 有幫助

### 避免 Context rot / Spec drift

Vibe Coding 長對話後 agent 容易混亂、誤解需求；compact 後更容易「照較新對話」做事。

### Context management

複雜需求用多輪聊天容易 long context，效能下降且 compact 可能丟資訊。

### 平行分工

中間產物 Spec 作為 source of truth，利於 review、拆任務與多人協作；最終交付是 Spec + Code。

---

## 為何用 nano / mini

Spec-kit 核心流程（specify / plan / tasks）對模型能力要求不高：

- 用 mini / nano 常可達約 90% 效果，成本約 10–20%
- Spec-kit Tax：比 Vibe Coding 多產生 Spec / Plan / Task
- 實務建議：用較強模型寫 Spec，用 mini 做 implement；並盡力控制 context

---

## 常見失敗模式

1. 還沒寫 Spec 就進 implement
2. 規格改了但 tasks 沒更新
3. 規格太模糊，agent 自由發揮
4. 驗收放最後，回頭成本很高

## 你可以帶走的 3 件事

1. spec → plan → tasks → implement 是可落地流程
2. 規格優先能降低返工成本
3. AI agent 要穩定，必須有 Spec + 驗收標準 loop

---

## 參考資源

- Spec-kit: https://github.com/github/spec-kit
- Spec-driven: https://github.com/github/spec-kit/blob/main/spec-driven.md
- Workshop playground: https://github.com/chechiachang/speckit-playground
- Session: https://aienterprise.ithome.com.tw/2026/session/4788

下午相關議程：LLM O11y：從 Observability 到 Decision System

