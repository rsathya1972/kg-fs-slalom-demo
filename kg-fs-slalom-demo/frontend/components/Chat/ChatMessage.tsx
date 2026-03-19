/**
 * Chat message bubble — displays user or assistant messages.
 */

import CitationCard from "./CitationCard";
import type { Citation } from "@/lib/types";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

export default function ChatMessage({
  role,
  content,
  citations,
}: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[85%] ${isUser ? "order-2" : ""}`}>
        {/* Role indicator */}
        <div
          className={`flex items-center gap-1.5 mb-1 ${isUser ? "justify-end" : ""}`}
        >
          {!isUser && (
            <div className="w-5 h-5 rounded-full bg-[#00A3AD] flex items-center justify-center">
              <span className="text-[10px] font-bold text-white">S</span>
            </div>
          )}
          <span className="text-[10px] font-medium text-slate-400 uppercase tracking-wide">
            {isUser ? "You" : "Field Intelligence"}
          </span>
        </div>

        {/* Message bubble */}
        <div
          className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? "bg-[#00A3AD] text-white rounded-tr-sm"
              : "bg-white border border-slate-200 text-slate-800 rounded-tl-sm shadow-sm"
          }`}
        >
          <p className="whitespace-pre-wrap">{content}</p>
        </div>

        {/* Citations */}
        {citations && citations.length > 0 && (
          <div className="mt-2 space-y-1.5">
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wide px-1">
              Sources
            </p>
            {citations.map((citation) => (
              <CitationCard key={citation.chunk_id} citation={citation} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
