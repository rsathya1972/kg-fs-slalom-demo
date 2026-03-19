/**
 * Empty state component — displayed when a list or view has no content.
 */

interface EmptyStateProps {
  /** Icon element to display (e.g. a Lucide icon) */
  icon: React.ReactNode;
  /** Short headline */
  title: string;
  /** Longer explanatory message */
  message: string;
  /** Optional call-to-action button */
  action?: React.ReactNode;
}

export default function EmptyState({
  icon,
  title,
  message,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="mb-4 text-slate-300">{icon}</div>
      <h3 className="text-base font-semibold text-slate-700 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 max-w-sm">{message}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
