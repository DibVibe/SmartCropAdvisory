import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from "axios";

// ==========================================
// 🔧 CONFIGURATION & TYPES
// ==========================================

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000/api/v1";

const AUTH_URL =
  process.env.NEXT_PUBLIC_AUTH_URL ||
  `${API_BASE_URL.replace("/api/v1", "")}/api/v1/users`;

// ==========================================
// 🛡️ TOKEN MANAGER CLASS
// ==========================================

export class TokenManager {
  private static readonly ACCESS_TOKEN_KEY = "auth_token"; // Keep your existing key
  private static readonly REFRESH_TOKEN_KEY = "refresh_token"; // Keep your existing key

  static getAccessToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem(this.ACCESS_TOKEN_KEY);
    }
    return null;
  }

  static getRefreshToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem(this.REFRESH_TOKEN_KEY);
    }
    return null;
  }

  static setTokens(access: string, refresh?: string): void {
    if (typeof window !== "undefined") {
      localStorage.setItem(this.ACCESS_TOKEN_KEY, access);
      if (refresh) {
        localStorage.setItem(this.REFRESH_TOKEN_KEY, refresh);
      }
    }
  }

  static clearTokens(): void {
    if (typeof window !== "undefined") {
      localStorage.removeItem(this.ACCESS_TOKEN_KEY);
      localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    }
  }

  static isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return Date.now() >= payload.exp * 1000;
    } catch {
      return true;
    }
  }
}

// ==========================================
// 🔥 ENHANCED AXIOS CLIENT
// ==========================================

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Increased timeout
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// ==========================================
// 🔄 ENHANCED REQUEST INTERCEPTOR
// ==========================================

apiClient.interceptors.request.use(
  (config) => {
    const token = TokenManager.getAccessToken();

    if (token && !TokenManager.isTokenExpired(token)) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add request metadata for debugging
    if (process.env.NODE_ENV === "development") {
      config.metadata = { startTime: new Date() };
    }

    return config;
  },
  (error) => {
    console.error("📤 Request Error:", error);
    return Promise.reject(error);
  }
);

// ==========================================
// 🔄 ENHANCED RESPONSE INTERCEPTOR WITH TOKEN REFRESH
// ==========================================

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (error?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });

  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => {
    // Log response time in development
    if (
      process.env.NODE_ENV === "development" &&
      response.config.metadata?.startTime
    ) {
      const endTime = new Date();
      const duration =
        endTime.getTime() - response.config.metadata.startTime.getTime();
      console.log(
        `📥 ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`
      );
    }

    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & {
      _retry?: boolean;
    };

    // Handle 401 errors with token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return apiClient(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = TokenManager.getRefreshToken();

        if (!refreshToken) {
          throw new Error("No refresh token available");
        }

        const response = await axios.post(`${AUTH_URL}/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        TokenManager.setTokens(access);

        processQueue(null, access);

        // Retry original request
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access}`;
        }
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        TokenManager.clearTokens();

        // Redirect to login only if we're in the browser
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }

        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Enhanced error logging
    console.error("📥 API Error:", {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });

    return Promise.reject(error);
  }
);

// ==========================================
// 🧪 CONNECTION TESTING FUNCTIONS
// ==========================================

export const testConnection = async (): Promise<boolean> => {
  try {
    // Test your Django API root endpoint
    const response = await axios.get(`${API_BASE_URL}/`, {
      timeout: 5000,
      headers: { Accept: "application/json" },
    });

    console.log("✅ Backend connected:", response.data);
    return true;
  } catch (error) {
    console.error("❌ Backend connection failed:", error);
    return false;
  }
};

export const testCORS = async (): Promise<boolean> => {
  try {
    // Test the CORS endpoint from your Django URLs
    const corsUrl = `${API_BASE_URL.replace("/api/v1", "")}/api/test/cors/`;
    const response = await axios.get(corsUrl, {
      timeout: 5000,
      headers: { Accept: "application/json" },
    });

    console.log("✅ CORS working:", response.data);
    return true;
  } catch (error) {
    console.error("❌ CORS test failed:", error);
    return false;
  }
};

export const testAuth = async (): Promise<boolean> => {
  try {
    const token = TokenManager.getAccessToken();
    if (!token) {
      console.log("ℹ️ No auth token available");
      return false;
    }

    // Test an authenticated endpoint
    const response = await apiClient.get("/users/profiles/");
    console.log("✅ Auth working:", !!response.data);
    return true;
  } catch (error) {
    console.error("❌ Auth test failed:", error);
    return false;
  }
};

export const getAPIStatus = async () => {
  console.log("🔍 Testing API connections...");

  const results = await Promise.allSettled([
    testConnection(),
    testCORS(),
    testAuth(),
  ]);

  const status = {
    connection: results[0].status === "fulfilled" ? results[0].value : false,
    cors: results[1].status === "fulfilled" ? results[1].value : false,
    auth: results[2].status === "fulfilled" ? results[2].value : false,
    overall: results
      .slice(0, 2)
      .every(
        (result) => result.status === "fulfilled" && result.value === true
      ),
  };

  console.log("📊 API Status:", status);
  return status;
};

// Quick health check function
export const healthCheck = async () => {
  try {
    const response = await axios.get(
      `${API_BASE_URL.replace("/api/v1", "")}/api/health/`,
      {
        timeout: 10000,
      }
    );
    return {
      healthy: true,
      data: response.data,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    return {
      healthy: false,
      error: error instanceof Error ? error.message : "Unknown error",
      timestamp: new Date().toISOString(),
    };
  }
};

export default apiClient;
