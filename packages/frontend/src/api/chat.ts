import type { ChatRequest, ChatResponse } from "../types/api";
import { createApiClient } from "./client";

export async function sendChat(req: ChatRequest): Promise {
  const client = createApiClient();
  const { data } = await client.post<ChatResponse>("/api/chat", req);
  return data;
}
