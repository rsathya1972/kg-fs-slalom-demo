"use client";

/**
 * Expandable citation card with source metadata and confidence badge.
 */

import { useState } from "react";
import { ChevronDown, ChevronUp, FileText } from "lucide-react";
import ConfidenceBadge from "@/components/Shared/ConfidenceBadge";
import type { Citation } from "@/lib/types";

interface CitationCardProps {
  citation: Citation;
}

export default function CitationCard({ citation }: CitationCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-lg text-xs overflow-hidden">
      {/* Header — always visible */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-slate-100 transition-colors"
        aria-expanded={expanded}
      >
        <FileText className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
        <span className="flex-1 text-slate-700 font-medium truncate">
          {citation.filename}
        </span>
        <span className="text-slate-400 text-[10px] mr-2">
          {citation.doc_type}
        </span>
        <ConfidenceBadge
          value={citation.final_score}
          label={`${Math.round(citation.final_score * 100)}%`}
        />
        {expanded ? (
          <ChevronUp className="w-3.5 h-3.5 text-slate-400 ml-1 flex-shrink-0" />
        ) : (
          <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-1 flex-shrink-0" />
        )}
      </button>

      {/* Expanded excerpt */}
      {expanded && (
        <div className="px-3 pb-3 border-t border-slate-200 pt-2">
          <p className="text-slate-600 leading-relaxed italic">
            &ldquo;{citation.excerpt}&rdquo;
          </p>
          {citation.page_number != null && (
            <p className="text-slate-400 mt-1">Page {citation.page_number}</p>
          )}
        </div>
      )}
    </div>
  );
}
