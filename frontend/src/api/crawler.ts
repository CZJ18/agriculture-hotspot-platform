import { apiClient } from "./client";

export interface CrawlerAuthRequired {
  status: "auth_required";
  platform: string;
  login_url: string;
  cookie_env: string;
  message: string;
  request?: CrawlerRequest;
}

export interface CrawlerRequest {
  platform: string;
  includeHotspots?: boolean;
  limit?: number;
}

export interface CrawlerRequestResult {
  id: number;
  requestId: number;
  status: "accepted" | "pending" | "running" | "completed" | "auth_required" | "error";
  platform: string;
  saved?: number;
  result?: Record<string, unknown>;
  errorMessage?: string | null;
  loginUrl?: string | null;
  cookieEnv?: string | null;
  hotspots: Array<Record<string, unknown>>;
  createdAt?: string;
  updatedAt?: string;
  finishedAt?: string | null;
}

export function runStableCrawlers() {
  return apiClient.post("/crawler/run");
}

export function runPlatformCrawler(platform: string) {
  return apiClient.post(`/crawler/run/${platform}`);
}

export function requestCrawler(payload: CrawlerRequest) {
  return apiClient.post<CrawlerRequestResult>("/crawler/request", payload);
}

export function listCrawlerRequests(limit = 50) {
  return apiClient.get<CrawlerRequestResult[]>("/crawler/requests", { params: { limit } });
}

export function getCrawlerRequest(requestId: number) {
  return apiClient.get<CrawlerRequestResult>(`/crawler/requests/${requestId}`);
}

export function isCrawlerAuthRequired(error: unknown): error is { response: { status: 428; data: { detail: CrawlerAuthRequired } } } {
  const maybe = error as { response?: { status?: number; data?: { detail?: { status?: string } } } };
  return maybe.response?.status === 428 && maybe.response.data?.detail?.status === "auth_required";
}
