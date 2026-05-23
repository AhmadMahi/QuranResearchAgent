# Islamic Research Agent

An AI-powered research assistant built with **LangGraph**, **GPT-4o-mini**, **ChromaDB**, and **Next.js**.

## Architecture

```
Frontend (Next.js · Vercel)
        │
        │  SSE stream
        ▼
Backend (FastAPI · Railway / Render)
        │
        ▼
LangGraph Pipeline
  ┌─────────────────────────────────────────────────────┐
  │  1. Quran Research Agent   → api.alquran.cloud      │
  │  2. Weather & Prayer Agent → api.aladhan.com        │
  │                              OpenWeatherMap         │
  │  3. Web Search Agent       → DuckDuckGo (free)      │
  │  4. Knowledge Base Agent   → ChromaDB               │
  │                              (text-embedding-3-small)│
  │  5. Report Formatter Agent → GPT-4o-mini            │
  └─────────────────────────────────────────────────────┘
```

**Free APIs used (no key required)**
| API | Purpose |
|-----|---------|
| `api.alquran.cloud` | Quran verse search |
| `api.aladhan.com` | Islamic prayer times |
| DuckDuckGo Search | Web research |

**Optional API keys**
| API | Purpose |
|-----|---------|
| OpenWeatherMap | Live weather data |

---

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp ../.env.example ../.env
# Edit .env — add OPENAI_API_KEY at minimum

uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local

npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

DeepEval quality tests run automatically when `OPENAI_API_KEY` is set.

---

## Deployment

### Backend — Railway / Render (free tier)

1. Push `backend/` to a Git repo
2. Create a new service and set the start command:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Add env vars: `OPENAI_API_KEY`, optionally `LANGSMITH_API_KEY`, `OPENWEATHERMAP_API_KEY`

### Frontend — Vercel

1. Import the repo in Vercel
2. Set **Root Directory** to `frontend`
3. Add env var: `NEXT_PUBLIC_BACKEND_URL=https://your-backend-url`
4. Deploy

---

## LangSmith Tracing

Set in `.env`:
```
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_TRACING=true
LANGCHAIN_PROJECT=SimpleResearchAgent
```

All agent runs will appear at [smith.langchain.com](https://smith.langchain.com).

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | GPT-4o-mini + text-embedding-3-small |
| `LANGSMITH_API_KEY` | Optional | LangSmith tracing |
| `LANGSMITH_TRACING` | Optional | `true` to enable tracing |
| `OPENWEATHERMAP_API_KEY` | Optional | Live weather (free tier) |
| `NEXT_PUBLIC_BACKEND_URL` | Frontend | URL of the FastAPI backend |
# QuranResearchAgent
