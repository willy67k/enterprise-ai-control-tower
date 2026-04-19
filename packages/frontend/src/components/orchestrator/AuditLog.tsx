import React, { useState } from "react";

interface AuditLogProps {
  entries: string[];
}

export const AuditLog: React.FC = ({ entries }) => {
  const [open, setOpen] = useState(false);

  if (!entries.length) return null;

  return (
    <div className="overflow-hidden rounded-xl bg-white ring-1 ring-gray-200">
      <button onClick={() => setOpen((v) => !v)} className="flex w-full items-center justify-between px-5 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50">
        <span className="flex items-center gap-2">
          <svg className="h-4 w-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
          Audit Log
          <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">{entries.length}</span>
        </span>
        <svg className={`h-4 w-4 text-gray-400 transition-transform ${open ? "rotate-180" : ""}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>
      {open && (
        <div className="border-t border-gray-100 px-5 py-3">
          <ol className="space-y-1.5">
            {entries.map((entry, i) => (
              <li key={i} className="flex gap-3 text-sm">
                <span className="mt-0.5 w-5 shrink-0 text-right font-mono text-xs text-gray-400">{i + 1}</span>
                <span className="text-gray-700">{entry}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
};
