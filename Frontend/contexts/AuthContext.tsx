"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import { useRouter } from "next/navigation";

// Types
interface User {
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

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (
    username: string,
    password: string
  ) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  register: (
    userData: RegisterData
  ) => Promise<{ success: boolean; error?: string }>;
  refreshToken: () => Promise<boolean>;
  updateProfile: (
    data: Partial<User["profile"]>
  ) => Promise<{ success: boolean; error?: string }>;
  changePassword: (
    oldPassword: string,
    newPassword: string
  ) => Promise<{ success: boolean; error?: string }>;
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

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Get API base URL
  const getApiUrl = (endpoint: string) => {
    const baseUrl =
      process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";
    return `${baseUrl}${endpoint}`;
  };

  // Get stored token
  const getStoredToken = (): string | null => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("authToken");
  };

  // Store token
  const storeToken = (token: string) => {
    localStorage.setItem("authToken", token);
  };

  // Remove token
  const removeToken = () => {
    localStorage.removeItem("authToken");
    // Remove old JWT tokens if they exist
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
  };

  // fetchUserProfile function
  const fetchUserProfile = async (token: string) => {
    try {
      console.log(
        "🔍 Fetching profile with token:",
        token.substring(0, 20) + "..."
      );

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/users/mongo-profile/`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      console.log("📡 Profile response status:", response.status);

      if (response.ok) {
        const responseData = await response.json();
        console.log("✅ Profile data received:", responseData);

        if (responseData.success && responseData.data) {
          setUser(responseData.data);
          return responseData.data;
        } else {
          console.log("❌ Profile response not successful:", responseData);
          return null;
        }
      } else {
        console.log("❌ Profile fetch failed with status:", response.status);
        return null;
      }
    } catch (error) {
      console.error("❌ Failed to fetch user profile:", error);
      return null;
    }
  };

  // Login function - Updated to match your Django endpoint
  const login = async (
    username: string,
    password: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      setLoading(true);
      console.log("🔐 Attempting login for:", username);

      const response = await fetch(getApiUrl("/users/login/"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      console.log("📡 Login response status:", response.status);

      if (response.ok) {
        const data = await response.json();
        console.log("✅ Login response:", data);

        // Your Django might return different token structure
        // Adjust this based on your actual Django response
        if (data.token || data.access || data.key) {
          const token = data.token || data.access || data.key;
          storeToken(token);

          // Fetch user profile
          const userProfile = await fetchUserProfile();
          if (userProfile) {
            setUser(userProfile);
            console.log("✅ Login successful");
            return { success: true };
          } else {
            removeToken();
            return { success: false, error: "Failed to load user profile" };
          }
        } else {
          return { success: false, error: "No token received from server" };
        }
      } else {
        let errorMessage = "Login failed";

        try {
          const errorData = await response.json();
          errorMessage =
            errorData.error ||
            errorData.detail ||
            errorData.non_field_errors?.[0] ||
            errorMessage;
        } catch {
          errorMessage = `Login failed: ${response.status} ${response.statusText}`;
        }

        return { success: false, error: errorMessage };
      }
    } catch (error) {
      console.error("Login error:", error);
      return {
        success: false,
        error:
          error instanceof Error
            ? error.message
            : "Network error. Please check your connection.",
      };
    } finally {
      setLoading(false);
    }
  };

  // Logout function - Updated to match your Django endpoint
  const logout = async (): Promise<void> => {
    try {
      const token = getStoredToken();

      if (token) {
        // Call Django logout endpoint
        try {
          await fetch(getApiUrl("/users/logout/"), {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          });
          console.log("✅ Server logout successful");
        } catch (error) {
          console.warn("Failed to logout on server:", error);
          // Don't throw error, continue with local logout
        }
      }
    } finally {
      // Always clear local state
      removeToken();
      setUser(null);
      console.log("👋 Local logout completed");
      router.push("/login");
    }
  };

  // Register function - Updated to match your Django endpoint
  const register = async (
    userData: RegisterData
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      setLoading(true);
      console.log("📝 Attempting registration for:", userData.username);

      const response = await fetch(getApiUrl("/users/register/"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      });

      console.log("📡 Registration response status:", response.status);

      if (response.ok) {
        const result = await response.json();
        console.log("✅ Registration response:", result);

        // Check if auto-login token is provided
        if (result.token || result.access || result.key) {
          const token = result.token || result.access || result.key;
          storeToken(token);

          const userProfile = await fetchUserProfile();
          if (userProfile) {
            setUser(userProfile);
            console.log("✅ Registration and auto-login successful");
            return { success: true };
          }
        }

        // If no auto-login, redirect to login
        console.log("✅ Registration successful, redirect to login");
        return { success: true };
      } else {
        let errorMessage = "Registration failed";

        try {
          const errorData = await response.json();
          errorMessage =
            errorData.detail ||
            errorData.username?.[0] ||
            errorData.email?.[0] ||
            errorData.password?.[0] ||
            errorMessage;
        } catch {
          errorMessage = `Registration failed: ${response.status} ${response.statusText}`;
        }

        return { success: false, error: errorMessage };
      }
    } catch (error) {
      console.error("Registration error:", error);
      return {
        success: false,
        error:
          error instanceof Error
            ? error.message
            : "Network error. Please try again.",
      };
    } finally {
      setLoading(false);
    }
  };

  // Refresh token - Simplified since your Django may not use JWT refresh pattern
  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const token = getStoredToken();
      if (!token) return false;

      // Try to fetch user profile to validate token
      const userProfile = await fetchUserProfile();
      if (userProfile) {
        setUser(userProfile);
        return true;
      } else {
        // Token is invalid
        await logout();
        return false;
      }
    } catch (error) {
      console.error("Token validation failed:", error);
      await logout();
      return false;
    }
  }, []);

  // Update profile function
  const updateProfile = async (
    data: Partial<User["profile"]>
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const token = getStoredToken();
      if (!token) {
        return { success: false, error: "Not authenticated" };
      }

      const response = await fetch(getApiUrl("/users/profile/"), {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        const updatedUser = await response.json();
        setUser(updatedUser);
        return { success: true };
      } else {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.detail || "Failed to update profile",
        };
      }
    } catch (error: any) {
      console.error("Profile update error:", error);
      return {
        success: false,
        error: error.message || "Failed to update profile",
      };
    }
  };

  // Change password function
  const changePassword = async (
    oldPassword: string,
    newPassword: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const token = getStoredToken();
      if (!token) {
        return { success: false, error: "Not authenticated" };
      }

      const response = await fetch(getApiUrl("/users/change-password/"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword,
        }),
      });

      if (response.ok) {
        return { success: true };
      } else {
        const errorData = await response.json();
        return {
          success: false,
          error:
            errorData.detail ||
            errorData.old_password?.[0] ||
            errorData.new_password?.[0] ||
            "Failed to change password",
        };
      }
    } catch (error: any) {
      console.error("Password change error:", error);
      return {
        success: false,
        error: error.message || "Failed to change password",
      };
    }
  };

  // Initialize authentication state
  useEffect(() => {
    const initAuth = async () => {
      console.log("🚀 Initializing auth state...");
      const token = getStoredToken();

      if (token) {
        console.log("🔑 Token found, validating...");
        const userProfile = await fetchUserProfile();
        if (userProfile) {
          setUser(userProfile);
          console.log("✅ Auth state initialized with user");
        } else {
          console.log("❌ Token validation failed, clearing");
          removeToken();
        }
      } else {
        console.log("ℹ️ No token found");
      }

      setLoading(false);
    };

    initAuth();
  }, []);

  // Periodic token validation (every 30 minutes)
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(
      () => {
        console.log("🔄 Validating token...");
        refreshToken();
      },
      30 * 60 * 1000
    );

    return () => clearInterval(interval);
  }, [user, refreshToken]);

  const value: AuthContextType = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    logout,
    register,
    refreshToken,
    updateProfile,
    changePassword,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
