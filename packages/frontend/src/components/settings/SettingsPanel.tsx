import React, { useState } from "react";
import { useSettings, type AppSettings } from "../../context/SettingsContext";
import type { LLMProvider } from "../../types/api";

const PROVIDERS: { value: LLMProvider; label: string }[] = [
  { value: "openai", label: "OpenAI" },
  { value: "gemini", label: "Google Gemini" },
  { value: "anthropic", label: "Anthropic Claude" },
];

export const SettingsPanel: React.FC = () => {
  const { settings, saveSettings } = useSettings();
  const [form, setForm] = useState<AppSettings>({ ...settings });
  const [saved, setSaved] = useState(false);

  function handleChange(e: React.ChangeEvent) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setSaved(false);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    saveSettings(form);
    setSaved(true);
  }

  return (
    <div className="flex h-full flex-col overflow-y-auto">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white px-8 py-5">
        <h1 className="text-xl font-semibold text-gray-900">Settings</h1>
        <p className="mt-0.5 text-sm text-gray-500">Configure backend connection and authentication.</p>
      </div>

      <div className="flex-1 px-8 py-8">
        <form onSubmit={handleSubmit} className="max-w-lg space-y-6">
          {/* Backend URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Backend URL</label>
            <input
              type="url"
              name="backendUrl"
              value={form.backendUrl}
              onChange={handleChange}
              placeholder="http://localhost:7801"
              className="mt-1.5 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
            />
          </div>

          {/* API Token */}
          <div>
            <label className="block text-sm font-medium text-gray-700">API Token</label>
            <input
              type="password"
              name="apiToken"
              value={form.apiToken}
              onChange={handleChange}
              placeholder="Bearer token (DEV_API_TOKEN)"
              autoComplete="off"
              className="mt-1.5 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
            />
            <p className="mt-1 text-xs text-gray-400">
              Sent as <code className="rounded bg-gray-100 px-1">Authorization: Bearer …</code>
            </p>
          </div>

          {/* Dev User Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Dev User Email <span className="font-normal text-gray-400">(optional)</span>
            </label>
            <input
              type="email"
              name="devUserEmail"
              value={form.devUserEmail}
              onChange={handleChange}
              placeholder="user@example.com"
              className="mt-1.5 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
            />
            <p className="mt-1 text-xs text-gray-400">
              Sent as <code className="rounded bg-gray-100 px-1">X-Dev-User-Email</code> header to select acting user.
            </p>
          </div>

          {/* Default Provider */}
          <div>
            <label className="block text-sm font-medium text-gray-700">Default LLM Provider</label>
            <select
              name="defaultProvider"
              value={form.defaultProvider}
              onChange={handleChange}
              className="mt-1.5 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
            >
              {PROVIDERS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>

          {/* Submit */}
          <div className="flex items-center gap-3 pt-2">
            <button type="submit" className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:outline-none">
              Save Settings
            </button>
            {saved && <span className="text-sm font-medium text-green-600">Saved!</span>}
          </div>
        </form>
      </div>
    </div>
  );
};
