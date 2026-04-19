import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { runOrchestrator } from "../../api/orchestrator";
import { useSettings } from "../../context/SettingsContext";
import type { LLMProvider, OrchestratorResponse } from "../../types/api";
import { AuditLog } from "./AuditLog";
import { TaskResults } from "./TaskResults";

const PROVIDERS: LLMProvider[] = ["openai", "gemini", "anthropic"];

function IntentPill({ intent }: { intent: string }) {
  const colors: Record = {
    document: "bg-blue-100 text-blue-700",
    finance: "bg-emerald-100 text-emerald-700",
    general: "bg-gray-100 text-gray-600",
  };
  const cls = colors[intent?.toLowerCase()] ?? "bg-gray-100 text-gray-600";
  return <span className={`rounded-full px-3 py-1 text-sm font-medium ${cls}`}>{intent}</span>;
}

export const OrchestratorPanel: React.FC = () => {
  const { settings } = useSettings();
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [provider, setProvider] = useState<LLMProvider>(settings.defaultProvider);
  const [model, setModel] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OrchestratorResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await runOrchestrator({
        query: q,
        top_k: topK,
        provider,
        model: model.trim() || undefined,
      });
      setResult(resp);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Orchestrator request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white px-8 py-5">
        <h1 className="text-xl font-semibold text-gray-900">Multi-Agent Orchestrator</h1>
        <p className="mt-0.5 text-sm text-gray-500">RBAC → Decompose → Router → Agents → Aggregate</p>
      </div>

      {/* Body */}
      <div className="flex-1 space-y-6 overflow-y-auto px-8 py-6">
        {/* Query form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Query</label>
            <textarea
              rows={4}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything — the orchestrator will route to the right agents…"
              className="w-full resize-none rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none"
            />
          </div>

          {/* Controls row */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2">
              <label className="text-xs font-medium text-gray-600">Top-K:</label>
              <input
                type="number"
                min={1}
                max={20}
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-16 rounded-lg border border-gray-300 px-2 py-1.5 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
              />
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
            <button type="submit" disabled={!query.trim() || loading} className="ml-auto flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 disabled:opacity-40">
              {loading ? (
                <>
                  <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Running…
                </>
              ) : (
                <>
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                  Run
                </>
              )}
            </button>
          </div>
        </form>

        {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">{error}</div>}

        {/* Result */}
        {result && (
          <div className="space-y-5">
            {/* Meta row */}
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-sm text-gray-500">Intent:</span>
              <IntentPill intent={result.intent} />
              {result.sub_queries.length > 0 && (
                <span className="text-sm text-gray-500">
                  {result.sub_queries.length} sub-task
                  {result.sub_queries.length !== 1 ? "s" : ""}
                </span>
              )}
              {result.trace_id && <span className="ml-auto max-w-xs truncate font-mono text-xs text-gray-400">trace: {result.trace_id}</span>}
            </div>

            {/* Final response */}
            <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
              <h2 className="mb-3 text-sm font-semibold tracking-wide text-gray-500 uppercase">Final Response</h2>
              <div className="prose prose-sm prose-p:my-1.5 prose-headings:font-semibold max-w-none">
                <ReactMarkdown>{result.final_response}</ReactMarkdown>
              </div>
            </div>

            {/* Sub-queries chips */}
            {result.sub_queries.length > 0 && (
              <div>
                <p className="mb-2 text-sm font-medium text-gray-600">Decomposed queries</p>
                <div className="flex flex-wrap gap-2">
                  {result.sub_queries.map((q, i) => (
                    <span key={i} className="rounded-full bg-indigo-50 px-3 py-1 text-xs text-indigo-700 ring-1 ring-indigo-200">
                      {q}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Task results accordion */}
            <TaskResults tasks={result.task_results} />

            {/* RAG sources (top-level) */}
            {result.documents.length > 0 && (
              <div>
                <h3 className="mb-2 text-sm font-semibold text-gray-700">RAG Sources ({result.documents.length})</h3>
                <div className="space-y-2">
                  {result.documents.map((src, i) => (
                    <div key={i} className="rounded-lg bg-gray-50 px-4 py-3 ring-1 ring-gray-200">
                      <p className="mb-0.5 text-xs text-gray-400">
                        Doc {src.document_id.slice(0, 8)}… · chunk #{src.chunk_index}
                      </p>
                      <p className="line-clamp-3 text-sm text-gray-700">{src.preview}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Audit log */}
            <AuditLog entries={result.audit_log} />
          </div>
        )}
      </div>
    </div>
  );
};
