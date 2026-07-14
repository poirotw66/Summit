# When Not to Vibe：從 Chat-driven coding 到 Spec-driven AI Engineering

- **來源**: https://chechia.net/slides/2026-07-01-speckit-cloud-summit/
- **活動**: Cloud Summit 2026
- **講者**: Che-Chia Chang（SRE @ Maicoin / Microsoft MVP）
- **類型**: 網頁投影片整理

## 本議程會告訴你

1. Chat-driven coding 的邊界
2. SDD 的核心概念
3. Spec-kit 落地流程
4. 何時切換與如何起步

## Chat-driven coding 的價值

- 快速探索，驗證想法，PoC
- 在短週期任務，Chat-driven 很有價值

## Chat-driven Coding 的挑戰

- 輸出不穩定
- 團隊協作難追蹤
- 複雜需求 + 多輪對話，容易產生 long context
- 對話拉長，模型偏移，容易 context drift

長 context 可能造成 LLM 效能下降（參考 arXiv:2404.06654）。模型的 context window 理論值，實際可用的 effective context 更短；最前與最後的 input 模型比較能使用（Lost in the Middle / Positional Biases）。

### 挑戰總結

- 不易控制 context
- context 前後有出入，導致 context drift
- 模型更記得最前面跟最後面的訊息

> Spec-kit 流程實際是不斷整理 context。

## Chat-driven Coding vs SDD

假設需求寫出來是十萬字：

- **Chat-driven**：透過多輪對話，把內容一段一段分散給模型
- **SDD**：Plan 時把內容整理成結構化 Spec，實作時讓模型一次讀進 Spec

## What is SDD（Spec-driven development）

- Spec > source of truth
- Spec > Implementation
- Feedback > Spec
- 模糊需求 → 可執行規格

### Spec 需要可驗收任務

驗收標準明確，例如：

- SOP/Runbook 步驟完成率 → %
- CI/CD Pipeline 成功率 → %
- Lead Time → 分鐘
- Infra / Cloud 成本 → 每月金額
- SLO 達成率 → %

## SDD 導入第一步

找第一個切換題目：

- 高人工成本
- 流程固定（SOP/Runbook）
- 低風險
- 被依賴性低

### 情境分享：跨平台帳號與權限稽核

- 平台：aws, azure, gcp, github, jenkins…
- 需求清楚：列出帳號、檢查條件、輸出報告
- 高人工、重複性高、容易漏

### 實際導入流程

1. 挑題目：低風險、高人工、需求清楚
2. 規格化：把需求寫成 Spec 與驗收條件
3. 拆任務：Spec → Plan → Task
4. 實作：Task 具體可驗收，agent 才能穩定交付

## What is Spec-kit

- Spec-kit 是 GitHub 的 SDD toolkit
- 是一個 SDD 流程框架
- 不是 prompt 技巧，是可重複工程流程
- 把需求、驗收、交付串成同一條線

### Spec-kit 核心流程

```text
/speckit.specify   列出需求與檢查條件...
/speckit.plan      修改先後順序...
/speckit.tasks     拆成獨立子任務，可分配給 subagent...
/speckit.analyze   檢查 Task 依賴性
/speckit.implement
```

### 情境落地

- ✅ 挑題目
- ✅ 規格化
- ✅ 驗收標準
- ✅ 拆任務：每個平台一組 task，平行實作
- 實作：subagent 分工，主流程整合

## Spec-kit 帶來的痛點

- 工作習慣改變：痛點左移，寫 code 時的痛苦提前到寫需求時
- Spec-kit tax：產生 Spec 會消耗額外 token（可用貴模型寫 Spec、便宜模型實作）
- 不適合舊專案：無法從舊程式碼逆向產生 Spec；從頭寫 Spec 燒時間與 token

### 改需求的成本變高

- Spec 寫好、Code 寫好後改需求 → Spec / Plan / Task / agent 都要重跑
- 小改動可以像 git commit 一樣疊上去
- 大改動或需求矛盾就要重寫 Spec（Spec-kit 可掃出 conflict，但不幫你解決）
- 需求變動頻繁的任務不適合 Spec-kit，反而會變得笨重

### Spec-kit 解決了什麼，沒解決什麼

- **解決**：需求結構化、任務拆解、協作流程
- **無法解決**：需求變動頻繁的任務；舊專案的 Spec 產生

## 你可以帶走的重點

- Chat-driven 適合探索，不適合所有正式交付
- When Not to Chat-driven：高風險、可驗收、多人協作場景
- SDD + Spec-kit 讓 AI 開發流程可工程化
- 加上 Eval + Loop，才能穩定落地

