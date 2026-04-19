import React, { useState } from "react";
import { DocumentList } from "./DocumentList";
import { RagPanel } from "./RagPanel";
import { UploadZone } from "./UploadZone";

type DocTab = "upload" | "list" | "rag";

const TABS: { id: DocTab; label: string }[] = [
  { id: "upload", label: "Upload" },
  { id: "list", label: "My Documents" },
  { id: "rag", label: "RAG Query" },
];

export const DocumentsPanel: React.FC = () => {
  const [tab, setTab] = useState<DocTab>("upload");

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white px-8 pt-5">
        <h1 className="mb-4 text-xl font-semibold text-gray-900">Documents</h1>
        <div className="-mb-px flex gap-0">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`border-b-2 px-5 py-2.5 text-sm font-medium transition-colors ${tab === t.id ? "border-indigo-600 text-indigo-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-8 py-6">
        {tab === "upload" && <UploadZone />}
        {tab === "list" && <DocumentList />}
        {tab === "rag" && <RagPanel />}
      </div>
    </div>
  );
};
