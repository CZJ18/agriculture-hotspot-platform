import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { FastapiClient } from "../client/fastapiClient.js";

export function registerGetPlatformHotspots(server: McpServer, client: FastapiClient) {
  server.registerTool(
    "get_platform_hotspots",
    {
      description: "Get hotspot items for a platform.",
      inputSchema: {
        platform: z.enum([
          "github_trending",
          "hacker_news",
          "news_rss",
          "bilibili",
          "zhihu",
          "weibo",
          "douyin",
          "wechat_channels",
          "youtube",
        ]),
        limit: z.number().int().min(1).max(100).default(30),
      },
    },
    async ({ platform, limit }) => ({
      content: [{ type: "text", text: JSON.stringify(await client.get("/api/hotspots", { platform, limit }), null, 2) }],
    }),
  );
}
