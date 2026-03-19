/**
 * Skeleton loader component — animated pulse placeholder for loading states.
 */

interface LoadingSkeletonProps {
  /** Number of lines to render (default: 3) */
  lines?: number;
  /** Additional CSS classes */
  className?: string;
}

export default function LoadingSkeleton({
  lines = 3,
  className = "",
}: LoadingSkeletonProps) {
  return (
    <div
      className={`bg-white rounded-xl border border-slate-200 shadow-sm p-4 ${className}`}
      aria-busy="true"
      aria-label="Loading..."
    >
      {/* Header placeholder */}
      <div className="flex items-center gap-3 mb-3">
        <div className="w-8 h-8 bg-slate-200 rounded-lg animate-pulse" />
        <div className="flex-1 space-y-1.5">
          <div className="h-3 bg-slate-200 rounded animate-pulse w-3/4" />
          <div className="h-2.5 bg-slate-100 rounded animate-pulse w-1/2" />
        </div>
      </div>

      {/* Line placeholders */}
      <div className="space-y-2">
        {[...Array(lines)].map((_, i) => (
          <div
            key={i}
            className="h-2.5 bg-slate-100 rounded animate-pulse"
            style={{ width: `${90 - i * 15}%` }}
          />
        ))}
      </div>
    </div>
  );
}
