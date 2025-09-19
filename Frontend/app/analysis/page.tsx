"use client";

import { useState, useEffect } from "react";
import { CropAnalysisForm } from "@/components/forms/CropAnalysisForm";
import {
  PhotoIcon,
  ChartBarIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";

// Safe Date Component to prevent hydration errors
interface SafeDateProps {
  date: string | Date;
  type?: "date" | "datetime";
  className?: string;
}

function SafeDate({ date, type = "date", className }: SafeDateProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <span className={className} suppressHydrationWarning>
        --
      </span>
    );
  }

  try {
    const dateObj = typeof date === "string" ? new Date(date) : date;

    if (type === "datetime") {
      return (
        <span className={className}>
          {dateObj.toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      );
    }

    return (
      <span className={className}>
        {dateObj.toLocaleDateString("en-GB", {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
        })}
      </span>
    );
  } catch (error) {
    return <span className={className}>Invalid Date</span>;
  }
}

interface AnalysisResult {
  success: boolean;
  data?: {
    crop_health: string;
    recommendations: string[];
    confidence: number;
    analysis_type: string;
    crop_type: string;
    image_stats?: {
      avg_green_intensity: number;
      avg_brightness: number;
      dimensions: string;
    };
    timestamp: string;
  };
  message?: string;
}

