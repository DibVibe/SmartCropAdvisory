"use client";

import { useState, useEffect } from "react";
import { formatDate, formatDateTime, formatDateISO } from "../../utils/dateUtils";

interface SafeDateProps {
  date: string | Date;
  type?: "date" | "datetime" | "iso";
  options?: Intl.DateTimeFormatOptions;
  className?: string;
  fallback?: string;
}

export function SafeDate({
  date,
  type = "date",
  options,
  className,
  fallback = "Loading...",
}: SafeDateProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // During SSR and before hydration, show fallback
  if (!mounted) {
    return (
      <span className={className} suppressHydrationWarning>
        {fallback}
      </span>
    );
  }

  // After hydration, use your existing utilities
  let formattedDate: string;

  try {
    switch (type) {
      case "datetime":
        formattedDate = formatDateTime(date);
        break;
      case "iso":
        formattedDate = formatDateISO(date);
        break;
      case "date":
      default:
        formattedDate = formatDate(date, options);
    }
  } catch (error) {
    console.error("SafeDate formatting error:", error);
    formattedDate = "Invalid Date";
  }

  return <span className={className}>{formattedDate}</span>;
}
