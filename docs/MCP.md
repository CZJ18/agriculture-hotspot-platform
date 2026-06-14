# MCP

The MCP server exposes Streamable HTTP at `/mcp` and calls the FastAPI backend internally.

Tools:

- `get_today_hotspots`
- `search_hotspots`
- `get_platform_hotspots`
- `analyze_daily_trends`
- `compare_platforms`
- `export_hotspots_excel`
- `get_custom_url_analysis`
- `search_custom_url_results`
- `parse_video_url`
- `download_video_url`
- `get_video_task`

Security:

- Bearer Token required.
- Origin must match `ALLOWED_ORIGINS`.
- MCP is an AI Agent extension surface, not a replacement for FastAPI.
- Video download tools delegate to FastAPI and inherit backend safety limits.
