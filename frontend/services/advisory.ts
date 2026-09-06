const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined" ? "/api" : "http://127.0.0.1:8000/api");

export type SupportedLanguage = "en" | "mr" | "hi" | "kn";

export interface AdvisoryData {
  id?: number;
  farm_id: number;
  farm_name?: string;
  crop: string;
  risk_type: string;
  risk_score: number;
  risk_level: string;
  title: string;
  explanation: string;
  recommendations: string[];
  preventive_actions: string[];
  urgency: string;
  time_window: string;
  language: SupportedLanguage;
  created_at?: string;
}

export const advisoryService = {
  async getAdvisory(farmId: number, lang: SupportedLanguage = "en"): Promise<AdvisoryData> {
    const res = await fetch(`${API_BASE_URL}/advisories/${farmId}?lang=${lang}`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`Failed to fetch advisory for farm #${farmId}`);
    }
    return res.json();
  },

  async generateAdvisory(
    farmId: number,
    lang: SupportedLanguage = "en",
    crop?: string,
    riskType?: string,
    riskLevel?: string
  ): Promise<AdvisoryData> {
    const res = await fetch(`${API_BASE_URL}/advisories/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        farm_id: farmId,
        language: lang,
        crop: crop || undefined,
        risk_type: riskType || undefined,
        risk_level: riskLevel || undefined,
      }),
    });
    if (!res.ok) {
      throw new Error(`Failed to generate advisory for farm #${farmId}`);
    }
    return res.json();
  },
};
