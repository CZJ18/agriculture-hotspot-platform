import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { FastapiClient } from "../client/fastapiClient.js";

export function registerSearchCustomUrlResults(server: McpServer, client: FastapiClient) {
  server.registerTool(
    "search_custom_url_results",
    {
      description: "Search stored custom URL task results by keyword.",
      inputSchema: { keyword: z.string().min(1) },
    },
    async ({ keyword }) => {
      const rows = (await client.get("/api/custom-url/tasks")) as Array<Record<string, string>>;
      const lowered = keyword.toLowerCase();
      const matched = rows.filter((row) => JSON.stringify(row).toLowerCase().includes(lowered));
      return { content: [{ type: "text", text: JSON.stringify(matched, null, 2) }] };
    },
  );
}
