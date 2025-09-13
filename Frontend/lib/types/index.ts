export interface User {
  id: string
  username: string
  email: string
  firstName?: string
  lastName?: string
  profile: UserProfile
  createdAt: string
  updatedAt: string
}

export interface UserProfile {
  userType: 'farmer' | 'expert' | 'admin'
  phoneNumber: string
  farmSize?: number
  experience?: number
  specialization?: string
  location?: Location
  avatar?: string
}

export interface Location {
  latitude: number
  longitude: number
  address: string
  city: string
  state: string
  country: string
  pincode?: string
}

export interface Field {
  id: string
  name: string
  area: number
  cropType: string
  latitude: number
  longitude: number
  soilType?: string
  irrigationType?: string
  plantingDate?: string
  harvestDate?: string
  status: 'active' | 'inactive' | 'harvested'
  createdAt: string
  updatedAt: string
}

export interface CropRecommendation {
  id: string
  cropName: string
  confidence: number
  season: 'kharif' | 'rabi' | 'summer'
  expectedYield: number
  profitability: number
  waterRequirement: number
  growthPeriod: number
  reasons: string[]
  risks: string[]
  recommendations: string[]
}

export interface SoilData {
  pH: number
  nitrogen: number
  phosphorus: number
  potassium: number
  organic_matter: number
  moisture: number
  temperature: number
  location: string
  season: 'kharif' | 'rabi' | 'summer'
}

export interface DiseaseDetection {
  id: string
  disease_name: string
  confidence: number
  is_healthy: boolean
  severity?: 'low' | 'medium' | 'high'
  recommendations?: string
  treatment?: string
  preventive_measures?: string[]
  affected_area?: number
  createdAt: string
}

export interface WeatherData {
  temperature: number
  humidity: number
  precipitation: number
  windSpeed: number
  pressure: number
  uvIndex: number
  visibility: number
  condition: string
  icon: string
  location: string
  timestamp: string
  forecast: WeatherForecast[]
}

export interface WeatherForecast {
  date: string
  temperature: {
    min: number
    max: number
  }
  condition: string
  icon: string
  precipitation: number
  humidity: number
  windSpeed: number
}

export interface WeatherAlert {
  id: string
  type: 'storm' | 'rain' | 'drought' | 'frost' | 'heatwave'
  severity: 'low' | 'medium' | 'high' | 'critical'
  title: string
  description: string
  startDate: string
  endDate: string
  affectedAreas: string[]
  recommendations: string[]
}

export interface IrrigationSchedule {
  id: string
  fieldId: string
  cropType: string
  scheduleType: 'manual' | 'automatic' | 'sensor-based'
  frequency: number
  duration: number
  waterAmount: number
  nextIrrigation: string
  lastIrrigation?: string
  isActive: boolean
  conditions: {
    minSoilMoisture: number
    maxSoilMoisture: number
    temperature: {
      min: number
      max: number
    }
  }
}

export interface MarketPrice {
  id: string
  cropName: string
  variety?: string
  price: number
  unit: 'kg' | 'quintal' | 'ton'
  market: string
  date: string
  trend: 'up' | 'down' | 'stable'
  changePercent: number
  demandLevel: 'low' | 'medium' | 'high'
}

export interface Advisory {
  id: string
  title: string
  content: string
  type: 'general' | 'crop-specific' | 'weather' | 'market' | 'disease'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  targetCrops?: string[]
  targetRegions?: string[]
  validFrom: string
  validTo: string
  author: {
    name: string
    designation: string
    organization: string
  }
  attachments?: string[]
  tags: string[]
  createdAt: string
}

export interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  category: 'weather' | 'irrigation' | 'disease' | 'market' | 'system'
  isRead: boolean
  actionRequired: boolean
  actionUrl?: string
  createdAt: string
  expiresAt?: string
}

export interface Activity {
  id: string
  type: 'crop_analysis' | 'irrigation' | 'weather' | 'market' | 'field' | 'user'
  description: string
  details?: any
  userId: string
  fieldId?: string
  status: 'success' | 'warning' | 'error' | 'info'
  timestamp: string
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  success: boolean
  data: T[]
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

// Form Types
export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  firstName?: string
  lastName?: string
  profile: {
    userType: 'farmer' | 'expert' | 'admin'
    phoneNumber: string
    farmSize?: number
  }
}

export interface UpdateProfileData {
  firstName?: string
  lastName?: string
  email?: string
  profile: Partial<UserProfile>
}

// Chart/Analytics Types
export interface ChartData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    backgroundColor?: string
    borderColor?: string
    borderWidth?: number
  }[]
}

export interface YieldPrediction {
  fieldId: string
  cropType: string
  predictedYield: number
  confidence: number
  factors: {
    weather: number
    soil: number
    irrigation: number
    fertilizer: number
  }
  recommendations: string[]
  estimatedHarvestDate: string
}
