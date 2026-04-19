# Enterprise AI Control Tower (EAIC)

Enterprise AI Control Tower is a production-grade AI orchestration and self-healing platform designed for enterprise-level document intelligence and automated workflows. It integrates advanced **RAG (Retrieval-Augmented Generation)** with a **Multi-agent collaboration framework** to solve complex business automation needs.

Enterprise AI Control Tower 是一個專為企業設計的 AI 自修復與任務編排平台。它整合了先進的 RAG (檢索增強生成) 技術與多智能體 (Multi-agent) 協作框架，旨在解決複雜的自動化作業與文檔檢測需求。

---

## 🏗️ System Architecture (系統架構)

The system is built as an **AI execution control plane**, where a central Orchestrator manages specialized agents and enforces enterprise security policies.

本系統構建為 **AI 執行控制平面**，由中央編排器管理各類專門的智能體，並強制執行企業安全策略。

```text
                ┌──────────────────────┐
                │     User / API       │
                └─────────┬────────────┘
                          │
                          ▼
            ┌──────────────────────────┐
            │ Orchestrator (LangGraph) │
            └─────────┬────────────────┘
                      │
      ┌───────────────┼──────────────────────┐
      ▼               ▼                      ▼
┌───────────┐  ┌──────────────┐   ┌────────────────┐
│ RBAC Agent│  │ Task Router  │   │ Audit Agent     │
└─────┬─────┘  └─────┬────────┘   └──────┬─────────┘
      │              │                   │
      ▼              ▼                   ▼
┌───────────┐  ┌──────────────┐  ┌────────────────┐
│ Document   │  │ Finance      │  │ Log Storage    │
│ Agent (RAG)│  │ Agent        │  │ (Postgres)     │
└─────┬─────┘  └─────┬────────┘  └────────────────┘
      │              │
      ▼              ▼
  Vector DB      External APIs
 (pgvector)     (LLM / Tools)
```

### Core Components (核心組件):
- **Orchestrator (LangGraph)**: Maintains system state and controls the execution flow of the AI logic.
  - **編排器 (LangGraph)**: 維護系統狀態並控制 AI 邏輯的執行流。
- **RBAC Guard Agent**: Enforces permission-aware AI execution based on user roles (Admin, Finance, Analyst, Viewer).
  - **權限控制智能體**: 根據用戶角色（管理者、財務、分析師、檢視者）強制執行具備權限意識的 AI 運作。
- **Document Intelligence Agent (RAG)**: Processes and retrieves information from enterprise documents using Vector DB.
  - **文檔智能智能體 (RAG)**: 使用向量資料庫從企業文檔中處理並檢索信息。
- **Audit Agent**: Tracks every step of the execution for full traceability and compliance.
  - **審計智能體**: 追蹤執行的每一個步驟，確保完整的可追溯性與合規性。

---

## 🚀 Key Features (核心功能)

- **Multi-Agent Orchestration**: Build complex AI decision flows using LangGraph.
  - **多智能體編排**: 基於 LangGraph 構建複雜的 AI 決策流。
- **Hybrid RAG System**: Precision retrieval using PgVector and multiple embedding models.
  - **混合型 RAG 系統**: 結合 PgVector 與多種嵌入模型進行精準檢索。
- **Multi-LLM Support**: Switch between OpenAI, Google Gemini, and Anthropic Claude.
  - **多模型支援**: 靈活切換 OpenAI、Google Gemini 與 Anthropic Claude 模型。
- **Full Observability**: Integrated with LangSmith for tracing latency, cost, and decision paths.
  - **全方位監控**: 深度整合 LangSmith，追蹤延遲、成本與決策路徑。

---

## 🛠 Tech Stack (技術棧)

- **Frontend**: React 19, Vite, Tailwind CSS, Axios.
- **Backend**: Python 3.11, FastAPI, SQLModel (SQLAlchemy).
- **AI Framework**: LangChain, LangGraph, LangSmith.
- **Database**: PostgreSQL with PgVector extension.
- **Deployment**: Docker, Docker Compose, UV (Package Management).

---

## 🏁 Getting Started (啟動方式)

### Method A: Docker (Fastest) / 方法 A: 使用 Docker (最快)

Ensure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed.

1. **Spin up all services / 一鍵啟動所有服務**:
   ```bash
   docker-compose up --build
   ```
2. **Access URLs / 存取連結**:
   - **Frontend UI**: [http://localhost:7800](http://localhost:7800)
   - **API Docs (Swagger)**: [http://localhost:7801/docs](http://localhost:7801/docs)

### Method B: Local Development / 方法 B: 本地開發環境

1. **Database / 資料庫**:
   ```bash
   docker-compose up -d postgres
   ```
2. **Backend / 後端**:
   ```bash
   cd packages/backend
   uv sync
   uv run python -m app.main
   ```
3. **Frontend / 前端**:
   ```bash
   cd packages/frontend
   npm install
   npm run dev
   ```

---

## 🔄 User Flow (用戶流程)

1. **Settings (環境設置)**: Configure API keys and backend URLs.
   - 用戶在 **Settings** 分頁配置 API 金鑰與後端連接線。
2. **Documents (文檔管理)**: Upload PDFs/Markdown to initialize the RAG knowledge base.
   - 上傳文檔以初始化 RAG 知識庫，系統會執行解析、分塊與向量化。
3. **Orchestrator (任務編排)**: Monitor AI agent tasks and decision nodes in real-time.
   - 實時監控 AI 任務執行與決策節點，觀察 AI 如何分解任務並調用工具。
4. **Chat (智能問答)**: Query the system using indexed knowledge for precise answers.
   - 基於已索引的內容進行問答，AI 會提供具備可追蹤性的回答。
