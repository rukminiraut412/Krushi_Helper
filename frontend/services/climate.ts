const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" ? "/api" : "http://127.0.0.1:8000/api");

export interface WeatherData {
  farm_id: number;
  farm_name: string;
  latitude: number | null;
  longitude: number | null;
  temperature: number;
  rainfall: number;
  humidity: number;
  wind_speed: number;
  forecast_rainfall: number;
  condition: string;
  timestamp: string;
  is_demo: boolean;
  data_source: string;
}

export interface SoilData {
  farm_id: number;
  farm_name: string;
  soil_type: string;
  soil_moisture: number;
  water_availability: string;
  soil_condition: string;
  ph_level: number;
  organic_matter_pct: number;
  timestamp: string;
  is_demo: boolean;
  data_source: string;
  sensor_status: string;
}

export interface HistoricalClimatePoint {
  date: string;
  rainfall_mm: number;
  temp_max_c: number;
  temp_min_c: number;
}

export interface RiskItem {
  score: number;
  level: "LOW" | "MEDIUM" | "HIGH";
  contributing_factors: string[];
}

export interface FarmRiskData {
  id?: number | null;
  farm_id: number;
  farm_name: string;
  created_at?: string | null;
  drought: RiskItem;
  flood: RiskItem;
  heat: RiskItem;
  extreme_rainfall: RiskItem;
  overall_risk: "LOW" | "MEDIUM" | "HIGH";
  highest_risk_type: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  main_contributing_factors: string[];
}

export interface RiskHistoryItem {
  id: number;
  farm_id: number;
  drought_score: number;
  flood_score: number;
  heat_score: number;
  extreme_rainfall_score: number;
  overall_risk: "LOW" | "MEDIUM" | "HIGH";
  highest_risk_type: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  main_contributing_factors: string[];
  created_at: string;
}

export const climateService = {
  async getWeather(farmId: number): Promise<WeatherData> {
    const res = await fetch(`${API_BASE_URL}/weather/${farmId}`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`Failed to load weather data for farm #${farmId}`);
    }
    return res.json();
  },

  async getSoil(farmId: number): Promise<SoilData> {
    const res = await fetch(`${API_BASE_URL}/soil/${farmId}`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`Failed to load soil telemetry for farm #${farmId}`);
    }
    return res.json();
  },

  async getHistorical(farmId: number): Promise<HistoricalClimatePoint[]> {
    const res = await fetch(`${API_BASE_URL}/weather/${farmId}/history`, {
      cache: "no-store",
    });
    if (!res.ok) {
      return [];
    }
    return res.json();
  },

  async getRiskAssessment(farmId: number): Promise<FarmRiskData> {
    const res = await fetch(`${API_BASE_URL}/risk/farm/${farmId}`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`Failed to compute AI risk predictions for farm #${farmId}`);
    }
    return res.json();
  },

  async getRiskHistory(farmId: number): Promise<RiskHistoryItem[]> {
    const res = await fetch(`${API_BASE_URL}/risk/farm/${farmId}/history`, {
      cache: "no-store",
    });
    if (!res.ok) {
      return [];
    }
    return res.json();
  },
};
