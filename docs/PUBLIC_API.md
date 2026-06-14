# Public API

This backend can be opened on the local network or a server by binding FastAPI to `0.0.0.0`.

## Local Network

```bash
cd backend
python run_public_api.py
```

Default URL:

```text
http://<your-lan-ip>:8000
http://<your-lan-ip>:8000/docs
```

## Windows Firewall

Run PowerShell as Administrator:

```powershell
New-NetFirewallRule -DisplayName "Hotspot AI FastAPI 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Any
```

Check the rule:

```powershell
Get-NetFirewallRule -DisplayName "Hotspot AI FastAPI 8000"
```

## Optional API Key

Set these values in `backend/.env` before exposing the service:

```env
PUBLIC_API_HOST=0.0.0.0
PUBLIC_API_PORT=8000
PUBLIC_API_AUTH_ENABLED=true
PUBLIC_API_KEY=change-this-to-a-long-random-value
CORS_ORIGINS=http://localhost:5173,http://your-frontend-domain
```

Protected `/api/*` calls must include one of:

```http
X-API-Key: change-this-to-a-long-random-value
Authorization: Bearer change-this-to-a-long-random-value
```

`/health`, `/docs`, `/redoc`, and `/openapi.json` remain open for discovery and health checks.

## Internet Deployment

For public internet access, put the backend behind Nginx or a cloud reverse proxy with HTTPS. Do not expose video downloads, crawler endpoints, or custom URL fetching without an API key and rate limiting.
