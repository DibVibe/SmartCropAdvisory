import './Globals.css';
import Header from '../components/Common/Header';
import Footer from '../components/Common/Footer';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: {
    default: 'SmartCropAdvisory - AI-Powered Agricultural Intelligence',
    template: '%s | SmartCropAdvisory'
  },
  description: 'Advanced AI-powered agricultural platform for crop disease detection, yield prediction, weather analysis, and smart farming recommendations.',
  keywords: [
    'agriculture',
    'AI farming',
    'crop disease detection',
    'yield prediction',
    'smart farming',
    'agricultural technology',
    'precision agriculture',
    'crop management',
    'weather forecasting',
    'soil analysis'
  ],
  authors: [{ name: 'SmartCropAdvisory Team' }],
  creator: 'SmartCropAdvisory',
  publisher: 'SmartCropAdvisory',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://smartcropadvisory.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://smartcropadvisory.com',
    siteName: 'SmartCropAdvisory',
    images: [{
      url: '/images/og-image.jpg',
      width: 1200,
      height: 630,
    }],
  },
  twitter: {
    card: 'summary_large_image',
    images: ['/images/twitter-image.jpg'],
    creator: '@smartcropadvisory',
  },
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
  category: 'technology',
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" className="h-full">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#22c55e" />
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
      </head>
      <body className="h-full bg-gray-50 font-sans antialiased">
        <div className="flex min-h-full flex-col">
          <Header />
          <main className="flex-1">
            {children}
          </main>
          <Footer />
        </div>
        
        {/* Performance and Analytics Scripts */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Service Worker Registration
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', () => {
                  navigator.serviceWorker.register('/sw.js')
                    .then(registration => console.log('SW registered: ', registration))
                    .catch(registrationError => console.log('SW registration failed: ', registrationError));
                });
              }
              
              // Performance Monitoring
              window.addEventListener('load', () => {
                const perfData = performance.getEntriesByType('navigation')[0];
                console.log('Page Load Time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
              });
              
              // Error Tracking
              window.addEventListener('error', (event) => {
                console.error('Global Error:', event.error);
                // Send to error tracking service
              });
              
              window.addEventListener('unhandledrejection', (event) => {
                console.error('Unhandled Promise Rejection:', event.reason);
                // Send to error tracking service
              });
            `,
          }}
        />
      </body>
    </html>
  );
}
