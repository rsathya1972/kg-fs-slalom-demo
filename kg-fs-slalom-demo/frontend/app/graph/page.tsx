"use client";

import { useEffect, useState } from "react";
import { Network } from "lucide-react";
import LoadingSkeleton from "@/components/Shared/LoadingSkeleton";
import ConfidenceBadge from "@/components/Shared/ConfidenceBadge";
import { api } from "@/lib/api";
import type { GraphNode } from "@/lib/types";

export default function GraphExplorerPage() {
  const [systems, setSystems] = useState<GraphNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>("all");

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.getGraphSystems(
          categoryFilter === "all" ? undefined : categoryFilter
        );
        setSystems(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load systems");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [categoryFilter]);

  const categories = ["all", "FSM", "GIS", "ADMS", "Asset Mgmt", "ERP", "OMS", "AMI", "Integration"];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900">Graph Explorer</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Browse technology systems, clients, consultants, and use cases in the
          knowledge graph.
        </p>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-2 mb-5">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => {
              setLoading(true);
              setCategoryFilter(cat);
            }}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              categoryFilter === cat
                ? "bg-[#00A3AD] text-white"
                : "bg-white text-slate-600 border border-slate-200 hover:border-[#00A3AD]"
            }`}
          >
            {cat === "all" ? "All Systems" : cat}
          </button>
        ))}
      </div>

      {/* Systems grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <LoadingSkeleton key={i} />
          ))}
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
          {error}
        </div>
      ) : systems.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <Network className="w-10 h-10 text-slate-300 mx-auto mb-3" />
          <p className="font-medium text-slate-700">No systems found</p>
          <p className="text-sm text-slate-500 mt-1">
            Run seed data loader to populate the graph with tech systems.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {systems.map((system) => (
            <div
              key={system.id}
              className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-semibold text-sm text-slate-900">
                    {(system.properties as Record<string, string>)?.product_name ?? system.label}
                  </p>
                  <p className="text-xs text-slate-500">
                    {(system.properties as Record<string, string>)?.vendor}
                  </p>
                </div>
                <ConfidenceBadge
                  value={(system.properties as Record<string, string>)?.category ?? ""}
                  label={(system.properties as Record<string, string>)?.category ?? ""}
                  variant="neutral"
                />
              </div>
              {(system.properties as Record<string, string>)?.description && (
                <p className="text-xs text-slate-600 line-clamp-3 mt-2">
                  {(system.properties as Record<string, string>).description}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
