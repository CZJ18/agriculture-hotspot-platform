import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { FastapiClient } from "../client/fastapiClient.js";

export function registerParseVideoUrl(server: McpServer, client: FastapiClient) {
  server.registerTool(
    "parse_video_url",
    {
      description: "Parse a video page URL and return metadata without downloading the video.",
      inputSchema: { url: z.string().url() },
    },
    async ({ url }) => ({
      content: [{ type: "text", text: JSON.stringify(await client.post("/api/video/parse", { url, download: false }), null, 2) }],
    }),
  );
}
