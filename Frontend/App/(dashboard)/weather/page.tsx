import DashboardLayout from "@/components/layout/DashboardLayout";
import WeatherDashboard from "@/components/weather/WeatherDashboard";

export default function WeatherPage() {
  return (
    <DashboardLayout>
      <WeatherDashboard />
    </DashboardLayout>
  );
}
