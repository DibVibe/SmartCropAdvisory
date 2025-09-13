"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useCropStore } from "@/lib/store/cropStore";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { formatCurrency } from "@/lib/utils";

const soilDataSchema = z.object({
  pH: z.number().min(0).max(14),
  nitrogen: z.number().min(0),
  phosphorus: z.number().min(0),
  potassium: z.number().min(0),
  organic_matter: z.number().min(0).max(100),
  moisture: z.number().min(0).max(100),
  temperature: z.number(),
  location: z.string().min(1, "Location is required"),
  season: z.enum(["kharif", "rabi", "summer"]),
});

type SoilDataForm = z.infer<typeof soilDataSchema>;

export default function CropRecommendations() {
  const { recommendations, getRecommendations, isLoading } = useCropStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SoilDataForm>({
    resolver: zodResolver(soilDataSchema),
    defaultValues: {
      season: "kharif",
    },
  });

  const onSubmit = async (data: SoilDataForm) => {
    try {
      await getRecommendations(data);
    } catch (error) {
      console.error("Failed to get recommendations:", error);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "text-green-600 bg-green-50";
    if (confidence >= 60) return "text-yellow-600 bg-yellow-50";
    return "text-red-600 bg-red-50";
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Get Crop Recommendations</h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Input
              label="pH Level"
              type="number"
              step="0.1"
              {...register("pH", { valueAsNumber: true })}
              error={errors.pH?.message}
            />

            <Input
              label="Nitrogen (N) mg/kg"
              type="number"
              {...register("nitrogen", { valueAsNumber: true })}
              error={errors.nitrogen?.message}
            />

            <Input
              label="Phosphorus (P) mg/kg"
              type="number"
              {...register("phosphorus", { valueAsNumber: true })}
              error={errors.phosphorus?.message}
            />

            <Input
              label="Potassium (K) mg/kg"
              type="number"
              {...register("potassium", { valueAsNumber: true })}
              error={errors.potassium?.message}
            />

            <Input
              label="Organic Matter (%)"
              type="number"
              step="0.1"
              {...register("organic_matter", { valueAsNumber: true })}
              error={errors.organic_matter?.message}
            />

            <Input
              label="Soil Moisture (%)"
              type="number"
              step="0.1"
              {...register("moisture", { valueAsNumber: true })}
              error={errors.moisture?.message}
            />

            <Input
              label="Temperature (°C)"
              type="number"
              {...register("temperature", { valueAsNumber: true })}
              error={errors.temperature?.message}
            />

            <Input
              label="Location"
              {...register("location")}
              error={errors.location?.message}
              placeholder="e.g., Punjab, India"
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Season
              </label>
              <select
                {...register("season")}
                className="block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              >
                <option value="kharif">Kharif (Monsoon)</option>
                <option value="rabi">Rabi (Winter)</option>
                <option value="summer">Summer</option>
              </select>
            </div>
          </div>

          <Button
            type="submit"
            isLoading={isLoading}
            className="w-full md:w-auto"
          >
            Get Recommendations
          </Button>
        </form>
      </div>

      {recommendations.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-4">Recommended Crops</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendations.map((crop, index) => (
              <div
                key={index}
                className="border rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <h4 className="text-lg font-medium text-gray-900">
                    {crop.cropName}
                  </h4>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(
                      crop.confidence
                    )}`}
                  >
                    {crop.confidence}% match
                  </span>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Season:</span>
                    <span className="font-medium capitalize">
                      {crop.season}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-gray-600">Expected Yield:</span>
                    <span className="font-medium">
                      {crop.expectedYield} tons/acre
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-gray-600">Profitability:</span>
                    <span className="font-medium text-green-600">
                      {formatCurrency(crop.profitability)}/acre
                    </span>
                  </div>
                </div>

                {crop.reasons && crop.reasons.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-700 mb-1">
                      Why this crop:
                    </p>
                    <ul className="text-xs text-gray-600 space-y-1">
                      {crop.reasons.map((reason, i) => (
                        <li key={i} className="flex items-start">
                          <span className="text-primary-500 mr-1">•</span>
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
