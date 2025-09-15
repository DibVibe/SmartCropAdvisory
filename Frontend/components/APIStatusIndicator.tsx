// components/APIStatusIndicator.tsx
"use client";

import { useEffect, useState } from "react";
import { getAPIStatus } from "../lib/api";

interface APIStatus {
  connection: boolean;
  cors: boolean;
  auth: boolean;
  overall: boolean;
  lastChecked?: Date;
}

export function APIStatusIndicator() {
  const [status, setStatus] = useState<APIStatus | null>(null);
  const [isChecking, setIsChecking] = useState(true);

  const checkStatus = async () => {
    setIsChecking(true);
    try {
      const result = await getAPIStatus();
      setStatus({ ...result, lastChecked: new Date() });
    } catch (error) {
      console.error("Failed to check API status:", error);
      setStatus({
        connection: false,
        cors: false,
        auth: false,
        overall: false,
        lastChecked: new Date(),
      });
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkStatus();

    // Check every 30 seconds
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = () => {
    if (isChecking) return "bg-yellow-400";
    if (!status) return "bg-gray-400";
    return status.overall ? "bg-green-400" : "bg-red-400";
  };

  const getStatusText = () => {
    if (isChecking) return "Checking...";
    if (!status) return "Unknown";
    if (status.overall) return "Django API Connected";
    if (status.connection && !status.cors) return "CORS Issue";
    if (!status.connection) return "Django API Disconnected";
    return "Partial Connection";
  };

  const getTooltip = () => {
    if (!status || isChecking) return "Checking API status...";

    const details = [
      `Connection: ${status.connection ? "✅" : "❌"}`,
      `CORS: ${status.cors ? "✅" : "❌"}`,
      `Auth: ${status.auth ? "✅" : "❌"}`,
    ];

    if (status.lastChecked) {
      details.push(`Last checked: ${status.lastChecked.toLocaleTimeString()}`);
    }

    return details.join("\n");
  };

  return (
    <div
      className="flex items-center space-x-2 cursor-help"
      title={getTooltip()}
      onClick={checkStatus}
    >
      <div
        className={`w-2 h-2 rounded-full ${getStatusColor()} ${
          isChecking ? "animate-pulse" : ""
        }`}
      ></div>
      <span className="text-xs text-gray-500">{getStatusText()}</span>
    </div>
  );
}
