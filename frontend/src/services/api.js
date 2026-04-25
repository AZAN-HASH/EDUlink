import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

const api = axios.create({
  baseURL: API_BASE_URL
});

api.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem("edulink_access_token");
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const refreshToken = localStorage.getItem("edulink_refresh_token");
    if (error.response?.status === 401 && refreshToken && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshResponse = await axios.post(
          `${API_BASE_URL}/refresh`,
          {},
          { headers: { Authorization: `Bearer ${refreshToken}` } }
        );
        const nextAccessToken = refreshResponse.data?.data?.access_token;
        if (nextAccessToken) {
          localStorage.setItem("edulink_access_token", nextAccessToken);
          originalRequest.headers.Authorization = `Bearer ${nextAccessToken}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem("edulink_access_token");
        localStorage.removeItem("edulink_refresh_token");
        localStorage.removeItem("edulink_user");
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
