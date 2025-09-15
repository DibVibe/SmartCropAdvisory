"use client";

import { RouteGuard } from "@/components/RouteGuard";
import { Dashboard } from "@/components/dashboard/Dashboard";

export default function DashboardPage() {
  return (
    <RouteGuard requireAuth={true}>
      <Dashboard />
    </RouteGuard>
  );
}
