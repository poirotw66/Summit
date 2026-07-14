# 從觀望到全公司落地：兩年 AI Agentic Coding 導入實戰

- **來源**: https://blog.wu-boy.com/2026/07/ai-agentic-coding-adoption-zh-tw/
- **活動**: 2026 Cloud Summit 台灣雲端大會
- **日期**: 2026.07.01
- **講者**: Bo-Yi Wu (@appleboy)

## 前言

去年這個時候，我們在想的是「AI 怎麼協助我們改善工作效率」；今年，問題反過來了——「我們該怎麼協助 AI，讓它加速我們的工作」。主詞和受詞對調，聽起來像文字遊戲，但這正是這兩年公司內部 AI Agentic Coding 導入路上，最核心的一次心態轉變。

這篇文章記錄的是一段真實走過的路：從少數人偷偷試用 Claude Code，到全公司日常使用；從 AI 產出佔比 66%，一路衝到 97%；從工程師「不信任、怕被取代、擔心資安」的三種觀望心態，到用成果說話、把個人技巧封裝成標準化的 Agent Skill；從每個團隊各自寫 MCP Server 導致的專案爆炸，到用統一認證閘道與 Marketplace 審查機制把整個生態圈的資安治理收攏起來。

三個部分，跟著我們真實走過的順序：這一年的全貌與成果 → 從觀望到全員 → 流程整合與安全治理。

## Part 1：這一年的全貌與成果

### 心態轉換：從「AI 幫我們」到「我們幫 AI」

這個對調不是修辭，它決定了後面所有決策的方向。

- 2025 年：我們在想 AI 怎麼「協助我們」改善工作效率——AI 是工具，我們是主角。
- 2026 年：我們在想如何「協助 AI」加速工作效率——我們幫 AI 鋪好基礎，讓它替我們加速。

換個更貼近日常管理的說法：主管不是自己埋頭做，而是幫團隊鋪好路、讓他們跑得更快——對 AI，是同一個道理。這篇文章後面談的認證閘道、Token 治理、Marketplace 審查，說到底都是在幫 AI 建基礎設施，而不是在教 AI 寫程式。

### 導入時間軸：從工具問世到全公司落地

| 時間 | 里程碑 |
| --- | --- |
| 2025-02 | Claude Code 橫空出世：AI coding agent 正式登場，外部生態的起點 |
| 2025-03 | 整合 AI Gateway：IT 協助把 Claude Code 串進內部 AI Gateway |
| 2025-05 | 串接 Observability：IT 接上可觀測性，開始量化導入效益 |
| 2025-09 | 導入 SWRD 部門：落地軟體研發相關部門 |
| 2025-10 | Anthropic 推出 Skill：改變了整個 Workflow 生態 |
| 2026-04 | 落地 HWRD 部門：擴展到硬體研發相關部門 |

三個階段：外部生態起點（工具問世）→ 內部整合（Gateway、Observability）→ 規模落地（部門一個接一個導入）。工具問世只是起點，真正決定能不能「落地」的，是中間那段看不見的內部基礎設施工作。

### GAISF Gateway：所有 AI 呼叫的單一進出口

不管是 CLI 工具、Web Service 還是 Browser，開發者端每一次 AI 呼叫都先統一從一道閘門進出，再由 Gateway 分流到公有雲與自建模型。

單一進出口一次解決四件事：

| 項目 | 說明 |
| --- | --- |
| 使用量分析 | 誰用了多少、用在哪，靠 Grafana & Loki 全看得見 |
| 內部稽核 | 每次呼叫都進 Log Service 留痕，事後可追溯 |
| 控管流量花費 | 集中計量與設限，雲端與 GPU 成本不再失控 |
| 權限控管 | 依部門與角色，決定可用的模型與範圍 |

Gateway 只保留稽核所需的資訊，Request / Response Body 都已過濾——在「看得到誰用了什麼」與「不窺探開發者實際內容」之間找到平衡。

### 用數據說話：AI 佔比從 66% 衝到 97%

| 月份 | 2025-08 | 09 | 10 | 11 | 12 | 2026-01 | 02 | 03 | 04 | 05 | 06 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AI 佔比 | 66% | 80% | 80% | 81% | 88% | 92% | 94% | 91% | 95% | 96% | 97% |
| 月產出量 | 0.22M | 0.57M | 0.46M | 0.76M | 1.18M | 1.56M | 1.40M | 1.31M | 1.89M | 2.08M | 2.26M |

十個月內，AI 佔比從 66% 爬升到 97%；同時月產出量成長將近 10 倍。工程師親自寫的量幾乎是一條平盤——不是工程師變少了，而是他們把時間換到規劃、審查、把關。

## Part 2：從觀望到全員

### 工程師為什麼不用？三種真實心態

