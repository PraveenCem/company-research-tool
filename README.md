# Company Research Tool

A full-stack company research application that searches the web and generates a structured, source-backed company briefing.

The application allows users to research a company, view information across multiple sections, save research reports, view previous reports, and delete reports.

## Features

- 🔎 Company research using web search
- ⚡ Parallel research across multiple categories
- 📊 Company overview
- 👥 Key leadership / executives
- 📰 Latest news
- 💰 Financial highlights
- ⚠️ Risk factors
- 🔗 Source links for researched information
- 📡 Streaming research progress using Server-Sent Events (SSE)
- 💾 Save completed research reports
- 📚 Research history
- 👁️ View previously saved reports
- 🗑️ Delete saved reports
- ✅ Input validation
- 🌐 React frontend with FastAPI backend
- 🗄️ SQLite database for report storage

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn
- Tavily Search API
- SSE / StreamingResponse

### Frontend

- React
- TypeScript
- Vite
- CSS

---

## Project Structure

```text
company-research-tool/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── requirements.txt
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   ├── research_agent.py
│   │   └── search_service.py
│   │
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── api.ts
│   │   ├── types.ts
│   │   └── ...
│   │
│   ├── package.json
│   └── ...
│
├── .gitignore
└── README.md
