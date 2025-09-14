'use client'

import { ReactNode } from 'react'
import { WeatherWidget } from './WeatherWidget'
import { CropStatus } from './CropStatus'
import { QuickActions } from './QuickActions'
import { RecentAlerts } from './RecentAlerts'
import { SystemStatus } from './SystemStatus'

interface DashboardProps {
  children?: ReactNode
}

export function Dashboard({ children }: DashboardProps) {
  return (
    <div className="space-y-6">
      {/* Main Dashboard Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Quick Actions */}
        <div className="lg:col-span-4">
          <QuickActions />
        </div>
        
        {/* Weather & Crop Status */}
        <div className="lg:col-span-2">
          <WeatherWidget />
        </div>
        <div className="lg:col-span-2">
          <CropStatus />
        </div>
        
        {/* System Status */}
        <div className="lg:col-span-2">
          <SystemStatus />
        </div>
        
        {/* Recent Alerts */}
        <div className="lg:col-span-2">
          <RecentAlerts />
        </div>
      </div>
      
      {/* Additional Content */}
      {children}
    </div>
  )
}
