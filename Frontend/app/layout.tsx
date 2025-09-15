import "./globals.css";
import type { Metadata } from "next";
import { Inter, Poppins } from "next/font/google";
import { Providers } from "./providers";
import { Navigation } from "../components/Navigation";
import { ToasterProvider } from "../components/Common/ToasterProvider";
import { LoadingProvider } from "../components/Common/LoadingProvider";
import { AuthProvider } from "../contexts/AuthContext";
import { APIProvider } from "../contexts/APIContext";
import { HeaderBar } from "../components/layout/HeaderBar";
import { NotificationCenter } from "../components/notifications/NotificationCenter";
import { APIStatusIndicator } from "../components/APIStatusIndicator";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  // ✅ FIXED: Add metadataBase to fix social media warnings
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_API_BASE_URL?.replace("/api/v1", "") ||
      "http://localhost:3000"
  ),
  title: {
    template: "%s | SmartCropAdvisory",
    default: "SmartCropAdvisory - AI-Powered Agricultural Intelligence System",
  },
  description:
    "Advanced agricultural intelligence system powered by AI and machine learning. Get crop analysis, weather insights, yield predictions, and smart farming recommendations.",
  keywords: [
    "agriculture",
    "farming",
    "AI",
    "crop analysis",
    "weather forecasting",
    "yield prediction",
    "smart farming",
    "agricultural technology",
    "machine learning",
    "crop disease detection",
    "irrigation advisory",
    "market analysis",
    "JWT authentication",
    "Django API",
    "MongoDB",
    "Redis cache",
  ],
  authors: [{ name: "SmartCropAdvisory Team" }],
  creator: "SmartCropAdvisory",
  publisher: "SmartCropAdvisory",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon-16x16.png",
    apple: "/apple-touch-icon.png",
  },
  manifest: "/site.webmanifest",
  openGraph: {
    type: "website",
    siteName: "SmartCropAdvisory",
    title: "SmartCropAdvisory - AI-Powered Agricultural Intelligence",
    description:
      "Advanced agricultural intelligence system powered by AI and machine learning with Django API backend.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "SmartCropAdvisory - AI-Powered Agricultural Intelligence",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "SmartCropAdvisory - AI-Powered Agricultural Intelligence",
    description:
      "Advanced agricultural intelligence system powered by AI and machine learning with Django API backend.",
    images: ["/og-image.png"],
  },
  // ✅ REMOVED: viewport and themeColor moved to viewport.ts
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${poppins.variable}`}
      suppressHydrationWarning
    >
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          rel="dns-prefetch"
          href={process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}
        />
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
          <AuthProvider>
            <APIProvider>
              <LoadingProvider>
                <div className="flex min-h-screen">
                  {/* Navigation Sidebar */}
                  <Navigation />

                  {/* Main Content Area */}
                  <main className="flex-1 lg:ml-64 flex flex-col overflow-hidden">
                    {/* Dynamic Header Bar */}
                    <HeaderBar />

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
                            <APIStatusIndicator />
                          </div>

                          <div className="flex items-center space-x-6 text-sm text-gray-600">
                            <a
                              href="/privacy"
                              className="hover:text-primary-600 transition-colors"
                            >
                              Privacy Policy
                            </a>
                            <a
                              href="/terms"
                              className="hover:text-primary-600 transition-colors"
                            >
                              Terms of Service
                            </a>
                            <a
                              href="/support"
                              className="hover:text-primary-600 transition-colors"
                            >
                              Support
                            </a>
                            <a
                              href={`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/docs/`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="hover:text-primary-600 transition-colors"
                            >
                              API Docs
                            </a>
                          </div>
                        </div>
                      </div>
                    </footer>
                  </main>

                  {/* Notification Center */}
                  <NotificationCenter />
                </div>

                {/* Toast Notifications */}
                <ToasterProvider />
              </LoadingProvider>
            </APIProvider>
          </AuthProvider>
        </Providers>
      </body>
    </html>
  );
}
