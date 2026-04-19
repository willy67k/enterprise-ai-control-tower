import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import type { TaskResult } from "../../types/api";

interface TaskResultsProps {
  tasks: TaskResult[];
}

function IntentBadge({ intent }: { intent: string }) {
  const colors: Record = {
    document: "bg-blue-100 text-blue-700",
    finance: "bg-emerald-100 text-emerald-700",
    general: "bg-gray-100 text-gray-600",
    unknown: "bg-gray-100 text-gray-400",
  };
  const cls = colors[intent?.toLowerCase()] ?? "bg-gray-100 text-gray-600";
  return <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${cls}`}>{intent || "—"}</span>;
}

function TaskCard({ task, index }: { task: TaskResult; index: number }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="overflow-hidden rounded-xl bg-white ring-1 ring-gray-200">
      <button onClick={() => setOpen((v) => !v)} className="flex w-full items-start justify-between gap-3 px-5 py-3 text-left hover:bg-gray-50">
        <div className="flex min-w-0 items-start gap-3">
          <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-700">{index + 1}</span>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-gray-800">{task.subquery}</p>
            <div className="mt-1">
              <IntentBadge intent={task.intent} />
            </div>
          </div>
        </div>
        <svg className={`mt-1 h-4 w-4 shrink-0 text-gray-400 transition-transform ${open ? "rotate-180" : ""}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {open && (
        <div className="space-y-4 border-t border-gray-100 px-5 py-4">
          {/* Answer */}
          <div>
            <p className="mb-2 text-xs font-semibold tracking-wide text-gray-400 uppercase">Answer</p>
            <div className="prose prose-sm prose-p:my-1 max-w-none">
              <ReactMarkdown>{task.answer}</ReactMarkdown>
            </div>
          </div>

          {/* Documents */}
          {task.documents && task.documents.length > 0 && (
            <div>
              <p className="mb-2 text-xs font-semibold tracking-wide text-gray-400 uppercase">Sources ({task.documents.length})</p>
              <div className="space-y-2">
                {task.documents.map((src, j) => (
                  <div key={j} className="rounded-lg bg-gray-50 px-4 py-2.5 ring-1 ring-gray-200">
                    <p className="mb-0.5 text-xs text-gray-400">
                      Doc {src.document_id.slice(0, 8)}… · chunk #{src.chunk_index}
                    </p>
                    <p className="line-clamp-2 text-sm text-gray-700">{src.preview}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export const TaskResults: React.FC = ({ tasks }) => {
  if (!tasks.length) return null;

  return (
    <div>
      <h3 className="mb-2 text-sm font-semibold text-gray-700">Sub-task Results ({tasks.length})</h3>
      <div className="space-y-2">
        {tasks.map((t, i) => (
          <TaskCard key={i} task={t} index={i} />
        ))}
      </div>
    </div>
  );
};
