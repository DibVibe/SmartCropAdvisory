"use client";

import { useState, useEffect } from "react";
import { IrrigationData } from "../../types/api";

interface IrrigationStatusProps {
  data?: IrrigationData | null;
  onRefresh?: () => Promise<void>;
}

export function IrrigationStatus({ data, onRefresh }: IrrigationStatusProps) {
  const [loading, setLoading] = useState(false);

  const handleRefresh = async () => {
    if (onRefresh) {
      setLoading(true);
      try {
        await onRefresh();
      } finally {
        setLoading(false);
      }
    }
  };

  const getStatusColor = (status: IrrigationData["status"]) => {
    switch (status) {
      case "active":
        return "text-green-600 bg-green-100";
      case "scheduled":
        return "text-blue-600 bg-blue-100";
      case "delayed":
        return "text-yellow-600 bg-yellow-100";
      case "completed":
        return "text-gray-600 bg-gray-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const getStatusIcon = (status: IrrigationData["status"]) => {
    switch (status) {
      case "active":
        return "💧";
      case "scheduled":
        return "⏰";
      case "delayed":
        return "⚠️";
      case "completed":
        return "✅";
      default:
        return "❓";
    }
  };

  const getStatusText = (status: IrrigationData["status"]) => {
    switch (status) {
      case "active":
        return "Actively Irrigating";
      case "scheduled":
        return "Scheduled";
      case "delayed":
        return "Delayed";
      case "completed":
        return "Completed";
      default:
        return "Unknown Status";
    }
  };

  const getSoilMoistureColor = (moisture: number) => {
    if (moisture >= 70) return "bg-blue-500";
    if (moisture >= 30) return "bg-yellow-500";
    return "bg-red-500";
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch {
      return dateString;
    }
  };

  const getNextIrrigationTime = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInHours = Math.ceil(
        (date.getTime() - now.getTime()) / (1000 * 60 * 60)
      );

      if (diffInHours < 0) {
        return "Overdue";
      } else if (diffInHours < 24) {
        return `In ${diffInHours} hours`;
      } else {
        const diffInDays = Math.ceil(diffInHours / 24);
        return `In ${diffInDays} days`;
      }
    } catch {
      return "Unknown";
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">
            💧 Irrigation System
          </h3>
        </div>
        <div className="card-body">
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="loading-pulse h-4 w-24 rounded"></div>
                <div className="loading-pulse h-4 w-16 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              💧 Irrigation System
            </h3>
            <button
              onClick={handleRefresh}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
              title="Refresh irrigation data"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </button>
          </div>
        </div>
        <div className="card-body">
          <div className="flex flex-col items-center justify-center py-8 text-gray-500">
            <div className="text-4xl mb-2">💧</div>
            <p className="text-sm">No irrigation data available</p>
            <button
              onClick={handleRefresh}
              className="mt-3 btn-secondary text-sm"
            >
              Load Data
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            💧 Irrigation System
          </h3>
          <div className="flex items-center space-x-2">
            <div
              className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(data.status)}`}
            >
              <span>{getStatusIcon(data.status)}</span>
              <span>{getStatusText(data.status)}</span>
            </div>
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors disabled:cursor-not-allowed"
              title="Refresh irrigation data"
            >
              <svg
                className={`w-4 h-4 ${loading ? "animate-spin" : ""}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div className="card-body">
        <div className="space-y-4">
          {/* Field Information */}
          <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <span className="text-blue-600">🌾</span>
              <span className="text-sm font-medium text-gray-900">
                Field ID
              </span>
            </div>
            <span className="text-sm font-semibold text-blue-600">
              {data.field_id}
            </span>
          </div>

          {/* Soil Moisture */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Soil Moisture</span>
              <span className="text-sm font-medium">{data.soil_moisture}%</span>
            </div>
            <div className="progress-bar">
              <div
                className={`progress-fill ${getSoilMoistureColor(data.soil_moisture)}`}
                style={{ width: `${data.soil_moisture}%` }}
              ></div>
            </div>
          </div>

          {/* Irrigation Details */}
          <div className="grid grid-cols-1 gap-3">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <span className="text-gray-600">💧</span>
                <span className="text-sm text-gray-600">Water Required</span>
              </div>
              <span className="text-sm font-medium">
                {data.water_requirement}L
              </span>
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <span className="text-gray-600">🔧</span>
                <span className="text-sm text-gray-600">Method</span>
              </div>
              <span className="text-sm font-medium capitalize">
                {data.irrigation_method}
              </span>
            </div>
          </div>

          {/* Next Irrigation Schedule */}
          <div className="pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">
              Schedule
            </h4>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Next Irrigation</span>
                <div className="text-right">
                  <div className="text-sm font-medium">
                    {getNextIrrigationTime(data.next_irrigation)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {formatDate(data.next_irrigation)}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Status-specific information */}
          {data.status === "delayed" && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <span className="text-yellow-600">⚠️</span>
                <span className="text-sm text-yellow-800 font-medium">
                  Irrigation Delayed
                </span>
              </div>
              <p className="text-xs text-yellow-700 mt-1">
                Check system status or weather conditions
              </p>
            </div>
          )}

          {data.status === "active" && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <span className="text-green-600">💧</span>
                <span className="text-sm text-green-800 font-medium">
                  Currently Irrigating
                </span>
              </div>
              <p className="text-xs text-green-700 mt-1">
                Field {data.field_id} is receiving water
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
