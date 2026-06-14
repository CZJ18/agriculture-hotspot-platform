import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { FastapiClient } from "../client/fastapiClient.js";

export function registerExportHotspotsExcel(server: McpServer, client: FastapiClient) {
  server.registerTool(
    "export_hotspots_excel",
    {
      description: "Return the FastAPI URL for downloading hotspot Excel.",
      inputSchema: { platform: z.string().optional() },
    },
    async ({ platform }) => ({
      content: [{ type: "text", text: await client.exportUrl("/api/export/hotspots.xlsx", { platform }) }],
    }),
  );
}
