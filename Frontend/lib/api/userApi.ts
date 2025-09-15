// api/userApi.ts
import { apiClient, TokenManager } from "./client";

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  profilePicture?: string;
  farmLocation?: {
    lat: number;
    lng: number;
    address: string;
  };
  preferredCrops: string[];
  farmSize: number;
  farmingExperience: string;
  phone?: string;
  subscriptionType: string;
  joinDate: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone?: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: UserProfile;
}

export const userApi = {
  // ==========================================
  // 🔐 AUTHENTICATION
  // ==========================================

  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post("/users/login/", credentials);
      const { access, refresh } = response.data;

      // Store tokens using TokenManager
      TokenManager.setTokens(access, refresh);

      return response.data;
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  },

  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    try {
      const response = await apiClient.post("/users/register/", userData);
      const { access, refresh } = response.data;

      // Store tokens using TokenManager
      TokenManager.setTokens(access, refresh);

      return response.data;
    } catch (error) {
      console.error("Registration failed:", error);
      throw error;
    }
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post("/users/logout/");
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      // Clear tokens using TokenManager
      TokenManager.clearTokens();
    }
  },

  refreshToken: async (): Promise<string> => {
    const refreshToken = TokenManager.getRefreshToken();
    if (!refreshToken) {
      throw new Error("No refresh token available");
    }

    const response = await apiClient.post("/users/token/refresh/", {
      refresh: refreshToken,
    });

    const { access } = response.data;
    TokenManager.setTokens(access);
    return access;
  },

  // ==========================================
  // 👤 PROFILE MANAGEMENT
  // ==========================================

  getProfile: async (): Promise<UserProfile> => {
    try {
      const response = await apiClient.get("/users/profiles/");
      return response.data;
    } catch (error) {
      console.error("Error fetching profile:", error);
      throw error;
    }
  },

  updateProfile: async (
    profileData: Partial<UserProfile>
  ): Promise<UserProfile> => {
    try {
      const response = await apiClient.patch("/users/profiles/", profileData);
      return response.data;
    } catch (error) {
      console.error("Error updating profile:", error);
      throw error;
    }
  },

  changePassword: async (passwordData: {
    old_password: string;
    new_password: string;
    confirm_password: string;
  }) => {
    try {
      const response = await apiClient.post(
        "/users/change-password/",
        passwordData
      );
      return response.data;
    } catch (error) {
      console.error("Error changing password:", error);
      throw error;
    }
  },

  uploadProfilePicture: async (formData: FormData) => {
    try {
      const response = await apiClient.post(
        "/users/profiles/upload_picture/",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      return response.data;
    } catch (error) {
      console.error("Error uploading profile picture:", error);
      throw error;
    }
  },

  // ==========================================
  // 📊 DASHBOARD & STATISTICS
  // ==========================================

  getDashboard: async () => {
    try {
      const response = await apiClient.get("/users/dashboard/");
      return response.data;
    } catch (error) {
      console.error("Error fetching dashboard:", error);
      return { error: "Failed to load dashboard" };
    }
  },

  getStatistics: async (days?: number) => {
    try {
      const params = days ? `?days=${days}` : "";
      const response = await apiClient.get(`/users/statistics/${params}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching statistics:", error);
      return { error: "Failed to load statistics" };
    }
  },

  // ==========================================
  // 🔔 NOTIFICATIONS
  // ==========================================

  getNotifications: async (unread?: boolean) => {
    try {
      const params = unread ? "?unread=true" : "";
      const response = await apiClient.get(`/users/notifications/${params}`);
      return response.data.results || response.data;
    } catch (error) {
      console.error("Error fetching notifications:", error);
      return [];
    }
  },

  markNotificationAsRead: async (notificationId: string) => {
    try {
      const response = await apiClient.patch(
        `/users/notifications/${notificationId}/`,
        {
          is_read: true,
        }
      );
      return response.data;
    } catch (error) {
      console.error("Error marking notification as read:", error);
      throw error;
    }
  },

  markAllNotificationsAsRead: async () => {
    try {
      const response = await apiClient.patch("/users/notifications/bulk/", {
        mark_as: "read",
      });
      return response.data;
    } catch (error) {
      console.error("Error marking all notifications as read:", error);
      throw error;
    }
  },

  // ==========================================
  // 📋 ACTIVITY & FEEDBACK
  // ==========================================

  getActivityLog: async (type?: string, days?: number) => {
    try {
      const params = new URLSearchParams();
      if (type) params.append("type", type);
      if (days) params.append("days", days.toString());

      const response = await apiClient.get(
        `/users/activities/?${params.toString()}`
      );
      return response.data.results || response.data;
    } catch (error) {
      console.error("Error fetching activity log:", error);
      return [];
    }
  },

  submitFeedback: async (feedback: {
    type: "bug" | "feature" | "improvement" | "general";
    title: string;
    description: string;
    priority?: "low" | "medium" | "high";
  }) => {
    try {
      const response = await apiClient.post("/users/feedback/", feedback);
      return response.data;
    } catch (error) {
      console.error("Error submitting feedback:", error);
      throw error;
    }
  },

  // ==========================================
  // 🔑 API KEYS & SUBSCRIPTION
  // ==========================================

  getApiKeys: async () => {
    try {
      const response = await apiClient.get("/users/api-keys/");
      return response.data;
    } catch (error) {
      console.error("Error fetching API keys:", error);
      return [];
    }
  },

  getSubscription: async () => {
    try {
      const response = await apiClient.get("/users/subscriptions/");
      return response.data;
    } catch (error) {
      console.error("Error fetching subscription:", error);
      return { error: "Failed to load subscription" };
    }
  },
};
