"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
type User = {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile?: {
    farm_name?: string;
    location?: string;
    phone_number?: string;
    farm_size?: number;
    crops?: string[];
  };
  is_active: boolean;
  date_joined: string;
  last_login?: string;
};
import {
  UserIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  ChevronDownIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  PhoneIcon,
  EnvelopeIcon,
  PencilIcon,
  ChartBarIcon,
  DocumentTextIcon,
  QuestionMarkCircleIcon,
} from "@heroicons/react/24/outline";

interface UserMenuProps {
  user: User;
  onLogout: () => Promise<void>;
}

export function UserMenu({ user, onLogout }: UserMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        setIsOpen(false);
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen]);

  // Handle logout
  const handleLogout = async () => {
    try {
      setIsLoggingOut(true);
      await onLogout();
      setIsOpen(false);
      router.push("/login");
    } catch (error) {
      console.error("Logout failed:", error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  // Get user initials for avatar
  const getUserInitials = () => {
    if (user.first_name && user.last_name) {
      return `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`.toUpperCase();
    } else if (user.username) {
      return user.username.charAt(0).toUpperCase();
    }
    return "U";
  };

  // Get user display name
  const getDisplayName = () => {
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    } else if (user.first_name) {
      return user.first_name;
    }
    return user.username;
  };

  // Menu items configuration
  const menuItems = [
    {
      label: "Profile Settings",
      icon: UserIcon,
      href: "/profile",
      description: "Manage your account and preferences",
    },
    {
      label: "Farm Management",
      icon: BuildingOfficeIcon,
      href: "/farms",
      description: "Manage your farms and fields",
    },
    {
      label: "Analytics & Reports",
      icon: ChartBarIcon,
      href: "/reports",
      description: "View detailed farm analytics",
    },
    {
      label: "Documentation",
      icon: DocumentTextIcon,
      href: "/docs",
      description: "Learn about features and best practices",
    },
    {
      label: "Settings",
      icon: Cog6ToothIcon,
      href: "/settings",
      description: "App settings and configurations",
    },
    {
      label: "Help & Support",
      icon: QuestionMarkCircleIcon,
      href: "/support",
      description: "Get help and contact support",
    },
  ];

  return (
    <div className="relative" ref={menuRef}>
      {/* User Menu Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        {/* User Avatar */}
        <div className="relative">
          <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center text-white text-sm font-semibold shadow-sm">
            {getUserInitials()}
          </div>
          {/* Online status indicator */}
          <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 border-2 border-white rounded-full"></div>
        </div>

        {/* User Info */}
        <div className="hidden sm:block text-left">
          <div className="text-sm font-medium text-gray-900 truncate max-w-32">
            {getDisplayName()}
          </div>
          <div className="text-xs text-gray-600 truncate max-w-32">
            {user.profile?.farm_name || user.email}
          </div>
        </div>

        {/* Chevron */}
        <ChevronDownIcon
          className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-200 z-50 overflow-hidden">
          {/* User Profile Header */}
          <div className="px-4 py-4 bg-gradient-to-r from-green-50 to-blue-50 border-b border-gray-200">
            <div className="flex items-start space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center text-white font-semibold text-lg shadow-sm">
                {getUserInitials()}
              </div>

              <div className="flex-1 min-w-0">
                <h3 className="text-base font-semibold text-gray-900 truncate">
                  {getDisplayName()}
                </h3>
                <p className="text-sm text-gray-600 truncate">
                  @{user.username}
                </p>

                {/* User Details */}
                <div className="mt-2 space-y-1">
                  {user.email && (
                    <div className="flex items-center text-xs text-gray-600">
                      <EnvelopeIcon className="w-3 h-3 mr-1.5" />
                      <span className="truncate">{user.email}</span>
                    </div>
                  )}

                  {user.profile?.farm_name && (
                    <div className="flex items-center text-xs text-gray-600">
                      <BuildingOfficeIcon className="w-3 h-3 mr-1.5" />
                      <span className="truncate">{user.profile.farm_name}</span>
                    </div>
                  )}

                  {user.profile?.location && (
                    <div className="flex items-center text-xs text-gray-600">
                      <MapPinIcon className="w-3 h-3 mr-1.5" />
                      <span className="truncate">{user.profile.location}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            {(user.profile?.farm_size || user.profile?.crops?.length) && (
              <div className="mt-3 pt-3 border-t border-green-100">
                <div className="flex justify-between text-xs text-gray-600">
                  {user.profile.farm_size && (
                    <div>
                      <span className="font-medium text-gray-700">
                        {user.profile.farm_size} hectares
                      </span>
                      <div>Farm Size</div>
                    </div>
                  )}
                  {user.profile.crops?.length && (
                    <div className="text-right">
                      <span className="font-medium text-gray-700">
                        {user.profile.crops.length} crops
                      </span>
                      <div>Active Crops</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Menu Items */}
          <div className="py-2">
            {menuItems.map((item, index) => {
              const Icon = item.icon;
              return (
                <Link
                  key={index}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className="block px-4 py-3 hover:bg-gray-50 transition-colors group"
                >
                  <div className="flex items-start space-x-3">
                    <Icon className="w-5 h-5 text-gray-500 group-hover:text-green-600 mt-0.5 transition-colors" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-gray-900 group-hover:text-green-700">
                        {item.label}
                      </div>
                      <div className="text-xs text-gray-600 mt-0.5">
                        {item.description}
                      </div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>

          {/* Account Actions */}
          <div className="border-t border-gray-200 py-2">
            <Link
              href="/profile/edit"
              onClick={() => setIsOpen(false)}
              className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors group"
            >
              <PencilIcon className="w-4 h-4 mr-3 text-gray-500 group-hover:text-blue-600 transition-colors" />
              Edit Profile
            </Link>

            <button
              onClick={handleLogout}
              disabled={isLoggingOut}
              className={`w-full flex items-center px-4 py-2 text-sm transition-colors group ${
                isLoggingOut
                  ? "text-gray-400 cursor-not-allowed"
                  : "text-red-700 hover:bg-red-50 hover:text-red-800"
              }`}
            >
              <ArrowRightOnRectangleIcon
                className={`w-4 h-4 mr-3 transition-colors ${
                  isLoggingOut
                    ? "text-gray-400"
                    : "text-red-500 group-hover:text-red-600"
                }`}
              />
              {isLoggingOut ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-gray-400 mr-2"></div>
                  Signing out...
                </div>
              ) : (
                "Sign Out"
              )}
            </button>
          </div>

          {/* Footer */}
          <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>
                Last login: {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'N/A'}
              </span>
              <span className="flex items-center">
                <span className="w-2 h-2 bg-green-400 rounded-full mr-1"></span>
                Online
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
