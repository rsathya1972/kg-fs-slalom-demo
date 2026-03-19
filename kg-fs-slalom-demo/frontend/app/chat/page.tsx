"use client";

import { useState } from "react";
import ChatInput from "@/components/Chat/ChatInput";
import ChatMessage from "@/components/Chat/ChatMessage";
import FollowUpSuggestions from "@/components/Chat/FollowUpSuggestions";
import EmptyState from "@/components/Shared/EmptyState";
import { MessageSquare } from "lucide-react";
import type { QueryResponse } from "@/lib/types";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: QueryResponse;
}

const INITIAL_SUGGESTIONS = [
  "What questions should I ask a utility SVP about their FSM platform?",
  "What systems does a large IOU typically use for work order management?",
  "Who at Slalom has experience with Salesforce FSM for utilities?",
  "What are the key integration patterns between FSM and GIS for utilities?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (question: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: question,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Phase 1a stub — real RAG call wired in Phase 1d
    await new Promise((resolve) => setTimeout(resolve, 800));

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content:
        "The RAG query engine is not yet active (Phase 1d). Once Phase 1c ingestion is complete and the hybrid retrieval layer is wired up, I'll be able to answer this question with grounded citations from the knowledge graph and ingested documents.",
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setIsLoading(false);
  };

  const handleSuggestion = (suggestion: string) => {
    handleSubmit(suggestion);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-14rem)]">
      <div className="mb-4">
        <h1 className="text-xl font-bold text-slate-900">
          Utility FSM Intelligence Chat
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Ask questions about clients, systems, use cases, and past engagements.
        </p>
      </div>

      {/* Message area */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center">
            <EmptyState
              icon={<MessageSquare className="w-10 h-10 text-slate-300" />}
              title="Ask your first question"
              message="Try one of the suggestions below or type your own question."
            />
            <div className="mt-6">
              <FollowUpSuggestions
                suggestions={INITIAL_SUGGESTIONS}
                onSelect={handleSuggestion}
              />
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              role={msg.role}
              content={msg.content}
              citations={msg.response?.citations}
            />
          ))
        )}

        {isLoading && (
          <div className="flex gap-2 items-center text-sm text-slate-400 px-2">
            <div className="w-2 h-2 rounded-full bg-[#00A3AD] animate-bounce" />
            <div className="w-2 h-2 rounded-full bg-[#00A3AD] animate-bounce [animation-delay:0.1s]" />
            <div className="w-2 h-2 rounded-full bg-[#00A3AD] animate-bounce [animation-delay:0.2s]" />
          </div>
        )}
      </div>

      {/* Chat input */}
      <div className="border-t border-slate-200 pt-4">
        <ChatInput onSubmit={handleSubmit} disabled={isLoading} />
      </div>
    </div>
  );
}
