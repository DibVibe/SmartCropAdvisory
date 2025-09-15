import {
  testConnection,
  testCORS,
  testAuth,
  getAPIStatus,
  healthCheck,
} from "./client";

// Re-export all testing functions
export { testConnection, testCORS, testAuth, getAPIStatus, healthCheck };

// Additional utility functions
export const isOnline = () => {
  if (typeof navigator !== "undefined") {
    return navigator.onLine;
  }
  return true;
};

export const getEnvironmentInfo = () => {
  return {
    apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL,
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
    authUrl: process.env.NEXT_PUBLIC_AUTH_URL,
    environment: process.env.NODE_ENV,
    isProduction: process.env.NODE_ENV === "production",
    isDevelopment: process.env.NODE_ENV === "development",
  };
};

export const debugApiCall = (url: string, method: string, data?: any) => {
  if (process.env.NODE_ENV === "development") {
    console.log(
      `🔄 API Call: ${method.toUpperCase()} ${url}`,
      data ? { data } : ""
    );
  }
};

// Connection status hook data
export const createConnectionMonitor = () => {
  let isChecking = false;
  let lastStatus: any = null;

  const monitor = {
    async check() {
      if (isChecking) return lastStatus;

      isChecking = true;
      try {
        const status = await getAPIStatus();
        lastStatus = { ...status, lastChecked: new Date() };
        return lastStatus;
      } finally {
        isChecking = false;
      }
    },

    getLastStatus() {
      return lastStatus;
    },
  };

  return monitor;
};
