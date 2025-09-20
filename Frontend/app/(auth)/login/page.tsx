"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "../../../contexts/AuthContext";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { LoadingState } from "../../../types/common";
import { LoginRequest } from "../../../types/auth";
import { EyeIcon, EyeSlashIcon } from "@heroicons/react/24/outline";

export default function LoginPage() {
  const {
    login,
    isAuthenticated,
    loading: authLoading,
    user,
    token,
    initialized,
  } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTimeoutRef = useRef<NodeJS.Timeout>();

  // Form state
  const [formData, setFormData] = useState<LoginRequest>({
    username: "",
    password: "",
  });
  const [loadingState, setLoadingState] = useState<LoadingState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [validationErrors, setValidationErrors] = useState<
    Partial<LoginRequest>
  >({});
  const [redirecting, setRedirecting] = useState(false);

  // Registration success message
  const message = searchParams.get("message");

  // Debug logging for auth state changes
  useEffect(() => {
    console.log("🔍 Auth State Debug:", {
      isAuthenticated,
      authLoading,
      initialized,
      hasUser: !!user,
      hasToken: !!token,
      loadingState,
      redirecting,
    });
  }, [
    isAuthenticated,
    authLoading,
    initialized,
    user,
    token,
    loadingState,
    redirecting,
  ]);

  // FIXED: Handle redirect when already authenticated
  useEffect(() => {
    // Clear any existing timeout
    if (redirectTimeoutRef.current) {
      clearTimeout(redirectTimeoutRef.current);
    }

    // Only redirect if:
    // 1. Auth is fully initialized
    // 2. User is authenticated
    // 3. Not currently processing a login
    // 4. Not already redirecting
    if (
      initialized &&
      isAuthenticated &&
      loadingState === "idle" &&
      !redirecting
    ) {
      console.log("👤 User already authenticated, initiating redirect...");
      console.log("📊 Auth details:", {
        user: user?.username,
        tokenLength: token?.length,
      });

      setRedirecting(true);
      const redirectTo = searchParams.get("redirect") || "/dashboard";

      // Use timeout to ensure state is stable
      redirectTimeoutRef.current = setTimeout(() => {
        console.log("🔄 Executing redirect to:", redirectTo);
        router.push(redirectTo);
      }, 500);
    }

    // Cleanup timeout on unmount
    return () => {
      if (redirectTimeoutRef.current) {
        clearTimeout(redirectTimeoutRef.current);
      }
    };
  }, [
    initialized,
    isAuthenticated,
    loadingState,
    redirecting,
    user,
    token,
    router,
    searchParams,
  ]);

  // Handle input changes
  const handleInputChange = (field: keyof LoginRequest, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Clear validation error when user starts typing
    if (validationErrors[field]) {
      setValidationErrors((prev) => ({ ...prev, [field]: undefined }));
    }

    // Clear general error
    if (error) {
      setError(null);
    }
  };

  // Form validation
  const validateForm = (): boolean => {
    const errors: Partial<LoginRequest> = {};

    if (!formData.username.trim()) {
      errors.username = "Username is required";
    } else if (formData.username.length < 3) {
      errors.username = "Username must be at least 3 characters";
    }

    if (!formData.password) {
      errors.password = "Password is required";
    } else if (formData.password.length < 6) {
      errors.password = "Password must be at least 6 characters";
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // FIXED: Enhanced form submission with better debugging
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoadingState("loading");
    setError(null);

    try {
      console.log("🔐 Starting login process...");
      console.log("📝 Form data:", {
        username: formData.username,
        passwordLength: formData.password.length,
      });

      const result = await login(formData.username, formData.password);
      console.log("📥 Login result:", result);

      if (result.success) {
        console.log("✅ Login successful!");
        setLoadingState("success");

        // Store remember me preference
        if (rememberMe) {
          localStorage.setItem("rememberMe", "true");
        }

        // Debug storage state
        setTimeout(() => {
          const storedToken = localStorage.getItem("authToken");
          const storedUser = localStorage.getItem("userData");
          console.log("🔍 Post-login storage check:", {
            tokenStored: !!storedToken,
            userStored: !!storedUser,
            tokenPreview: storedToken
              ? storedToken.substring(0, 20) + "..."
              : "none",
          });
        }, 200);

        // Handle redirect after successful login
        const redirectTo = searchParams.get("redirect") || "/dashboard";
        console.log("📍 Preparing redirect to:", redirectTo);

        // Wait for auth context to update
        setTimeout(() => {
          console.log("🔄 Initiating post-login redirect...");
          setRedirecting(true);

          setTimeout(() => {
            console.log("🚀 Executing redirect to:", redirectTo);
            router.push(redirectTo);
          }, 300);
        }, 800); // Increased delay to ensure auth state is fully updated
      } else {
        console.log("❌ Login failed:", result.error);
        setLoadingState("error");
        setError(result.error || "Login failed. Please try again.");
      }
    } catch (err) {
      console.error("❌ Login exception:", err);
      setLoadingState("error");
      setError(
        err instanceof Error ? err.message : "An unexpected error occurred"
      );
    }
  };

  // Enhanced demo login with offline fallback
  const handleDemoLogin = async () => {
    setLoadingState("loading");
    setError(null);

    try {
      console.log("🧪 Attempting demo login...");
      const result = await login("demo_farmer", "demo123");

      if (result.success) {
        console.log("✅ Demo login successful");
        setLoadingState("success");
        setRedirecting(true);

        setTimeout(() => {
          console.log("🚀 Demo redirect to dashboard");
          router.push("/dashboard");
        }, 800);
      } else {
        console.log("❌ Demo login failed:", result.error);
        // Check if it's a network error and use offline mode
        if (result.error?.includes('Unable to connect') || result.error?.includes('Network error')) {
          console.log("🌐 Backend unavailable, using offline demo mode");
          
          // Create a mock user for demo purposes
          const mockUser = {
            id: "demo-123",
            username: "demo_farmer",
            email: "demo@smartcrop.com",
            first_name: "Demo",
            last_name: "Farmer",
            is_active: true,
            date_joined: new Date().toISOString(),
            profile: {
              farm_name: "Demo Farm",
              location: "Demo Location",
              crops: ["corn", "wheat"]
            }
          };
          
          // Store demo data locally
          localStorage.setItem("authToken", "demo-token-offline-mode");
          localStorage.setItem("userData", JSON.stringify(mockUser));
          localStorage.setItem("offlineMode", "true");
          
          setLoadingState("success");
          setRedirecting(true);
          
          setTimeout(() => {
            console.log("🚀 Offline demo redirect to dashboard");
            window.location.href = "/dashboard"; // Force page reload to pick up new auth state
          }, 800);
        } else {
          setLoadingState("error");
          setError("Demo account not available. Please use your credentials.");
        }
      }
    } catch (err) {
      console.error("❌ Demo login error:", err);
      
      // If it's a network error, enable offline mode
      const errorMessage = err instanceof Error ? err.message : String(err);
      if (errorMessage.includes('Unable to connect') || errorMessage.includes('Network error')) {
        console.log("🌐 Enabling offline demo mode due to network error");
        
        const mockUser = {
          id: "demo-123",
          username: "demo_farmer",
          email: "demo@smartcrop.com",
          first_name: "Demo",
          last_name: "Farmer",
          is_active: true,
          date_joined: new Date().toISOString(),
          profile: {
            farm_name: "Demo Farm",
            location: "Demo Location",
            crops: ["corn", "wheat"]
          }
        };
        
        localStorage.setItem("authToken", "demo-token-offline-mode");
        localStorage.setItem("userData", JSON.stringify(mockUser));
        localStorage.setItem("offlineMode", "true");
        
        setLoadingState("success");
        setRedirecting(true);
        
        setTimeout(() => {
          console.log("🚀 Offline demo redirect to dashboard");
          window.location.href = "/dashboard";
        }, 800);
      } else {
        setLoadingState("error");
        setError("Demo login failed");
      }
    }
  };

  // Show loading screen while auth is initializing or redirecting
  if (!initialized || authLoading || redirecting) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">
            {!initialized
              ? "Initializing..."
              : authLoading
                ? "Checking authentication..."
                : "Redirecting to dashboard..."}
          </p>
          <p className="text-xs text-gray-400 mt-2">
            Debug:{" "}
            {JSON.stringify({
              initialized,
              authLoading,
              redirecting,
              isAuthenticated,
            })}
          </p>
        </div>
      </div>
    );
  }

  // Don't render login form if user is authenticated
  if (isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">
            Welcome back, {user?.first_name || user?.username}!
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Redirecting to your dashboard...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-green-600 rounded-full flex items-center justify-center">
            <span className="text-2xl">🌾</span>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Welcome to SmartCropAdvisory
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Sign in to your agricultural intelligence dashboard
          </p>

          {/* Debug Info (only in development) */}
          {process.env.NODE_ENV === "development" && (
            <div className="mt-2 text-xs text-gray-400 bg-gray-100 rounded p-2">
              Debug: Auth={isAuthenticated ? "Y" : "N"}, Init=
              {initialized ? "Y" : "N"}, Loading={authLoading ? "Y" : "N"}
            </div>
          )}
        </div>

        {/* Registration Success Message */}
        {message && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-green-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 13l4 4L19 7"
                  ></path>
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">{message}</p>
              </div>
            </div>
          </div>
        )}

        {/* Login Form */}
        <div className="bg-white py-8 px-6 shadow-xl rounded-xl border border-gray-100">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* General Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg
                      className="h-5 w-5 text-red-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.502 0L4.732 15.5c-.77.833.192 2.5 1.732 2.5z"
                      ></path>
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-red-800">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Username Field */}
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Username
              </label>
              <div className="relative">
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  className={`appearance-none relative block w-full px-3 py-3 pl-10 border ${
                    validationErrors.username
                      ? "border-red-300 focus:ring-red-500 focus:border-red-500"
                      : "border-gray-300 focus:ring-green-500 focus:border-green-500"
                  } placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:z-10 transition-colors`}
                  placeholder="Enter your username"
                  value={formData.username}
                  onChange={(e) =>
                    handleInputChange("username", e.target.value)
                  }
                  disabled={loadingState === "loading"}
                />
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg
                    className="h-5 w-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    ></path>
                  </svg>
                </div>
              </div>
              {validationErrors.username && (
                <p className="mt-1 text-sm text-red-600">
                  {validationErrors.username}
                </p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  className={`appearance-none relative block w-full px-3 py-3 pl-10 pr-10 border ${
                    validationErrors.password
                      ? "border-red-300 focus:ring-red-500 focus:border-red-500"
                      : "border-gray-300 focus:ring-green-500 focus:border-green-500"
                  } placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:z-10 transition-colors`}
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) =>
                    handleInputChange("password", e.target.value)
                  }
                  disabled={loadingState === "loading"}
                />
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg
                    className="h-5 w-5 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M12 15v2m-6 2h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    ></path>
                  </svg>
                </div>
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              {validationErrors.password && (
                <p className="mt-1 text-sm text-red-600">
                  {validationErrors.password}
                </p>
              )}
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <label
                  htmlFor="remember-me"
                  className="ml-2 block text-sm text-gray-900"
                >
                  Remember me
                </label>
              </div>

              <div className="text-sm">
                <Link
                  href="/forgot-password"
                  className="font-medium text-green-600 hover:text-green-500 transition-colors"
                >
                  Forgot your password?
                </Link>
              </div>
            </div>

            {/* Submit Button */}
            <div>
              <button
                type="submit"
                disabled={loadingState === "loading"}
                className={`group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white transition-all duration-200 ${
                  loadingState === "loading"
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                }`}
              >
                {loadingState === "loading" ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Signing in...
                  </div>
                ) : (
                  <div className="flex items-center">
                    <svg
                      className="w-4 h-4 mr-2"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
                      ></path>
                    </svg>
                    Sign in to Dashboard
                  </div>
                )}
              </button>
            </div>

            {/* Demo Login Button */}
            <div>
              <button
                type="button"
                onClick={handleDemoLogin}
                disabled={loadingState === "loading"}
                className={`w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-lg transition-colors ${
                  loadingState === "loading"
                    ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                    : "bg-white text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                }`}
              >
                <span className="mr-2">🧪</span>
                Try Demo Account
              </button>
            </div>
          </form>

          {/* Sign Up Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{" "}
              <Link
                href="/register"
                className="font-medium text-green-600 hover:text-green-500 transition-colors"
              >
                Sign up for free
              </Link>
            </p>
          </div>

          {/* Features Preview */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-900 mb-3">
              What you'll get:
            </h3>
            <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
              <div className="flex items-center">
                <span className="mr-2">🌾</span>
                Crop Analysis
              </div>
              <div className="flex items-center">
                <span className="mr-2">🌤️</span>
                Weather Insights
              </div>
              <div className="flex items-center">
                <span className="mr-2">💧</span>
                Irrigation Advisory
              </div>
              <div className="flex items-center">
                <span className="mr-2">📈</span>
                Market Analysis
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-gray-500">
          <p>
            By signing in, you agree to our{" "}
            <Link href="/terms" className="text-green-600 hover:text-green-500">
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link
              href="/privacy"
              className="text-green-600 hover:text-green-500"
            >
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
