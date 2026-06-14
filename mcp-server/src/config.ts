export const config = {
  port: Number(process.env.PORT ?? 3001),
  fastapiBaseUrl: process.env.FASTAPI_BASE_URL ?? "http://localhost:8000",
  bearerToken: process.env.MCP_BEARER_TOKEN ?? "change-me",
  allowedOrigins: (process.env.ALLOWED_ORIGINS ?? "http://localhost:5173")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean),
};
