"use client";

import { HelpCircle } from "lucide-react";
import EmptyState from "@/components/Shared/EmptyState";

export default function DiscoveryPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900">
          Discovery Question Bank
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Browse and search guided discovery questions for utility FSM sales and
          assessment conversations.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8">
        <EmptyState
          icon={<HelpCircle className="w-10 h-10 text-slate-300" />}
          title="Discovery Bank Viewer Coming Soon"
          message="The discovery question bank seed data is loaded in the graph. The interactive viewer — with branching logic, use case filters, and contextual follow-up suggestions — ships in Phase 1b."
        />
      </div>
    </div>
  );
}
