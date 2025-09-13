'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '../lib1/hooks/useAuth'

export default function HomePage() {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">🌾</span>
              <span className="text-xl font-bold text-primary-600">
                SmartCrop
              </span>
              <span className="text-xl font-light text-gray-600">Advisory</span>
            </div>

            <div className="flex items-center space-x-4">
              <Link
                href="/login"
                className="text-gray-600 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="bg-primary-600 text-white hover:bg-primary-700 px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <div className="mb-8">
              <span className="text-6xl mb-6 block">🌱</span>
              <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
                Smart Farming with
                <span className="text-primary-600 block">
                  AI-Powered Insights
                </span>
              </h1>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8 leading-relaxed">
                Revolutionize your farming with intelligent crop
                recommendations, disease detection, weather predictions, and
                irrigation management. Make data-driven decisions for better
                yields.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Link
                href="/register"
                className="bg-primary-600 text-white hover:bg-primary-700 px-8 py-4 rounded-lg text-lg font-medium transition-all transform hover:scale-105 shadow-lg"
              >
                Start Free Trial
              </Link>
              <Link
                href="/login"
                className="bg-white text-primary-600 hover:bg-gray-50 border-2 border-primary-600 px-8 py-4 rounded-lg text-lg font-medium transition-all transform hover:scale-105 shadow-lg"
              >
                Sign In
              </Link>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-20">
            {[
              {
                icon: '🔬',
                title: 'Disease Detection',
                description:
                  'AI-powered image analysis to identify plant diseases early and suggest treatments',
              },
              {
                icon: '🌾',
                title: 'Crop Recommendations',
                description:
                  'Get personalized crop suggestions based on soil conditions and climate data',
              },
              {
                icon: '💧',
                title: 'Smart Irrigation',
                description:
                  'Optimize water usage with intelligent irrigation scheduling and monitoring',
              },
              {
                icon: '🌤️',
                title: 'Weather Insights',
                description:
                  'Real-time weather data and forecasts to plan your farming activities',
              },
              {
                icon: '📈',
                title: 'Market Analysis',
                description:
                  'Stay updated with crop prices and market trends for better profitability',
              },
              {
                icon: '📊',
                title: 'Yield Prediction',
                description:
                  'Predict harvest outcomes using machine learning and historical data',
              },
              {
                icon: '💡',
                title: 'Expert Advisory',
                description:
                  'Connect with agricultural experts for personalized farming advice',
              },
              {
                icon: '📱',
                title: 'Mobile Ready',
                description:
                  'Access all features on-the-go with our responsive mobile interface',
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>

          {/* Stats Section */}
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-20">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Trusted by Thousands of Farmers
              </h2>
              <p className="text-gray-600">Join the agricultural revolution</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              {[
                { number: '10,000+', label: 'Active Farmers' },
                { number: '50,000+', label: 'Fields Monitored' },
                { number: '95%', label: 'Accuracy Rate' },
                { number: '30%', label: 'Yield Increase' },
              ].map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl font-bold text-primary-600 mb-2">
                    {stat.number}
                  </div>
                  <div className="text-gray-600">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* How It Works */}
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-gray-600 mb-12">
              Get started in three simple steps
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  step: '1',
                  title: 'Create Account',
                  description: 'Sign up and add your field information',
                },
                {
                  step: '2',
                  title: 'Input Data',
                  description: 'Provide soil conditions and crop preferences',
                },
                {
                  step: '3',
                  title: 'Get Insights',
                  description:
                    'Receive AI-powered recommendations and monitoring',
                },
              ].map((step, index) => (
                <div key={index} className="relative">
                  <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                    <span className="text-primary-600 font-bold text-xl">
                      {step.step}
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {step.title}
                  </h3>
                  <p className="text-gray-600">{step.description}</p>

                  {index < 2 && (
                    <div className="hidden md:block absolute top-8 left-full w-full">
                      <div className="border-t-2 border-dashed border-primary-300"></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* CTA Section */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-12 text-center text-white">
            <h2 className="text-3xl font-bold mb-4">
              Ready to Transform Your Farming?
            </h2>
            <p className="text-primary-100 text-lg mb-8 max-w-2xl mx-auto">
              Join thousands of farmers who are already using SmartCrop Advisory
              to increase their yields and optimize their operations.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/register"
                className="bg-white text-primary-600 hover:bg-gray-100 px-8 py-4 rounded-lg text-lg font-medium transition-all transform hover:scale-105"
              >
                Start Your Free Trial
              </Link>
              <Link
                href="/demo"
                className="border-2 border-white text-white hover:bg-white hover:text-primary-600 px-8 py-4 rounded-lg text-lg font-medium transition-all transform hover:scale-105"
              >
                Request Demo
              </Link>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <span className="text-2xl">🌾</span>
                <span className="text-xl font-bold">SmartCrop Advisory</span>
              </div>
              <p className="text-gray-400">
                Empowering farmers with AI-driven agricultural solutions for
                sustainable farming.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Features</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Disease Detection</li>
                <li>Crop Recommendations</li>
                <li>Weather Monitoring</li>
                <li>Market Analysis</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Help Center</li>
                <li>Documentation</li>
                <li>Contact Us</li>
                <li>Community</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4">Connect</h3>
              <ul className="space-y-2 text-gray-400">
                <li>Twitter</li>
                <li>LinkedIn</li>
                <li>YouTube</li>
                <li>Blog</li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 mt-8 text-center text-gray-400">
            <p>&copy; 2024 SmartCrop Advisory. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
