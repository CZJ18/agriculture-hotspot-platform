import { apiClient } from "./client";

export interface DailyAnalysis {
  id: number;
  date: string;
  summary?: string;
  keywords: string[];
  sentiment_overview?: string;
  trend_opinion?: string;
  platform_comparison?: string;
  content_suggestions?: string;
}

export function analyzeDaily(date?: string) {
  return apiClient.post<DailyAnalysis>("/analysis/daily", { date });
}

export function fetchLatestAnalysis() {
  return apiClient.get<DailyAnalysis>("/analysis/latest");
}
