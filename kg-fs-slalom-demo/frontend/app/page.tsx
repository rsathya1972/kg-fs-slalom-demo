import Link from "next/link";
import { MessageSquare, Calendar, Network, Upload } from "lucide-react";

const quickAccessCards = [
  {
    title: "Chat",
    description:
      "Ask questions about utility FSM engagements, system landscapes, and discovery strategies. Grounded in your knowledge graph.",
    href: "/chat",
    icon: MessageSquare,
    color: "bg-[#00A3AD]",
    badge: "AI-Powered",
  },
  {
    title: "Meeting Prep",
    description:
      "Generate pre-meeting briefs with relevant system context, past engagement references, and suggested discovery questions.",
    href: "/meeting-prep",
    icon: Calendar,
    color: "bg-slate-700",
    badge: "Phase 1b",
  },
  {
    title: "Graph Explorer",
    description:
      "Browse the knowledge graph: clients, technology systems, consultants, use cases, and integration patterns.",
    href: "/graph",
    icon: Network,
    color: "bg-indigo-600",
    badge: "Live",
  },
  {
    title: "Ingest Documents",
    description:
      "Upload project narratives, transcripts, whitepapers, and Q&A banks to enrich the knowledge graph.",
    href: "/admin/ingest",
    icon: Upload,
    color: "bg-amber-600",
    badge: "Admin",
  },
];

export default function DashboardPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">
          Field Services Intelligence Platform
        </h1>
        <p className="mt-1 text-slate-500 text-sm">
          Your collective utility FSM practice knowledge — ready for every
          client meeting.
        </p>
      </div>

      {/* Quick access cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {quickAccessCards.map((card) => {
          const Icon = card.icon;
          return (
            <Link
              key={card.href}
              href={card.href}
              className="group block bg-white rounded-xl shadow-sm border border-slate-200 p-5 hover:shadow-md hover:border-[#00A3AD] transition-all duration-200"
            >
              <div className="flex items-start justify-between mb-3">
                <div
                  className={`${card.color} w-10 h-10 rounded-lg flex items-center justify-center`}
                >
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <span className="text-[10px] font-semibold uppercase tracking-wide text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                  {card.badge}
                </span>
              </div>
              <h2 className="font-semibold text-slate-900 group-hover:text-[#00A3AD] transition-colors">
                {card.title}
              </h2>
              <p className="mt-1 text-sm text-slate-500 leading-snug">
                {card.description}
              </p>
            </Link>
          );
        })}
      </div>

      {/* Phase status */}
      <div className="mt-10 bg-white rounded-xl border border-slate-200 shadow-sm p-5">
        <h2 className="font-semibold text-slate-800 mb-3 text-sm uppercase tracking-wide">
          Build Status
        </h2>
        <div className="space-y-2">
          {[
            { phase: "Phase 1a", label: "Foundation scaffold, schema, seed data", status: "complete" },
            { phase: "Phase 1b", label: "SME knowledge capture, data ingestion pipeline", status: "next" },
            { phase: "Phase 1c", label: "NER extraction, embedding, hybrid retrieval", status: "planned" },
            { phase: "Phase 1d", label: "RAG generation, hallucination check, chat UI", status: "planned" },
          ].map((item) => (
            <div key={item.phase} className="flex items-center gap-3 text-sm">
              <span
                className={`w-2 h-2 rounded-full ${
                  item.status === "complete"
                    ? "bg-green-400"
                    : item.status === "next"
                    ? "bg-amber-400"
                    : "bg-slate-200"
                }`}
              />
              <span className="font-medium text-slate-700 w-20">
                {item.phase}
              </span>
              <span className="text-slate-500">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
