# MCP Server

Streamable HTTP MCP server for AI agents. It exposes `/mcp` and delegates business operations to the FastAPI backend.

## Run

```bash
npm install
copy .env.example .env
npm run dev
```

Requests to `/mcp` must include:

```http
Authorization: Bearer change-me
Origin: http://localhost:5173
```
