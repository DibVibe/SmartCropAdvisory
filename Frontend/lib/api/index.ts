// API Client
export {
  default as apiClient,
  TokenManager,
  testConnection,
  testCORS,
  testAuth,
  getAPIStatus,
  healthCheck,
} from "./client";

// Default export for the main API instance
export { default } from "./client";

// API Services
export * from "./cropApi";
export * from "./weatherApi";
export * from "./marketApi";
export * from "./userApi";
export * from "./advisoryApi";

// Re-export for convenience
export { cropApi } from "./cropApi";
export { weatherApi } from "./weatherApi";
export { marketApi } from "./marketApi";
export { userApi } from "./userApi";
export { advisoryApi } from "./advisoryApi";
