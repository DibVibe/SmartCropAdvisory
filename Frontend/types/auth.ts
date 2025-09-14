import { User } from "./api";

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
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

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  loading: boolean;
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (
    username: string,
    password: string
  ) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  register: (
    userData: RegisterRequest
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

export interface LoginFormData extends LoginRequest {
  rememberMe?: boolean;
}

export interface RegisterFormData extends RegisterRequest {
  confirmPassword: string;
  agreeToTerms: boolean;
}
