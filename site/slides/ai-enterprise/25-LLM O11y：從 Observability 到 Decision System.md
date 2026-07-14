# LLM O11y：從 Observability 到 Decision System

- **來源**: https://chechia.net/slides/2026-07-01-langfuse-ai-ent/
- **活動**: AI Enterprise Summit 2026 · 正式議程
- **副標**: 從監測到資料決策
- **講者**: Che-Chia Chang（SRE @ Maicoin / Microsoft MVP）
- **對應 Lab 投影片**: https://chechia.net/slides/2026-07-01-ws-langfuse-ai-ent/

## 開場：身為技術負責人，如何回答這些問題？

同事常會問：

- Spec-kit SDD 聽說很好用
- rtk 聽說省 Token，我們要不要用？
- Opus／新模型聽說更強、升級不加錢，為何不升級？
- 某模型 Benchmark 贏現在用的，要不要換供應商？

常見回應方式：每個都試、看大大／供應商文章、給代理商或公有雲推薦。

但 **新工具冒出速度 > 人研究速度**。缺的不是更快的研究速度，而是 **數據化決策**。

真正缺的是：LLM 解決方案的量化評估系統——團隊信任現有 Stack、不會 FOMO，並有能力驗證改動影響。

---

## 今天的大綱

1. AI 時代的工具抉擇，缺乏數據化決策
2. 建立 baseline 與第一次優化
3. LLM as a Judge
4. Dataset & Experiment
5. 釐清需求：提升 Coding Agent 效能
6. Decision System

（技術細節與操作見上午／對應 Lab：LLM O11y Workshop）

---

## 有了 Observability Stack 之後

- 看到量化數據：Token Usage、Latency、Error Rate
- Chargeback：團隊使用者看到自己的成本
- 基於監測紀錄的預算控管，而非市場喊價
- 建立成本與 Token Usage baseline：什麼是符合／超過預算

---

## Step 1：建立 baseline 與第一次優化

- 理解使用的 CLI（VSCode Copilot、Codex、OpenCode 行為不同）
- 停用無用 Tools（Built-in 50+，實務常用常只有 10+；Extension 也會加 Tools）
- 透過 AI Gateway
- 控制 CLI System Instruction 內容

第一次優化後常見效果：

- Token Overhead：20000+ → 1000+
- 成本：約 0.1 USD → 0.005 USD（約 5%）
- 降低 Long Context 機率（例如 ≥272K tokens 變兩倍價）
- 把 Context Window 留給真正有用的 Context

---

## Step 2：LLM as a Judge

- Step 1 依 Tracing Metadata 做 **成本** 最佳化
- LLM-as-a-Judge 依 Tracing Input/Output 做 **品質** 最佳化
- 傳統測試場景侷限，難覆蓋 LLM 多變場景

以 Observation 為單位評估 API Call：

- 小 scope 量化評估，反映局部品質
- 暫且以管窺天：分析錯誤類型、找改進方向

第二次優化：控制變因（Token／Latency／Cost／Model Version），優化 Prompt 與 Instruction；Judge 不變，持續提升局部評分。

### Multi-turn Agent

Long-running agent 很難直接只看最終答案。應針對單一步驟評估，例如 Plan 或 `apply_patch` tool call。

---

## Step 3：Dataset & Experiment

**Dataset**：從 Daily Work Tracing 挖出的考古題

- Input = 真實工作需求
- Output = 上次 Model 回答
- Judge 分數 = 品質訊號

**Experiment**：同一份考古題，換變因重跑

- Model 5.4 → 5.5
- Tools 改動前後
- Instruction 改動前後

依需求把 Dataset 分類（例：Plan 看 Context Precision；Coding 看 Answer Correctness），也可依分數分 good／其他。

Data preprocessing：清理格式、抽出 features（如 `Output.tool_calls.args`）、transform、partition、持久化。

第三次優化：針對情境選最適合工具與 Model（Pro／Mini／Nano、Thinking Effort、不同 CLI）——不是等模型變強，而是做品質與成本平衡。

---

## Step 0：釐清需求（其實該最先做）

實務上很多團隊：

- 沒清楚定義需求
- 對 LLM 理解有落差
- 就開始討論要不要換工具

建議「先有監測」：先看到顯微镜下的世界，再用數據調整團隊認知。

效率定義：

$$
\text{整體效率} = \frac{\text{產出數量} \times \text{產出品質}}{\text{Token Cost} \times \text{花費時間}}
$$

需求 → Action 範例：

- 不同任務選不同 Model／Routing
- Context Management → rtk
- 加速 Greenfield → Spec-kit

### On the same page

- Dev Team：Cost Chargeback、Model & Tool Evaluation
- Stakeholders：對齊正確率、Error Rate、Latency、Cost——不是「有 AI 就能十倍產出、開除人類」

---

## Takeaway：從零開始的 Decision System

1. Step 1：建立 baseline 與第一次優化
2. Step 2：LLM as a Judge
3. Step 3：Dataset & Experiment
4. Step 0：釐清需求
5. Decision：釐清需求 → Take Action

缺數據時，不要用「聽說」做決策；先建 O11y，再驗證改動。