export default function CropAnalysisPage() {
  const [activeTab, setActiveTab] = useState("analysis");
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult | null>(
    null
  );
  const [analysisHistory, setAnalysisHistory] = useState<AnalysisResult[]>([]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const tabs = [
    { id: "analysis", name: "Crop Analysis", icon: PhotoIcon },
    { id: "history", name: "Analysis History", icon: ClockIcon },
    { id: "reports", name: "Reports", icon: DocumentTextIcon },
    { id: "insights", name: "AI Insights", icon: ChartBarIcon },
  ];

  const handleAnalysisComplete = (result: AnalysisResult) => {
    console.log("📊 Analysis completed:", result);
    setAnalysisResults(result);

    // Add to history if successful
    if (result.success && result.data) {
      setAnalysisHistory((prev) => [result, ...prev.slice(0, 9)]); // Keep last 10
    }
  };

  const getHealthStatusColor = (health: string) => {
    switch (health.toLowerCase()) {
      case "healthy":
        return "text-green-700 bg-green-100 border-green-200";
      case "moderate":
        return "text-yellow-700 bg-yellow-100 border-yellow-200";
      case "needs attention":
        return "text-red-700 bg-red-100 border-red-200";
      default:
        return "text-gray-700 bg-gray-100 border-gray-200";
    }
  };

  const recentAnalyses = [
    {
      id: 1,
      cropType: "Wheat",
      date: "2024-01-10",
      status: "Healthy",
      confidence: 94,
      issues: 0,
      statusColor: "text-green-600 bg-green-100",
    },
    {
      id: 2,
      cropType: "Corn",
      date: "2024-01-09",
      status: "Warning",
      confidence: 87,
      issues: 2,
      statusColor: "text-yellow-600 bg-yellow-100",
    },
    {
      id: 3,
      cropType: "Rice",
      date: "2024-01-08",
      status: "Critical",
      confidence: 91,
      issues: 1,
      statusColor: "text-red-600 bg-red-100",
    },
  ];

  const aiInsights = [
    {
      title: "Crop Health Trends",
      description:
        "Your wheat crops show 15% improvement in health scores over the past month.",
      type: "positive",
    },
    {
      title: "Nutrient Analysis",
      description:
        "Nitrogen levels are optimal, but phosphorus shows signs of deficiency in Field A.",
      type: "warning",
    },
    {
      title: "Growth Stage Prediction",
      description:
        "Based on current conditions, harvest is predicted for mid-March.",
      type: "info",
    },
  ];

  // Show loading state until mounted
  if (!mounted) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
            >
              <div className="h-16 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between space-y-4 lg:space-y-0">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Crop Analysis</h1>
            <p className="text-gray-600 mt-2">
              Upload crop images for AI-powered analysis and get detailed
              insights about crop health, growth stages, and recommendations.
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 text-green-800 px-4 py-2 rounded-lg text-sm font-medium">
              🤖 AI Analysis Ready
            </div>
            <div className="text-sm text-gray-500">
              Last updated: <SafeDate date={new Date()} />
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Total Analyses
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {analysisHistory.length + 1247}
              </p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <ChartBarIcon className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">
              +{analysisHistory.length} today
            </span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Healthy Crops</p>
              <p className="text-2xl font-bold text-gray-900">89%</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">
              +5% improvement
            </span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Issues Detected
              </p>
              <p className="text-2xl font-bold text-gray-900">23</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-red-600 text-sm font-medium">
              +3 new issues
            </span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">
                Avg Confidence
              </p>
              <p className="text-2xl font-bold text-gray-900">92%</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <PhotoIcon className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4">
            <span className="text-green-600 text-sm font-medium">
              High accuracy
            </span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${
                    activeTab === tab.id
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }
                `}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === "analysis" && (
            <div className="space-y-6">
              <CropAnalysisForm onAnalysisComplete={handleAnalysisComplete} />

              {/* Analysis Results Display */}
              {analysisResults && (
                <div className="mt-8">
                  {analysisResults.success && analysisResults.data ? (
                    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold text-gray-900">
                          🌾 Analysis Results
                        </h3>
                        <div className="text-sm text-gray-500">
                          <SafeDate
                            date={analysisResults.data.timestamp}
                            type="datetime"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Health Status */}
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Crop Health Status
                            </label>
                            <div
                              className={`inline-flex px-4 py-2 rounded-lg border text-sm font-medium ${getHealthStatusColor(analysisResults.data.crop_health)}`}
                            >
                              {analysisResults.data.crop_health}
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Confidence Score
                            </label>
                            <div className="flex items-center space-x-3">
                              <div className="flex-1 bg-gray-200 rounded-full h-3">
                                <div
                                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                                  style={{
                                    width: `${analysisResults.data.confidence * 100}%`,
                                  }}
                                ></div>
                              </div>
                              <span className="text-sm font-medium text-gray-900">
                                {(
                                  analysisResults.data.confidence * 100
                                ).toFixed(1)}
                                %
                              </span>
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Crop Type
                            </label>
                            <p className="text-gray-900 font-medium capitalize">
                              {analysisResults.data.crop_type}
                            </p>
                          </div>

                          {analysisResults.data.image_stats && (
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Image Statistics
                              </label>
                              <div className="text-sm text-gray-600 space-y-1">
                                <p>
                                  Dimensions:{" "}
                                  {analysisResults.data.image_stats.dimensions}
                                </p>
                                <p>
                                  Green Intensity:{" "}
                                  {
                                    analysisResults.data.image_stats
                                      .avg_green_intensity
                                  }
                                </p>
                                <p>
                                  Brightness:{" "}
                                  {
                                    analysisResults.data.image_stats
                                      .avg_brightness
                                  }
                                </p>
                              </div>
                            </div>
                          )}
                        </div>

                        {/* Recommendations */}
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-3">
                            AI Recommendations
                          </label>
                          <div className="space-y-3">
                            {analysisResults.data.recommendations.map(
                              (recommendation, index) => (
                                <div
                                  key={index}
                                  className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg border border-blue-200"
                                >
                                  <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 text-sm font-semibold">
                                    {index + 1}
                                  </div>
                                  <p className="text-sm text-blue-900">
                                    {recommendation}
                                  </p>
                                </div>
                              )
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="mt-6 pt-6 border-t border-gray-200 flex flex-wrap gap-3">
                        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                          Save Results
                        </button>
                        <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                          Generate Report
                        </button>
                        <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                          Share Analysis
                        </button>
                        <button
                          onClick={() => setAnalysisResults(null)}
                          className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          Clear Results
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="mt-8 p-6 bg-red-50 border border-red-200 rounded-xl">
                      <h3 className="text-lg font-semibold text-red-800 mb-2">
                        ❌ Analysis Failed
                      </h3>
                      <p className="text-red-700">
                        {analysisResults.message ||
                          "An error occurred during analysis. Please try again."}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Placeholder when no results */}
              {!analysisResults && (
                <div className="mt-8 p-8 bg-gray-50 rounded-xl text-center">
                  <PhotoIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Ready for Analysis
                  </h3>
                  <p className="text-gray-600">
                    Upload a crop image above to get detailed AI-powered
                    analysis and recommendations.
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === "history" && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">
                  Analysis History
                </h3>
                <div className="text-sm text-gray-500">
                  {analysisHistory.length + recentAnalyses.length} total
                  analyses
                </div>
              </div>

              <div className="space-y-4">
                {/* Recent analyses from current session */}
                {analysisHistory.map((analysis, index) => (
                  <div
                    key={`current-${index}`}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow bg-blue-50 border-blue-200"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-blue-200 rounded-lg flex items-center justify-center">
                          <PhotoIcon className="h-6 w-6 text-blue-600" />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900 capitalize">
                            {analysis.data?.crop_type}
                          </h4>
                          <p className="text-sm text-gray-500">
                            <SafeDate
                              date={analysis.data?.timestamp || ""}
                              type="datetime"
                            />
                          </p>
                        </div>
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          New
                        </span>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div
                            className={`inline-flex px-3 py-1 rounded-full text-sm font-medium border ${getHealthStatusColor(analysis.data?.crop_health || "")}`}
                          >
                            {analysis.data?.crop_health}
                          </div>
                          <p className="text-sm text-gray-500 mt-1">
                            {((analysis.data?.confidence || 0) * 100).toFixed(
                              1
                            )}
                            % confidence
                          </p>
                        </div>
                        <button className="text-blue-600 hover:text-blue-800 font-medium text-sm">
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Previous analyses */}
                {recentAnalyses.map((analysis) => (
                  <div
                    key={analysis.id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                          <PhotoIcon className="h-6 w-6 text-gray-600" />
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900">
                            {analysis.cropType}
                          </h4>
                          <p className="text-sm text-gray-500">
                            Analyzed on <SafeDate date={analysis.date} />
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div
                            className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${analysis.statusColor}`}
                          >
                            {analysis.status}
                          </div>
                          <p className="text-sm text-gray-500 mt-1">
                            {analysis.confidence}% confidence
                          </p>
                        </div>
                        <button className="text-blue-600 hover:text-blue-800 font-medium text-sm">
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                ))}

                {analysisHistory.length === 0 &&
                  recentAnalyses.length === 0 && (
                    <div className="text-center py-12">
                      <ClockIcon className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-4 text-lg font-medium text-gray-900">
                        No Analysis History
                      </h3>
                      <p className="mt-2 text-gray-500">
                        Start analyzing crops to build your history.
                      </p>
                    </div>
                  )}
              </div>
            </div>
          )}

          {activeTab === "reports" && (
            <div className="text-center py-12">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">
                No Reports Available
              </h3>
              <p className="mt-2 text-gray-500">
                Reports will be generated after completing analyses.
              </p>
              {analysisHistory.length > 0 && (
                <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  Generate Report from Recent Analyses
                </button>
              )}
            </div>
          )}

          {activeTab === "insights" && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">
                AI Insights & Recommendations
              </h3>
              <div className="space-y-4">
                {aiInsights.map((insight, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex items-start space-x-3">
                      <div
                        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold
                        ${
                          insight.type === "positive"
                            ? "bg-green-100 text-green-800"
                            : insight.type === "warning"
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-blue-100 text-blue-800"
                        }`}
                      >
                        {insight.type === "positive"
                          ? "✓"
                          : insight.type === "warning"
                            ? "⚠"
                            : "i"}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">
                          {insight.title}
                        </h4>
                        <p className="text-gray-600 mt-1">
                          {insight.description}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
