"use client";

import { useState, useRef } from "react";
import { useAuth } from "@/contexts/AuthContext";
import {
  PhotoIcon,
  CloudArrowUpIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";

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

interface CropAnalysisFormProps {
  onAnalysisComplete: (result: AnalysisResult) => void;
}

export function CropAnalysisForm({
  onAnalysisComplete,
}: CropAnalysisFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [cropType, setCropType] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { user } = useAuth();

  const cropTypes = [
    { value: "wheat", label: "🌾 Wheat" },
    { value: "corn", label: "🌽 Corn" },
    { value: "rice", label: "🌾 Rice" },
    { value: "soybean", label: "🌱 Soybean" },
    { value: "cotton", label: "🌿 Cotton" },
    { value: "tomato", label: "🍅 Tomato" },
    { value: "potato", label: "🥔 Potato" },
    { value: "other", label: "🌿 Other" },
  ];

  const handleFileSelect = (file: File) => {
    if (file && file.type.startsWith("image/")) {
      setSelectedFile(file);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setError("Please select a valid image file");
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedFile) {
      setError("Please select an image file");
      return;
    }

    if (!cropType) {
      setError("Please select a crop type");
      return;
    }

    if (!user) {
      setError("Please log in to perform analysis");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log("🚀 Starting analysis...", {
        file: selectedFile.name,
        cropType,
        fileSize: selectedFile.size,
      });

      const formData = new FormData();
      formData.append("image", selectedFile);
      formData.append("crop_type", cropType);

      const token = localStorage.getItem("authToken");
      if (!token) {
        throw new Error("Authentication token not found");
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/crop-analysis/analyze/`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      console.log("📡 Response status:", response.status);

      const result = await response.json();
      console.log("📊 Analysis result:", result);

      if (response.ok && result.success) {
        onAnalysisComplete(result);
        // Reset form
        setSelectedFile(null);
        setPreviewUrl(null);
        setCropType("");
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
      } else {
        const errorMessage =
          result.message ||
          result.error ||
          `Analysis failed (${response.status})`;
        setError(errorMessage);
        onAnalysisComplete({ success: false, message: errorMessage });
      }
    } catch (err) {
      console.error("❌ Analysis error:", err);
      const errorMessage =
        err instanceof Error ? err.message : "Network error occurred";
      setError(errorMessage);
      onAnalysisComplete({ success: false, message: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* File Upload Area */}
      <div className="space-y-4">
        <label className="block text-sm font-medium text-gray-700">
          Upload Crop Image
        </label>

        <div
          className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
            dragOver
              ? "border-blue-400 bg-blue-50"
              : selectedFile
                ? "border-green-300 bg-green-50"
                : "border-gray-300 hover:border-gray-400"
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          {previewUrl ? (
            <div className="space-y-4">
              <div className="relative inline-block">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="max-w-xs max-h-48 rounded-lg shadow-md mx-auto"
                />
                <button
                  type="button"
                  onClick={clearSelection}
                  className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600"
                >
                  ×
                </button>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {selectedFile?.name}
                </p>
                <p className="text-xs text-gray-500">
                  {selectedFile
                    ? `${(selectedFile.size / 1024 / 1024).toFixed(2)} MB`
                    : ""}
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
              <div>
                <p className="text-gray-600">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="font-medium text-blue-600 hover:text-blue-500"
                  >
                    Click to upload
                  </button>{" "}
                  or drag and drop
                </p>
                <p className="text-xs text-gray-500">
                  PNG, JPG, GIF up to 10MB
                </p>
              </div>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileInputChange}
            className="hidden"
          />
        </div>
      </div>

      {/* Crop Type Selection */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Crop Type
        </label>
        <select
          value={cropType}
          onChange={(e) => setCropType(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
          required
        >
          <option value="">Select crop type...</option>
          {cropTypes.map((crop) => (
            <option key={crop.value} value={crop.value}>
              {crop.label}
            </option>
          ))}
        </select>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <ExclamationTriangleIcon className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-800">Analysis Error</p>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading || !selectedFile || !cropType}
          className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
            loading || !selectedFile || !cropType
              ? "bg-gray-300 text-gray-500 cursor-not-allowed"
              : "bg-blue-600 text-white hover:bg-blue-700 shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
          }`}
        >
          {loading ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
              <span>Analyzing...</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <PhotoIcon className="h-5 w-5" />
              <span>Analyze Crop</span>
            </div>
          )}
        </button>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-blue-900 mb-2">
          💡 Analysis Tips
        </h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Use clear, well-lit images for better analysis accuracy</li>
          <li>• Include close-up shots of leaves and stems when possible</li>
          <li>• Avoid blurry or heavily shadowed images</li>
          <li>• Multiple angles provide more comprehensive analysis</li>
        </ul>
      </div>
    </form>
  );
}
