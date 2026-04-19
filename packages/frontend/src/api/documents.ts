import type { DocumentListResponse, DocumentUploadResponse, RagQueryRequest, RagQueryResponse } from "../types/api";
import { createApiClient } from "./client";

export async function uploadDocument(file: File, title?: string): Promise {
  const client = createApiClient();
  const form = new FormData();
  form.append("file", file);
  if (title) form.append("title", title);
  const { data } = await client.post<DocumentUploadResponse>("/api/documents/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
  return data;
}

export async function listDocuments(): Promise {
  const client = createApiClient();
  const { data } = await client.get<DocumentListResponse>("/api/documents");
  return data;
}

export async function ragQuery(req: RagQueryRequest): Promise {
  const client = createApiClient();
  const { data } = await client.post<RagQueryResponse>("/api/documents/rag", req);
  return data;
}
