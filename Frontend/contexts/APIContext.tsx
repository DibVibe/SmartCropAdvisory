"use client";

import React, { createContext, useContext } from "react";
import api from "@/lib/api/api";

// Types
export interface WeatherData {
  temperature: number;
  feels_like?: number;
  condition: string;
  humidity: number;
  pressure: number;
  wind_speed: number;
  wind_direction?: number;
  visibility?: number;
  uv_index?: number;
  location?: string;
  timestamp: string;
}

export interface WeatherForecast {
  date: string;
  condition: string;
  max_temp: number;
  min_temp: number;
  humidity: number;
  precipitation: number;
  wind_speed: number;
}

export interface CropData {
  id: string;
  name: string;
  variety: string;
  planting_date: string;
  expected_harvest: string;
  growth_stage: string;
  health_status: "healthy" | "disease" | "pest" | "stress";
  field_id: string;
  area: number;
  yield_prediction?: number;
  last_inspection?: string;
}

export interface Alert {
  id: string;
  type: "weather" | "disease" | "pest" | "irrigation" | "harvest" | "market";
  severity: "low" | "medium" | "high" | "critical";
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  action_required: boolean;
  crop_id?: string;
  field_id?: string;
}

export interface MarketData {
  commodity: string;
  current_price: number;
  price_change: number;
  price_trend: "up" | "down" | "stable";
  market_id: string;
  last_updated: string;
}

export interface IrrigationData {
  field_id: string;
  next_irrigation: string;
  water_requirement: number;
  soil_moisture: number;
  irrigation_method: string;
  status: "scheduled" | "active" | "completed" | "delayed";
}

export interface DashboardData {
  weather: WeatherData | null;
  crops: CropData[];
  alerts: Alert[];
  market: MarketData[] | null;
  irrigation: IrrigationData[] | null;
  lastUpdated: Date;
}

export interface SystemHealth {
  status: "healthy" | "unhealthy";
  timestamp: string;
  services: {
    database: {
      sqlite: string;
      mongodb: string;
    };
    cache: string;
    api: string;
  };
  environment: string;
  cors_enabled: boolean;
  authentication: string;
}

// Service Classes
class WeatherService {
  async getCurrentWeather(lat: number, lon: number): Promise<WeatherData> {
    // Backend router mounts WeatherAPIViewSet at /api/v1/weather/api/current/
    const response = await api.get(`/weather/api/current/?lat=${lat}&lon=${lon}`);
    return response.data;
  }

  async getForecast(
    lat: number,
    lon: number,
    days: number = 7
  ): Promise<WeatherForecast[]> {
    const response = await api.get(
      `/weather/forecast/?lat=${lat}&lon=${lon}&days=${days}`
    );
    return response.data;
  }

  async getWeatherAlerts(locationId: string): Promise<Alert[]> {
    const response = await api.get(
      `/weather/alerts/?location_id=${locationId}`
    );
    return response.data;
  }

  async getAgriculturalAdvisory(
    cropId: string,
    growthStage: string,
    location: { lat: number; lon: number }
  ): Promise<any> {
    const response = await api.post("/weather/agricultural-advisory/", {
      crop_id: cropId,
      growth_stage: growthStage,
      location,
    });
    return response.data;
  }
}

class CropService {
  async getUserCrops(): Promise<CropData[]> {
    const response = await api.get("/crop/user-crops/");
    return response.data;
  }

