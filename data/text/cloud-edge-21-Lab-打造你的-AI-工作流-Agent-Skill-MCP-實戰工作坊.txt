# 當 AI 已經能寫 Code——打造你的 AI 工作流：Agent Skill + MCP 實戰工作坊回顧

- **來源**: https://blog.wu-boy.com/2026/07/ai-workflow-agent-skill-mcp-workshop-zh-tw/
- **活動**: 2026 iThome 臺灣雲端大會 · LAB
- **日期**: 2026 年 7 月 1 日
- **時長**: 90 分鐘
- **講者**: Bo-Yi Wu (@appleboy)

## 前言

2026 年 7 月 1 日，在 iThome 臺灣雲端大會帶了一場 90 分鐘的 LAB 實戰工作坊。這篇文章整理當天的核心內容與動手練習。

同一天還有議程演講回顧： [從觀望到全公司落地：兩年 AI Agentic Coding 導入實戰](https://blog.wu-boy.com/2026/07/ai-agentic-coding-adoption-zh-tw/)。那場講「為什麼與怎麼推」，這場 LAB 則是「實際動手做」。

## 這場工作坊在做什麼

以真實專案為練習場，用 Claude Code 搭配 Agent Skill 與 MCP，完整跑過一輪 SDLC：從規劃、開發，到自動化 Review 與提交。

兩個轉變：

1. 「寫規格」取代「寫程式」成為新的核心競爭力。
2. 從「執行者」升級為「策略者」——把團隊最佳實踐封裝成可複用的 Skill。

## 核心命題：工程師的價值，往上移了一層

從「親手把 code 寫出來」，轉移到「定義問題、設計流程、指揮 AI」。

| 類別 | AI 產出 | 人類產出 | AI 佔比 |
| --- | --- | --- | --- |
| 程式碼 Code | 6.86M 行 | 1.06M 行 | 86.6%（約 6.5 倍） |
| 文件 Docs | 4.97M 行 | 0.22M 行 | 95.7%（約 22.5 倍） |
| 測試 Tests | 0.92M 行 | 0.03M 行 | 96.4%（約 27 倍） |
| 總計 | 12.74M 行 | 1.31M 行 | 90.7% |

過去最常被犧牲的文件與測試，反而被 AI 補得最滿。

## SDLC 全流程分工

- **AI 主導**：Develop、Testing、Docs
- **人為專注**：Plan、PR Review
- **補強**：CI/CD（人主導、AI 加強）

一句話：繁重的交給 AI，方向與品質的把關留給人。

## Part 1：概念對齊——Agent Skill × MCP

### Agent Skill：決定 AI「怎麼做」

把團隊的最佳實踐、流程與規範，封裝成 AI 可複用的能力。

### MCP：讓 AI「接上服務」

把 AI 接上開發環境與外部系統（Jira、Gitea、Confluence……）。

### 企業級 MCP 安全架構

每個請求先過 MCP Gateway 上的 `mcp-oauth2` plugin 驗 JWT：

1. Challenge：無 token → 401 + `WWW-Authenticate`
2. Discovery：讀 `/.well-known/oauth-protected-resource` 找到 IDP
3. Authorize：Auth Code + PKCE，IDP 簽發 RS256 token
4. Verify：JWKS 驗簽章，再驗 `iss`/`aud`/`exp`/`scope`
5. Forward：通過才轉發，附上 `X-MCP-Subject` 與 `X-MCP-Scope`

內部 MCP Servers 只信 Gateway 轉發進來的身分標頭，自己不碰 token。

## Part 2：AI SDLC 全流程實戰

### `/plan-feature`：寫程式之前，先把計畫講清楚

多數 AI coding 失敗，不是因為模型不夠強，而是人沒給足夠的 context。

**該 plan 的情況：**

- 「新增 / 建立 / 實作 / 開發 / 上線」一個功能
- 提示很短、說不清楚
- 只講功能、沒給檔案路徑的需求

**可直接做：** 錯字修正、單行設定、單純重新命名、已給完整規格。

有疑慮時，就 plan（When in doubt, plan）。

八步驟：

1. 釐清目標（Clarify goal）
2. 探索程式庫（Explore code）
3. 界定範圍（Identify scope）
4. 驗證策略（Verification）
5. 畫設計圖（Sketch diagram）
6. 撰寫 plan.md
7. 取得核可 ✋——寫程式前停在這
8. 建議交接（Recommend handoff）

`plan.md` 結構建議：Goal / Architecture / Scope（可改 vs 不可改）/ Patterns / Constraints / Verification / Done definition / Risks / Open questions。

### 三個品質 Skill

1. `/simplify`——收掉過度設計
2. `/security-review`——自動安全審查
3. `/code-review max -fix`——最高強度審查 + 自動修

### Commit 與 PR

- `/commit-message`——讀 staged diff，產出 Conventional Commit
- `/pr-prepare`——標題、摘要、變更重點、測試方式

⚠️ 下指令之前，先自己看過代碼確認沒問題再執行。

### PR 後的 AI Review 選項

1. GitHub Action：Claude Code Review
2. 原生整合：GitHub Copilot Review
3. OpenAI Codex Review

### 自動迴圈：`/loop 3m /copilot-review`

每 3 分鐘一輪：查留言 → 逐條修 → push → resolve → 再審。

上限約 10 輪；再多通常是架構分歧，請人工介入。

## 總結：AI 不是取代 CI/CD，而是把它補完

| 以前的缺口 | AI 補完之後 |
| --- | --- |
| 自動化測試常被犧牲 | ✓ AI 補齊 |
| Code Review 人力不足被省略 | ✓ 自動 review |
| CI 紅燈卡很久沒人修 | ✓ 修到綠燈 |
| 文件 / commit / PR 隨便寫 | ✓ 規格化 |
| 看板 / 狀態靠人手動更新 | ✓ 自動回寫 |

回去之後：挑一個最有感的缺口，用今天的某個 Skill 先讓一格跑到綠燈——可從 `/plan-feature` 或 `/loop 3m /copilot-review` 開始。

---

Bo-Yi Wu（appleboy）／聯發科技後端架構工程師。GitHub: [@appleboy](https://github.com/appleboy)｜Blog: [blog.wu-boy.com](https://blog.wu-boy.com)

