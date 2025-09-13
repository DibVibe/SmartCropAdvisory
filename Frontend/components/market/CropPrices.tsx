"use client";

import { formatCurrency } from "@/lib/utils";

export default function CropPrices() {
  const crops = [
    { name: "Wheat", price: 2280, change: 0.9, volume: "1.3K quintals" },
    { name: "Rice", price: 3380, change: -0.6, volume: "820 quintals" },
    { name: "Cotton", price: 5650, change: 2.3, volume: "650 quintals" },
    { name: "Sugarcane", price: 340, change: 1.5, volume: "2.1K quintals" },
    { name: "Soybean", price: 4200, change: -1.2, volume: "950 quintals" },
    { name: "Maize", price: 1850, change: 0.7, volume: "1.1K quintals" },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Today's Prices
      </h2>

      <div className="space-y-4">
        {crops.map((crop, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
          >
            <div>
              <h4 className="font-medium text-gray-900">{crop.name}</h4>
              <p className="text-xs text-gray-600">{crop.volume}</p>
            </div>

            <div className="text-right">
              <p className="font-semibold text-gray-900">
                {formatCurrency(crop.price)}/quintal
              </p>
              <div
                className={`text-sm ${
                  crop.change >= 0 ? "text-green-600" : "text-red-600"
                }`}
              >
                {crop.change >= 0 ? "↗" : "↘"} {Math.abs(crop.change)}%
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t">
        <div className="text-center">
          <p className="text-sm text-gray-600 mb-2">Market Status</p>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            🟢 Market Open
          </span>
        </div>
      </div>
    </div>
  );
}
