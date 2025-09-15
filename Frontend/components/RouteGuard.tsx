"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

interface RouteGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  redirectTo?: string;
}

export function RouteGuard({
  children,
  requireAuth = true,
  redirectTo = "/login",
}: RouteGuardProps) {
  const { user, loading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Don't do anything while auth is still loading
    if (loading) return;

    console.log("🛡️ RouteGuard check:", {
      requireAuth,
      isAuthenticated,
      loading,
    });

    if (requireAuth && !isAuthenticated) {
      console.log(
        "🔒 Auth required but not authenticated, redirecting to:",
        redirectTo
      );
      router.push(redirectTo);
      return;
    }

    if (!requireAuth && isAuthenticated) {
      console.log("🏠 Already authenticated, redirecting to dashboard");
      router.push("/dashboard");
      return;
    }
  }, [isAuthenticated, loading, requireAuth, redirectTo, router]);

  // Show loading while auth is initializing
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show nothing while redirecting
  if (requireAuth && !isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  if (!requireAuth && isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
