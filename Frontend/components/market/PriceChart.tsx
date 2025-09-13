"use client";

import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function PriceChart() {
  const [selectedCrop, setSelectedCrop] = useState("wheat");
  const [timeRange, setTimeRange] = useState("30d");

  const priceData = {
    wheat: [
      { date: "2024-01-01", price: 2150, volume: 1200 },
      { date: "2024-01-15", price: 2180, volume: 1350 },
      { date: "2024-02-01", price: 2200, volume: 1100 },
      { date: "2024-02-15", price: 2250, volume: 1400 },
      { date: "2024-03-01", price: 2300, volume: 1250 },
      { date: "2024-03-15", price: 2280, volume: 1300 },
    ],
    rice: [
      { date: "2024-01-01", price: 3200, volume: 800 },
      { date: "2024-01-15", price: 3250, volume: 900 },
      { date: "2024-02-01", price: 3300, volume: 750 },
      { date: "2024-02-15", price: 3350, volume: 850 },
      { date: "2024-03-01", price: 3400, volume: 800 },
      { date: "2024-03-15", price: 3380, volume: 820 },
    ],
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Price Trends</h2>
        <div className="flex space-x-3">
          <select
            value={selectedCrop}
            onChange={(e) => setSelectedCrop(e.target.value)}
            className="rounded-md border border-gray-300 px-3 py-1 text-sm"
          >
            <option value="wheat">Wheat</option>
            <option value="rice">Rice</option>
            <option value="corn">Corn</option>
          </select>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="rounded-md border border-gray-300 px-3 py-1 text-sm"
          >
            <option value="7d">7 Days</option>
            <option value="30d">30 Days</option>
            <option value="90d">90 Days</option>
            <option value="1y">1 Year</option>
          </select>
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={priceData[selectedCrop as keyof typeof priceData]}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} axisLine={false} />
            <YAxis tick={{ fontSize: 12 }} axisLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #e5e7eb",
                borderRadius: "8px",
                boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
              }}
              formatter={(value: any, name: string) => [
                name === "price" ? `₹${value}/quintal` : `${value} quintals`,
                name === "price" ? "Price" : "Volume",
              ]}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#22c55e"
              strokeWidth={3}
              dot={{ fill: "#22c55e", strokeWidth: 2, r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-4 pt-4 border-t">
        <div className="text-center">
          <p className="text-sm text-gray-600">Current Price</p>
          <p className="text-lg font-semibold text-gray-900">₹2,280</p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600">Change (24h)</p>
          <p className="text-lg font-semibold text-green-600">+₹20 (+0.9%)</p>
        </div>
        <div className="text-center">
          <p className="text-sm text-gray-600">Volume</p>
          <p className="text-lg font-semibold text-gray-900">1,300 Q</p>
        </div>
      </div>
    </div>
  );
}
