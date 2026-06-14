# Deployment

Recommended deployment:

- Ubuntu server.
- Nginx reverse proxy.
- FastAPI, database, crawlers, and AI jobs on the server.
- Frontend can be deployed with Nginx or Vercel after UI implementation.
- MCP server runs separately and forwards to FastAPI.

For a public API, see `docs/PUBLIC_API.md`.

FastAPI systemd command example:

```ini
ExecStart=/opt/hotspot-ai/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
WorkingDirectory=/opt/hotspot-ai/backend
```

MCP systemd command example:

```ini
ExecStart=/usr/bin/npm run dev
WorkingDirectory=/opt/hotspot-ai/mcp-server
```
