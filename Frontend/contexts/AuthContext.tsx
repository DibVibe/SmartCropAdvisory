"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
} from "react";
import { useRouter } from "next/navigation";

// ==========================================
// 🔷 TYPE DEFINITIONS
// ==========================================

interface UserProfile {
  farm_name?: string;
  location?: string;
  phone_number?: string;
  farm_size?: number;
  crops?: string[];
  profile_picture?: string;
  bio?: string;
}

interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  profile?: UserProfile;
  is_active: boolean;
  date_joined: string;
  last_login?: string;
}

interface AuthResponse {
  success: boolean;
  error?: string;
  data?: any;
  message?: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  farm_details?: {
    farm_name?: string;
    location?: string;
    phone_number?: string;
    farm_size?: number;
  };
}

interface LoginResponse {
  success: boolean;
  message?: string;
  token?: string;
  user?: User;
  profile?: UserProfile;
  error?: string;
}

interface AuthContextType {
  // State
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  token: string | null;
  initialized: boolean;

  // Actions
  login: (username: string, password: string) => Promise<AuthResponse>;
  logout: () => Promise<void>;
  register: (userData: RegisterData) => Promise<AuthResponse>;
  refreshAuth: () => Promise<boolean>;
  updateProfile: (data: Partial<UserProfile>) => Promise<AuthResponse>;
  changePassword: (
    oldPassword: string,
    newPassword: string
  ) => Promise<AuthResponse>;

  // Utilities
  getAuthHeaders: () => Record<string, string>;
  isTokenValid: () => boolean;
  clearAuthData: () => void;
}

// ==========================================
// 🔷 CONTEXT CREATION
// ==========================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

