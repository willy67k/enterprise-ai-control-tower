import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { ragQuery } from "../../api/documents";
import { useSettings } from "../../context/SettingsContext";
import type { LLMProvider, RagQueryResponse } from "../../types/api";

const PROVIDERS: LLMProvider[] = ["openai", "gemini", "anthropic"];

export const RagPanel: React.FC = () => {
  const { settings } = useSettings();
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [provider, setProvider] = useState<LLMProvider>(settings.defaultProvider);
  const [model, setModel] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RagQueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = question.trim();
    if (!q || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await ragQuery({
        question: q,
        top_k: topK,
        provider,
        model: model.trim() || undefined,
      });
      setResult(resp);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "RAG query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-700">Question</label>
          <textarea
            rows={3}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your uploaded documents…"
            className="w-full resize-none rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
          />
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <label className="text-xs font-medium text-gray-600">Top-K:</label>
            <input type="number" min={1} max={20} value={topK} onChange={(e) => setTopK(Number(e.target.value))} className="w-16 rounded-lg border border-gray-300 px-2 py-1.5 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none" />
          </div>
          <select value={provider} onChange={(e) => setProvider(e.target.value as LLMProvider)} className="rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none">
            {PROVIDERS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <input
            type="text"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            placeholder="model (optional)"
            className="w-36 rounded-lg border border-gray-300 px-2 py-1.5 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
          />
          <button type="submit" disabled={!question.trim() || loading} className="ml-auto rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 disabled:opacity-40">
            {loading ? "Searching…" : "Ask"}
          </button>
        </div>
      </form>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">{error}</div>}

      {/* Result */}
      {result && (
        <div className="space-y-4">
          <div className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-gray-200">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-700">Answer</h3>
              <span className="text-xs text-gray-400">
                {result.provider} · {result.model}
              </span>
            </div>
            <div className="prose prose-sm prose-p:my-1 max-w-none">
              <ReactMarkdown>{result.reply}</ReactMarkdown>
            </div>
          </div>

          {result.sources.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-semibold text-gray-700">Sources ({result.sources.length})</h3>
              <div className="space-y-2">
                {result.sources.map((src, i) => (
                  <div key={i} className="rounded-lg bg-gray-50 px-4 py-3 ring-1 ring-gray-200">
                    <p className="mb-1 text-xs font-medium text-gray-500">
                      Doc {src.document_id.slice(0, 8)}… · chunk #{src.chunk_index}
                    </p>
                    <p className="line-clamp-3 text-sm text-gray-700">{src.preview}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
