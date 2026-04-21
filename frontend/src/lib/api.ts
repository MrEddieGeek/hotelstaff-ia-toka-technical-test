import axios, { type AxiosInstance } from 'axios';

import { useAuth } from '@/store/auth';

const baseURL = import.meta.env.VITE_BFF_URL ?? 'http://localhost:8080';

export const api: AxiosInstance = axios.create({ baseURL, timeout: 30_000 });

api.interceptors.request.use((config) => {
  const token = useAuth.getState().accessToken;
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error?.response?.status === 401) {
      useAuth.getState().clear();
    }
    return Promise.reject(error);
  },
);

export const extractApiError = (err: unknown): string => {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as { detail?: string; error?: string } | undefined;
    return data?.detail ?? data?.error ?? err.message;
  }
  return err instanceof Error ? err.message : 'Error desconocido';
};
