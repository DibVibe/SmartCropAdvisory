import { Dashboard } from "@/components/dashboard/Dashboard";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard | SmartCropAdvisory",
  description: "Your agricultural intelligence dashboard",
};

export default function DashboardPage() {
  return <Dashboard />;
}
