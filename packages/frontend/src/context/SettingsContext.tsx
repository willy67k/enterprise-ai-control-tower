import React, { createContext, useCallback, useContext, useState } from "react";
import type { LLMProvider } from "../types/api";

const STORAGE_KEY = "aict_settings";

export interface AppSettings {
  backendUrl: string;
  apiToken: string;
  devUserEmail: string;
  defaultProvider: LLMProvider;
}

const DEFAULT_SETTINGS: AppSettings = {
  backendUrl: import.meta.env.VITE_BACKEND_URL ?? "http://localhost:7801",
  apiToken: "",
  devUserEmail: "",
  defaultProvider: "openai",
};

function loadSettings(): AppSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) };
  } catch {
    /* ignore */
  }
  return { ...DEFAULT_SETTINGS };
}

interface SettingsContextValue {
  settings: AppSettings;
  saveSettings: (_next: AppSettings) => void;
}

const SettingsContext = createContext<SettingsContextValue>({
  settings: DEFAULT_SETTINGS,
  saveSettings: () => {},
});

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<AppSettings>(loadSettings);

  const saveSettings = useCallback((next: AppSettings) => {
    setSettings(next);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      /* ignore */
    }
  }, []);

  return <SettingsContext.Provider value={{ settings, saveSettings }}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  return useContext(SettingsContext);
}
