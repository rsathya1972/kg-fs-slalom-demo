/**
 * Shared TypeScript interfaces for the Slalom Field Services Intelligence Platform.
 * Keep in sync with backend Pydantic model response shapes.
 */

// ---- Query / RAG ----

export interface QueryRequest {
  question: string;
  tenant_id?: string;
  filters?: Record<string, string>;
  max_results?: number;
}

export interface Citation {
  chunk_id: string;
  doc_id: string;
  filename: string;
  doc_type: string;
  excerpt: string;
  final_score: number;
  page_number?: number | null;
}

export interface ConsultantReferral {
  consultant_id: string;
  name: string;
  title: string;
  utility_experience_years: number;
  relevant_engagements: string[];
  contact_email?: string | null;
}

export interface QueryResponse {
  id: string;
  question: string;
  answer: string;
  citations: Citation[];
  consultant_referrals: ConsultantReferral[];
  follow_up_suggestions: string[];
  faithfulness_score?: number | null;
  tenant_id: string;
  generated_at: string;
}

// ---- Discovery Questions ----

export interface LikelyAnswer {
  answer_text: string;
  implication: string;
  leads_to: string | null;
  follow_up_note?: string;
}

export interface DiscoveryQuestion {
  id: string;
  text: string;
  category: "technical" | "process" | "strategic" | "organizational";
  sequence_order: number;
  likely_answers: LikelyAnswer[];
}

// ---- Meeting Prep ----

export interface MeetingBrief {
  client_name: string;
  meeting_date: string;
  likely_systems: string[];
  key_stakeholders: string[];
  suggested_questions: DiscoveryQuestion[];
  relevant_engagements: string[];
  red_flags: string[];
  generated_at: string;
}

// ---- Graph Entities ----

export interface GraphNode {
  id: string;
  label: string;
  properties: Record<string, unknown>;
}

export interface GraphEdge {
  from_id: string;
  to_id: string;
  type: string;
  properties: Record<string, unknown>;
}

// ---- Tech Systems ----

export interface TechSystem {
  id: string;
  vendor: string;
  product_name: string;
  category: string;
  utility_relevant: boolean;
  description: string;
  misconception?: string | null;
  client_count?: number;
}

// ---- Clients ----

export interface Client {
  id: string;
  name: string;
  utility_type: string;
  hq_state?: string | null;
  revenue_band?: string | null;
  engagement_count: number;
  system_count: number;
}

// ---- Consultants ----

export interface Consultant {
  id: string;
  name: string;
  title?: string | null;
  utility_experience_years: number;
  location?: string | null;
  fsm_systems: string[];
  engagement_count: number;
}

// ---- Ingestion ----

export type IngestStatus = "queued" | "processing" | "completed" | "failed" | "dead_letter";

export interface IngestJob {
  job_id: string;
  filename: string;
  status: IngestStatus;
  chunk_count: number | null;
  entity_count: number | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

// ---- Feedback ----

export interface FeedbackRequest {
  response_id: string;
  rating: "up" | "down";
  comment?: string | null;
  tenant_id?: string;
}
