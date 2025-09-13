import DashboardLayout from "@/components/layout/DashboardLayout";
import IrrigationDashboard from "@/components/irrigation/IrrigationDashboard";

export default function IrrigationPage() {
  return (
    <DashboardLayout>
      <IrrigationDashboard />
    </DashboardLayout>
  );
}
