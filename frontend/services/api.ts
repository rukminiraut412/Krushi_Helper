import { HealthResponse } from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" ? "/api" : "http://127.0.0.1:8000/api");

export const apiService = {
  /**
   * Check health status of the KrushiRakshak FastAPI backend service
   */
  async getHealth(): Promise<HealthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: "GET",
        headers: {
          "Accept": "application/json",
        },
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
      }

      const data: HealthResponse = await response.json();
      return data;
    } catch (error) {
      console.warn("Backend health check failed:", error);
      throw error;
    }
  },
};
