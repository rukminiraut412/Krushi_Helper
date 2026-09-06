const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" ? "/api" : "http://127.0.0.1:8000/api");

export interface AlertItem {
  id: number;
  farmer_id: number;
  farm_id: number;
  farm_name: string;
  crop: string;
  risk_type: string;
  risk_score: number;
  risk_level: string;
  short_explanation: string;
  recommended_action: string;
  is_read: boolean;
  created_at: string;
}

export interface AlertListResponse {
  farmer_id: number;
  unread_count: number;
  alerts: AlertItem[];
}

export const alertService = {
  async getAlerts(farmerId: number): Promise<AlertListResponse> {
    const res = await fetch(`${API_BASE_URL}/alerts/${farmerId}`, {
      cache: "no-store",
    });
    if (!res.ok) {
      return { farmer_id: farmerId, unread_count: 0, alerts: [] };
    }
    return res.json();
  },

  async markAsRead(alertId: number): Promise<AlertItem> {
    const res = await fetch(`${API_BASE_URL}/alerts/${alertId}/read`, {
      method: "PATCH",
    });
    if (!res.ok) {
      throw new Error(`Failed to mark alert #${alertId} as read`);
    }
    return res.json();
  },

  async simulateAlert(farmId: number, riskType = "Drought", riskScore = 88): Promise<AlertItem> {
    const res = await fetch(`${API_BASE_URL}/alerts/simulate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        farm_id: farmId,
        risk_type: riskType,
        risk_score: riskScore,
      }),
    });
    if (!res.ok) {
      throw new Error("Failed to simulate alert");
    }
    return res.json();
  },
};
