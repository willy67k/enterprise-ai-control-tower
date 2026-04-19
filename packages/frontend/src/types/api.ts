// ── LLM ──────────────────────────────────────────────────────────────────────
export type LLMProvider = "openai" | "gemini" | "anthropic";

// ── Chat ─────────────────────────────────────────────────────────────────────
export interface ChatRequest {
  prompt: string;
  provider?: LLMProvider;
  model?: string;
}

export interface ChatResponse {
  reply: string;
  model: string;
  provider: LLMProvider;
}

// ── Orchestrator ──────────────────────────────────────────────────────────────
export interface OrchestratorRequest {
  query: string;
  top_k?: number;
  provider?: LLMProvider;
  model?: string;
}

export interface TaskResult {
  subquery: string;
  intent: string;
  answer: string;
  documents?: RagSourceSnippet[];
  tool_result?: Record;
}

export interface OrchestratorResponse {
  trace_id: string;
  agent_run_id: string;
  final_response: string;
  intent: string;
  original_query: string;
  sub_queries: string[];
  task_results: TaskResult[];
  audit_log: string[];
  documents: RagSourceSnippet[];
  tool_result: Record;
}

// ── Documents ─────────────────────────────────────────────────────────────────
export interface DocumentUploadResponse {
  id: string;
  title?: string;
  source_type?: string;
  chunk_count?: number;
  stored_filename?: string;
  content_sha256: string;
  deduplicated: boolean;
  ingestion_status: "pending" | "ready" | "failed";
}

export interface DocumentListItem {
  id: string;
  title?: string;
  source_type?: string;
  ingestion_status: "pending" | "ready" | "failed";
  created_at: string;
}

export interface DocumentListResponse {
  documents: DocumentListItem[];
}

// ── RAG ───────────────────────────────────────────────────────────────────────
export interface RagSourceSnippet {
  document_id: string;
  chunk_index: number;
  preview: string;
}

export interface RagQueryRequest {
  question: string;
  top_k?: number;
  provider?: LLMProvider;
  model?: string;
}

export interface RagQueryResponse {
  reply: string;
  model: string;
  provider: LLMProvider;
  sources: RagSourceSnippet[];
}

// ── Health ────────────────────────────────────────────────────────────────────
export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
  langsmith_tracing: boolean;
  langsmith_project?: string;
}
