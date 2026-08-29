import axios from "axios";

// Set VITE_API_BASE_URL in a .env file (see .env.example) once the backend
// is deployed (Render/Railway/Fly.io - see root README.md for why Vercel
// alone can't host the backend). Falls back to local dev backend.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const getHealth = () => apiClient.get("/health").then((r) => r.data);
export const getCameras = () => apiClient.get("/cameras").then((r) => r.data);
export const getMockEvents = (cameraId) =>
  apiClient.get("/vehicles/events/mock", { params: { camera_id: cameraId } }).then((r) => r.data);
export const recommendNextAction = (payload) =>
  apiClient.post("/investigations/recommend", payload).then((r) => r.data);
export const fuseEvidence = (payload) =>
  apiClient.post("/evidence/fuse", payload).then((r) => r.data);
export const getVideos = () => apiClient.get("/videos").then((r) => r.data);
export const uploadVideo = (formData) => apiClient.post("/videos/upload", formData).then((r) => r.data);
export const reprocessVideo = (videoId) => apiClient.post(`/videos/${videoId}/process`).then((r) => r.data);
export const setTrainingDataset = (videoId, enabled) => apiClient.patch(`/videos/${videoId}/training-dataset`, null, { params: { enabled } }).then((r) => r.data);
