interface WeatherAlert {
  id: string;
  type: "warning" | "watch" | "advisory";
  title: string;
  description: string;
  severity: "low" | "medium" | "high";
  validUntil: string;
}

interface WeatherAlertsProps {
  alerts: WeatherAlert[];
}

export default function WeatherAlerts({ alerts }: WeatherAlertsProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "bg-red-50 border-red-200 text-red-800";
      case "medium":
        return "bg-yellow-50 border-yellow-200 text-yellow-800";
      default:
        return "bg-blue-50 border-blue-200 text-blue-800";
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "warning":
        return "⚠️";
      case "watch":
        return "👀";
      default:
        return "ℹ️";
    }
  };

  const mockAlerts: WeatherAlert[] = [
    {
      id: "1",
      type: "warning",
      title: "Heavy Rain Warning",
      description:
        "Heavy rainfall expected tomorrow evening. Secure loose equipment and delay spraying activities.",
      severity: "high",
      validUntil: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: "2",
      type: "advisory",
      title: "High Temperature Advisory",
      description:
        "Temperatures will reach 35°C next week. Increase irrigation frequency for heat-sensitive crops.",
      severity: "medium",
      validUntil: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    },
  ];

  const displayAlerts = alerts.length > 0 ? alerts : mockAlerts;

  return (
    <div className="space-y-3">
      {displayAlerts.map((alert) => (
        <div
          key={alert.id}
          className={`p-4 rounded-lg border ${getSeverityColor(
            alert.severity
          )}`}
        >
          <div className="flex items-start">
            <div className="flex-shrink-0 mr-3">
              <span className="text-xl">{getAlertIcon(alert.type)}</span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <h3 className="text-sm font-medium capitalize">
                  {alert.title}
                </h3>
                <span className="text-xs opacity-75">
                  Valid until{" "}
                  {new Date(alert.validUntil).toLocaleDateString("en-IN")}
                </span>
              </div>
              <p className="text-sm opacity-90">{alert.description}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
