import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { FastapiClient } from "../client/fastapiClient.js";

export function registerComparePlatforms(server: McpServer, client: FastapiClient) {
  server.registerTool(
    "compare_platforms",
    {
      description: "Compare hotspot counts and top titles across platforms.",
      inputSchema: { limit: z.number().int().min(1).max(200).default(100) },
    },
    async ({ limit }) => {
      const rows = (await client.get("/api/hotspots", { limit })) as Array<{ platform: string; title: string }>;
      const grouped = rows.reduce<Record<string, string[]>>((acc, row) => {
        acc[row.platform] ??= [];
        acc[row.platform].push(row.title);
        return acc;
      }, {});
      return { content: [{ type: "text", text: JSON.stringify(grouped, null, 2) }] };
    },
  );
}
