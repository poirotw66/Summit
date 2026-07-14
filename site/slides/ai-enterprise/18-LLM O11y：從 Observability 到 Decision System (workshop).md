# LLM O11y：從 Observability 到 Decision System（Workshop）

- **來源**: https://chechia.net/slides/2026-07-01-ws-langfuse-ai-ent/
- **活動**: AI Enterprise Summit 2026 · Workshop
- **副標**: 量化並提升 Coding Agent 效率
- **講者**: Che-Chia Chang（SRE @ Maicoin / Microsoft MVP）
- **範例 repo**: https://github.com/chechiachang/llm-o11y

## Workshop 行前準備

- 攜帶筆電、可上網
- 安裝 VS Code
- Clone workshop 範例程式碼
- 講師提供 Azure OpenAI API Key
- 已習慣其他 agent CLI（如 Codex CLI）可用原本方式

```bash
git clone https://github.com/chechiachang/llm-o11y.git
cd llm-o11y
docker compose config
docker compose pull
docker compose up -d
```

服務入口：

- Bifrost AI Gateway：http://localhost:8080/
- Langfuse UI：http://localhost:3000/（示例帳密見現場投影片）
- MinIO UI：http://localhost:9001/

於 VS Code Chat 將 Model 指向 Bifrost Gateway（`chatLanguageModels.json` 的 `url` 設為 `http://localhost:8080/v1/responses`）。

---

## 大綱

1. AI Gateway & Observability stack
2. Tracing & Token 花費，Agent 如何花 Token
3. 情境 1：同事問 rtk 好像會省 Token，要不要導入
4. LLM-as-a-Judge Evaluator
5. Dataset & Experiment（基於 past tracing）
6. 情境 2：Evaluate multi-turn agent

遇到問題：先問 ChatGPT 再問講師；重點在動手累積經驗。

---

## 現況整理：Bifrost 與 Langfuse

### Bifrost AI Gateway

- 團隊／公司 LLM Proxy
- 支援多模型、Routing、預算、虛擬 API Key
- OTel tracing，可串 Langfuse 等 o11y 工具

### Langfuse

- Tracing 收集與分析
- LLM-as-a-Judge、Datasets、Evaluation（OSS / MIT）

關係：Gateway 管模型與進出；Observability 管 tracing／分析。Bifrost 進階 o11y 多為 Enterprise；Langfuse 這些能力開源可用。

最方便做法：`CLI → AI Gateway → Observability`

---

## Task：理解 Token 花費

### Task 1: Reduce Overhead

請 VSCode Chat 說一個笑話，產生 tracing；在 Langfuse Observations 看：

- 總共花多少 Token？
- 花在哪裡？有無 cached Token？

### Task 2: Understand Cached Token

同一 session 再說第二、第三個笑話，比較 Token；`/compact` 或 `/clear` 後再說第四個，觀察差異。

### Task 3: 調整 Tools

`gen_ai.request.tools` 每個 API call 都會帶工具列表（agent CLI 低消）。停用不必要 tools 後再開新 session，看 Token 是否下降。

建議：

- 拆分 Plan agent（readonly）與 Write agent
- 停用少用工具：Browser、某些 extension、Notebooks…  
- 不建議全關：Agent / search / Read File 等是核心

### Task 4: 調整 Instructions

就算 Tools 全關，仍可能剩 2000+ Token 基礎花費。檢查：

- `AGENTS.md`（`chat.useAgentsMdFile=true`）
- `.github/copilot-instructions.md`
- system instruction 來源

可用 `/debug` 看 metadata、system instruction、多輪內容。

### 小結：Know Your Agent

進入全自動前先確認設定；手動浪費錢 → 自動花式燒錢。以 team 為單位 review agent 設定。

---

## Case 1：導入 rtk 是否有幫助

情境：同事問 https://github.com/rtk-ai/rtk 好像會省 Token？

評估框架：

1. **理解自己團隊**：問題核心是什麼？學新框架成本？
2. **Know Your Stuff**：rtk 是什麼、支援哪些 cmd？
3. **Know Your Case**：從 Langfuse 看目前 Token 花在哪、最常跑哪些 cmd
4. **Experiment**：`rtk init --copilot` 觀察變化，再 `rtk unpatch`
5. **適不適合**：會多花／省下多少 Token
6. **團隊對齊**：為何會覺得「省 Token」？結論是什麼

效率定義：

$$
\text{效率} = \frac{\text{產出數量} \times \text{產出品質}}{\text{Token Cost} \times \text{花費時間}}
$$

Workshop 前半主要觀察 Token Cost。

---

## LLM-as-a-Judge

在 Langfuse：Evaluation → LLM-as-a-Judge → 建 LLM connection（Azure）→ 建 Evaluator（如 Helpfulness）。

### Task 5: Judge Helpfulness / Debugging

- 觀察分數與評分理由是否合理
- 常見問題：部分 Observation 沒有 output，導致評分失真
- Multi-step agent：最終 Output 才在後面；可先以單一步驟／tool call 為單位評分

### Task 6: Custom Evaluator（例：Apply Patch Safely）

用 filter 只評特定 tool（如 `apply_patch`、`run_in_terminal`），並做 variable mapping。

小結：llm-as-a-judge 只是開頭，重點是建立可持續修正的規則——對你們團隊，什麼樣的 Coding Agent 才算好。

> Observability → Decision System：Evaluator 像顯微鏡，避免以管窺天。

---

## Dataset & Experiment

- 從 daily tracing 建立 dataset（腳本示例：`./scripts/create-langfuse-dataset-from-observations.sh`）
- 資料前處理很重要：原始 tracing 雜亂，需過濾 Input / Expected Output / metadata
- Experiment：同一份考古題，換 model／tools／instruction 重跑
- 情境：同事問要不要換 gpt-5.5 → 用 experiment 看是否真的提升；不同任務選不同模型

### Multi-turn / Long-running Agent 練習

可結合 Spec-kit 流程做長流程觀測（`/speckit.specify` → plan → tasks → implement），或直接給 Coding Agent 真實功能需求並觀察 judge 分數。

---

## 總結

從監測 Token／Tracing，到 LLM-as-a-Judge，再到 Dataset & Experiment，把「聽說」變成「數據化決策」。

