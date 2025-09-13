"use client";

import { useState } from "react";
import DashboardLayout from "@/components/layout/DashboardLayout";
import DiseaseDetector from "@/components/crops/DiseaseDetector";
import CropRecommendations from "@/components/crops/CropRecommendations";

export default function CropAnalysisPage() {
  const [activeTab, setActiveTab] = useState<"disease" | "recommendations">(
    "disease"
  );

  const tabs = [
    { id: "disease", label: "Disease Detection", icon: "🔬" },
    { id: "recommendations", label: "Crop Recommendations", icon: "🌱" },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Crop Analysis</h1>

        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                    activeTab === tab.id
                      ? "border-primary-500 text-primary-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === "disease" && <DiseaseDetector />}
            {activeTab === "recommendations" && <CropRecommendations />}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
