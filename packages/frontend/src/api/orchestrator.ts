import type { OrchestratorRequest, OrchestratorResponse } from "../types/api";
import { createApiClient } from "./client";

export async function runOrchestrator(req: OrchestratorRequest): Promise {
  const client = createApiClient();
  const { data } = await client.post<OrchestratorResponse>("/api/orchestrator/run", req);
  return data;
}
