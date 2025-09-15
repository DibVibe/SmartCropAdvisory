"use client";

import { useState } from "react";
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
} from "@heroicons/react/24/outline";

const navigation = [
  { name: "Dashboard", href: "/", icon: HomeIcon, badge: null },
  { name: "Crop Analysis", href: "/analysis", icon: ChartBarIcon, badge: null },
  {
    name: "Disease Detection",
    href: "/analysis/disease",
    icon: BeakerIcon,
    badge: "AI",
  },
  {
    name: "Yield Prediction",
    href: "/analysis/yield",
    icon: ClipboardDocumentListIcon,
    badge: null,
  },
  { name: "Weather", href: "/weather", icon: CloudIcon, badge: null },
  { name: "Irrigation", href: "/irrigation", icon: CloudIcon, badge: null },
  { name: "Field Maps", href: "/maps", icon: MapIcon, badge: null },
  { name: "Market Analysis", href: "/market", icon: ChartBarIcon, badge: null },
  { name: "Settings", href: "/settings", icon: Cog6ToothIcon, badge: null },
  { name: "Profile", href: "/profile", icon: UserCircleIcon, badge: null },
];

export function Navigation() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();

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
        <NavigationList pathname={pathname} />
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0">
        <div className="flex flex-col flex-1 bg-white border-r border-gray-200">
          {/* Logo */}
          <div className="flex items-center px-6 py-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <span className="text-white text-xl">🌾</span>
              </div>
              <div>
                <div className="text-lg font-semibold text-gray-900">
                  SmartCrop
                </div>
                <div className="text-xs text-gray-500">Advisory</div>
              </div>
            </div>
          </div>

          <NavigationList pathname={pathname} />

          {/* Bottom section */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                U
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-900 truncate">
                  User Account
                </div>
                <div className="text-xs text-gray-500">Farmer</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile menu button */}
      <button
        onClick={() => setSidebarOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-30 p-2 bg-white rounded-lg shadow-md border border-gray-200 text-gray-600 hover:text-gray-900"
      >
        <Bars3Icon className="w-6 h-6" />
      </button>
    </>
  );
}

function NavigationList({ pathname }: { pathname: string }) {
  return (
    <nav className="flex-1 px-4 py-6 space-y-2">
      {navigation.map((item) => {
        const isActive =
          pathname === item.href ||
          (item.href !== "/" && pathname.startsWith(item.href));

        return (
          <Link
            key={item.name}
            href={item.href}
            className={`
              group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200
              ${
                isActive
                  ? "bg-primary-100 text-primary-800 border-r-2 border-primary-600"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              }
            `}
          >
            <item.icon
              className={`
                flex-shrink-0 w-5 h-5 mr-3
                ${isActive ? "text-primary-600" : "text-gray-400 group-hover:text-gray-600"}
              `}
            />
            <span className="flex-1">{item.name}</span>
            {item.badge && (
              <span className="ml-2 px-2 py-0.5 text-xs font-medium bg-primary-100 text-primary-800 rounded-full">
                {item.badge}
              </span>
            )}
          </Link>
        );
      })}

      {/* Quick Stats in Navigation */}
      <div className="pt-6 mt-6 border-t border-gray-200">
        <div className="px-3 py-2">
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
            Quick Stats
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Active Fields</span>
              <span className="font-semibold text-green-600">42</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Health Score</span>
              <span className="font-semibold text-green-600">94%</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Alerts</span>
              <span className="font-semibold text-yellow-600">3</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

// Add default export for maximum compatibility
export default Navigation;