  async detectDisease(imageFile: File): Promise<any> {
    const formData = new FormData();
    formData.append("image", imageFile);

    const response = await api.post("/crop/disease/detect/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  }

  async predictYield(
    fieldId: string,
    cropId: string,
    season: string
  ): Promise<any> {
    const response = await api.post("/crop/yield/predict/", {
      field_id: fieldId,
      crop_id: cropId,
      season,
    });
    return response.data;
  }

  async getCropRecommendation(
    soilData: any,
    location: { lat: number; lon: number },
    season: string
  ): Promise<any> {
    const response = await api.post("/crop/recommend/", {
      soil_data: soilData,
      location,
      season,
    });
    return response.data;
  }

  async getAnalysisHistory(
    fieldId?: string,
    days: number = 30
  ): Promise<any[]> {
    const params = new URLSearchParams();
    if (fieldId) params.append("field_id", fieldId);
    params.append("days", days.toString());

    const response = await api.get(`/crop/analysis/history/?${params}`);
    return response.data;
  }

  async analyzeSoil(soilData: {
    npk: number[];
    ph: number;
    moisture: number;
    organic_carbon: number;
  }): Promise<any> {
    const response = await api.post("/crop/soil/analyze/", soilData);
    return response.data;
  }

  async identifyPest(imageFile: File): Promise<any> {
    const formData = new FormData();
    formData.append("image", imageFile);

    const response = await api.post("/crop/pest/identify/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  }
}

class IrrigationService {
  async getScheduleStatus(): Promise<IrrigationData[]> {
    const response = await api.get("/irrigation/schedule/status/");
    return response.data;
  }

  async createSchedule(
    fieldId: string,
    method: string,
    frequency: string
  ): Promise<any> {
    const response = await api.post("/irrigation/schedule/create/", {
      field_id: fieldId,
      method,
      frequency,
    });
    return response.data;
  }

  async optimizeSchedule(fieldId: string): Promise<any> {
    const response = await api.get(
      `/irrigation/schedule/optimize/?field_id=${fieldId}`
    );
    return response.data;
  }

  async recordMoisture(
    fieldId: string,
    moistureLevel: number,
    depth: number
  ): Promise<any> {
    const response = await api.post("/irrigation/moisture/record/", {
      field_id: fieldId,
      moisture_level: moistureLevel,
      depth,
    });
    return response.data;
  }

  async getMoistureHistory(fieldId: string, days: number = 30): Promise<any[]> {
    const response = await api.get(
      `/irrigation/moisture/history/?field_id=${fieldId}&days=${days}`
    );
    return response.data;
  }

  async calculateWaterRequirement(
    cropId: string,
    area: number,
    growthStage: string
  ): Promise<any> {
    const response = await api.post("/irrigation/water-requirement/", {
      crop_id: cropId,
      area,
      growth_stage: growthStage,
    });
    return response.data;
  }
}

class MarketService {
  async getCurrentPrices(
    commodity?: string,
    marketId?: string
  ): Promise<MarketData[]> {
    const params = new URLSearchParams();
    if (commodity) params.append("commodity", commodity);
    if (marketId) params.append("market_id", marketId);

    const response = await api.get(`/market/prices/current/?${params}`);
    return response.data;
  }

  async predictPrices(
    commodity: string,
    daysAhead: number,
    marketId: string
  ): Promise<any> {
    const response = await api.post("/market/prices/predict/", {
      commodity,
      days_ahead: daysAhead,
      market_id: marketId,
    });
    return response.data;
  }

  async getMarketTrends(
    commodity: string,
    period: string = "monthly"
  ): Promise<any> {
    const response = await api.get(
      `/market/trends/?commodity=${commodity}&period=${period}`
    );
    return response.data;
  }

  async forecastDemand(
    commodity: string,
    region: string,
    timeframe: string
  ): Promise<any> {
    const response = await api.post("/market/demand/forecast/", {
      commodity,
      region,
      timeframe,
    });
    return response.data;
  }

  async findNearbyMarkets(
    lat: number,
    lon: number,
    radius: number = 50
  ): Promise<any[]> {
    const response = await api.get(
      `/market/nearby/?lat=${lat}&lon=${lon}&radius=${radius}`
    );
    return response.data;
  }

  async calculateProfit(
    crop: string,
    quantity: number,
    marketId: string
  ): Promise<any> {
    const response = await api.post("/market/profit/calculate/", {
      crop,
      quantity,
      market_id: marketId,
    });
    return response.data;
  }
}

class AdvisoryService {
  async getRecentAlerts(limit: number = 10): Promise<Alert[]> {
    const response = await api.get(`/advisory/alerts/recent/?limit=${limit}`);
    return response.data;
  }

  async getPersonalizedAdvice(
    userPreferences: any,
    currentConditions: any
  ): Promise<any> {
    const response = await api.post("/advisory/personalized/", {
      user_preferences: userPreferences,
      current_conditions: currentConditions,
    });
    return response.data;
  }

  async getDailyTips(): Promise<any[]> {
    const response = await api.get("/advisory/tips/daily/");
    return response.data;
  }

  async consultExpert(
    query: string,
    category: string,
    urgency: string
  ): Promise<any> {
    const response = await api.post("/advisory/expert/consult/", {
      query,
      category,
      urgency,
    });
    return response.data;
  }

  async getBestPractices(crop: string, stage: string): Promise<any[]> {
    const response = await api.get(
      `/advisory/best-practices/?crop=${crop}&stage=${stage}`
    );
    return response.data;
  }

  async markAlertAsRead(alertId: string): Promise<void> {
    await api.patch(`/advisory/alerts/${alertId}/read/`);
  }
}

class SystemService {
  async getHealthCheck(): Promise<SystemHealth> {
    const response = await api.get("/health/");
    return response.data;
  }

  async getSystemStatus(): Promise<any> {
    // System status is outside v1: /api/status/
    const base = process.env.NEXT_PUBLIC_API_BASE_URL || "";
    const root = base.replace("/api/v1", "");
    const response = await axios.get(`${root}/api/status/`);
    return response.data;
  }

  async getAPIInfo(): Promise<any> {
    const response = await api.get("/info/");
    return response.data;
  }

  async getUsageAnalytics(): Promise<any> {
    const response = await api.get("/analytics/usage/");
    return response.data;
  }
}

class UserService {
  async getProfile(): Promise<any> {
    const response = await api.get("/users/profile/");
    return response.data;
  }

  async updateProfile(data: any): Promise<any> {
    const response = await api.patch("/users/profile/", data);
    return response.data;
  }

  async getFarms(): Promise<any[]> {
    const response = await api.get("/users/farms/");
    return response.data;
  }

  async createFarm(farmData: any): Promise<any> {
    const response = await api.post("/users/farms/", farmData);
    return response.data;
  }

  async addField(farmId: string, fieldData: any): Promise<any> {
    const response = await api.post(
      `/users/farms/${farmId}/fields/`,
      fieldData
    );
    return response.data;
  }

  async getDashboard(farmId?: string): Promise<any> {
    const params = farmId ? `?farm_id=${farmId}` : "";
    const response = await api.get(`/users/dashboard/${params}`);
    return response.data;
  }

  async recordExpense(
    category: string,
    amount: number,
    description: string
  ): Promise<any> {
    const response = await api.post("/users/expenses/", {
      category,
      amount,
      description,
    });
    return response.data;
  }
}

// API Context Type
interface APIContextType {
  weatherService: WeatherService;
  cropService: CropService;
  irrigationService: IrrigationService;
  marketService: MarketService;
  advisoryService: AdvisoryService;
  systemService: SystemService;
  userService: UserService;
}

// Create Context
const APIContext = createContext<APIContextType | undefined>(undefined);

export const useAPI = () => {
  const context = useContext(APIContext);
  if (context === undefined) {
    throw new Error("useAPI must be used within an APIProvider");
  }
  return context;
};

export const APIProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const value: APIContextType = {
    weatherService: new WeatherService(),
    cropService: new CropService(),
    irrigationService: new IrrigationService(),
    marketService: new MarketService(),
    advisoryService: new AdvisoryService(),
    systemService: new SystemService(),
    userService: new UserService(),
  };

  return <APIContext.Provider value={value}>{children}</APIContext.Provider>;
};
