"use client";

import { CropData } from "../../types/api";

interface CropStatusProps {
  crops: CropData[];
  onRefresh: () => Promise<void>;
}

export function CropStatus({ crops, onRefresh }: CropStatusProps) {
  // Calculate crop health statistics from the passed data
  const calculateStats = () => {
    if (!crops || crops.length === 0) {
      return { healthy: 0, needsAttention: 0, critical: 0, healthScore: 0 };
    }

    let healthy = 0;
    let needsAttention = 0;
    let critical = 0;

    crops.forEach((crop) => {
      switch (crop.health_status) {
        case "healthy":
          healthy++;
          break;
        case "stress":
          needsAttention++;
          break;
        case "disease":
        case "pest":
          critical++;
          break;
        default:
          healthy++;
      }
    });

    const totalFields = crops.length;
    const healthScore =
      totalFields > 0 ? Math.round((healthy / totalFields) * 100) : 0;

    return { healthy, needsAttention, critical, healthScore };
  };

  const { healthy, needsAttention, critical, healthScore } = calculateStats();

  return (
    <div className="card h-64">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              🌱 Crop Health Status
            </h3>
            <p className="text-sm text-gray-600">
              {crops.length > 0
                ? `${crops.length} fields monitored`
                : "No fields data"}
            </p>
          </div>
          <button
            onClick={onRefresh}
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
      <div className="card-body">
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-900">
                Healthy Fields
              </span>
            </div>
            <span className="text-lg font-bold text-green-600">{healthy}</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-900">
                Stressed Plants
              </span>
            </div>
            <span className="text-lg font-bold text-yellow-600">
              {needsAttention}
            </span>
          </div>

          <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-sm font-medium text-gray-900">
                Disease/Pest Issues
              </span>
            </div>
            <span className="text-lg font-bold text-red-600">{critical}</span>
          </div>

          <div className="pt-2 border-t border-gray-100">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Overall Health Score</span>
              <span className="font-bold text-primary-600">{healthScore}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
