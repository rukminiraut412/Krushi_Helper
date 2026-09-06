export interface HealthResponse {
  status: string;
  service: string;
}

export interface User {
  id: number;
  name: string;
  mobile: string;
  role: "FARMER" | "ADMIN";
  preferred_language: string;
  created_at?: string;
  village?: string;
  district?: string;
  state?: string;
  latitude?: number;
  longitude?: number;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  role: "FARMER" | "ADMIN";
  user: User;
}

export interface Farm {
  id: number;
  farmer_id: number;
  farm_name: string;
  area: number;
  crop: string;
  sowing_date: string | null;
  soil_type: string | null;
  irrigation_available: boolean;
  latitude: number | null;
  longitude: number | null;
  created_at: string;
}

export interface FarmCreatePayload {
  farm_name: string;
  area: number;
  crop: string;
  sowing_date?: string;
  soil_type?: string;
  irrigation_available: boolean;
  latitude?: number;
  longitude?: number;
}

export interface FarmUpdatePayload {
  farm_name?: string;
  area?: number;
  crop?: string;
  sowing_date?: string;
  soil_type?: string;
  irrigation_available?: boolean;
  latitude?: number;
  longitude?: number;
}
