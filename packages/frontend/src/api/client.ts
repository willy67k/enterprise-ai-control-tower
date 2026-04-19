import axios from "axios";
import type { AppSettings } from "../context/SettingsContext";

const STORAGE_KEY = "aict_settings";

function getSettings(): Pick {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as Partial;
      return {
        backendUrl: parsed.backendUrl ?? (import.meta.env.VITE_BACKEND_URL as string) ?? "http://localhost:7801",
        apiToken: parsed.apiToken ?? "",
        devUserEmail: parsed.devUserEmail ?? "",
      };
    }
  } catch {
    /* ignore */
  }
  return {
    backendUrl: (import.meta.env.VITE_BACKEND_URL as string) ?? "http://localhost:7801",
    apiToken: "",
    devUserEmail: "",
  };
}

export function createApiClient() {
  const { backendUrl, apiToken, devUserEmail } = getSettings();

  const headers: Record = {};
  if (apiToken) headers["Authorization"] = `Bearer ${apiToken}`;
  if (devUserEmail) headers["X-Dev-User-Email"] = devUserEmail;

  return axios.create({ baseURL: backendUrl, headers });
}
