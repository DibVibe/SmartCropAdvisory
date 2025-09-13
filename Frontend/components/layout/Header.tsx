'use client'

import { useState } from 'react'
import { useAuth } from '../../lib/hooks/useAuth'
import Button from '@/components/ui/Button'

export default function Header() {
  const [showMobileMenu, setShowMobileMenu] = useState(false)
  const { user, logout } = useAuth()

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Mobile menu button */}
        <button
          className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500"
          onClick={() => setShowMobileMenu(!showMobileMenu)}
        >
          <svg
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>

        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="hidden md:block">
            <div className="relative">
              <input
                type="text"
                placeholder="Search..."
                className="block w-80 rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder-gray-500 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
          </div>

          {/* Notifications */}
          <button className="p-2 text-gray-400 hover:text-gray-500">
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 17h5l-5 5v-5zM10.586 17H7a3 3 0 01-3-3V5a3 3 0 013-3h8a3 3 0 013 3v4"
              />
            </svg>
          </button>

          {/* Profile dropdown */}
          <div className="relative">
            <button className="flex items-center space-x-3 text-sm focus:outline-none">
              <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                <span className="text-white font-medium">
                  {user?.username?.[0]?.toUpperCase()}
                </span>
              </div>
              <span className="hidden lg:block font-medium text-gray-900">
                {user?.username}
              </span>
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
