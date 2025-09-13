"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface SoilMoistureChartProps {
  data?: any[];
}

export default function SoilMoistureChart({ data }: SoilMoistureChartProps) {
  const mockData = [
    { time: "00:00", fieldA: 65, fieldB: 78, fieldC: 45 },
    { time: "04:00", fieldA: 62, fieldB: 75, fieldC: 42 },
    { time: "08:00", fieldA: 68, fieldB: 82, fieldC: 48 },
    { time: "12:00", fieldA: 64, fieldB: 79, fieldC: 44 },
    { time: "16:00", fieldA: 61, fieldB: 76, fieldC: 41 },
    { time: "20:00", fieldA: 67, fieldB: 81, fieldC: 47 },
  ];

  const chartData = data || mockData;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Soil Moisture Levels
      </h2>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis dataKey="time" tick={{ fontSize: 12 }} axisLine={false} />
            <YAxis tick={{ fontSize: 12 }} axisLine={false} domain={[0, 100]} />
            <Tooltip
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #e5e7eb",
                borderRadius: "8px",
                boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
              }}
            />
            <Line
              type="monotone"
              dataKey="fieldA"
              stroke="#22c55e"
              strokeWidth={2}
              name="Field A - Wheat"
              dot={{ fill: "#22c55e", strokeWidth: 2, r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="fieldB"
              stroke="#3b82f6"
              strokeWidth={2}
              name="Field B - Rice"
              dot={{ fill: "#3b82f6", strokeWidth: 2, r: 4 }}
            />
            <Line
              type="monotone"
              dataKey="fieldC"
              stroke="#f59e0b"
              strokeWidth={2}
              name="Field C - Cotton"
              dot={{ fill: "#f59e0b", strokeWidth: 2, r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="flex justify-center space-x-6 mt-4 text-sm">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
          <span>Field A - Wheat</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
          <span>Field B - Rice</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
          <span>Field C - Cotton</span>
        </div>
      </div>
    </div>
  );
}
