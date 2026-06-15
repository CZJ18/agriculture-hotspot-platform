import { apiClient } from "./client";

export interface VideoTask {
  id: number;
  url: string;
  final_url?: string;
  platform?: string;
  title?: string;
  author?: string;
  description?: string;
  thumbnail_url?: string;
  duration?: string;
  published_at?: string;
  view_count?: string;
  direct_video_url?: string;
  download_requested: boolean;
  download_status: "not_requested" | "pending" | "completed" | "blocked" | "failed";
  download_path?: string;
  download_url?: string;
  status: "pending" | "fetching" | "completed" | "blocked" | "failed";
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export function parseVideoUrl(url: string, download = false) {
  return apiClient.post<VideoTask>("/video/parse", { url, download });
}

export function fetchVideoTasks() {
  return apiClient.get<VideoTask[]>("/video/tasks");
}

export function fetchVideoTask(taskId: number) {
  return apiClient.get<VideoTask>(`/video/tasks/${taskId}`);
}

export function videoDownloadUrl(task: VideoTask) {
  if (!task.download_url) {
    return undefined;
  }
  const baseURL = apiClient.defaults.baseURL ?? "";
  return task.download_url.startsWith("http") ? task.download_url : `${baseURL}${task.download_url.replace(/^\/api/, "")}`;
}
