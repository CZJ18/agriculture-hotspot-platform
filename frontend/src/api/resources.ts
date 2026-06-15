import { apiClient } from "./client";

export interface ResourceVideoInfo {
  taskId: number;
  url: string;
  finalUrl?: string;
  platform?: string;
  title?: string;
  author?: string;
  description?: string;
  thumbnailUrl?: string;
  duration?: string;
  publishedAt?: string;
  viewCount?: string;
  directVideoUrl?: string;
  downloadRequested: boolean;
  downloadStatus: "not_requested" | "pending" | "completed" | "blocked" | "failed";
  downloadUrl?: string;
  storagePath?: string;
  status: "pending" | "fetching" | "completed" | "blocked" | "failed";
  errorMessage?: string;
}

export interface ResourceVideo {
  id: number;
  title: string;
  source: "Bilibili" | "YouTube" | "官网" | "高校公开课" | "项目组" | string;
  sourceUrl: string;
  finalUrl?: string;
  platform?: string;
  category: string;
  tags: string[];
  description: string;
  cover: string;
  thumbnailUrl?: string;
  duration: string;
  views: string | number;
  directVideoUrl?: string;
  downloadRequested: boolean;
  downloadStatus: "not_requested" | "pending" | "completed" | "blocked" | "failed";
  downloadUrl?: string;
  playUrl: string;
  videoTaskId?: number;
  videoInfo?: ResourceVideoInfo;
  favorite: boolean;
  createdAt: string;
  notes?: string;
}

export interface ResourceVideoList {
  items: ResourceVideo[];
  total: number;
}

export interface ResourceVideoQuery {
  keyword?: string;
  category?: string;
  source?: string;
  topicId?: number;
  favorite?: boolean;
  sort?: "latest" | "hot" | "favorite";
}

export interface CreateResourceVideoInput {
  videoTaskId?: number;
  title?: string;
  source?: string;
  sourceUrl?: string;
  category?: string;
  tags?: string[];
  description?: string;
  cover?: string;
  duration?: string;
  views?: string | number;
  favorite?: boolean;
  notes?: string;
}

export function fetchResourceVideos(params: ResourceVideoQuery = {}) {
  return apiClient.get<ResourceVideoList>("/resources/videos", { params });
}

export function createResourceVideo(payload: CreateResourceVideoInput) {
  return apiClient.post<ResourceVideo>("/resources/videos", payload);
}

export function updateResourceVideo(videoId: number, payload: Partial<CreateResourceVideoInput>) {
  return apiClient.put<ResourceVideo>(`/resources/videos/${videoId}`, payload);
}

export function deleteResourceVideo(videoId: number) {
  return apiClient.delete<{ deleted: boolean }>(`/resources/videos/${videoId}`);
}

export function setResourceVideoFavorite(videoId: number, favorite: boolean) {
  return apiClient.post<ResourceVideo>(`/resources/videos/${videoId}/favorite`, { favorite });
}

export function saveResourceVideoNotes(videoId: number, notes: string) {
  return apiClient.patch<ResourceVideo>(`/resources/videos/${videoId}/notes`, { notes });
}

export function resourceVideoPlayableUrl(video: ResourceVideo) {
  return video.downloadUrl ?? video.directVideoUrl ?? video.playUrl ?? video.sourceUrl;
}
