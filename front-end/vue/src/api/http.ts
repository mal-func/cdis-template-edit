import axios, { type InternalAxiosRequestConfig } from "axios";
import { appConfig } from "@/config/env";

export class ApiError extends Error {
  constructor(message: string, readonly code: string, readonly statusCode?: number) {
    super(message);
    this.name = "ApiError";
  }
}

const http = axios.create({
  baseURL: appConfig.apiBaseUrl,
  timeout: appConfig.apiTimeout,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

const CSRF_COOKIE = "csrf_token";
const CSRF_HEADER = "x-csrf-token";
export const SESSION_EXPIRED_EVENT = "auth:session-expired";
const mutatingMethods = new Set(["post", "put", "patch", "delete"]);

function readCookie(name: string): string | undefined {
  const prefix = name + "=";
  return document.cookie.split(";").map((part) => part.trim()).find((part) => part.startsWith(prefix))?.slice(prefix.length);
}
function csrfHeaders(): Record<string, string> {
  const token = readCookie(CSRF_COOKIE);
  return token ? { [CSRF_HEADER]: decodeURIComponent(token) } : {};
}

let refreshPromise: Promise<void> | null = null;
function refreshSession(): Promise<void> {
  refreshPromise ??= http.post("/auth/refresh", undefined, { headers: csrfHeaders() })
    .then(() => undefined)
    .finally(() => { refreshPromise = null; });
  return refreshPromise;
}

http.interceptors.request.use((config) => {
  if (config.method && mutatingMethods.has(config.method.toLowerCase())) {
    const token = readCookie(CSRF_COOKIE);
    if (token) config.headers.set(CSRF_HEADER, decodeURIComponent(token));
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (!axios.isAxiosError(error) || !error.config) {
      return Promise.reject(new ApiError("Network request failed.", "NETWORK_ERROR"));
    }
    const config = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    const url = config.url ?? "";
    const bootstrap = ["/auth/login", "/auth/register", "/auth/refresh"].some((path) => url.includes(path));
    if (error.response?.status === 401 && !config._retry && !bootstrap) {
      config._retry = true;
      try {
        await refreshSession();
        return http(config);
      } catch {
        window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT));
      }
    }
    const body = error.response?.data as { success?: boolean; error?: { message?: string; code?: string } } | undefined;
    return Promise.reject(new ApiError(
      body?.error?.message ?? error.message ?? "Something went wrong. Please try again.",
      body?.error?.code ?? "API_ERROR",
      error.response?.status,
    ));
  },
);

type QueryParams = Record<string, string | number | boolean | undefined>;
export const api = {
  async get<T>(url: string, params?: QueryParams): Promise<T> {
    const response = await http.get<{ data: T }>(url, { params });
    return response.data.data;
  },
  async post<T>(url: string, data?: unknown): Promise<T> {
    const response = await http.post<{ data: T }>(url, data);
    return response.data.data;
  },
  async put<T>(url: string, data?: unknown): Promise<T> {
    const response = await http.put<{ data: T }>(url, data);
    return response.data.data;
  },
  async patch<T>(url: string, data?: unknown): Promise<T> {
    const response = await http.patch<{ data: T }>(url, data);
    return response.data.data;
  },
  async delete<T>(url: string): Promise<T> {
    const response = await http.delete<{ data: T }>(url);
    return response.data.data;
  },
};