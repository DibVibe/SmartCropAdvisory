"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  HomeIcon,
  ChartBarIcon,
  ClipboardDocumentListIcon,
  CloudIcon,
  BeakerIcon,
  MapIcon,
  Cog6ToothIcon,
  UserCircleIcon,
  Bars3Icon,
  XMarkIcon,
  CameraIcon,
  ChartPieIcon,
  BanknotesIcon,
  WrenchScrewdriverIcon,
  // Add these for enhanced functionality
  BellIcon,
  ClockIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";
import { useAuth } from "@/contexts/AuthContext";

const navigation = [
  { name: "Dashboard", href: "/", icon: HomeIcon, badge: null },

  // Group Analysis Features Together
  { name: "Crop Analysis", href: "/analysis", icon: CameraIcon, badge: "New" },
  {
    name: "Disease Detection",
    href: "/analysis/disease",
    icon: BeakerIcon,
    badge: "AI",
  },
  {
    name: "Yield Prediction",
    href: "/analysis/yield",
    icon: ChartPieIcon,
    badge: null,
  },

  // Environmental & Field Management
  { name: "Weather", href: "/weather", icon: CloudIcon, badge: null },
  {
    name: "Irrigation",
    href: "/irrigation",
    icon: WrenchScrewdriverIcon,
    badge: null,
  },
  { name: "Field Maps", href: "/maps", icon: MapIcon, badge: null },

  // Business Intelligence
  {
    name: "Market Analysis",
    href: "/market",
    icon: BanknotesIcon,
    badge: null,
  },

  // User Management
  { name: "Settings", href: "/settings", icon: Cog6ToothIcon, badge: null },
  { name: "Profile", href: "/profile", icon: UserCircleIcon, badge: null },
];

// Mock data - replace with actual API calls or context
interface AnalysisStats {
  activeFields: number;
  healthScore: number;
  alerts: number;
  analysesToday: number;
  isAnalyzing: boolean;
  recentAnalyses: Array<{
    id: string;
    cropType: string;
    timestamp: string;
    status: "completed" | "failed" | "processing";
  }>;
}

