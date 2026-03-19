/**
 * Typed API client for the Slalom Field Services Intelligence Platform backend.
 *
 * All methods go through this module — never use raw fetch() in components.
 * The base URL is read from NEXT_PUBLIC_API_URL (defaults to http://localhost:8000/api).
 */

import type {
  QueryRequest,
  QueryResponse,
  TechSystem,
  Client,
  Consultant,
  IngestJob,
  FeedbackRequest,
  GraphNode,
} from "./types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

// ---- Error class ----

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(`API Error ${status}: ${detail}`);
    this.name = "ApiError";
  }
}

// ---- Fetch wrapper ----

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      // ignore JSON parse error
    }
    throw new ApiError(response.status, detail);
  }

  return response.json() as Promise<T>;
}

// ---- API methods ----

export const api = {
  // ---- Health ----

  /** Ping the backend health endpoint. */
  health: () =>
    request<{ status: string; neo4j: string; opensearch: string; timestamp: string }>(
      "/health",
    ),

  // ---- RAG Query ----

  /** Submit a natural language query for RAG-powered retrieval and generation. */
  submitQuery: (body: QueryRequest) =>
    request<QueryResponse>("/query", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // ---- Graph ----

  /** List all utility clients with engagement counts. */
  getClients: (tenantId = "utilities") =>
    request<Client[]>(`/graph/clients?tenant_id=${tenantId}`),

  /** List technology systems, optionally filtered by category. */
  getGraphSystems: (category?: string, tenantId = "utilities") => {
    const params = new URLSearchParams({ tenant_id: tenantId });
    if (category) params.set("category", category);
    return request<GraphNode[]>(`/graph/systems?${params.toString()}`);
  },

  /** List consultants with utility FSM experience. */
  getConsultants: (tenantId = "utilities") =>
    request<Consultant[]>(`/graph/consultants?tenant_id=${tenantId}`),

  /** List FSM use cases. */
  getUseCases: (tenantId = "utilities") =>
    request<GraphNode[]>(`/graph/use-cases?tenant_id=${tenantId}`),

  /** Execute a named Cypher query. */
  runNamedQuery: (queryName: string, params: Record<string, unknown>) =>
    request<{ query_name: string; result: Record<string, unknown>[]; row_count: number }>(
      "/graph/query",
      {
        method: "POST",
        body: JSON.stringify({ query_name: queryName, params }),
      },
    ),

  // ---- Ingestion ----

  /** Upload a document for ingestion. */
  uploadDocument: async (file: File, tenantId = "utilities"): Promise<IngestJob> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("tenant_id", tenantId);

    const response = await fetch(`${BASE_URL}/ingest/document`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      throw new ApiError(response.status, body.detail ?? "Upload failed");
    }

    return response.json();
  },

  /** List all ingestion jobs for a tenant. */
  listIngestJobs: (tenantId = "utilities") =>
    request<IngestJob[]>(`/ingest/jobs?tenant_id=${tenantId}`),

  /** Get status of a specific ingestion job. */
  getIngestJob: (jobId: string) =>
    request<IngestJob>(`/ingest/jobs/${jobId}`),

  // ---- Review Queue ----

  /** Get the review queue for entity disambiguation. */
  getReviewQueue: (tenantId = "utilities", status = "pending") =>
    request<Record<string, unknown>[]>(
      `/review-queue?tenant_id=${tenantId}&status=${status}`,
    ),

  /** Approve a review queue item. */
  approveReviewItem: (itemId: string, resolvedNodeId?: string) =>
    request<Record<string, unknown>>(`/review-queue/${itemId}/approve`, {
      method: "POST",
      body: JSON.stringify({ resolved_node_id: resolvedNodeId }),
    }),

  /** Reject a review queue item. */
  rejectReviewItem: (itemId: string, reason?: string) =>
    request<Record<string, unknown>>(
      `/review-queue/${itemId}/reject?reason=${encodeURIComponent(reason ?? "")}`,
      { method: "POST" },
    ),

  // ---- Feedback ----

  /** Submit thumbs up/down feedback on a response. */
  submitFeedback: (body: FeedbackRequest) =>
    request<{ status: string; message: string }>("/feedback", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
