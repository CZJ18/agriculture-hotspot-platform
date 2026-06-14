import { apiClient } from "./client";

export interface CrawlerAuthRequired {
  status: "auth_required";
  platform: string;
  login_url: string;
  cookie_env: string;
  message: string;
}

export function runStableCrawlers() {
  return apiClient.post("/crawler/run");
}

export function runPlatformCrawler(platform: string) {
  return apiClient.post(`/crawler/run/${platform}`);
}

export function isCrawlerAuthRequired(error: unknown): error is { response: { status: 428; data: { detail: CrawlerAuthRequired } } } {
  const maybe = error as { response?: { status?: number; data?: { detail?: { status?: string } } } };
  return maybe.response?.status === 428 && maybe.response.data?.detail?.status === "auth_required";
}
