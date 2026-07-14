# Microsoft Agent Framework + Orleans 打造雲地協同 AI 工作流

- **來源**: https://windperson.github.io/CloudSummit_2026-slide/
- **活動**: Cloud Summit 2026
- **講者**: 老鮑伯
- **類型**: 網頁投影片整理

## Agenda

1. MAF（Microsoft Agent Framework）介紹
2. Microsoft Orleans 簡介，結合 MAF 建立多代理系統
3. Azure AI Search Agentic Retrieval（AgenticRAG）多代理範例
4. OpenClaw .NET C# 兩個主流實現版本

---

## MAF（Microsoft Agent Framework）

Microsoft Agent Framework（MAF）是微軟開發的 MIT 授權開源 AI Agent 系統開發框架。

- 官網：https://learn.microsoft.com/agent-framework
- GitHub：https://aka.ms/AgentFramework

提供 .NET C# 與 Python API：除了控管 LLM 的 AI Agent，亦有多代理工作流（Workflow）協調功能。

### AI Agent 的定義（學術）

- 自主性：能在沒有人工干預下運行
- 感知能力：感知環境並收集資訊
- 決策能力：根據資訊做出合理決策
- 行動能力：執行決策並影響環境

### MAF 控制 LLM 架構

MAF 提供一致的 `AIAgent` API，底層用 `IChatClient`（OpenAI API），可切換不同 LLM Host。

除了雲端 OpenAI / Azure AI，地端 Ollama、LM Studio 等若提供 OpenAI compatible REST API，也可串接。

### Session 管理

- 可用 MAF 框架的 Session 管理
- 也可用底層 LLM Hosting Service 自己的 Session 管理

預設 `InMemoryChatHistoryProvider` 將對話記在記憶體；也可自訂 `ChatHistoryProvider`，或用 `CosmosDbChatHistoryProvider`。

另有 `AIContextProvider` 抽象類別，可自訂與 LLM 互動的 Context 儲存。

### Tooling & MCP

上層抽象為 `AITool`，可呼叫：

- .NET C# Method
- MCP endpoint
- 另一個 `AIAgent`

非 Foundry Hosted MCP Server 時，建議用第三方套件 Agent Framework Toolkit。

### Skill / Workflow / 其他

- Agent Skill：可讀 `.md` 檔或由 C# 文字注入
- Agent Workflow：多種協調模式（比 AutoGen 更多樣）
- 其他：A2A、Middleware、OpenTelemetry
- C# 尚未完全齊的：AG-UI、DevUI、CodeAct、Microsoft Foundry Local

---

## Microsoft Orleans + MAF

Orleans 適合處理「同時多人／多狀態、又要有一定回應速度」的系統（non-functional requirement）。

過去嘗試：

- AutoGen v0.4.x-dotnet（未完成）
- project-oagents（Semantic Kernel C# + Orleans）

### 範例重點

在 Orleans Grain 中整合 MAF `AIAgent`，例如在 Grain 內建立 orchestration / rag / search agent。

參考：Building Stateful AI Agents at Scale with Microsoft Orleans

Orleans 簡介錄影：https://youtu.be/oiJvbKReiTw

範例 #2 相關直播：https://www.youtube.com/live/OQqhQpHR3Gg

---

## Azure AI Search Agentic Retrieval（AgenticRAG）

與傳統 RAG 不同：AgenticRAG 會用 LLM Agent 分析查詢，拆成多個檢索任務／工具呼叫，再整合生成回應。

注意：

- Azure AI Search 與 Microsoft Foundry 需設定正確的 Managed Identity role
- C# SDK 仍在 Preview，版本可能不相容
- 設定好的 Azure AI Search 預設有 MCP endpoint，可用 Auth Token 叫用（雲端與地端 LLM 皆可）

---

## OpenClaw .NET C# 兩個主流實現

1. **OpenClaw.NET（AgentQi）** — https://agentqi.dev/docs/start-here
2. **OpenClaw .NET（El Bruno / Microsoft Reactor）** — https://elbruno.github.io/openclawnet/

官方教學：

- https://devblogs.microsoft.com/agent-framework/meet-your-agent-harness-and-claw/
- 範例：https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/02-agents/Harness

---

## 其他參考資料

- Aspire for agents：https://build.microsoft.com/en-US/sessions/BRK205
- NuGet `Microsoft.Agents.AI`：https://www.nuget.org/packages/Microsoft.Agents.AI
- Chat History Storage Patterns：https://devblogs.microsoft.com/agent-framework/chat-history-storage-patterns-in-microsoft-agent-framework/
- eShopLite：https://github.com/Azure-Samples/eShopLite
- What is Agentic RAG?：https://learn.microsoft.com/en-us/shows/ai-agents-for-beginners/what-is-agentic-rag

