import { apiClient } from "./client";

export interface Hotspot {
  id: number;
  platform: string;
  rank?: number;
  title: string;
  url: string;
  heat?: string;
  category?: string;
  author?: string;
  summary?: string;
  sentiment?: string;
  keywords: string[];
  captured_at?: string;
}

export type HotspotPlatform =
  | "github_trending"
  | "hacker_news"
  | "news_rss"
  | "bilibili"
  | "zhihu"
  | "weibo"
  | "douyin"
  | "wechat_channels"
  | "youtube";

export function fetchHotspots(params?: { platform?: HotspotPlatform; limit?: number }) {
  return apiClient.get<Hotspot[]>("/hotspots", { params });
}

export function fetchPlatforms() {
  return apiClient.get<HotspotPlatform[]>("/hotspots/platforms");
}
