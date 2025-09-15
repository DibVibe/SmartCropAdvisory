"use client";

import { useEffect, useState } from "react";

interface ClientDateProps {
  date: string | Date;
  format?: "short" | "long" | "numeric";
  className?: string;
}

export function ClientDate({
  date,
  format = "short",
  className,
}: ClientDateProps) {
  const [formattedDate, setFormattedDate] = useState<string>("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const dateObj = typeof date === "string" ? new Date(date) : date;

    const formatted = dateObj.toLocaleDateString("en-US", {
      year: "numeric",
      month:
        format === "long" ? "long" : format === "short" ? "short" : "numeric",
      day: "numeric",
    });

    setFormattedDate(formatted);
  }, [date, format]);

  if (!mounted) {
    return <span className={className}>Loading...</span>;
  }

  return <span className={className}>{formattedDate}</span>;
}
