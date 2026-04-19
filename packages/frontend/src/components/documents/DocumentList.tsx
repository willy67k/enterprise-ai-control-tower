import React, { useCallback, useEffect, useState } from "react";
import { listDocuments } from "../../api/documents";
import type { DocumentListItem } from "../../types/api";

function statusBadge(s: "pending" | "ready" | "failed") {
  if (s === "ready") return "inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700";
  if (s === "failed") return "inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-700";
  return "inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-700";
}

export const DocumentList: React.FC = () => {
  const [docs, setDocs] = useState<DocumentListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await listDocuments();
      setDocs(resp.documents);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocs();
  }, [fetchDocs]);

  if (loading)
    return (
      <div className="flex items-center gap-2 py-4 text-sm text-gray-500">
        <svg className="h-4 w-4 animate-spin text-indigo-600" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
        Loading documents…
      </div>
    );

  if (error)
    return (
      <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">
        {error}
        <button onClick={fetchDocs} className="ml-2 underline hover:no-underline">
          Retry
        </button>
      </div>
    );

  if (!docs.length) return <div className="py-8 text-center text-sm text-gray-400">No documents yet. Upload some files first.</div>;

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm text-gray-500">{docs.length} document(s)</p>
        <button onClick={fetchDocs} className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-50">
          Refresh
        </button>
      </div>
      <div className="overflow-hidden rounded-xl ring-1 ring-gray-200">
        <table className="min-w-full divide-y divide-gray-200 bg-white">
          <thead className="bg-gray-50">
            <tr>
              {["Title", "Type", "Status", "Created"].map((h) => (
                <th key={h} className="px-4 py-3 text-left text-xs font-medium tracking-wide text-gray-500 uppercase">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {docs.map((doc) => (
              <tr key={doc.id} className="hover:bg-gray-50">
                <td className="max-w-xs truncate px-4 py-3 text-sm font-medium text-gray-800">{doc.title ?? "—"}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{doc.source_type ?? "—"}</td>
                <td className="px-4 py-3">
                  <span className={statusBadge(doc.ingestion_status)}>{doc.ingestion_status}</span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-400">{new Date(doc.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
