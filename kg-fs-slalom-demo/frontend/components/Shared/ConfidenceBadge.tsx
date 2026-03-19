/**
 * Confidence badge — colored indicator for confidence levels or categorical labels.
 *
 * Variants:
 *   - high:    Green (>= 0.80 confidence or positive state)
 *   - medium:  Yellow (0.50–0.79 confidence or neutral state)
 *   - low:     Red (< 0.50 confidence or error state)
 *   - neutral: Slate (non-confidence categorical labels)
 */

type BadgeVariant = "high" | "medium" | "low" | "neutral";

interface ConfidenceBadgeProps {
  /** Numeric confidence value 0.0–1.0 (used to auto-derive variant if variant not provided) */
  value?: string | number;
  /** Display label text */
  label: string;
  /** Explicit variant override */
  variant?: BadgeVariant;
}

function deriveVariant(value: string | number | undefined): BadgeVariant {
  if (value === undefined) return "neutral";
  const num = typeof value === "number" ? value : parseFloat(value);
  if (isNaN(num)) return "neutral";
  if (num >= 0.8) return "high";
  if (num >= 0.5) return "medium";
  return "low";
}

const variantClasses: Record<BadgeVariant, string> = {
  high: "bg-green-100 text-green-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-red-100 text-red-700",
  neutral: "bg-slate-100 text-slate-600",
};

export default function ConfidenceBadge({
  value,
  label,
  variant,
}: ConfidenceBadgeProps) {
  const resolvedVariant = variant ?? deriveVariant(value);
  const classes = variantClasses[resolvedVariant];

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wide ${classes}`}
    >
      {label}
    </span>
  );
}
