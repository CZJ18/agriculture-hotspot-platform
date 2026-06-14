# Security

Custom URL fetching is designed to avoid open-proxy and SSRF abuse.

Implemented controls:

- Only `http` and `https`.
- Blocks `file`, `ftp`, `gopher`, localhost, loopback, private, link-local, reserved, unspecified, multicast, and metadata IP targets.
- DNS resolution is checked before outbound fetching.
- Redirects are limited and every redirected target is revalidated.
- Response size defaults to 2 MB.
- Request timeout defaults to 10 seconds.
- Binary, archive, executable, audio, and video extensions are blocked.
- Accepted content types are `text/html`, `application/xhtml+xml`, and `text/plain`.
- In-memory per-client rate limiting is applied to custom URL endpoints.
- Optional platform cookies are read from environment variables only; do not commit `.env` or store account passwords.
- Optional video downloads are limited to public direct video file URLs and capped by `VIDEO_MAX_DOWNLOAD_BYTES`; platform stream extraction, DRM bypass, CAPTCHA bypass, and paywall bypass are not implemented by default.
- `yt-dlp` integration is disabled by default. When enabled, it is constrained by `VIDEO_YTDLP_ALLOWED_DOMAINS`, `VIDEO_MAX_DOWNLOAD_BYTES`, and the backend download directory.

Production notes:

- Put FastAPI and MCP behind Nginx.
- Use HTTPS.
- Change `MCP_BEARER_TOKEN`.
- Prefer Redis or gateway-level rate limiting in multi-worker deployments.
- Use low-frequency scheduled crawling for authenticated accounts to reduce lockout and compliance risk.
