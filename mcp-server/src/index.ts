import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { config } from "./config.js";
import { verifyBearerToken, verifyOrigin } from "./auth.js";
import { FastapiClient } from "./client/fastapiClient.js";
import { registerAnalyzeDailyTrends } from "./tools/analyzeDailyTrends.js";
import { registerComparePlatforms } from "./tools/comparePlatforms.js";
import { registerExportHotspotsExcel } from "./tools/exportHotspotsExcel.js";
import { registerGetCustomUrlAnalysis } from "./tools/getCustomUrlAnalysis.js";
import { registerGetPlatformHotspots } from "./tools/getPlatformHotspots.js";
import { registerGetTodayHotspots } from "./tools/getTodayHotspots.js";
import { registerGetVideoTask } from "./tools/getVideoTask.js";
import { registerDownloadVideoUrl } from "./tools/downloadVideoUrl.js";
import { registerParseVideoUrl } from "./tools/parseVideoUrl.js";
import { registerSearchCustomUrlResults } from "./tools/searchCustomUrlResults.js";
import { registerSearchHotspots } from "./tools/searchHotspots.js";

const server = new McpServer({ name: "hotspot-ai-system", version: "0.1.0" });
const client = new FastapiClient();

registerGetTodayHotspots(server, client);
registerSearchHotspots(server, client);
registerGetPlatformHotspots(server, client);
registerAnalyzeDailyTrends(server, client);
registerComparePlatforms(server, client);
registerExportHotspotsExcel(server, client);
registerGetCustomUrlAnalysis(server, client);
registerSearchCustomUrlResults(server, client);
registerParseVideoUrl(server, client);
registerDownloadVideoUrl(server, client);
registerGetVideoTask(server, client);

const app = express();
const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });

app.use(express.json({ limit: "1mb" }));
app.use("/mcp", verifyOrigin, verifyBearerToken);

app.all("/mcp", async (req, res) => {
  await transport.handleRequest(req, res, req.body);
});

app.get("/health", (_req, res) => res.json({ status: "ok" }));

await server.connect(transport);

app.listen(config.port, () => {
  console.log(`MCP server listening on http://localhost:${config.port}/mcp`);
});
