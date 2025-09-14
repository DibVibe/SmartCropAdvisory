"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

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

interface AuthTokens {
  access: string;
  refresh: string;
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

  // Get stored tokens
  const getStoredTokens = (): AuthTokens | null => {
    if (typeof window === "undefined") return null;

    const access = localStorage.getItem("accessToken");
    const refresh = localStorage.getItem("refreshToken");

    return access && refresh ? { access, refresh } : null;
  };

  // Store tokens
  const storeTokens = (tokens: AuthTokens) => {
    localStorage.setItem("accessToken", tokens.access);
    localStorage.setItem("refreshToken", tokens.refresh);
  };

  // Remove tokens
  const removeTokens = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
  };

  // Fetch user profile
  const fetchUserProfile = async (): Promise<User | null> => {
    try {
      const response = await api.get("/users/profile/");
      return response.data;
    } catch (error) {
      console.error("Failed to fetch user profile:", error);
      return null;
    }
  };

  // Refresh access token
  const refreshToken = useCallback(async (): Promise<boolean> => {
    try {
      const tokens = getStoredTokens();
      if (!tokens?.refresh) {
        return false;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_AUTH_URL}/token/refresh/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ refresh: tokens.refresh }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        storeTokens({ access: data.access, refresh: tokens.refresh });
        return true;
      } else {
        // Refresh token is invalid
        await logout();
        return false;
      }
    } catch (error) {
      console.error("Token refresh failed:", error);
      await logout();
      return false;
    }
  }, []);

  // Login function
  const login = async (
    username: string,
    password: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      setLoading(true);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_AUTH_URL}/token/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, password }),
        }
      );

      if (response.ok) {
        const tokens: AuthTokens = await response.json();
        storeTokens(tokens);

        // Fetch user profile
        const userProfile = await fetchUserProfile();
        if (userProfile) {
          setUser(userProfile);

          // Redirect to dashboard
          router.push("/dashboard");

          return { success: true };
        } else {
          removeTokens();
          return { success: false, error: "Failed to load user profile" };
        }
      } else {
        const errorData = await response.json();
        return {
          success: false,
          error:
            errorData.detail ||
            errorData.non_field_errors?.[0] ||
            "Login failed",
        };
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

  // Logout function
  const logout = async (): Promise<void> => {
    try {
      const tokens = getStoredTokens();
      if (tokens?.refresh) {
        // Try to blacklist the refresh token
        try {
          await fetch(`${process.env.NEXT_PUBLIC_AUTH_URL}/token/blacklist/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${tokens.access}`,
            },
            body: JSON.stringify({ refresh: tokens.refresh }),
          });
        } catch (error) {
          console.warn("Failed to blacklist token:", error);
        }
      }
    } finally {
      // Always clear local state and storage
      removeTokens();
      setUser(null);
      router.push("/login");
    }
  };

  // Register function
  const register = async (
    userData: RegisterData
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      setLoading(true);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/users/register/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(userData),
        }
      );

      if (response.ok) {
        const result = await response.json();

        // Auto-login after successful registration
        if (result.tokens) {
          storeTokens(result.tokens);
          const userProfile = await fetchUserProfile();
          if (userProfile) {
            setUser(userProfile);
            router.push("/dashboard");
            return { success: true };
          }
        }

        // If no auto-login, redirect to login
        router.push("/login?message=Registration successful. Please log in.");
        return { success: true };
      } else {
        const errorData = await response.json();
        const errorMessage =
          errorData.detail ||
          errorData.username?.[0] ||
          errorData.email?.[0] ||
          errorData.password?.[0] ||
          "Registration failed";
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

  // Update profile function
  const updateProfile = async (
    data: Partial<User["profile"]>
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await api.patch("/users/profile/", data);

      if (response.data) {
        setUser((prev) =>
          prev ? { ...prev, profile: { ...prev.profile, ...data } } : null
        );
        return { success: true };
      }
      return { success: false, error: "Failed to update profile" };
    } catch (error: any) {
      console.error("Profile update error:", error);
      return {
        success: false,
        error:
          error.response?.data?.detail ||
          error.message ||
          "Failed to update profile",
      };
    }
  };

  // Change password function
  const changePassword = async (
    oldPassword: string,
    newPassword: string
  ): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await api.post("/users/change-password/", {
        old_password: oldPassword,
        new_password: newPassword,
      });

      if (response.status === 200) {
        return { success: true };
      }
      return { success: false, error: "Failed to change password" };
    } catch (error: any) {
      console.error("Password change error:", error);
      return {
        success: false,
        error:
          error.response?.data?.detail ||
          error.response?.data?.old_password?.[0] ||
          error.response?.data?.new_password?.[0] ||
          "Failed to change password",
      };
    }
  };

  // Initialize authentication state
  useEffect(() => {
    const initAuth = async () => {
      const tokens = getStoredTokens();

      if (tokens) {
        // Verify token and fetch user profile
        const userProfile = await fetchUserProfile();
        if (userProfile) {
          setUser(userProfile);
        } else {
          // Try to refresh token
          const refreshed = await refreshToken();
          if (refreshed) {
            const retryProfile = await fetchUserProfile();
            if (retryProfile) {
              setUser(retryProfile);
            } else {
              removeTokens();
            }
          } else {
            removeTokens();
          }
        }
      }

      setLoading(false);
    };

    initAuth();
  }, [refreshToken]);

  // Auto-refresh token before expiry
  useEffect(() => {
    if (!user) return;

    // Refresh token every 50 minutes (tokens expire in 60 minutes)
    const interval = setInterval(
      () => {
        refreshToken();
      },
      50 * 60 * 1000
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
