import { authService } from "./auth";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" ? "/api" : "http://127.0.0.1:8000/api");

function getAdminHeaders(): HeadersInit {
  const token = authService.getToken();
  if (!token) {
    throw new Error("Admin authentication required. Please log in.");
  }
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export interface RiskDistribution {
  low: number;
  medium: number;
  high: number;
}

export interface CropCount {
  crop: string;
  count: number;
  area_acres: number;
}

export interface PriorityInterventionItem {
  farm_id: number;
  farm_name: string;
  farmer_id: number;
  farmer_name: string;
  mobile: string;
  crop: string;
  area: number;
  latitude: number | null;
  longitude: number | null;
  village: string | null;
  district: string | null;
  state: string | null;
  risk_type: string;
  risk_score: number;
  risk_level: string;
  vulnerability_level: string;
  recommended_action: string;
  timestamp: string;
}

export interface RecentHighRiskFarm {
  farm_id: number;
  farm_name: string;
  farmer_name: string;
  crop: string;
  risk_type: string;
  risk_score: number;
  risk_level: string;
  created_at: string;
}

export interface AdminDashboardStats {
  total_farmers: number;
  total_farms: number;
  high_risk_farms: number;
  medium_risk_farms: number;
  low_risk_farms: number;
  drought_risk_farms: number;
  flood_risk_farms: number;
  heat_stress_farms: number;
  extreme_rainfall_farms: number;
  risk_distribution: RiskDistribution;
  risk_level_percentages: Record<string, number>;
  crop_distribution: CropCount[];
  recent_high_risk_farms: RecentHighRiskFarm[];
  priority_intervention_list: PriorityInterventionItem[];
}

export interface RiskMapPoint {
  farm_id: number;
  farm_name: string;
  farmer_name: string;
  mobile: string;
  crop: string;
  area: number;
  latitude: number;
  longitude: number;
  village: string | null;
  district: string | null;
  state: string | null;
  risk_type: string;
  risk_score: number;
  risk_level: string;
  vulnerability_score: number;
  vulnerability_level: string;
  contributing_factors: string[];
  irrigation_available: boolean;
  soil_type: string | null;
  latest_evaluated_at: string | null;
}

export interface VulnerableAreaSummary {
  district: string;
  state: string;
  farm_count: number;
  avg_risk_score: number;
  avg_vulnerability_score: number;
  dominant_hazard: string;
  high_risk_count: number;
}

export interface VulnerabilityAssessment {
  most_vulnerable_farms: PriorityInterventionItem[];
  vulnerable_areas: VulnerableAreaSummary[];
  priority_intervention_areas: string[];
  main_risk_factors: string[];
  total_vulnerable_farms: number;
}

export interface AdminFarmerItem {
  id: number;
  user_id: number;
  name: string;
  mobile: string;
  village: string | null;
  district: string | null;
  state: string | null;
  preferred_language: string;
  farm_count: number;
  highest_risk_level: string | null;
  highest_risk_score: number | null;
  created_at: string;
}

export const adminService = {
  async getDashboardStats(): Promise<AdminDashboardStats> {
    const res = await fetch(`${API_BASE_URL}/admin/dashboard`, {
      method: "GET",
      headers: getAdminHeaders(),
      cache: "no-store",
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to fetch government dashboard stats");
    }

    return res.json();
  },

  async getRiskMapPoints(): Promise<RiskMapPoint[]> {
    const res = await fetch(`${API_BASE_URL}/admin/risk-map`, {
      method: "GET",
      headers: getAdminHeaders(),
      cache: "no-store",
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to fetch risk map points");
    }

    return res.json();
  },

  async getVulnerabilityAssessment(): Promise<VulnerabilityAssessment> {
    const res = await fetch(`${API_BASE_URL}/admin/vulnerability`, {
      method: "GET",
      headers: getAdminHeaders(),
      cache: "no-store",
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to fetch vulnerability assessment");
    }

    return res.json();
  },

  async getFarmers(): Promise<AdminFarmerItem[]> {
    const res = await fetch(`${API_BASE_URL}/admin/farmers`, {
      method: "GET",
      headers: getAdminHeaders(),
      cache: "no-store",
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to fetch farmers list");
    }

    return res.json();
  },
};
