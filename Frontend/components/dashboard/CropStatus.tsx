"use client";

import { CropData } from "../../types/api";

interface CropStatusProps {
  crops: CropData[] | null | undefined;
  onRefresh: () => Promise<void>;
}

interface CropStats {
  healthy: number;
  needsAttention: number;
  critical: number;
  healthScore: number;
  totalFields: number;
}

export function CropStatus({ crops, onRefresh }: CropStatusProps) {
  // Calculate crop health statistics from the passed data
  const calculateStats = (): CropStats => {
    // Handle null, undefined, or empty arrays
    if (!crops || !Array.isArray(crops) || crops.length === 0) {
      return {
        healthy: 0,
        needsAttention: 0,
        critical: 0,
        healthScore: 0,
        totalFields: 0,
      };
    }

    let healthy = 0;
    let needsAttention = 0;
    let critical = 0;

    // Safe to use forEach now since we've checked crops is a valid array
    crops.forEach((crop) => {
      if (!crop || !crop.health_status) {
        // Handle crops with missing health_status
        healthy++; // Default to healthy if status is missing
        return;
      }

      switch (crop.health_status.toLowerCase().trim()) {
        case "healthy":
        case "good":
          healthy++;
          break;
        case "stress":
        case "stressed":
        case "warning":
        case "attention":
          needsAttention++;
          break;
        case "disease":
        case "pest":
        case "critical":
        case "bad":
        case "poor":
          critical++;
          break;
        default:
          healthy++; // Default to healthy for unknown statuses
      }
    });

    const totalFields = crops.length;
    const healthScore =
      totalFields > 0 ? Math.round((healthy / totalFields) * 100) : 0;

    return { healthy, needsAttention, critical, healthScore, totalFields };
  };

  const handleRefresh = async (): Promise<void> => {
    try {
      await onRefresh();
    } catch (error) {
      console.error("Failed to refresh crop data:", error);
    }
  };

  const { healthy, needsAttention, critical, healthScore, totalFields } =
    calculateStats();

  // Loading state when crops is null/undefined
  if (crops === null || crops === undefined) {
    return (
      <div className="card h-64">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                🌱 Crop Health Status
              </h3>
              <p className="text-sm text-gray-600">Loading crop data...</p>
            </div>
            <button
              onClick={handleRefresh}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
              title="Refresh crop data"
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
        <div className="card-body flex items-center justify-center">
          <div className="text-center text-gray-500">
            <div className="text-2xl mb-2">🌱</div>
            <p>Loading crop health data...</p>
          </div>
        </div>
      </div>
    );
  }

  // Empty state
  if (totalFields === 0) {
    return (
      <div className="card h-64">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                🌱 Crop Health Status
              </h3>
              <p className="text-sm text-gray-600">No fields data available</p>
            </div>
            <button
              onClick={handleRefresh}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
              title="Refresh crop data"
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
        <div className="card-body flex items-center justify-center">
          <div className="text-center text-gray-500">
            <div className="text-4xl mb-4">🌾</div>
            <p className="mb-2">No crop fields found</p>
            <button onClick={handleRefresh} className="btn-secondary btn-sm">
              Refresh Data
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card h-64">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              🌱 Crop Health Status
            </h3>
            <p className="text-sm text-gray-600">
              {totalFields === 1
                ? "1 field monitored"
                : `${totalFields} fields monitored`}
            </p>
          </div>
          <button
            onClick={handleRefresh}
            className="p-1 text-gray-400 hover:text-gray-600 transition-colors rounded-full hover:bg-gray-100"
            title="Refresh crop data"
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
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-100">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full flex-shrink-0"></div>
              <span className="text-sm font-medium text-gray-900">
                Healthy Fields
              </span>
            </div>
            <span className="text-lg font-bold text-green-600">{healthy}</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-100">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-yellow-500 rounded-full flex-shrink-0"></div>
              <span className="text-sm font-medium text-gray-900">
                Stressed Plants
              </span>
            </div>
            <span className="text-lg font-bold text-yellow-600">
              {needsAttention}
            </span>
          </div>

          <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-100">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-red-500 rounded-full flex-shrink-0"></div>
              <span className="text-sm font-medium text-gray-900">
                Disease/Pest Issues
              </span>
            </div>
            <span className="text-lg font-bold text-red-600">{critical}</span>
          </div>

          <div className="pt-2 border-t border-gray-100">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Overall Health Score</span>
              <span
                className={`font-bold ${
                  healthScore >= 80
                    ? "text-green-600"
                    : healthScore >= 60
                      ? "text-yellow-600"
                      : "text-red-600"
                }`}
              >
                {healthScore}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
