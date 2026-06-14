import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { FastapiClient } from "../client/fastapiClient.js";

export function registerAnalyzeDailyTrends(server: McpServer, client: FastapiClient) {
  server.registerTool(
    "analyze_daily_trends",
    {
      description: "Run or fetch daily AI trend analysis.",
      inputSchema: { date: z.string().optional() },
    },
    async ({ date }) => ({
      content: [{ type: "text", text: JSON.stringify(await client.post("/api/analysis/daily", { date }), null, 2) }],
    }),
  );
}
