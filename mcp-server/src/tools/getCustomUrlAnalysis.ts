import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { FastapiClient } from "../client/fastapiClient.js";

export function registerGetCustomUrlAnalysis(server: McpServer, client: FastapiClient) {
  server.registerTool(
    "get_custom_url_analysis",
    {
      description: "Analyze one public URL through the FastAPI custom URL pipeline.",
      inputSchema: { url: z.string().url() },
    },
    async ({ url }) => ({
      content: [{ type: "text", text: JSON.stringify(await client.post("/api/custom-url/analyze", { url }), null, 2) }],
    }),
  );
}
