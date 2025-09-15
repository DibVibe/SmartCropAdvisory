import { WeatherData, CropData, Alert, MarketData, IrrigationData } from './api'
export interface DashboardStats {
  total_crops: number;
  healthy_crops: number;
  alerts_count: number;
  weather_status: string;
}

export interface DashboardData {
  weather: WeatherData | null;
  crops: CropData[];
  alerts: Alert[];
  market: MarketData[] | null;
  irrigation: IrrigationData[] | null;
  stats: DashboardStats;
  lastUpdated: Date;
}
