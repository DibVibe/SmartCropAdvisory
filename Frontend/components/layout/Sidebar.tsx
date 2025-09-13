'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '../../lib1/utils'
import { useAuth } from '../../lib1/hooks/useAuth'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: '🏠' },
  { name: 'Fields', href: '/fields', icon: '🌾' },
  { name: 'Crop Analysis', href: '/crop-analysis', icon: '🔬' },
  { name: 'Weather', href: '/weather', icon: '🌤️' },
  { name: 'Irrigation', href: '/irrigation', icon: '💧' },
  { name: 'Market', href: '/market', icon: '📈' },
  { name: 'Advisory', href: '/advisory', icon: '💡' },
  { name: 'Reports', href: '/reports', icon: '📊' },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  return (
    <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg lg:block hidden">
      <div className="flex h-16 items-center justify-center border-b border-gray-200">
        <h1 className="text-xl font-bold text-primary-600">SmartCrop</h1>
      </div>

      <nav className="mt-8 px-4 space-y-1">
        {navigation.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors',
              pathname === item.href
                ? 'bg-primary-100 text-primary-900'
                : 'text-gray-700 hover:bg-gray-50'
            )}
          >
            <span className="mr-3 text-lg">{item.icon}</span>
            {item.name}
          </Link>
        ))}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
            <span className="text-white font-medium">
              {user?.username?.[0]?.toUpperCase()}
            </span>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">
              {user?.username}
            </p>
            <p className="text-xs text-gray-500 capitalize">
              {user?.profile?.userType}
            </p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full text-left text-sm text-gray-500 hover:text-gray-700"
        >
          Sign out
        </button>
      </div>
    </div>
  )
}
