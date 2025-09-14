export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile?: {
    farm_name?: string;
    location?: string;
    phone_number?: string;
    farm_size?: number;
    crops?: string[];
  };
  is_active: boolean;
  date_joined: string;
  last_login: string;
}

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

export interface APIResponse<T> {
  data: T;
  message?: string;
  status: "success" | "error";
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
