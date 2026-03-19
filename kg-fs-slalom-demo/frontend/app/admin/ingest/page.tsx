"use client";

import { Upload, Clock, CheckCircle, XCircle, AlertCircle } from "lucide-react";

type JobStatus = "queued" | "processing" | "completed" | "failed" | "dead_letter";

interface MockJob {
  id: string;
  filename: string;
  status: JobStatus;
  chunk_count: number | null;
  entity_count: number | null;
  created_at: string;
}

const MOCK_JOBS: MockJob[] = [
  {
    id: "job-001",
    filename: "sdge_fsm_assessment_narrative.docx",
    status: "completed",
    chunk_count: 48,
    entity_count: 0,
    created_at: "2026-03-19T08:30:00Z",
  },
  {
    id: "job-002",
    filename: "utility_discovery_qa_bank_v3.pdf",
    status: "completed",
    chunk_count: 22,
    entity_count: 0,
    created_at: "2026-03-19T09:15:00Z",
  },
  {
    id: "job-003",
    filename: "sce_technology_landscape.pptx",
    status: "processing",
    chunk_count: null,
    entity_count: null,
    created_at: "2026-03-19T10:00:00Z",
  },
  {
    id: "job-004",
    filename: "pg_e_transcript_2025_q4.txt",
    status: "queued",
    chunk_count: null,
    entity_count: null,
    created_at: "2026-03-19T10:05:00Z",
  },
  {
    id: "job-005",
    filename: "bad_file_corrupt.pdf",
    status: "failed",
    chunk_count: null,
    entity_count: null,
    created_at: "2026-03-19T09:45:00Z",
  },
];

const statusConfig: Record<JobStatus, { icon: React.ReactNode; label: string; className: string }> = {
  queued: {
    icon: <Clock className="w-3.5 h-3.5" />,
    label: "Queued",
    className: "bg-slate-100 text-slate-600",
  },
  processing: {
    icon: <AlertCircle className="w-3.5 h-3.5 animate-pulse" />,
    label: "Processing",
    className: "bg-amber-100 text-amber-700",
  },
  completed: {
    icon: <CheckCircle className="w-3.5 h-3.5" />,
    label: "Completed",
    className: "bg-green-100 text-green-700",
  },
  failed: {
    icon: <XCircle className="w-3.5 h-3.5" />,
    label: "Failed",
    className: "bg-red-100 text-red-700",
  },
  dead_letter: {
    icon: <XCircle className="w-3.5 h-3.5" />,
    label: "Dead Letter",
    className: "bg-red-200 text-red-800",
  },
};

function StatusBadge({ status }: { status: JobStatus }) {
  const cfg = statusConfig[status];
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${cfg.className}`}
    >
      {cfg.icon}
      {cfg.label}
    </span>
  );
}

export default function IngestStatusPage() {
  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">
            Ingestion Status
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Document ingestion job queue — read-only status view.
          </p>
        </div>
        <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-1.5 text-xs text-amber-700">
          <AlertCircle className="w-3.5 h-3.5" />
          Showing mock data — Phase 1c pipeline not yet active
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        {[
          { label: "Total Jobs", value: MOCK_JOBS.length, color: "text-slate-900" },
          {
            label: "Completed",
            value: MOCK_JOBS.filter((j) => j.status === "completed").length,
            color: "text-green-600",
          },
          {
            label: "Processing",
            value: MOCK_JOBS.filter((j) => j.status === "processing").length,
            color: "text-amber-600",
          },
          {
            label: "Failed",
            value: MOCK_JOBS.filter((j) => j.status === "failed" || j.status === "dead_letter").length,
            color: "text-red-600",
          },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-white rounded-xl border border-slate-200 shadow-sm p-4"
          >
            <p className="text-xs text-slate-500 mb-1">{stat.label}</p>
            <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Job table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Filename
              </th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Status
              </th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Chunks
              </th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Entities
              </th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Created
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {MOCK_JOBS.map((job) => (
              <tr key={job.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-mono text-xs text-slate-800 max-w-xs truncate">
                  <div className="flex items-center gap-2">
                    <Upload className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                    {job.filename}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <StatusBadge status={job.status} />
                </td>
                <td className="px-4 py-3 text-slate-600">
                  {job.chunk_count ?? "—"}
                </td>
                <td className="px-4 py-3 text-slate-600">
                  {job.entity_count ?? "—"}
                </td>
                <td className="px-4 py-3 text-slate-500 text-xs">
                  {new Date(job.created_at).toLocaleTimeString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
