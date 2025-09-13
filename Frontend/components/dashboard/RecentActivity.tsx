"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import { formatDate } from "@/lib/utils";

export default function RecentActivity() {
  const { data: activities, isLoading } = useQuery({
    queryKey: ["recent-activities"],
    queryFn: async () => {
      const response = await apiClient.get("/activities/recent/");
      return response.data;
    },
  });

  const mockActivities = [
    {
      id: 1,
      type: "crop_analysis",
      description: "Disease detected in Field A - Wheat crop",
      timestamp: new Date().toISOString(),
      status: "warning",
    },
    {
      id: 2,
      type: "irrigation",
      description: "Irrigation cycle completed for Field B",
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      status: "success",
    },
    {
      id: 3,
      type: "weather",
      description: "Weather alert: Heavy rain expected tomorrow",
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      status: "info",
    },
  ];

  const displayActivities = activities || mockActivities;

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <div className="animate-pulse space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex space-x-3">
              <div className="w-2 h-2 bg-gray-200 rounded-full mt-2"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "text-green-500";
      case "warning":
        return "text-yellow-500";
      case "error":
        return "text-red-500";
      default:
        return "text-blue-500";
    }
  };

  const getStatusIcon = (type: string) => {
    switch (type) {
      case "crop_analysis":
        return "🔬";
      case "irrigation":
        return "💧";
      case "weather":
        return "🌤️";
      case "market":
        return "📈";
      default:
        return "📝";
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Recent Activity
      </h3>

      <div className="flow-root">
        <ul className="-mb-8 space-y-6">
          {displayActivities.map((activity: any, index: number) => (
            <li key={activity.id}>
              <div className="relative pb-8">
                {index !== displayActivities.length - 1 && (
                  <span
                    className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                    aria-hidden="true"
                  />
                )}
                <div className="relative flex space-x-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100">
                    <span className="text-lg">
                      {getStatusIcon(activity.type)}
                    </span>
                  </div>
                  <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                    <div>
                      <p className="text-sm text-gray-900">
                        {activity.description}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatDate(activity.timestamp)}
                      </p>
                    </div>
                    <div className="text-right text-sm whitespace-nowrap text-gray-500">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          activity.status
                        )}`}
                      >
                        {activity.status}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
