import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { FastapiClient } from "../client/fastapiClient.js";

export function registerGetTodayHotspots(server: McpServer, client: FastapiClient) {
  server.registerTool(
    "get_today_hotspots",
    {
      description: "Get latest captured hotspot items.",
      inputSchema: { limit: z.number().int().min(1).max(100).default(30) },
    },
    async ({ limit }) => ({
      content: [{ type: "text", text: JSON.stringify(await client.get("/api/hotspots", { limit }), null, 2) }],
    }),
  );
}
