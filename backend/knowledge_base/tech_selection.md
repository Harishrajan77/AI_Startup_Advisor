# Technology Stack Selection & MVP Scoping Guide

Selecting the right technology stack is a trade-off between speed-to-market, cost, developer availability, scalability, and technical constraints.

## 1. Golden Rules of MVP Tech Selection
1. **Optimize for Speed of Learning**: The goal of an MVP is to validate hypotheses, not build a perfect architecture. Choose technologies the team already knows or that have massive communities and pre-built libraries.
2. **Postpone Premature Scaling**: Do not design for 10 million concurrent users on Day 1. Design for 1,000 active users, but keep data models clean so you can refactor or scale later.
3. **Minimize Infrastructure Overhead**: Prefer managed services, serverless backends, and simple database architectures to minimize DevOps hours.

## 2. Standard Tech Archetypes

### Archetype A: Standard Web App (Fast & Dynamic)
- **Frontend**: React (Vite) or Next.js. Next.js is ideal for SEO-heavy landing pages or dynamic rendering; Vite is perfect for dashboard-heavy SaaS apps.
- **Backend**: FastAPI (Python), Express (Node.js), or Nest.js. Choose Python if the product involves AI, ML, or heavy data processing. Choose Node.js if the team has Javascript engineers.
- **Database**: PostgreSQL (relational, scalable, pgvector support) or MongoDB (document-based, fast schema iteration).
- **Hosting**: Vercel (frontend), Render/Railway (backend/DB), or AWS App Runner.

### Archetype B: Mobile-First App (iOS & Android)
- **Framework**: React Native (Expo) or Flutter. Expo is the fastest way to build, test, and ship cross-platform mobile apps using Javascript.
- **Backend**: FastAPI or Node.js.
- **Database**: PostgreSQL on Supabase (highly managed, real-time sync, auth pre-built).

### Archetype C: AI & LLM-Powered App (Agentic & RAG)
- **AI Orchestration**: LangChain, LangGraph, or LlamaIndex. LangGraph is preferred for stateful, cyclical agent behaviors.
- **Vector DB**: FAISS (in-memory/local file, excellent for MVP), Chroma (lightweight, easy setup), or pgvector on PostgreSQL (production standard).
- **Models**: OpenAI API (GPT-4o), Anthropic Claude, or Google Gemini. Google Gemini provides large context windows (2M tokens) at low costs.

## 3. MVP Scoping Framework
To define the MVP scope, categorise features into the **MoSCoW** framework:
- **Must Have**: Core value proposition. (e.g., For a fitness app: tracking workouts and generating AI advice).
- **Should Have**: Important features that can be manually bypassed in the beginning. (e.g., social sharing, calendar integration).
- **Could Have**: Nice-to-have features for future iterations. (e.g., Apple Watch integrations, custom avatar generation).
- **Won't Have (for now)**: Complex integrations, advanced enterprise security compliance, multi-region database replication.
