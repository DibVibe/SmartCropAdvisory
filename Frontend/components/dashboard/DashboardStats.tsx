interface Stat {
  name: string;
  value: string;
  change: string;
  changeType: "increase" | "decrease";
  icon: string;
}

interface DashboardStatsProps {
  stats?: {
    totalFields: number;
    activeCrops: number;
    healthyFields: number;
    pendingTasks: number;
  };
}

export default function DashboardStats({ stats }: DashboardStatsProps) {
  const dashboardStats: Stat[] = [
    {
      name: "Total Fields",
      value: stats?.totalFields?.toString() || "0",
      change: "+2.1%",
      changeType: "increase",
      icon: "🌾",
    },
    {
      name: "Active Crops",
      value: stats?.activeCrops?.toString() || "0",
      change: "+4.3%",
      changeType: "increase",
      icon: "🌱",
    },
    {
      name: "Healthy Fields",
      value: `${stats?.healthyFields || 0}%`,
      change: "+1.2%",
      changeType: "increase",
      icon: "✅",
    },
    {
      name: "Pending Tasks",
      value: stats?.pendingTasks?.toString() || "0",
      change: "-2.1%",
      changeType: "decrease",
      icon: "⏰",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {dashboardStats.map((stat) => (
        <div
          key={stat.name}
          className="bg-white rounded-lg shadow p-6 border border-gray-200"
        >
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <span className="text-2xl">{stat.icon}</span>
            </div>
            <div className="ml-4 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  {stat.name}
                </dt>
                <dd className="flex items-baseline">
                  <div className="text-2xl font-semibold text-gray-900">
                    {stat.value}
                  </div>
                  <div
                    className={`ml-2 flex items-baseline text-sm font-semibold ${
                      stat.changeType === "increase"
                        ? "text-green-600"
                        : "text-red-600"
                    }`}
                  >
                    <svg
                      className={`self-center flex-shrink-0 h-4 w-4 ${
                        stat.changeType === "increase"
                          ? "text-green-500"
                          : "text-red-500"
                      }`}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d={
                          stat.changeType === "increase"
                            ? "M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z"
                            : "M14.707 12.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l2.293-2.293a1 1 0 011.414 0z"
                        }
                        clipRule="evenodd"
                      />
                    </svg>
                    <span className="sr-only">
                      {stat.changeType === "increase"
                        ? "Increased"
                        : "Decreased"}{" "}
                      by
                    </span>
                    {stat.change}
                  </div>
                </dd>
              </dl>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
