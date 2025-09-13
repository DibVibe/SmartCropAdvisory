import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import DashboardPage from "@/app/(dashboard)/dashboard/page";

// Mock the useAuth hook
jest.mock("@/lib/hooks/useAuth", () => ({
  useAuth: () => ({
    user: { id: "1", username: "testuser", profile: { userType: "farmer" } },
    isAuthenticated: true,
    isLoading: false,
  }),
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe("Dashboard Page", () => {
  it("renders dashboard correctly", async () => {
    render(<DashboardPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText("Farm Dashboard")).toBeInTheDocument();
    });
  });
});
