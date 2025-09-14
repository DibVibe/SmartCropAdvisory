export interface APIResponse<T> {
  data: T;
  message?: string;
  status: "success" | "error";
  timestamp?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export type LoadingState = "idle" | "loading" | "success" | "error";

export interface SelectOption {
  value: string;
  label: string;
}
