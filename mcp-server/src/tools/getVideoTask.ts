import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { FastapiClient } from "../client/fastapiClient.js";

export function registerGetVideoTask(server: McpServer, client: FastapiClient) {
  server.registerTool(
    "get_video_task",
    {
      description: "Get a video parse/download task by id.",
      inputSchema: { taskId: z.number().int().positive() },
    },
    async ({ taskId }) => ({
      content: [{ type: "text", text: JSON.stringify(await client.get(`/api/video/tasks/${taskId}`), null, 2) }],
    }),
  );
}