// ==========================================
// 🔷 AUTH PROVIDER COMPONENT
// ==========================================

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  // State Management
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);

  // Refs to prevent unnecessary re-renders and manage state
  const initializingRef = useRef(false);
  const loginInProgressRef = useRef(false);
  const router = useRouter();

  // Constants
  const TOKEN_KEY = "authToken";
  const USER_KEY = "userData";
  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

  // ==========================================
  // 🔧 UTILITY FUNCTIONS
  // ==========================================

  const getApiUrl = (endpoint: string): string => {
    const cleanEndpoint = endpoint.startsWith("/")
      ? endpoint.slice(1)
      : endpoint;
    const finalUrl = `${API_BASE_URL}/${cleanEndpoint}`;

    console.log(`🔗 URL constructed: ${finalUrl}`);
    return finalUrl;
  };

  const getAuthHeaders = useCallback((): Record<string, string> => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "application/json",
    };

    if (token) {
      headers.Authorization = `Token ${token}`;
    }

    return headers;
  }, [token]);

  const isTokenValid = useCallback((): boolean => {
    const valid = !!token && token.length > 20;
    console.log(`🔍 Token validation: ${valid ? "✅ Valid" : "❌ Invalid"}`);
    return valid;
  }, [token]);

  // ==========================================
  // 🗄️ ENHANCED STORAGE UTILITIES
  // ==========================================

  const storeAuthData = useCallback((authToken: string, userData: User) => {
    try {
      console.log("💾 Storing auth data...");
      console.log("👤 User:", userData.username);
      console.log("🔑 Token:", authToken.substring(0, 20) + "...");

      if (typeof window !== "undefined") {
        // Store in localStorage
        localStorage.setItem(TOKEN_KEY, authToken);
        localStorage.setItem(USER_KEY, JSON.stringify(userData));

        // Verify storage immediately
        const storedToken = localStorage.getItem(TOKEN_KEY);
        const storedUser = localStorage.getItem(USER_KEY);

        if (!storedToken || !storedUser) {
          throw new Error("Failed to store auth data in localStorage");
        }

        console.log("✅ LocalStorage verification passed");
      }

      // Set state
      setToken(authToken);
      setUser(userData);

      // Verify state was set
      console.log("✅ Auth state updated successfully");
      console.log("📊 Final state:", {
        hasToken: !!authToken,
        hasUser: !!userData,
        userId: userData.id,
        username: userData.username,
      });
    } catch (error) {
      console.error("❌ Failed to store auth data:", error);
      throw error;
    }
  }, []);

  const clearAuthData = useCallback(() => {
    try {
      console.log("🗑️ Clearing auth data...");

      if (typeof window !== "undefined") {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        // Clear any legacy tokens
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        localStorage.removeItem("rememberMe");
      }

      setToken(null);
      setUser(null);

      console.log("✅ Auth data cleared successfully");
    } catch (error) {
      console.error("❌ Failed to clear auth data:", error);
    }
  }, []);

  const loadAuthData = useCallback((): { token: string; user: User } | null => {
    if (typeof window === "undefined") {
      console.log("🏠 Server-side rendering - no storage access");
      return null;
    }

    try {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      const storedUser = localStorage.getItem(USER_KEY);

      console.log("📥 Loading auth data:", {
        hasToken: !!storedToken,
        hasUser: !!storedUser,
        tokenPreview: storedToken
          ? storedToken.substring(0, 20) + "..."
          : "none",
      });

      if (storedToken && storedUser) {
        const userData = JSON.parse(storedUser);
        console.log("✅ Auth data loaded for user:", userData.username);
        return { token: storedToken, user: userData };
      }

      console.log("ℹ️ No valid auth data found in storage");
      return null;
    } catch (error) {
      console.error("❌ Failed to load auth data:", error);
      clearAuthData();
      return null;
    }
  }, [clearAuthData]);

  // ==========================================
  // 🌐 API UTILITIES
  // ==========================================

  const apiCall = async (
    endpoint: string,
    options: RequestInit = {}
  ): Promise<any> => {
    try {
      const url = getApiUrl(endpoint);
      const headers = {
        ...getAuthHeaders(),
        ...(options.headers || {}),
      };

      console.log(`🌐 API Call: ${options.method || "GET"} ${url}`);
      console.log("📋 Headers:", JSON.stringify(headers, null, 2));

      const response = await fetch(url, {
        ...options,
        headers,
      });

      console.log(`📡 Response: ${response.status} ${response.statusText}`);

      // Handle different content types
      const contentType = response.headers.get("content-type");
      let data;

      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else {
        const textResponse = await response.text();
        data = { message: textResponse, text: textResponse };
      }

      if (!response.ok) {
        // Handle different error formats
        const errorMessage =
          data.message ||
          data.error ||
          data.detail ||
          data.non_field_errors?.[0] ||
          `HTTP ${response.status}: ${response.statusText}`;

        console.log("❌ API Error Details:", {
          status: response.status,
          statusText: response.statusText,
          errorMessage,
          fullResponse: data,
        });

        throw new Error(errorMessage);
      }

      console.log("✅ API call successful");
      console.log("📊 Response data:", data);
      return data;
    } catch (error) {
      console.error("❌ API call failed:", error);
      
      // Handle network errors more gracefully
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to connect to server. Please ensure the backend is running on http://localhost:8000');
      }
      
      // Handle cases where error doesn't have expected properties
      if (error instanceof Error) {
        throw error;
      }
      
      // Fallback for unknown error types
      throw new Error('Network error occurred. Please check your connection.');
    }
  };

  // ==========================================
  // 🔐 ENHANCED AUTHENTICATION METHODS
  // ==========================================

  const login = async (
    username: string,
    password: string
  ): Promise<AuthResponse> => {
    // Prevent concurrent logins
    if (loginInProgressRef.current) {
      console.log("⏳ Login already in progress, skipping...");
      return { success: false, error: "Login already in progress" };
    }

    try {
      loginInProgressRef.current = true;
      setLoading(true);
      console.log("🔐 Starting login process for:", username);

      const response = await apiCall("users/login/", {
        method: "POST",
        body: JSON.stringify({
          username: username.trim(),
          password: password,
        }),
      });

      console.log("📥 Login response received:", {
        success: response.success,
        hasToken: !!response.token,
        hasUser: !!response.user,
        message: response.message,
      });

      if (response.success && response.token && response.user) {
        // Construct user data from response
        const userData: User = {
          ...response.user,
          profile: response.profile || response.user?.profile || undefined,
        };

        console.log("👤 User data constructed:", {
          id: userData.id,
          username: userData.username,
          email: userData.email,
          hasProfile: !!userData.profile,
        });

        // Store authentication data with error handling
        await new Promise((resolve, reject) => {
          try {
            storeAuthData(response.token, userData);
            resolve(void 0);
          } catch (error) {
            reject(error);
          }
        });

        // Small delay to ensure state is fully updated
        await new Promise((resolve) => setTimeout(resolve, 100));

        // Verify final state
        console.log("🔍 Post-login state verification:", {
          hasToken: !!token,
          hasUser: !!user,
          userMatch: user?.username === userData.username,
          tokenMatch: token === response.token,
        });

        console.log("✅ Login completed successfully for:", userData.username);

        return {
          success: true,
          data: userData,
          message: response.message || "Login successful",
        };
      } else {
        const error =
          response.message ||
          response.error ||
          "Login failed - missing required data";
        console.log("❌ Login failed:", {
          error,
          hasSuccess: response.success,
          hasToken: !!response.token,
          hasUser: !!response.user,
        });
        return { success: false, error };
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Network error occurred";
      console.error("❌ Login exception:", {
        error: errorMessage,
        type: typeof error,
        details: error,
      });
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
      loginInProgressRef.current = false;
      console.log("🔓 Login process completed");
    }
  };

  const logout = async (): Promise<void> => {
    try {
      console.log("👋 Starting logout process...");

      // Attempt server-side logout if token exists
      if (token && isTokenValid()) {
        try {
          await apiCall("users/logout/", { method: "POST" });
          console.log("✅ Server logout successful");
        } catch (error) {
          console.warn("⚠️ Server logout failed:", error);
          // Don't throw error, continue with local logout
        }
      }

      // Always clear local auth data
      clearAuthData();
      console.log("✅ Local logout completed");

      // Redirect to login page
      console.log("🔄 Redirecting to login page...");
      router.push("/login");
    } catch (error) {
      console.error("❌ Logout error:", error);
      // Still clear local data even if logout fails
      clearAuthData();
      router.push("/login");
    }
  };

  const refreshAuth = useCallback(async (): Promise<boolean> => {
    if (!token || !isTokenValid()) {
      console.log("❌ No valid token for refresh");
      return false;
    }

    try {
      console.log("🔄 Refreshing authentication...");

      const response = await apiCall("users/profile/");

      if (response.success && response.data) {
        const userData: User = {
          ...response.data,
          profile: response.data.profile || response.profile || undefined,
        };

        // Update user data
        setUser(userData);

        // Update stored user data
        if (typeof window !== "undefined") {
          localStorage.setItem(USER_KEY, JSON.stringify(userData));
        }

        console.log("✅ Auth refresh successful for:", userData.username);
        return true;
      } else {
        console.log("❌ Auth refresh failed: Invalid response");
        return false;
      }
    } catch (error) {
      console.error("❌ Auth refresh failed:", error);
      return false;
    }
  }, [token, isTokenValid]);

  const register = async (userData: RegisterData): Promise<AuthResponse> => {
    try {
      setLoading(true);
      console.log("📝 Starting registration for:", userData.username);

      const response = await apiCall("users/register/", {
        method: "POST",
        body: JSON.stringify(userData),
      });

      console.log("📥 Registration response:", response);

      if (response.success) {
        // Check if auto-login is enabled (token provided)
        if (response.token && response.user) {
          const user: User = {
            ...response.user,
            profile: response.profile || response.user?.profile || undefined,
          };

          storeAuthData(response.token, user);
          console.log("✅ Registration and auto-login successful");
        } else {
          console.log("✅ Registration successful, manual login required");
        }

        return {
          success: true,
          data: response,
          message: response.message || "Registration successful",
        };
      } else {
        const error =
          response.message || response.error || "Registration failed";
        return { success: false, error };
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Registration failed";
      console.error("❌ Registration error:", errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (
    profileData: Partial<UserProfile>
  ): Promise<AuthResponse> => {
    try {
      if (!isTokenValid()) {
        return { success: false, error: "Not authenticated" };
      }

      console.log("📝 Updating profile...");

      const response = await apiCall("users/profile/", {
        method: "PATCH",
        body: JSON.stringify(profileData),
      });

      if (response.success && user) {
        const updatedUser: User = {
          ...user,
          profile: {
            ...user.profile,
            ...response.data?.profile,
            ...profileData,
          },
        };

        setUser(updatedUser);

        if (typeof window !== "undefined") {
          localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
        }

        console.log("✅ Profile update successful");
        return {
          success: true,
          data: updatedUser,
          message: response.message || "Profile updated successfully",
        };
      } else {
        const error =
          response.message || response.error || "Profile update failed";
        return { success: false, error };
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Profile update failed";
      console.error("❌ Profile update error:", errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const changePassword = async (
    oldPassword: string,
    newPassword: string
  ): Promise<AuthResponse> => {
    try {
      if (!isTokenValid()) {
        return { success: false, error: "Not authenticated" };
      }

      console.log("🔐 Changing password...");

      const response = await apiCall("users/change-password/", {
        method: "POST",
        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword,
        }),
      });

      if (response.success) {
        console.log("✅ Password change successful");
        return {
          success: true,
          message: response.message || "Password changed successfully",
        };
      } else {
        const error =
          response.message || response.error || "Password change failed";
        return { success: false, error };
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Password change failed";
      console.error("❌ Password change error:", errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // ==========================================
  // 🚀 ENHANCED INITIALIZATION
  // ==========================================

  useEffect(() => {
    const initAuth = async () => {
      // Prevent multiple initializations
      if (initializingRef.current || initialized) {
        console.log("⏭️ Skipping auth init - already done");
        return;
      }

      initializingRef.current = true;
      console.log("🚀 Starting authentication initialization...");
      console.log("🌐 API Base URL:", API_BASE_URL);
      console.log("🔧 Environment:", process.env.NODE_ENV);

      try {
        // Small delay to ensure DOM is ready
        await new Promise((resolve) => setTimeout(resolve, 50));

        const authData = loadAuthData();

        if (authData) {
          console.log("🔑 Processing stored auth data...");

          // Set initial state
          setToken(authData.token);
          setUser(authData.user);

          console.log("✅ Initial auth state set from storage");

          // Validate token in background (non-blocking)
          setTimeout(async () => {
            try {
              console.log("🔄 Validating stored token...");
              const isValid = await refreshAuth();
              if (!isValid) {
                console.log("⚠️ Stored token is invalid, clearing...");
                clearAuthData();
              } else {
                console.log("✅ Stored token is valid");
              }
            } catch (error) {
              console.log("⚠️ Token validation failed:", error);
              clearAuthData();
            }
          }, 500); // Delay to not block UI
        } else {
          console.log("ℹ️ No stored auth data found - fresh start");
        }
      } catch (error) {
        console.error("❌ Auth initialization error:", error);
        clearAuthData();
      } finally {
        setLoading(false);
        setInitialized(true);
        initializingRef.current = false;

        console.log("✅ Auth initialization completed");
        console.log("📊 Final init state:", {
          hasUser: !!user,
          hasToken: !!token,
          isAuthenticated: !!(user && token),
          initialized: true,
        });
      }
    };

    initAuth();
  }, []); // Empty dependency array - only run once

  // ==========================================
  // 🔄 PERIODIC TOKEN VALIDATION
  // ==========================================

  useEffect(() => {
    if (!user || !token || !initialized) {
      console.log("⏭️ Skipping periodic validation - not ready");
      return;
    }

    console.log("⏰ Setting up periodic token validation");

    const interval = setInterval(
      () => {
        console.log("🔄 Performing periodic token validation...");
        refreshAuth().catch((error) => {
          console.error("❌ Periodic validation failed:", error);
        });
      },
      30 * 60 * 1000
    ); // 30 minutes

    return () => {
      console.log("🛑 Clearing token validation interval");
      clearInterval(interval);
    };
  }, [user, token, initialized, refreshAuth]);

  // ==========================================
  // 🎯 CONTEXT VALUE
  // ==========================================

  const contextValue: AuthContextType = {
    // State
    user,
    loading,
    isAuthenticated: !!user && !!token,
    token,
    initialized,

    // Actions
    login,
    logout,
    register,
    refreshAuth,
    updateProfile,
    changePassword,

    // Utilities
    getAuthHeaders,
    isTokenValid,
    clearAuthData,
  };

  // Debug context value changes
  useEffect(() => {
    console.log("🔄 AuthContext state update:", {
      hasUser: !!user,
      hasToken: !!token,
      isAuthenticated: !!(user && token),
      loading,
      initialized,
      username: user?.username || "none",
      tokenPreview: token ? token.substring(0, 20) + "..." : "none",
    });
  }, [user, token, loading, initialized]);

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};

export default AuthProvider;
