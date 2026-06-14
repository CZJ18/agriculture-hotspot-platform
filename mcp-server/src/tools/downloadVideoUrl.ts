import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { FastapiClient } from "../client/fastapiClient.js";

export function registerDownloadVideoUrl(server: McpServer, client: FastapiClient) {
  server.registerTool(
    "download_video_url",
    {
      description:
        "Request an opt-in video download through FastAPI. The backend enforces enable flags, host allowlists, size limits, and no DRM/paywall/CAPTCHA bypass.",
      inputSchema: { url: z.string().url() },
    },
    async ({ url }) => ({
      content: [{ type: "text", text: JSON.stringify(await client.post("/api/video/parse", { url, download: true }), null, 2) }],
    }),
  );
}
