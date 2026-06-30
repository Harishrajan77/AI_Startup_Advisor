# AI Startup Advisor 🚀

AI Startup Advisor is an Agentic AI application designed to validate and pressure-test startup ideas before investing time and capital. Using a stateful multi-agent system built on **LangGraph**, it coordinates 6 specialized LLM nodes to perform real-time competitor research, compute RAG-driven bottom-up market sizing, build risk audit templates, compile technology architecture blueprints, and synthesize executive-ready venture reports.

---

## 🌟 Key Features

* **Multi-Agent Orchestration**: Built with **LangGraph**, facilitating stateful transitions and automated data flow across 6 specialized LLM agents (Planner, Competitor Researcher, Market Analyst, Risk Auditor, Technology Advisor, Report Generator).
* **Centralized Groq Orchestration**: Powered by **Groq** (utilizing `llama-3.3-70b-versatile` by default) via a unified LLM factory for lightning-fast text generation and agent logic.
* **Offline RAG & Local Embeddings**: Runs **100% locally** using Sentence-Transformers (`all-MiniLM-L6-v2`) via `HuggingFaceEmbeddings` to generate vector representations, eliminating external API keys for index lookup and data queries.
* **Premium Glassmorphic Dashboard**: Real-time progress visualizers, live agent audit trail terminals, history sidebar panels, and interactive tabbed reports.
* **Smarter UI Sizing & Calculations**: Formats TAM/SAM/SOM metrics automatically into clean currency displays (e.g. `$65,000,000`), and recursively parses structured segment calculation objects into hierarchical cards.
* **Venture Report Downloads**: Trigger immediate local downloads of full reports as raw `.md` files styled with custom colors.
* **Fail-Safe Web Search**: Searches real-time competitor data via Tavily API with automatic LLM parametric memory fallback.
* **Robust Database Integration**: Automatically builds tables and registers records inside SQLite (default, local dev) or PostgreSQL.

---

## 🛠️ Multi-Agent Architecture

```
                 [User Idea Input]
                        │
                        ▼
             ┌─────────────────────┐
             │    Planner Agent    │
             └─────────────────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │Competitor Researcher│ <─── (Tavily Search / LLM Fallback)
             └─────────────────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │   Market Analyst    │ <─── (Bottom-up calculation & RAG Context)
             └─────────────────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │    Risk Auditor     │ <─── (SWOT & Risk Mitigation Matrix)
             └─────────────────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │ Technology Advisor  │ <─── (CTO Stack & Cost Budgeting)
             └─────────────────────┘
                        │
                        ▼
             ┌─────────────────────┐
             │  Report Generator   │
             └─────────────────────┘
                        │
                        ▼
            [Interactive Dashboard] ───> (Download MD Report)
```

1. **Planner Agent**: Analyzes the idea and defines the specific validation roadmap.
2. **Competitor Researcher**: Discovers market alternatives and compiles strength/weakness logs.
3. **Market Analyst**: Computes bottom-up TAM/SAM/SOM metrics using pricing and scaling variables.
4. **Risk Auditor**: Maps vulnerabilities into an interactive SWOT grid and mitigation matrix.
5. **Technology Advisor**: Recommends software stacks, drafts MoSCoW MVP feature scopes, and estimates monthly cloud hosting spend.
6. **Report Generator**: Combines all structured states into a cohesive Markdown document.

---

## 💻 Tech Stack

* **Backend**: FastAPI, LangGraph, LangChain, FAISS (Vector Store), SQLAlchemy, sentence-transformers, Groq.
* **Frontend**: React (Vite), TypeScript, Lucide Icons, Vanilla CSS (Custom Glassmorphism Variables).
* **Containerization**: Docker Compose.

---

## 🚀 Environment Configuration

Configure your API keys in the `.env` file located in the root directory (or `backend/.env`).

```env
# LLM Provider Configuration ("groq")
MODEL_PROVIDER=groq

# Groq Configuration (Required)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Tavily Web Search API Key (Optional, fallbacks to LLM parametric search)
TAVILY_API_KEY=your_tavily_api_key_here

# (Optional) Application Naming Configurations
PROJECT_NAME="AI Startup Advisor"
VITE_APP_NAME="AI Startup Advisor"
VITE_APP_SUBTITLE="validation engine"
```

---

## 🐳 Quick Start (Using Docker Compose)

1. **Clone the repository and enter the folder**:
   ```bash
   cd AI_Startup_Advisor
   ```

2. **Setup your `.env`**:
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```

3. **Start the application containers**:
   ```bash
   docker-compose up --build
   ```

4. **Access the services**:
   * **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
   * **FastAPI Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💻 Local Development (Without Docker)

### Backend Setup
1. **Enter backend directory and create a virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   ```
2. **Activate the virtual environment**:
   * **Windows (PowerShell)**: `.\venv\Scripts\Activate.ps1`
   * **macOS/Linux**: `source venv/bin/activate`
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` in the `backend/` directory** and populate your keys.
5. **Run the FastAPI app**:
   ```bash
   python -m app.main
   ```
   *(The server will boot, sync the local SQLite database `startup_advisor.db`, construct/verify the FAISS vector index using local sentence embeddings, and serve on port `8000`)*

### Frontend Setup
1. **Enter frontend directory and install dependencies**:
   ```bash
   cd frontend
   npm install
   ```
2. **Launch the development server**:
   ```bash
   npm run dev
   ```
3. **Open [http://localhost:5173](http://localhost:5173)** in your browser.

---

## 🧪 Running Tests

To run the automated backend test suite (covering database schemas, RAG indexing, and LangGraph workflow transitions):
1. Activate virtual environment in `backend/`
2. Run pytest:
   ```bash
   python -m pytest
   ```

---

## 💡 Troubleshooting & Windows Notes

* **Windows OpenMP DLL Conflict**: If Python crashes or aborts during FAISS import on Windows due to duplicate DLL initialization (such as conflicts between Intel OpenMP runtimes), the backend automatically sets `os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"` at boot to prevent crashes.
* **Vector Store Dimension Mismatch**: If you change configuration settings or switch embedding dimensions, the FAISS loader will automatically catch the dimension mismatch, delete the old index files, and build a fresh vector database from the knowledge base markdown files at startup.
