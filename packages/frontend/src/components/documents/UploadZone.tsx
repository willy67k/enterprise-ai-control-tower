import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { uploadDocument } from "../../api/documents";
import type { DocumentUploadResponse } from "../../types/api";

interface UploadResult {
  filename: string;
  response: DocumentUploadResponse;
  status: number;
}

export const UploadZone: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<UploadResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (accepted: File[]) => {
    if (!accepted.length) return;
    setUploading(true);
    setError(null);
    const newResults: UploadResult[] = [];

    for (const file of accepted) {
      try {
        const resp = await uploadDocument(file);
        newResults.push({ filename: file.name, response: resp, status: resp.deduplicated ? 200 : 202 });
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Upload failed";
        setError(`${file.name}: ${msg}`);
      }
    }

    setResults((prev) => [...newResults, ...prev]);
    setUploading(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "text/plain": [".txt"] },
    disabled: uploading,
  });

  function statusColor(s: "pending" | "ready" | "failed") {
    if (s === "ready") return "bg-green-100 text-green-700";
    if (s === "failed") return "bg-red-100 text-red-700";
    return "bg-yellow-100 text-yellow-700";
  }

  return (
    <div className="space-y-5">
      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-12 transition-colors ${
          isDragActive ? "border-indigo-500 bg-indigo-50" : "border-gray-300 bg-gray-50 hover:border-indigo-400 hover:bg-gray-100"
        } ${uploading ? "pointer-events-none opacity-60" : ""}`}
      >
        <input {...getInputProps()} />
        <svg className="mb-3 h-10 w-10 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
        {uploading ? (
          <p className="text-sm text-gray-500">Uploading…</p>
        ) : isDragActive ? (
          <p className="text-sm font-medium text-indigo-600">Drop files here</p>
        ) : (
          <>
            <p className="text-sm font-medium text-gray-700">Drag & drop files, or click to browse</p>
            <p className="mt-1 text-xs text-gray-400">Supports .txt and .pdf (max 10 MB)</p>
          </>
        )}
      </div>

      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">{error}</div>}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-2">
          {results.map((r, i) => (
            <div key={i} className="flex items-center gap-3 rounded-lg bg-white px-4 py-3 shadow-sm ring-1 ring-gray-200">
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-gray-800">{r.filename}</p>
                <p className="text-xs text-gray-400">
                  {r.response.title} · {r.response.source_type}
                  {r.response.deduplicated && " · deduplicated"}
                </p>
              </div>
              <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor(r.response.ingestion_status)}`}>{r.response.ingestion_status}</span>
              <span className="shrink-0 rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">{r.status === 200 ? "200 OK" : "202 Accepted"}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
