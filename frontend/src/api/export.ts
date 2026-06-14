import { apiClient } from "./client";

export function buildHotspotsExcelUrl(platform?: string) {
  const url = new URL("/api/export/hotspots.xlsx", apiClient.defaults.baseURL?.replace(/\/api\/?$/, "") ?? "http://localhost:8000");
  if (platform) url.searchParams.set("platform", platform);
  return url.toString();
}
