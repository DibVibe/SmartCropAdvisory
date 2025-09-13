"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import Button from "@/components/ui/Button";
import toast from "react-hot-toast";

export default function IrrigationControls() {
  const [selectedField, setSelectedField] = useState("field-1");
  const queryClient = useQueryClient();

  const startIrrigationMutation = useMutation({
    mutationFn: async (fieldId: string) => {
      const response = await apiClient.post(
        `/irrigation/fields/${fieldId}/start/`
      );
      return response.data;
    },
    onSuccess: () => {
      toast.success("Irrigation started successfully");
      queryClient.invalidateQueries(["irrigation-dashboard"]);
    },
    onError: () => {
      toast.error("Failed to start irrigation");
    },
  });

  const stopIrrigationMutation = useMutation({
    mutationFn: async (fieldId: string) => {
      const response = await apiClient.post(
        `/irrigation/fields/${fieldId}/stop/`
      );
      return response.data;
    },
    onSuccess: () => {
      toast.success("Irrigation stopped successfully");
      queryClient.invalidateQueries(["irrigation-dashboard"]);
    },
    onError: () => {
      toast.error("Failed to stop irrigation");
    },
  });

  const fields = [
    { id: "field-1", name: "Field A - Wheat", status: "idle", moisture: 68 },
    { id: "field-2", name: "Field B - Rice", status: "active", moisture: 82 },
    { id: "field-3", name: "Field C - Cotton", status: "idle", moisture: 45 },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "text-green-600 bg-green-50";
      case "scheduled":
        return "text-yellow-600 bg-yellow-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getMoistureColor = (moisture: number) => {
    if (moisture > 70) return "text-green-600";
    if (moisture > 50) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Manual Controls
      </h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Field
          </label>
          <select
            value={selectedField}
            onChange={(e) => setSelectedField(e.target.value)}
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            {fields.map((field) => (
              <option key={field.id} value={field.id}>
                {field.name}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-3">
          {fields.map((field) => (
            <div
              key={field.id}
              className="flex items-center justify-between p-3 border rounded-lg"
            >
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="text-sm font-medium text-gray-900">
                    {field.name}
                  </h4>
                  <span
                    className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${getStatusColor(
                      field.status
                    )}`}
                  >
                    {field.status}
                  </span>
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <span>Soil Moisture: </span>
                  <span
                    className={`font-medium ml-1 ${getMoistureColor(
                      field.moisture
                    )}`}
                  >
                    {field.moisture}%
                  </span>
                </div>
              </div>

              <div className="flex space-x-2 ml-4">
                {field.status === "idle" ? (
                  <Button
                    size="sm"
                    onClick={() => startIrrigationMutation.mutate(field.id)}
                    isLoading={startIrrigationMutation.isLoading}
                    disabled={field.moisture > 80}
                  >
                    Start
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={() => stopIrrigationMutation.mutate(field.id)}
                    isLoading={stopIrrigationMutation.isLoading}
                  >
                    Stop
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="pt-4 border-t">
          <h3 className="text-sm font-medium text-gray-900 mb-3">
            Quick Actions
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <Button variant="outline" size="sm">
              Emergency Stop All
            </Button>
            <Button variant="outline" size="sm">
              Auto Schedule
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
