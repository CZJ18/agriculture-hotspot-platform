import { apiClient } from "./client";

export interface CustomUrlTask {
  id: number;
  url: string;
  domain?: string;
  platform?: string;
  title?: string;
  description?: string;
  content_excerpt?: string;
  summary?: string;
  keywords: string[];
  sentiment?: string;
  category?: string;
  trend_opinion?: string;
  status: "pending" | "fetching" | "analyzing" | "completed" | "failed" | "blocked";
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface CustomUrlAnalyzeResponse {
  task_id: number;
  status: CustomUrlTask["status"];
  title?: string;
  platform?: string;
  summary?: string;
  keywords: string[];
  sentiment?: string;
  category?: string;
  trend_opinion?: string;
  source_url: string;
}

export function submitCustomUrl(url: string) {
  return apiClient.post<CustomUrlTask>("/custom-url/submit", { url });
}

export function fetchCustomUrlTasks() {
  return apiClient.get<CustomUrlTask[]>("/custom-url/tasks");
}

export function fetchCustomUrlTask(taskId: number) {
  return apiClient.get<CustomUrlTask>(`/custom-url/tasks/${taskId}`);
}

export function analyzeCustomUrl(url: string) {
  return apiClient.post<CustomUrlAnalyzeResponse>("/custom-url/analyze", { url });
}
