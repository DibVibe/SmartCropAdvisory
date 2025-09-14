// Custom hooks for SmartCropAdvisory
export { useWeather, type WeatherData, type UseWeatherOptions } from './useWeather'
export { useCropData, type CropData, type CropField, type UseCropDataOptions } from './useCropData'

// Additional hooks to be implemented
export const useAuth = () => ({ user: null, isAuthenticated: false, login: () => {}, logout: () => {} });
export const useMarketData = () => ({ data: null, loading: true, error: null });
export const useAnalysis = () => ({ data: null, loading: true, error: null });
