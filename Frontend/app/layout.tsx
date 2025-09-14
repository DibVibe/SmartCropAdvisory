import './globals.css'
import type { Metadata } from 'next'
import { Inter, Poppins } from 'next/font/google'
import { Providers } from './providers'
import { Navigation } from '@/components/Navigation'
import { ToasterProvider } from '@/components/Common/ToasterProvider'
import { LoadingProvider } from '@/components/Common/LoadingProvider'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const poppins = Poppins({ 
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-poppins',
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    template: '%s | SmartCropAdvisory',
    default: 'SmartCropAdvisory - AI-Powered Agricultural Intelligence System',
  },
  description: 'Advanced agricultural intelligence system powered by AI and machine learning. Get crop analysis, weather insights, yield predictions, and smart farming recommendations.',
  keywords: [
    'agriculture',
    'farming',
    'AI',
    'crop analysis',
    'weather forecasting',
    'yield prediction',
    'smart farming',
    'agricultural technology',
    'machine learning',
    'crop disease detection',
    'irrigation advisory',
    'market analysis'
  ],
  authors: [{ name: 'SmartCropAdvisory Team' }],
  creator: 'SmartCropAdvisory',
  publisher: 'SmartCropAdvisory',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
  openGraph: {
    type: 'website',
    siteName: 'SmartCropAdvisory',
    title: 'SmartCropAdvisory - AI-Powered Agricultural Intelligence',
    description: 'Advanced agricultural intelligence system powered by AI and machine learning.',
    images: [{
      url: '/og-image.png',
      width: 1200,
      height: 630,
      alt: 'SmartCropAdvisory - AI-Powered Agricultural Intelligence',
    }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SmartCropAdvisory - AI-Powered Agricultural Intelligence',
    description: 'Advanced agricultural intelligence system powered by AI and machine learning.',
    images: ['/og-image.png'],
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#22c55e' },
    { media: '(prefers-color-scheme: dark)', color: '#15803d' },
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html 
      lang="en" 
      className={`${inter.variable} ${poppins.variable}`}
      suppressHydrationWarning
    >
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="dns-prefetch" href="//api.openweathermap.org" />
        <link rel="dns-prefetch" href="//maps.googleapis.com" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="SmartCropAdvisory" />
      </head>
      <body 
        className="min-h-screen bg-gray-50 font-sans antialiased"
        suppressHydrationWarning
      >
        <Providers>
          <LoadingProvider>
            <div className="flex min-h-screen">
              {/* Navigation Sidebar */}
              <Navigation />
              
              {/* Main Content Area */}
              <main className="flex-1 lg:ml-64 flex flex-col overflow-hidden">
                {/* Top Navigation Bar */}
                <header className="bg-white shadow-sm border-b border-gray-200 z-10">
                  <div className="container-fluid py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <h1 className="text-2xl font-bold text-gray-900 text-display">
                          🌾 SmartCropAdvisory
                        </h1>
                        <div className="hidden sm:block">
                          <span className="badge badge-primary">
                            AI-Powered Agricultural Intelligence
                          </span>
                        </div>
                      </div>
                      
                      {/* User Profile & Settings */}
                      <div className="flex items-center space-x-4">
                        <div className="hidden md:flex items-center space-x-2 text-sm text-gray-600">
                          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                          <span>System Online</span>
                        </div>
                        
                        {/* Weather Quick View */}
                        <div className="hidden lg:flex items-center space-x-2 px-3 py-1 bg-agricultural-sky bg-opacity-20 rounded-full">
                          <span className="text-agricultural-sky">☀️</span>
                          <span className="text-sm font-medium">25°C</span>
                        </div>
                        
                        {/* Notifications */}
                        <button className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM7 7h5l-5-5v5z" />
                          </svg>
                          <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full text-xs text-white flex items-center justify-center">3</span>
                        </button>
                        
                        {/* User Menu */}
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                            U
                          </div>
                          <span className="hidden sm:block text-sm font-medium text-gray-700">User</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </header>
                
                {/* Page Content */}
                <div className="flex-1 overflow-auto">
                  <div className="container-fluid section-spacing">
                    {children}
                  </div>
                </div>
                
                {/* Footer */}
                <footer className="bg-white border-t border-gray-200 py-6 no-print">
                  <div className="container-fluid">
                    <div className="flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0">
                      <div className="flex items-center space-x-4">
                        <p className="text-sm text-gray-600">
                          © 2025 SmartCropAdvisory. All rights reserved.
                        </p>
                        <div className="flex items-center space-x-2">
                          <span className="w-2 h-2 bg-green-400 rounded-full"></span>
                          <span className="text-xs text-gray-500">API Connected</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-6 text-sm text-gray-600">
                        <a href="#" className="hover:text-primary-600 transition-colors">Privacy Policy</a>
                        <a href="#" className="hover:text-primary-600 transition-colors">Terms of Service</a>
                        <a href="#" className="hover:text-primary-600 transition-colors">Support</a>
                        <a href="#" className="hover:text-primary-600 transition-colors">API Docs</a>
                      </div>
                    </div>
                  </div>
                </footer>
              </main>
            </div>
            
            {/* Toast Notifications */}
            <ToasterProvider />
          </LoadingProvider>
        </Providers>
      </body>
    </html>
  )
}