1. 不信任品質——「AI 寫的還要全部重看，不如自己寫。」
2. 怕被取代——「學這個是不是在淘汰自己？」
3. 資安疑慮——「code / 公司資料會不會被送出去？接內部系統怎麼授權？」

前兩種是心態問題，可以靠時間和成果慢慢磨；第三點才是真正卡住規模化的那一個。

### 主管的兩難：缺一條「安全的路」

- 不推：眼看著別的團隊用 AI 把效率拉開，自己團隊原地踏步。
- 硬推：一旦有人把金鑰寫進 Git、機敏資料丟到外部，鍋是主管自己背。

缺的不是決心，是一條技術上「安全可控」的路。

### 用成果說話，不要用命令

真正有效的路徑是三步走：

1. 個人試用——找愛玩、有影響力的 2–3 人，做出同事會羨慕的成果。
2. 團隊標準化——把個人技巧封裝成共用資產，全團隊複用。
3. 全公司落地——靠 AI Skill Marketplace 平台統一分發，後端介接公司內部 Git 服務。

第二步具體做法是 Anthropic Agent Skill 標準。從 plan 到 merge 的開發流程：

| 步驟 | 內容 | 角色 |
| --- | --- | --- |
| 01 Plan | `/plan-feature` → plan.md | 人・對齊方向 |
| 02 Develop | 依 plan.md 實作 | AI |
| 03 Quality | `/simplify` `/security-review` `/code-review --fix` | AI |
| 04 Commit | `/commit-message` → Conventional Commit | AI |
| 05 PR | `/pr-prepare` → PR 描述 | AI |
| 06 Review | `/loop` `/copilot-review` 查→修→再審 | AI 自動迭代 |
| 07 Merge | CI 綠燈 → Merge | 人・最終把關 |

規劃階段和最終合併，人為把關；中間從開發到審查迴圈，AI 自動迭代跑完。

## Part 3：流程整合與安全治理

### 全公司落地的真正門檻：專案爆炸

每個團隊都用 AI 快速產出服務，專案數量從 5x、2xx，爆炸成長到 1xxx 個。這麼多 CLI / MCP / Agent 要接內部系統，認證與授權怎麼管，變成無法回避的問題。

### Agent Skill 與 MCP 的分工

| Agent Skill（主導） | MCP（專責） |
| --- | --- |
| 「怎麼做」——整體使用知識 + 流程 | 「接什麼」——整合第三方服務 |
| 使用知識與規範、整體 Workflow 編排 | 第三方服務整合、Auth 安全連線與驗證 |

### MCP 推廣的阻力：Token 明碼躺在 Client 端

認證 Token 是明文，直接躺在開發者的 Client 端（`settings.json`、CLI `--header`、shell history）。

### 被 AI 放大的三大資安風險

1. 認證各自造輪子——每個服務自己接 LDAP，帳密邏輯散落、標準不一。
2. 金鑰寫死流入 Git（最致命）——CLI / MCP 沒有瀏覽器登入流程，帳密 / API Key 寫死隨 code 推上 Git。
3. Token 發出就失控——誰持有、何時過期、能否撤銷全不知道。

### 解法一：統一認證閘道

不管是 CLI、MCP Server、AI Agent 還是內部服務，全部只走一個門：IdP（OAuth 2.0 / OIDC）。

不同場景對應不同的 OAuth 流程：

- Web → Auth Code + PKCE
- CLI・Agent → Device Flow
- 服務對服務 → Client Credentials / private_key_jwt

Device Flow + PKCE：帳密只在使用者瀏覽器登入那一步出現，走公司既有 SSO；CLI / MCP 端全程只拿到短效 access token，存進 OS keyring 加密。

### 解法二：Token 治理（RFC 8707 Resource Indicators）

每個 MCP 都當成獨立的 OAuth Resource：token 綁死在某一個 MCP，`aud` 不符直接被擋。最小權限、收斂爆炸半徑；RS256 + JWKS 在地驗章；每個 token 可查詢、可設到期、即時撤銷。

### 解法三：MCP Gateway 把關

Client → MCP Gateway（`mcp-oauth2` plugin 驗 JWT）→ 內部 MCP 集群。內部 MCP Server 只信 Gateway 轉發進來的身分標頭。

一次完整握手五步：Challenge → Discovery → Authorize → Verify → Forward。

### 解法四：AI Marketplace 上架與認證

同一個 PR，觸發三道並行掃描，三道全綠才放行：

1. Coverity Scan（SAST）
2. Trivy Scan（SCA）
3. Code Review（AI Review）

## 小結

用成果說話，把關鍵一次做對。

- 心態上：從「AI 幫我們」翻轉成「我們幫 AI」。
- 推廣上：個人試用 → 團隊標準化 → 全公司落地。
- 治理上：統一認證閘道 + Token 治理 + CI 三道掃描。

AI 產出佔比衝上 97% 本身沒那麼重要；真正重要的是，這 97% 是建立在一條「安全可控」的路上跑出來的。

