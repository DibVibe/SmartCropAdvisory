'use client';

import React from 'react';
import Link from 'next/link';
import WeatherWidget from '../components/Dashboard/WeatherWidget';
import DiseaseDetector from '../components/Analysis/DiseaseDetector';
import YieldPredictor from '../components/Analysis/YieldPredictor';
import CropRecommender from '../components/Analysis/CropRecommender';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-r from-green-600 to-emerald-600 py-20 sm:py-32">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl">
              🌾 SmartCropAdvisory
            </h1>
            <p className="mt-6 text-lg leading-8 text-green-100">
              AI-Powered Agricultural Intelligence System for modern farmers. 
              Get advanced crop disease detection, yield predictions, and smart farming recommendations.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                href="#features"
                className="rounded-md bg-white px-3.5 py-2.5 text-sm font-semibold text-green-600 shadow-sm hover:bg-green-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white transition-all duration-200"
              >
                🚀 Get Started
              </Link>
              <Link
                href="#demo"
                className="text-sm font-semibold leading-6 text-white hover:text-green-100 transition-colors duration-200"
              >
                📺 Watch Demo <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
          
          {/* Hero Stats */}
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <dl className="grid grid-cols-1 gap-x-8 gap-y-6 text-center lg:grid-cols-4">
              <div className="mx-auto flex max-w-xs flex-col gap-y-4">
                <dt className="text-base leading-7 text-green-100">Active Farmers</dt>
                <dd className="order-first text-3xl font-semibold tracking-tight text-white sm:text-5xl">
                  50K+
                </dd>
              </div>
              <div className="mx-auto flex max-w-xs flex-col gap-y-4">
                <dt className="text-base leading-7 text-green-100">Crop Analyses</dt>
                <dd className="order-first text-3xl font-semibold tracking-tight text-white sm:text-5xl">
                  1M+
                </dd>
              </div>
              <div className="mx-auto flex max-w-xs flex-col gap-y-4">
                <dt className="text-base leading-7 text-green-100">Accuracy Rate</dt>
                <dd className="order-first text-3xl font-semibold tracking-tight text-white sm:text-5xl">
                  97%
                </dd>
              </div>
              <div className="mx-auto flex max-w-xs flex-col gap-y-4">
                <dt className="text-base leading-7 text-green-100">Countries Served</dt>
                <dd className="order-first text-3xl font-semibold tracking-tight text-white sm:text-5xl">
                  28
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-base font-semibold leading-7 text-green-600">🧠 AI-Powered Features</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Everything you need for smart farming
            </p>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Leverage cutting-edge AI technology to make informed decisions about your crops, 
              from disease detection to yield optimization.
            </p>
          </div>
          
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
              <div className="flex flex-col">
                <dt className="text-base font-semibold leading-7 text-gray-900">
                  <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-lg bg-green-600">
                    <span className="text-white text-lg">🔬</span>
                  </div>
                  Crop Disease Detection
                </dt>
                <dd className="mt-1 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">
                    Upload images of your crops and get instant AI-powered disease identification 
                    with 97% accuracy. Receive treatment recommendations and prevention strategies.
                  </p>
                  <p className="mt-6">
                    <Link href="#disease-detector" className="text-sm font-semibold leading-6 text-green-600">
                      Try Disease Detection <span aria-hidden="true">→</span>
                    </Link>
                  </p>
                </dd>
              </div>
              
              <div className="flex flex-col">
                <dt className="text-base font-semibold leading-7 text-gray-900">
                  <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-lg bg-green-600">
                    <span className="text-white text-lg">📊</span>
                  </div>
                  Yield Prediction
                </dt>
                <dd className="mt-1 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">
                    Predict crop yields based on soil conditions, weather patterns, and historical data. 
                    Plan your harvests and market strategies with confidence.
                  </p>
                  <p className="mt-6">
                    <Link href="#yield-predictor" className="text-sm font-semibold leading-6 text-green-600">
                      Predict Yields <span aria-hidden="true">→</span>
                    </Link>
                  </p>
                </dd>
              </div>
              
              <div className="flex flex-col">
                <dt className="text-base font-semibold leading-7 text-gray-900">
                  <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-lg bg-green-600">
                    <span className="text-white text-lg">🌱</span>
                  </div>
                  Crop Recommendations
                </dt>
                <dd className="mt-1 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">
                    Get personalized crop suggestions based on your soil analysis, climate conditions, 
                    and market trends. Maximize profits with data-driven decisions.
                  </p>
                  <p className="mt-6">
                    <Link href="#crop-recommender" className="text-sm font-semibold leading-6 text-green-600">
                      Get Recommendations <span aria-hidden="true">→</span>
                    </Link>
                  </p>
                </dd>
              </div>
              
              <div className="flex flex-col">
                <dt className="text-base font-semibold leading-7 text-gray-900">
                  <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-lg bg-green-600">
                    <span className="text-white text-lg">🌤️</span>
                  </div>
                  Weather Integration
                </dt>
                <dd className="mt-1 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">
                    Real-time weather monitoring with agricultural insights. Get alerts for optimal 
                    planting, irrigation, and harvesting times.
                  </p>
                  <p className="mt-6">
                    <Link href="#weather-widget" className="text-sm font-semibold leading-6 text-green-600">
                      View Weather <span aria-hidden="true">→</span>
                    </Link>
                  </p>
                </dd>
              </div>
              
              <div className="flex flex-col">
                <dt className="text-base font-semibold leading-7 text-gray-900">
                  <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-lg bg-green-600">
                    <span className="text-white text-lg">💧</span>
                  </div>
                  Irrigation Advisory
                </dt>
                <dd className="mt-1 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">
                    Smart irrigation scheduling based on soil moisture, weather forecasts, and crop requirements. 
                    Optimize water usage and reduce costs.
                  </p>
                  <p className="mt-6">
                    <Link href="#irrigation" className="text-sm font-semibold leading-6 text-green-600">
                      Irrigation Guide <span aria-hidden="true">→</span>
                    </Link>
                  </p>
                </dd>
              </div>
              
              <div className="flex flex-col">
                <dt className="text-base font-semibold leading-7 text-gray-900">
                  <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-lg bg-green-600">
                    <span className="text-white text-lg">📈</span>
                  </div>
                  Market Analysis
                </dt>
                <dd className="mt-1 flex flex-auto flex-col text-base leading-7 text-gray-600">
                  <p className="flex-auto">
                    Track crop prices, market trends, and demand forecasts. Make informed decisions 
                    about what to grow and when to sell.
                  </p>
                  <p className="mt-6">
                    <Link href="#market-analysis" className="text-sm font-semibold leading-6 text-green-600">
                      Market Insights <span aria-hidden="true">→</span>
                    </Link>
                  </p>
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </section>

      {/* Live Demo Section */}
      <section id="demo" className="bg-gray-50 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center mb-16">
            <h2 className="text-base font-semibold leading-7 text-green-600">🚀 Live Demo</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Try our AI tools right now
            </p>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Experience the power of AI-driven agriculture with our interactive tools.
            </p>
          </div>

          {/* Weather Widget Demo */}
          <div id="weather-widget" className="mb-16">
            <div className="mx-auto max-w-4xl">
              <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">🌤️ Weather Intelligence</h3>
              <WeatherWidget />
            </div>
          </div>

          {/* Tabs for Different Tools */}
          <div className="mx-auto max-w-6xl">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8 justify-center" aria-label="Tabs">
                <button className="border-green-500 text-green-600 whitespace-nowrap border-b-2 py-2 px-1 text-sm font-medium">
                  🔬 Disease Detection
                </button>
                <button className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 whitespace-nowrap border-b-2 py-2 px-1 text-sm font-medium">
                  📊 Yield Prediction
                </button>
                <button className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 whitespace-nowrap border-b-2 py-2 px-1 text-sm font-medium">
                  🌱 Crop Recommendations
                </button>
              </nav>
            </div>
            
            <div className="mt-8">
              {/* Disease Detector */}
              <div id="disease-detector" className="mb-16">
                <DiseaseDetector />
              </div>
              
              {/* Yield Predictor */}
              <div id="yield-predictor" className="mb-16">
                <YieldPredictor />
              </div>
              
              {/* Crop Recommender */}
              <div id="crop-recommender" className="mb-16">
                <CropRecommender />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-base font-semibold leading-7 text-green-600">⚡ Powered By</h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Cutting-edge technology stack
            </p>
          </div>
          
          <div className="mx-auto mt-16 grid max-w-lg grid-cols-3 items-center gap-8 sm:grid-cols-6 lg:max-w-none">
            {['🤖 TensorFlow', '🐍 Django', '⚛️ React', '🔥 Redis', '🐘 PostgreSQL', '☁️ AWS'].map((tech) => (
              <div key={tech} className="col-span-1 text-center">
                <div className="text-xl font-bold text-gray-600">{tech}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative isolate overflow-hidden bg-green-600 py-24 sm:py-32">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Ready to revolutionize your farming?
            </h2>
            <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-green-100">
              Join thousands of farmers already using SmartCropAdvisory to increase yields, 
              reduce costs, and make data-driven farming decisions.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                href="#signup"
                className="rounded-md bg-white px-3.5 py-2.5 text-sm font-semibold text-green-600 shadow-sm hover:bg-green-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white transition-all duration-200"
              >
                🚀 Start Free Trial
              </Link>
              <Link
                href="#contact"
                className="text-sm font-semibold leading-6 text-white hover:text-green-100 transition-colors duration-200"
              >
                📞 Contact Sales <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
