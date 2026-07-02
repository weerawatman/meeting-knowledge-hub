# Meeting Knowledge Hub

On-premise AI meeting intelligence pipeline.

## SAT Secretary BOT track

The Microsoft Teams live AI meeting module is now documented and scaffolded around
`SAT Secretary BOT`, a visible Teams participant that is policy-gated before it can
start captions, transcript capture, and preview workflows.

Key planning documents:

- `docs/PRD_Teams_Meeting_AI.md`
- `docs/Architecture_Teams_Live_AI.md`
- `docs/TASKS_Teams_Meeting_AI.md`

Initial implementation surfaces:

- Node API: `/api/teams-ai/*`
- AI Worker live scaffold: `/worker/live/*`
- Web UI: `/live`

## Setup

### Docker

Run the full local overview stack:

```bash
docker compose up --build -d
```

Open:

- Web: http://localhost:5173
- API health: http://localhost:3001/health

Demo login:

- `admin@company.com`
- `admin123`

The default worker image is lightweight for project scaffolding. To build the
worker with demo AI dependencies such as faster-whisper and sentence-transformers:

```bash
docker compose build --build-arg INSTALL_EXTRAS=demo worker
```

### Local Python

1. Create a virtual environment using Python 3.11+
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Run API:
   ```bash
   uvicorn meeting_knowledge_hub.api.app:app --reload
   ```
