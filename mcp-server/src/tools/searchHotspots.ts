import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { FastapiClient } from "../client/fastapiClient.js";

export function registerSearchHotspots(server: McpServer, client: FastapiClient) {
  server.registerTool(
    "search_hotspots",
    {
      description: "Search latest hotspots by keyword on titles returned from FastAPI.",
      inputSchema: { keyword: z.string().min(1), limit: z.number().int().min(1).max(200).default(100) },
    },
    async ({ keyword, limit }) => {
      const rows = (await client.get("/api/hotspots", { limit })) as Array<{ title?: string }>;
      const matched = rows.filter((row) => row.title?.toLowerCase().includes(keyword.toLowerCase()));
      return { content: [{ type: "text", text: JSON.stringify(matched, null, 2) }] };
    },
  );
}