export function Navigation() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState<AnalysisStats>({
    activeFields: 42,
    healthScore: 94,
    alerts: 3,
    analysesToday: 12,
    isAnalyzing: false,
    recentAnalyses: [],
  });
  const pathname = usePathname();
  const { user } = useAuth();

  // Simulate real-time updates (replace with actual WebSocket or polling)
  useEffect(() => {
    const interval = setInterval(() => {
      // This would be replaced with actual API calls
      setStats((prev) => ({
        ...prev,
        analysesToday: prev.analysesToday + Math.random() > 0.95 ? 1 : 0,
        healthScore: Math.min(
          100,
          prev.healthScore + (Math.random() - 0.5) * 2
        ),
      }));
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <div className="absolute inset-0 bg-black bg-opacity-50" />
        </div>
      )}

      {/* Mobile sidebar */}
      <div
        className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out lg:hidden
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
      `}
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">🌾</span>
            <span className="text-lg font-semibold text-gray-900">
              SmartCrop
            </span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>
        <NavigationList pathname={pathname} stats={stats} />
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0">
        <div className="flex flex-col flex-1 bg-white border-r border-gray-200">
          {/* Logo */}
          <div className="flex items-center px-6 py-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center relative">
                <span className="text-white text-xl">🌾</span>
                {stats.isAnalyzing && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                )}
              </div>
              <div>
                <div className="text-lg font-semibold text-gray-900">
                  SmartCrop
                </div>
                <div className="text-xs text-gray-500 flex items-center space-x-1">
                  <span>AI Advisory</span>
                  {stats.isAnalyzing && (
                    <>
                      <span>•</span>
                      <span className="text-blue-500 animate-pulse">
                        Analyzing
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>

          <NavigationList pathname={pathname} stats={stats} />

          {/* Bottom section - Enhanced */}
          <div className="border-t border-gray-200 p-4">
            {/* Analysis Status Banner */}
            {stats.isAnalyzing && (
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                  <span className="text-sm font-medium text-blue-800">
                    Analysis in progress...
                  </span>
                </div>
              </div>
            )}

            {/* User Account */}
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                {(user?.first_name?.charAt(0) || user?.username?.charAt(0) || "U").toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900 truncate">
                  {user?.first_name || user?.username || "User Account"}
                </div>
                <div className="text-xs text-gray-500">Farmer</div>
              </div>
              {stats.alerts > 0 && (
                <div className="relative">
                  <BellIcon className="h-4 w-4 text-yellow-500" />
                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Mobile menu button with notification indicator */}
      <button
        onClick={() => setSidebarOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-30 p-2 bg-white rounded-lg shadow-md border border-gray-200 text-gray-600 hover:text-gray-900 relative"
      >
        <Bars3Icon className="w-6 h-6" />
        {(stats.alerts > 0 || stats.isAnalyzing) && (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
        )}
      </button>
    </>
  );
}

function NavigationList({
  pathname,
  stats,
}: {
  pathname: string;
  stats: AnalysisStats;
}) {
  return (
    <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
      {/* Analysis Section */}
      <div className="pb-4">
        <div className="flex items-center justify-between px-3 mb-3">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            🔬 Analysis Tools
          </h3>
          {stats.isAnalyzing && (
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
          )}
        </div>
        {navigation.slice(0, 4).map((item) => (
          <NavigationItem
            key={item.name}
            item={item}
            pathname={pathname}
            isAnalyzing={stats.isAnalyzing && item.href === "/analysis"}
          />
        ))}
      </div>

      {/* Field Management Section */}
      <div className="pb-4">
        <h3 className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
          🚜 Field Management
        </h3>
        {navigation.slice(4, 7).map((item) => (
          <NavigationItem key={item.name} item={item} pathname={pathname} />
        ))}
      </div>

      {/* Business & Settings Section */}
      <div className="pb-4">
        <h3 className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
          💼 Business & Settings
        </h3>
        {navigation.slice(7).map((item) => (
          <NavigationItem key={item.name} item={item} pathname={pathname} />
        ))}
      </div>

      {/* Enhanced Quick Stats */}
      <div className="pt-6 mt-6 border-t border-gray-200">
        <div className="px-3 py-2">
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
            📊 Quick Stats
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Active Fields</span>
              <span className="font-semibold text-green-600">
                {stats.activeFields}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Health Score</span>
              <div className="flex items-center space-x-1">
                <div
                  className={`w-2 h-2 rounded-full ${
                    stats.healthScore >= 90
                      ? "bg-green-500"
                      : stats.healthScore >= 70
                        ? "bg-yellow-500"
                        : "bg-red-500"
                  }`}
                ></div>
                <span
                  className={`font-semibold ${
                    stats.healthScore >= 90
                      ? "text-green-600"
                      : stats.healthScore >= 70
                        ? "text-yellow-600"
                        : "text-red-600"
                  }`}
                >
                  {Math.round(stats.healthScore)}%
                </span>
              </div>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Alerts</span>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                <span className="font-semibold text-yellow-600">
                  {stats.alerts}
                </span>
              </div>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Analyses Today</span>
              <div className="flex items-center space-x-1">
                {stats.isAnalyzing && (
                  <div className="w-2 h-2 border border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                )}
                <span className="font-semibold text-blue-600">
                  {stats.analysesToday}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Analysis Activity */}
      {stats.recentAnalyses.length > 0 && (
        <div className="pt-4 mt-4 border-t border-gray-200">
          <div className="px-3 py-2">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center">
              <ClockIcon className="w-3 h-3 mr-1" />
              Recent Activity
            </div>
            <div className="space-y-2">
              {stats.recentAnalyses.slice(0, 3).map((analysis) => (
                <div
                  key={analysis.id}
                  className="flex items-center justify-between text-xs"
                >
                  <div className="flex items-center space-x-2">
                    {analysis.status === "completed" && (
                      <CheckCircleIcon className="w-3 h-3 text-green-500" />
                    )}
                    {analysis.status === "processing" && (
                      <div className="w-3 h-3 border border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                    )}
                    {analysis.status === "failed" && (
                      <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                    )}
                    <span className="text-gray-600 truncate">
                      {analysis.cropType}
                    </span>
                  </div>
                  <span className="text-gray-400">
                    {new Date(analysis.timestamp).toLocaleTimeString("en-US", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}

function NavigationItem({
  item,
  pathname,
  isAnalyzing = false,
}: {
  item: (typeof navigation)[0];
  pathname: string;
  isAnalyzing?: boolean;
}) {
  const isActive =
    pathname === item.href ||
    (item.href !== "/" && pathname.startsWith(item.href));

  return (
    <Link
      href={item.href}
      className={`
        group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 mb-1 relative
        ${
          isActive
            ? "bg-primary-100 text-primary-800 border-r-2 border-primary-600 shadow-sm"
            : "text-gray-600 hover:bg-gray-100 hover:text-gray-900 hover:shadow-sm"
        }
      `}
    >
      <item.icon
        className={`
          flex-shrink-0 w-5 h-5 mr-3 transition-colors duration-200
          ${isActive ? "text-primary-600" : "text-gray-400 group-hover:text-gray-600"}
          ${isAnalyzing ? "animate-pulse" : ""}
        `}
      />
      <span className="flex-1">{item.name}</span>

      {/* Analysis in progress indicator */}
      {isAnalyzing && (
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse mr-2"></div>
      )}

      {item.badge && (
        <span
          className={`
            ml-2 px-2 py-0.5 text-xs font-medium rounded-full transition-all duration-200
            ${
              item.badge === "AI"
                ? "bg-purple-100 text-purple-800"
                : item.badge === "New"
                  ? "bg-green-100 text-green-800 animate-pulse"
                  : "bg-primary-100 text-primary-800"
            }
          `}
        >
          {item.badge}
        </span>
      )}

      {isActive && (
        <div className="absolute left-0 w-1 h-8 bg-primary-600 rounded-r-full"></div>
      )}
    </Link>
  );
}

// Add default export for maximum compatibility
export default Navigation;
