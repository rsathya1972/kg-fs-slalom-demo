"use client";

/**
 * Toast notification component — displays success, error, and info messages.
 *
 * Usage:
 *   <Toast message="Document uploaded!" variant="success" onClose={() => setToast(null)} />
 */

import { useEffect } from "react";
import { CheckCircle, XCircle, Info, X } from "lucide-react";

type ToastVariant = "success" | "error" | "info";

interface ToastProps {
  message: string;
  variant?: ToastVariant;
  /** Duration in ms before auto-dismiss (default: 4000, 0 = no auto-dismiss) */
  duration?: number;
  onClose: () => void;
}

const variantConfig: Record<
  ToastVariant,
  { icon: React.ReactNode; containerClass: string; iconClass: string }
> = {
  success: {
    icon: <CheckCircle className="w-4 h-4" />,
    containerClass: "bg-green-50 border-green-200 text-green-800",
    iconClass: "text-green-600",
  },
  error: {
    icon: <XCircle className="w-4 h-4" />,
    containerClass: "bg-red-50 border-red-200 text-red-800",
    iconClass: "text-red-600",
  },
  info: {
    icon: <Info className="w-4 h-4" />,
    containerClass: "bg-blue-50 border-blue-200 text-blue-800",
    iconClass: "text-blue-600",
  },
};

export default function Toast({
  message,
  variant = "info",
  duration = 4000,
  onClose,
}: ToastProps) {
  const { icon, containerClass, iconClass } = variantConfig[variant];

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  return (
    <div
      role="alert"
      className={`fixed bottom-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg text-sm max-w-sm animate-in slide-in-from-bottom-2 ${containerClass}`}
    >
      <span className={iconClass}>{icon}</span>
      <span className="flex-1">{message}</span>
      <button
        onClick={onClose}
        className="ml-2 opacity-60 hover:opacity-100 transition-opacity"
        aria-label="Close notification"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
