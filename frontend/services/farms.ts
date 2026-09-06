import { Farm, FarmCreatePayload, FarmUpdatePayload } from "@/types";
import { authService } from "./auth";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" ? "/api" : "http://127.0.0.1:8000/api");

function getAuthHeaders(): HeadersInit {
  const token = authService.getToken();
  if (!token) {
    throw new Error("Authentication required. Please log in.");
  }
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export const farmService = {
  async getFarms(): Promise<Farm[]> {
    const res = await fetch(`${API_BASE_URL}/farms`, {
      method: "GET",
      headers: getAuthHeaders(),
      cache: "no-store",
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to fetch farms");
    }

    return res.json();
  },

  async getFarm(id: number): Promise<Farm> {
    const res = await fetch(`${API_BASE_URL}/farms/${id}`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to fetch farm details");
    }

    return res.json();
  },

  async createFarm(payload: FarmCreatePayload): Promise<Farm> {
    const res = await fetch(`${API_BASE_URL}/farms`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to create farm");
    }

    return res.json();
  },

  async updateFarm(id: number, payload: FarmUpdatePayload): Promise<Farm> {
    const res = await fetch(`${API_BASE_URL}/farms/${id}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to update farm");
    }

    return res.json();
  },

  async deleteFarm(id: number): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE_URL}/farms/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to delete farm");
    }

    return res.json();
  },
};
