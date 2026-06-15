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

export interface ResourceCategory {
  id: number;
  name: string;
  parent: string | null;
  icon: string;
  order: number;
  status: "启用" | "停用" | string;
  description: string;
  updatedAt: string;
  children?: ResourceCategory[];
}

export interface ResourceTopic {
  id: number;
  title: string;
  description: string;
  count: number;
  accent?: "green" | "blue" | "cyan" | "amber" | "lime" | string;
}

export interface ResourceNotification {
  id: number;
  title: string;
  message: string;
  time: string;
  read: boolean;
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

export interface UpsertResourceCategoryInput {
  name: string;
  parent?: string | null;
  icon?: string;
  order?: number;
  status?: "启用" | "停用" | string;
  description?: string;
}

export interface CreateResourceTopicInput {
  title: string;
  description?: string;
  accent?: "green" | "blue" | "cyan" | "amber" | "lime" | string;
}

export interface CreateResourceNotificationInput {
  title: string;
  message?: string;
}

export interface TopicVideoAddResponse {
  topicId: number;
  videoId: number;
  added: boolean;
  video: ResourceVideo;
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

export function fetchResourceCategories() {
  return apiClient.get<ResourceCategory[]>("/resources/categories");
}

export function createResourceCategory(payload: UpsertResourceCategoryInput) {
  return apiClient.post<ResourceCategory>("/resources/categories", payload);
}

export function updateResourceCategory(categoryId: number, payload: Partial<UpsertResourceCategoryInput>) {
  return apiClient.put<ResourceCategory>(`/resources/categories/${categoryId}`, payload);
}

export function deleteResourceCategory(categoryId: number) {
  return apiClient.delete<{ deleted: boolean }>(`/resources/categories/${categoryId}`);
}

export function fetchResourceCategoryTree() {
  return apiClient.get<ResourceCategory[]>("/resources/categories/tree");
}

export function setResourceCategoryStatus(categoryId: number, status: "启用" | "停用" | string) {
  return apiClient.patch<ResourceCategory>(`/resources/categories/${categoryId}/status`, { status });
}

export function bulkImportResourceCategories(items: UpsertResourceCategoryInput[]) {
  return apiClient.post<{ created: number; items: ResourceCategory[] }>("/resources/categories/bulk-import", { items });
}

export function exportResourceCategories() {
  return apiClient.get<{ items: ResourceCategory[]; total: number }>("/resources/categories/export");
}

export function fetchResourceTopics() {
  return apiClient.get<ResourceTopic[]>("/resources/topics");
}

export function createResourceTopic(payload: CreateResourceTopicInput) {
  return apiClient.post<ResourceTopic>("/resources/topics", payload);
}

export function fetchResourceTopicVideos(topicId: number) {
  return apiClient.get<ResourceVideoList>(`/resources/topics/${topicId}/videos`);
}

export function addResourceVideoToTopic(topicId: number, videoId: number) {
  return apiClient.post<TopicVideoAddResponse>(`/resources/topics/${topicId}/videos`, { videoId });
}

export function removeResourceVideoFromTopic(topicId: number, videoId: number) {
  return apiClient.delete<{ topicId: number; videoId: number; removed: boolean }>(`/resources/topics/${topicId}/videos/${videoId}`);
}

export function fetchResourceNotifications() {
  return apiClient.get<ResourceNotification[]>("/resources/notifications");
}

export function createResourceNotification(payload: CreateResourceNotificationInput) {
  return apiClient.post<ResourceNotification>("/resources/notifications", payload);
}

export function markResourceNotificationRead(notificationId: number) {
  return apiClient.patch<ResourceNotification>(`/resources/notifications/${notificationId}/read`);
}

export function markAllResourceNotificationsRead() {
  return apiClient.post<{ updated: number }>("/resources/notifications/read-all");
}

export function resourceVideoPlayableUrl(video: ResourceVideo) {
  return video.downloadUrl ?? video.directVideoUrl ?? video.playUrl ?? video.sourceUrl;
}
