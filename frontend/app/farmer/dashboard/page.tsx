"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { authService } from "@/services/auth";
import { farmService } from "@/services/farms";
import {
  climateService,
  WeatherData,
  SoilData,
  FarmRiskData,
  RiskHistoryItem,
} from "@/services/climate";
import {
  advisoryService,
  AdvisoryData,
  SupportedLanguage,
} from "@/services/advisory";
import { alertService, AlertItem } from "@/services/alerts";
import { Farm, User } from "@/types";
import {
  Sprout,
  Thermometer,
  CloudRain,
  Droplets,
  Wind,
  Layers,
  Activity,
  AlertCircle,
  CheckCircle2,
  Info,
  Calendar,
  MapPin,
  Flame,
  CloudLightning,
  Waves,
  Sun,
  ShieldAlert,
  Clock,
  Database,
  Languages,
  Sparkles,
  ShieldCheck,
  RefreshCw,
  Bell,
  Check,
  ChevronRight,
  LogOut,
  Maximize2,
  ExternalLink,
  PlusCircle,
  Radio,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

// Dynamically import Leaflet Map with SSR disabled
const FarmDisplayMap = dynamic(
  () => import("@/components/FarmDisplayMap").then((mod) => mod.FarmDisplayMap),
  {
    ssr: false,
    loading: () => (
      <div className="h-72 bg-gray-100 animate-pulse rounded-2xl flex items-center justify-center text-xs text-gray-400">
        Loading farm satellite map...
      </div>
    ),
  }
);

const LANGUAGES: { code: SupportedLanguage; label: string; native: string }[] = [
  { code: "en", label: "English", native: "English" },
  { code: "mr", label: "Marathi", native: "मराठी" },
  { code: "hi", label: "Hindi", native: "हिंदी" },
  { code: "kn", label: "Kannada", native: "ಕನ್ನಡ" },
];

export default function FarmerDashboardPage() {
  const router = useRouter();

  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [selectedFarmId, setSelectedFarmId] = useState<number | null>(null);

  const [selectedLang, setSelectedLang] = useState<SupportedLanguage>("en");
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [soil, setSoil] = useState<SoilData | null>(null);
  const [risk, setRisk] = useState<FarmRiskData | null>(null);
  const [history, setHistory] = useState<RiskHistoryItem[]>([]);
  const [advisory, setAdvisory] = useState<AdvisoryData | null>(null);

  // Alerts
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [alertsExpanded, setAlertsExpanded] = useState<boolean>(true);

  // UI state
  const [loadingFarms, setLoadingFarms] = useState<boolean>(true);
  const [loadingTelemetry, setLoadingTelemetry] = useState<boolean>(false);
  const [loadingAdvisory, setLoadingAdvisory] = useState<boolean>(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [notice, setNotice] = useState<{ type: "success" | "error" | "info"; text: string } | null>(null);

  const showNotice = (type: "success" | "error" | "info", text: string) => {
    setNotice({ type, text });
    setTimeout(() => setNotice(null), 5000);
  };

  // 1. Initial Authentication & Farms Load
  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push("/login?redirect=/farmer/dashboard");
      return;
    }

    const user = authService.getUser();
    if (!user) {
      router.push("/login");
      return;
    }
    setCurrentUser(user);
    if (user.preferred_language && ["en", "mr", "hi", "kn"].includes(user.preferred_language)) {
      setSelectedLang(user.preferred_language as SupportedLanguage);
    }

    const fetchFarms = async () => {
      setLoadingFarms(true);
      try {
        const farmList = await farmService.getFarms();
        setFarms(farmList);
        if (farmList.length > 0) {
          setSelectedFarmId(farmList[0].id);
        }
      } catch (err: any) {
        showNotice("error", err.message || "Failed to load farms");
      } finally {
        setLoadingFarms(false);
      }
    };

    fetchFarms();
  }, [router]);

  // Selected farm object
  const selectedFarm = farms.find((f) => f.id === selectedFarmId);

  // 2. Fetch Alerts for Farmer
  const loadAlerts = useCallback(async (farmerId: number) => {
    try {
      const res = await alertService.getAlerts(farmerId);
      setAlerts(res.alerts);
      setUnreadCount(res.unread_count);
    } catch {
      // Non-critical alert load failure
    }
  }, []);

  // 3. Synchronous Farm Telemetry, Risk & Advisory Updates
  const loadFarmData = useCallback(
    async (farmId: number, lang: SupportedLanguage) => {
      setLoadingTelemetry(true);
      try {
        // Parallel requests to backend APIs
        const [wData, sData, rData, hData, aData] = await Promise.all([
          climateService.getWeather(farmId).catch(() => null),
          climateService.getSoil(farmId).catch(() => null),
          climateService.getRiskAssessment(farmId).catch(() => null),
          climateService.getRiskHistory(farmId).catch(() => []),
          advisoryService.getAdvisory(farmId, lang).catch(() => null),
        ]);

        setWeather(wData);
        setSoil(sData);
        setRisk(rData);
        setHistory(hData);
        setAdvisory(aData);

        // Refresh alerts since high-risk predictions auto-create alerts
        if (currentUser?.id) {
          loadAlerts(currentUser.id);
        }
      } catch (err: any) {
        showNotice("error", "Error synchronizing farm intelligence: " + err.message);
      } finally {
        setLoadingTelemetry(false);
      }
    },
    [currentUser?.id, loadAlerts]
  );

  // When selectedFarmId changes, refresh everything
  useEffect(() => {
    if (selectedFarmId) {
      loadFarmData(selectedFarmId, selectedLang);
    }
    if (currentUser?.id) {
      loadAlerts(currentUser.id);
    }
  }, [selectedFarmId, loadFarmData, currentUser?.id, loadAlerts]);

  // Language switch handler (updates advisory only)
  const handleLanguageChange = async (newLang: SupportedLanguage) => {
    setSelectedLang(newLang);
    if (!selectedFarmId) return;

    setLoadingAdvisory(true);
    try {
      const updated = await advisoryService.getAdvisory(selectedFarmId, newLang);
      setAdvisory(updated);
    } catch (err: any) {
      showNotice("error", "Failed to translate advisory: " + err.message);
    } finally {
      setLoadingAdvisory(false);
    }
  };

  // Alert mark as read handler
  const handleMarkAsRead = async (alertId: number) => {
    setActionLoading(`read-${alertId}`);
    try {
      await alertService.markAsRead(alertId);
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, is_read: true } : a))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
      showNotice("success", `Alert #${alertId} marked as read.`);
    } catch (err: any) {
      showNotice("error", err.message || "Failed to update alert");
    } finally {
      setActionLoading(null);
    }
  };

  // Simulate High Risk Alert for demonstration
  const handleSimulateAlert = async () => {
    if (!selectedFarmId) return;
    setActionLoading("simulate-alert");
    try {
      const created = await alertService.simulateAlert(
        selectedFarmId,
        "Extreme Rainfall",
        88
      );
      setAlerts((prev) => [created, ...prev]);
      setUnreadCount((prev) => prev + 1);
      showNotice("success", `New HIGH risk alert created for ${created.farm_name}!`);
    } catch (err: any) {
      showNotice("error", err.message || "Simulation failed");
    } finally {
      setActionLoading(null);
    }
  };

  // Refresh AI Risk Prediction
  const handleRefreshPrediction = async () => {
    if (!selectedFarmId) return;
    setActionLoading("refresh-risk");
    try {
      const refreshedRisk = await climateService.getRiskAssessment(selectedFarmId);
      setRisk(refreshedRisk);
      const refreshedAdvisory = await advisoryService.getAdvisory(selectedFarmId, selectedLang);
      setAdvisory(refreshedAdvisory);
      if (currentUser?.id) {
        await loadAlerts(currentUser.id);
      }
      showNotice("success", "AI risk assessment and advisory refreshed!");
    } catch (err: any) {
      showNotice("error", "Re-prediction failed: " + err.message);
    } finally {
      setActionLoading(null);
    }
  };

  // Chart data formatting
  const chartData = history
    .slice()
    .reverse()
    .map((item, idx) => ({
      name: `Run #${idx + 1}`,
      drought: item.drought_score,
      flood: item.flood_score,
      heat: item.heat_score,
      extreme_rainfall: item.extreme_rainfall_score,
      overall: item.risk_score,
      date: new Date(item.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    }));

  const getRiskBadge = (level?: string) => {
    switch (level?.toUpperCase()) {
      case "HIGH":
        return "bg-rose-100 text-rose-800 border-rose-200";
      case "MEDIUM":
        return "bg-amber-100 text-amber-800 border-amber-200";
      case "LOW":
      default:
        return "bg-emerald-100 text-emerald-800 border-emerald-200";
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans pb-16">
      {/* Top Header / Farmer Identity Banner */}
      <div className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-700 flex items-center justify-center text-white shadow-md">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold text-gray-900 leading-tight">
                  Welcome, {currentUser?.name || "Farmer"}
                </h1>
                <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                  {currentUser?.role || "FARMER"}
                </span>
              </div>
              <p className="text-xs text-gray-500">
                {currentUser?.village ? `${currentUser.village}, ` : ""}
                {currentUser?.district ? `${currentUser.district}, ` : ""}
                {currentUser?.state || "India"} &bull; Mobile: {currentUser?.mobile}
              </p>
            </div>
          </div>

          {/* Quick Actions & Navigation */}
          <div className="flex items-center gap-2 sm:gap-3">
            <Link
              href="/farmer/farms"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <Layers className="w-3.5 h-3.5 text-gray-600" />
              <span>Manage Farms</span>
            </Link>

            <Link
              href="/farmer/climate"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg transition-colors"
            >
              <Activity className="w-3.5 h-3.5 text-emerald-600" />
              <span>Telemetry Hub</span>
            </Link>

            <button
              onClick={() => {
                authService.clearSession();
                router.push("/login");
              }}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-medium text-rose-600 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </div>

      {/* Floating Notice / Toast */}
      {notice && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-3">
          <div
            className={`p-3 rounded-xl border flex items-center justify-between text-sm shadow-sm ${
              notice.type === "success"
                ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                : notice.type === "error"
                ? "bg-rose-50 border-rose-200 text-rose-800"
                : "bg-blue-50 border-blue-200 text-blue-800"
            }`}
          >
            <div className="flex items-center gap-2">
              {notice.type === "success" && <CheckCircle2 className="w-4 h-4 text-emerald-600" />}
              {notice.type === "error" && <AlertCircle className="w-4 h-4 text-rose-600" />}
              {notice.type === "info" && <Info className="w-4 h-4 text-blue-600" />}
              <span>{notice.text}</span>
            </div>
            <button
              onClick={() => setNotice(null)}
              className="text-gray-400 hover:text-gray-600 text-xs px-2 py-0.5"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Main Dashboard Grid */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6 space-y-6">
        {/* =========================================================================
            SECTION 1: Farm Selector & Quick Farm Metadata
           ========================================================================= */}
        <section className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            {/* Multi-Farm Dropdown Selector */}
            <div className="flex-1">
              <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1.5">
                Active Farm Profile ({farms.length} registered)
              </label>
              {loadingFarms ? (
                <div className="h-10 bg-gray-100 animate-pulse rounded-lg w-72" />
              ) : farms.length === 0 ? (
                <div className="flex items-center gap-3">
                  <p className="text-sm text-gray-600">No farms registered yet.</p>
                  <Link
                    href="/farmer/farms"
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-600 hover:text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200"
                  >
                    <PlusCircle className="w-3.5 h-3.5" />
                    Add Your First Farm
                  </Link>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <select
                    value={selectedFarmId || ""}
                    onChange={(e) => setSelectedFarmId(Number(e.target.value))}
                    className="w-full max-w-md px-3.5 py-2.5 bg-gray-50 hover:bg-gray-100 border border-gray-300 rounded-xl font-semibold text-gray-900 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all cursor-pointer"
                  >
                    {farms.map((f) => (
                      <option key={f.id} value={f.id}>
                        {f.farm_name} &bull; {f.crop} ({f.area} acres)
                      </option>
                    ))}
                  </select>
                  <Link
                    href="/farmer/farms"
                    className="hidden sm:inline-flex items-center gap-1 px-3 py-2 text-xs font-medium text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 rounded-xl"
                  >
                    <PlusCircle className="w-3.5 h-3.5 text-emerald-600" />
                    <span>New Farm</span>
                  </Link>
                </div>
              )}
            </div>

            {/* Farm Quick Details Pill Bar */}
            {selectedFarm && (
              <div className="flex flex-wrap items-center gap-2 text-xs text-gray-600 bg-slate-50 p-2.5 rounded-xl border border-gray-200">
                <div className="flex items-center gap-1 px-2 py-1 bg-white rounded-lg border border-gray-100 font-medium">
                  <Sprout className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Crop: <strong className="text-gray-900">{selectedFarm.crop}</strong></span>
                </div>
                <div className="flex items-center gap-1 px-2 py-1 bg-white rounded-lg border border-gray-100 font-medium">
                  <Maximize2 className="w-3.5 h-3.5 text-blue-600" />
                  <span>Area: <strong className="text-gray-900">{selectedFarm.area} acres</strong></span>
                </div>
                <div className="flex items-center gap-1 px-2 py-1 bg-white rounded-lg border border-gray-100 font-medium">
                  <Droplets className="w-3.5 h-3.5 text-teal-600" />
                  <span>Irrigation: <strong className="text-gray-900">{selectedFarm.irrigation_available ? "Yes" : "No"}</strong></span>
                </div>
                <div className="flex items-center gap-1 px-2 py-1 bg-white rounded-lg border border-gray-100 font-medium">
                  <MapPin className="w-3.5 h-3.5 text-rose-500" />
                  <span>
                    {selectedFarm.latitude?.toFixed(3)}°, {selectedFarm.longitude?.toFixed(3)}°
                  </span>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* =========================================================================
            SECTION 2: High-Risk Alerts Banner & Drawer (Step 10 Requirement)
           ========================================================================= */}
        <section className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-4 bg-gradient-to-r from-rose-50 via-amber-50 to-orange-50 border-b border-gray-200 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="relative">
                <div className="w-9 h-9 rounded-xl bg-rose-600 text-white flex items-center justify-center shadow-md shadow-rose-600/20">
                  <Bell className="w-4 h-4" />
                </div>
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-rose-600 text-white rounded-full text-[10px] font-extrabold flex items-center justify-center animate-pulse border-2 border-white">
                    {unreadCount}
                  </span>
                )}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-bold text-gray-900">
                    High-Risk Climate Alerts &amp; Early Warnings
                  </h2>
                  <span className="text-[11px] px-2 py-0.5 rounded-full font-semibold bg-rose-100 text-rose-800 border border-rose-200">
                    {unreadCount} Unread
                  </span>
                </div>
                <p className="text-xs text-gray-600">
                  Automated warnings triggered when farm climate risk reaches <strong>HIGH (71–100)</strong>.
                </p>
              </div>
            </div>

            {/* Alert Controls */}
            <div className="flex items-center gap-2">
              <button
                onClick={handleSimulateAlert}
                disabled={actionLoading === "simulate-alert" || !selectedFarmId}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-rose-700 bg-white hover:bg-rose-100 border border-rose-300 rounded-lg shadow-sm transition-all disabled:opacity-50"
                title="Create a test HIGH-risk warning event"
              >
                <Radio className="w-3.5 h-3.5 text-rose-600 animate-pulse" />
                <span>{actionLoading === "simulate-alert" ? "Simulating..." : "Simulate HIGH Risk Alert"}</span>
              </button>

              <button
                onClick={() => setAlertsExpanded(!alertsExpanded)}
                className="px-2.5 py-1.5 text-xs font-medium text-gray-600 hover:text-gray-900 bg-white rounded-lg border border-gray-200"
              >
                {alertsExpanded ? "Collapse" : "Expand"} ({alerts.length})
              </button>
            </div>
          </div>

          {/* Alerts Content */}
          {alertsExpanded && (
            <div className="p-4 divide-y divide-gray-100 max-h-96 overflow-y-auto">
              {alerts.length === 0 ? (
                <div className="py-6 text-center text-gray-500">
                  <ShieldCheck className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
                  <p className="text-sm font-medium text-gray-800">No active high-risk alerts.</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Your farms are currently operating under safe climate thresholds.
                  </p>
                </div>
              ) : (
                alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={`py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition-colors ${
                      !alert.is_read ? "bg-rose-50/40 -mx-4 px-4" : ""
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs font-bold px-2 py-0.5 rounded bg-rose-600 text-white uppercase tracking-wider">
                          {alert.risk_type} RISK
                        </span>
                        <span className="text-xs font-semibold text-gray-900">
                          {alert.farm_name} &bull; {alert.crop}
                        </span>
                        <span className="text-[11px] font-bold text-rose-700 bg-rose-100 px-1.5 py-0.5 rounded">
                          Score: {alert.risk_score}/100
                        </span>
                        {!alert.is_read ? (
                          <span className="text-[10px] font-semibold text-rose-700 bg-rose-200/70 px-1.5 py-0.5 rounded">
                            UNREAD
                          </span>
                        ) : (
                          <span className="text-[10px] font-medium text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                            Read
                          </span>
                        )}
                        <span className="text-[11px] text-gray-400">
                          {new Date(alert.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-xs text-gray-700 font-medium">
                        {alert.short_explanation}
                      </p>
                      <div className="flex items-center gap-1.5 text-xs text-emerald-800 bg-emerald-50/80 px-2 py-1 rounded-md border border-emerald-200">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                        <span><strong>Action:</strong> {alert.recommended_action}</span>
                      </div>
                    </div>

                    {/* Action Button */}
                    <div className="flex-shrink-0 self-end sm:self-center">
                      {!alert.is_read ? (
                        <button
                          onClick={() => handleMarkAsRead(alert.id)}
                          disabled={actionLoading === `read-${alert.id}`}
                          className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold text-gray-700 bg-white hover:bg-gray-100 border border-gray-300 rounded-lg shadow-sm transition-all"
                        >
                          <Check className="w-3.5 h-3.5 text-emerald-600" />
                          <span>{actionLoading === `read-${alert.id}` ? "Saving..." : "Mark Read"}</span>
                        </button>
                      ) : (
                        <span className="text-xs text-gray-400 font-medium italic flex items-center gap-1">
                          <Check className="w-3 h-3 text-gray-400" /> Acknowledged
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </section>

        {/* =========================================================================
            SECTION 3: AI Climate Risk Assessment & Hazard Gauges
           ========================================================================= */}
        <section className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 pb-3">
            <div>
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-indigo-600" />
                <h2 className="text-base font-bold text-gray-900">
                  AI Farm-Level Climate Risk Assessment
                </h2>
                {risk && (
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${getRiskBadge(
                      risk.risk_level
                    )}`}
                  >
                    {risk.risk_level} RISK ({risk.risk_score}/100)
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500">
                Random Forest ML inference combining microclimate, soil sensors, and regional historical benchmarks.
              </p>
            </div>

            <button
              onClick={handleRefreshPrediction}
              disabled={actionLoading === "refresh-risk" || !selectedFarmId}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${actionLoading === "refresh-risk" ? "animate-spin" : ""}`}
              />
              <span>Re-run AI Assessment</span>
            </button>
          </div>

          {loadingTelemetry ? (
            <div className="h-44 bg-gray-100 animate-pulse rounded-xl" />
          ) : !risk ? (
            <div className="py-8 text-center text-gray-500 text-sm">
              No risk model data available for this farm yet.
            </div>
          ) : (
            <div className="space-y-4">
              {/* 4 Hazard Risk Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
                {/* 1. Drought */}
                <div className="p-3.5 rounded-xl border border-gray-200 bg-gradient-to-br from-white to-amber-50/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-gray-700 flex items-center gap-1.5">
                      <Sun className="w-4 h-4 text-amber-500" />
                      Drought Risk
                    </span>
                    <span className={`text-xs font-extrabold px-1.5 py-0.5 rounded ${getRiskBadge(risk.drought.level)}`}>
                      {risk.drought.level}
                    </span>
                  </div>
                  <div className="flex items-baseline justify-between mb-1.5">
                    <span className="text-2xl font-black text-gray-900">{risk.drought.score}</span>
                    <span className="text-[11px] text-gray-400">/ 100</span>
                  </div>
                  <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        risk.drought.score >= 71
                          ? "bg-rose-500"
                          : risk.drought.score >= 31
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                      }`}
                      style={{ width: `${Math.min(risk.drought.score, 100)}%` }}
                    />
                  </div>
                  <div className="text-[10px] text-gray-500 mt-2 truncate">
                    {risk.drought.contributing_factors?.slice(0, 2).join(", ") || "Normal factors"}
                  </div>
                </div>

                {/* 2. Flood / Waterlogging */}
                <div className="p-3.5 rounded-xl border border-gray-200 bg-gradient-to-br from-white to-blue-50/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-gray-700 flex items-center gap-1.5">
                      <Waves className="w-4 h-4 text-blue-500" />
                      Flood / Waterlogging
                    </span>
                    <span className={`text-xs font-extrabold px-1.5 py-0.5 rounded ${getRiskBadge(risk.flood.level)}`}>
                      {risk.flood.level}
                    </span>
                  </div>
                  <div className="flex items-baseline justify-between mb-1.5">
                    <span className="text-2xl font-black text-gray-900">{risk.flood.score}</span>
                    <span className="text-[11px] text-gray-400">/ 100</span>
                  </div>
                  <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        risk.flood.score >= 71
                          ? "bg-rose-500"
                          : risk.flood.score >= 31
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                      }`}
                      style={{ width: `${Math.min(risk.flood.score, 100)}%` }}
                    />
                  </div>
                  <div className="text-[10px] text-gray-500 mt-2 truncate">
                    {risk.flood.contributing_factors?.slice(0, 2).join(", ") || "Normal factors"}
                  </div>
                </div>

                {/* 3. Heat Stress */}
                <div className="p-3.5 rounded-xl border border-gray-200 bg-gradient-to-br from-white to-rose-50/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-gray-700 flex items-center gap-1.5">
                      <Flame className="w-4 h-4 text-rose-500" />
                      Heat Stress
                    </span>
                    <span className={`text-xs font-extrabold px-1.5 py-0.5 rounded ${getRiskBadge(risk.heat.level)}`}>
                      {risk.heat.level}
                    </span>
                  </div>
                  <div className="flex items-baseline justify-between mb-1.5">
                    <span className="text-2xl font-black text-gray-900">{risk.heat.score}</span>
                    <span className="text-[11px] text-gray-400">/ 100</span>
                  </div>
                  <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        risk.heat.score >= 71
                          ? "bg-rose-500"
                          : risk.heat.score >= 31
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                      }`}
                      style={{ width: `${Math.min(risk.heat.score, 100)}%` }}
                    />
                  </div>
                  <div className="text-[10px] text-gray-500 mt-2 truncate">
                    {risk.heat.contributing_factors?.slice(0, 2).join(", ") || "Normal factors"}
                  </div>
                </div>

                {/* 4. Extreme Rainfall */}
                <div className="p-3.5 rounded-xl border border-gray-200 bg-gradient-to-br from-white to-cyan-50/30 flex flex-col justify-between">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-gray-700 flex items-center gap-1.5">
                      <CloudLightning className="w-4 h-4 text-cyan-600" />
                      Extreme Rainfall
                    </span>
                    <span className={`text-xs font-extrabold px-1.5 py-0.5 rounded ${getRiskBadge(risk.extreme_rainfall.level)}`}>
                      {risk.extreme_rainfall.level}
                    </span>
                  </div>
                  <div className="flex items-baseline justify-between mb-1.5">
                    <span className="text-2xl font-black text-gray-900">{risk.extreme_rainfall.score}</span>
                    <span className="text-[11px] text-gray-400">/ 100</span>
                  </div>
                  <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${
                        risk.extreme_rainfall.score >= 71
                          ? "bg-rose-500"
                          : risk.extreme_rainfall.score >= 31
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                      }`}
                      style={{ width: `${Math.min(risk.extreme_rainfall.score, 100)}%` }}
                    />
                  </div>
                  <div className="text-[10px] text-gray-500 mt-2 truncate">
                    {risk.extreme_rainfall.contributing_factors?.slice(0, 2).join(", ") || "Normal factors"}
                  </div>
                </div>
              </div>

              {/* Main Contributing Factors Bar */}
              <div className="bg-slate-50 p-3 rounded-xl border border-gray-200 flex flex-wrap items-center gap-2">
                <span className="text-xs font-bold text-gray-700 flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                  Primary Contributing Factors:
                </span>
                {risk.main_contributing_factors && risk.main_contributing_factors.length > 0 ? (
                  risk.main_contributing_factors.map((factor, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-2.5 py-0.5 rounded-full bg-white text-gray-800 font-medium border border-gray-200 shadow-2xs"
                    >
                      &bull; {factor}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-gray-500 italic">No adverse risk drivers detected.</span>
                )}
              </div>
            </div>
          )}
        </section>

        {/* =========================================================================
            SECTION 4: Real-time Telemetry (Weather & Soil)
           ========================================================================= */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Weather Telemetry */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">
                  <CloudRain className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-gray-900">Atmospheric Weather</h3>
                  <p className="text-[11px] text-gray-500">Live Microclimate Telemetry</p>
                </div>
              </div>
              <span className="text-[10px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100">
                {weather?.condition || "Partly Cloudy"}
              </span>
            </div>

            {loadingTelemetry ? (
              <div className="h-32 bg-gray-100 animate-pulse rounded-xl" />
            ) : !weather ? (
              <p className="text-xs text-gray-500 py-4">Weather data not available.</p>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-3 bg-slate-50 rounded-xl border border-gray-100">
                  <div className="flex items-center gap-1.5 text-gray-500 mb-1">
                    <Thermometer className="w-3.5 h-3.5 text-rose-500" />
                    <span>Temperature</span>
                  </div>
                  <span className="text-lg font-bold text-gray-900">{weather.temperature}°C</span>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-gray-100">
                  <div className="flex items-center gap-1.5 text-gray-500 mb-1">
                    <Droplets className="w-3.5 h-3.5 text-cyan-500" />
                    <span>Rainfall</span>
                  </div>
                  <span className="text-lg font-bold text-gray-900">{weather.rainfall} mm</span>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-gray-100">
                  <div className="flex items-center gap-1.5 text-gray-500 mb-1">
                    <Activity className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Humidity</span>
                  </div>
                  <span className="text-lg font-bold text-gray-900">{weather.humidity}%</span>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-gray-100">
                  <div className="flex items-center gap-1.5 text-gray-500 mb-1">
                    <Wind className="w-3.5 h-3.5 text-teal-500" />
                    <span>Wind Speed</span>
                  </div>
                  <span className="text-lg font-bold text-gray-900">{weather.wind_speed} km/h</span>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-gray-100 col-span-2 sm:col-span-2">
                  <div className="flex items-center gap-1.5 text-gray-500 mb-1">
                    <CloudRain className="w-3.5 h-3.5 text-blue-500" />
                    <span>48h Forecast Rainfall</span>
                  </div>
                  <span className="text-lg font-bold text-gray-900">
                    {weather.forecast_rainfall} mm
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Soil Telemetry */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center">
                  <Layers className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-gray-900">Soil Health &amp; Moisture</h3>
                  <p className="text-[11px] text-gray-500">Subsurface IoT Sensor Status</p>
                </div>
              </div>
              <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
                {soil?.sensor_status || "Active Sensor Node"}
              </span>
            </div>

            {loadingTelemetry ? (
              <div className="h-32 bg-gray-100 animate-pulse rounded-xl" />
            ) : !soil ? (
              <p className="text-xs text-gray-500 py-4">Soil data not available.</p>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-3 bg-slate-50 rounded-xl border border-gray-100">
                  <div className="flex items-center gap-1.5 text-gray-500 mb-1">
                    <Droplets className="w-3.5 h-3.5 text-teal-600" />
                    <span>Soil Moisture</span>
                  </div>
                  <span className="text-lg font-bold text-gray-900">{soil.soil_moisture}%</span>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-gray-100">
                  <div className="flex items-center gap-1.5 text-gray-500 mb-1">
                    <Layers className="w-3.5 h-3.5 text-amber-700" />
                    <span>Soil Type</span>
                  </div>
                  <span className="text-sm font-bold text-gray-900 truncate block">
                    {soil.soil_type}
                  </span>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-gray-100">
                  <div className="flex items-center gap-1.5 text-gray-500 mb-1">
                    <Activity className="w-3.5 h-3.5 text-blue-600" />
                    <span>Water Avail.</span>
                  </div>
                  <span className="text-sm font-bold text-gray-900 truncate block">
                    {soil.water_availability}
                  </span>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-gray-100 col-span-2 sm:col-span-3 flex items-center justify-between">
                  <div>
                    <span className="text-[11px] text-gray-500 block">Soil Condition &amp; pH</span>
                    <strong className="text-sm text-gray-900">
                      {soil.soil_condition} (pH {soil.ph_level})
                    </strong>
                  </div>
                  <div className="text-right">
                    <span className="text-[11px] text-gray-500 block">Organic Carbon</span>
                    <strong className="text-sm text-gray-900">{soil.organic_matter_pct}%</strong>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* =========================================================================
            SECTION 5: Personalized Multilingual Advisory Engine
           ========================================================================= */}
        <section className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 pb-3">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-emerald-600" />
                <h2 className="text-base font-bold text-gray-900">
                  Personalized Agronomic Advisory Engine
                </h2>
                {advisory && (
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
                    Urgency: {advisory.urgency}
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500">
                Actionable agronomic guidance generated for {selectedFarm?.crop || "your crop"} based on AI risk prediction.
              </p>
            </div>

            {/* Language Selector Buttons */}
            <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl border border-gray-200">
              <Languages className="w-4 h-4 text-gray-500 ml-1.5 mr-0.5" />
              {LANGUAGES.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => handleLanguageChange(lang.code)}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-lg transition-all ${
                    selectedLang === lang.code
                      ? "bg-emerald-600 text-white shadow-xs"
                      : "text-gray-600 hover:text-gray-900 hover:bg-white"
                  }`}
                >
                  {lang.native}
                </button>
              ))}
            </div>
          </div>

          {loadingAdvisory ? (
            <div className="h-40 bg-gray-100 animate-pulse rounded-xl" />
          ) : !advisory ? (
            <div className="py-6 text-center text-gray-500 text-sm">
              Advisory is generating...
            </div>
          ) : (
            <div className="space-y-4">
              {/* Advisory Title & Urgency Box */}
              <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200/80">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                  <h3 className="text-base font-bold text-emerald-950">
                    {advisory.title}
                  </h3>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="flex items-center gap-1 text-emerald-800 font-semibold">
                      <Clock className="w-3.5 h-3.5 text-emerald-600" />
                      Window: {advisory.time_window}
                    </span>
                  </div>
                </div>
                <p className="text-xs text-emerald-900 leading-relaxed font-medium">
                  {advisory.explanation}
                </p>
              </div>

              {/* Recommendations & Preventive Actions Two Columns */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Crop-specific recommendations */}
                <div className="p-4 rounded-xl border border-gray-200 bg-white">
                  <div className="flex items-center gap-2 mb-3 text-xs font-bold text-gray-800">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    <span>Crop-Specific Actions ({selectedFarm?.crop})</span>
                  </div>
                  <ul className="space-y-2">
                    {advisory.recommendations?.map((item, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-xs text-gray-700">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                        <span className="leading-snug">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Long-term Preventive Measures */}
                <div className="p-4 rounded-xl border border-gray-200 bg-white">
                  <div className="flex items-center gap-2 mb-3 text-xs font-bold text-gray-800">
                    <ShieldCheck className="w-4 h-4 text-teal-600" />
                    <span>Long-Term Preventive Measures</span>
                  </div>
                  <ul className="space-y-2">
                    {advisory.preventive_actions?.map((item, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-xs text-gray-700">
                        <span className="w-1.5 h-1.5 rounded-full bg-teal-500 mt-1.5 flex-shrink-0" />
                        <span className="leading-snug">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* =========================================================================
            SECTION 6: Interactive Farm Map & Risk Trends Chart
           ========================================================================= */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Interactive Leaflet Farm Map */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm space-y-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-emerald-600" />
                  <h3 className="text-sm font-bold text-gray-900">
                    Farm Geo-Location Map
                  </h3>
                </div>
                <span className="text-[10px] text-gray-500">
                  {selectedFarm?.latitude?.toFixed(4)}° N, {selectedFarm?.longitude?.toFixed(4)}° E
                </span>
              </div>
              <p className="text-xs text-gray-500 mb-3">
                Selected farm pin synced with GPS coordinates and parcel boundaries.
              </p>
            </div>

            <div className="rounded-xl overflow-hidden border border-gray-200 shadow-inner">
              <FarmDisplayMap
                latitude={selectedFarm?.latitude}
                longitude={selectedFarm?.longitude}
                farmName={selectedFarm?.farm_name || "Farm"}
                crop={selectedFarm?.crop}
                area={selectedFarm?.area}
              />
            </div>
          </div>

          {/* Recharts AI Risk History Chart */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-sm space-y-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-indigo-600" />
                  <h3 className="text-sm font-bold text-gray-900">
                    AI Risk Evolution History
                  </h3>
                </div>
                <span className="text-[10px] text-gray-500">
                  Last {chartData.length} Assessments
                </span>
              </div>
              <p className="text-xs text-gray-500 mb-3">
                Historical multi-hazard progression across prediction runs.
              </p>
            </div>

            <div className="h-72 w-full pt-2">
              {chartData.length === 0 ? (
                <div className="h-full flex items-center justify-center text-xs text-gray-400">
                  No previous risk inference runs found.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorDrought" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorFlood" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorHeat" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorExtreme" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#64748b" }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "#64748b" }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#ffffff",
                        borderColor: "#e2e8f0",
                        borderRadius: "10px",
                        fontSize: "12px",
                        boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                      }}
                    />
                    <Legend
                      verticalAlign="top"
                      height={36}
                      wrapperStyle={{ fontSize: "11px", fontWeight: 600 }}
                    />
                    <Area
                      type="monotone"
                      dataKey="drought"
                      name="Drought"
                      stroke="#f59e0b"
                      fillOpacity={1}
                      fill="url(#colorDrought)"
                    />
                    <Area
                      type="monotone"
                      dataKey="flood"
                      name="Flood"
                      stroke="#3b82f6"
                      fillOpacity={1}
                      fill="url(#colorFlood)"
                    />
                    <Area
                      type="monotone"
                      dataKey="heat"
                      name="Heat"
                      stroke="#ef4444"
                      fillOpacity={1}
                      fill="url(#colorHeat)"
                    />
                    <Area
                      type="monotone"
                      dataKey="extreme_rainfall"
                      name="Extreme Rain"
                      stroke="#06b6d4"
                      fillOpacity={1}
                      fill="url(#colorExtreme)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
