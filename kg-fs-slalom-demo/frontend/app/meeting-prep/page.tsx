"use client";

import { Calendar } from "lucide-react";
import EmptyState from "@/components/Shared/EmptyState";

export default function MeetingPrepPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900">Meeting Prep</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Generate a pre-meeting brief with system context, past engagement
          references, and suggested discovery questions.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8">
        <EmptyState
          icon={<Calendar className="w-10 h-10 text-slate-300" />}
          title="Meeting Prep Coming in Phase 1b"
          message="Once SME knowledge capture and the discovery Q&A bank are loaded, this module will generate tailored pre-meeting briefs with client context, likely tech stack, and recommended discovery questions."
        />
      </div>
    </div>
  );
}
