"use client";

import React, { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { authService } from "@/services/auth";
import { farmService } from "@/services/farms";
import {
  climateService,
  WeatherData,
  SoilData,
  HistoricalClimatePoint,
  FarmRiskData,
  RiskHistoryItem,
} from "@/services/climate";
import {
  advisoryService,
  AdvisoryData,
  SupportedLanguage,
} from "@/services/advisory";
import { Farm, User } from "@/types";
import {
  Sprout,
  Thermometer,
  CloudRain,
  Droplets,
  Wind,
  Layers,
  Activity,
  ArrowLeft,
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
  HelpCircle,
  Clock,
  Database,
  Languages,
  Sparkles,
  ShieldCheck,
  RefreshCw,
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

const LANGUAGES: { code: SupportedLanguage; label: string; native: string }[] = [
  { code: "en", label: "English", native: "English" },
  { code: "mr", label: "Marathi", native: "मराठी" },
  { code: "hi", label: "Hindi", native: "हिंदी" },
  { code: "kn", label: "Kannada", native: "ಕನ್ನಡ" },
];

function ClimateDataContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialFarmId = searchParams.get("farmId");

  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [selectedFarmId, setSelectedFarmId] = useState<number | null>(
    initialFarmId ? parseInt(initialFarmId) : null
  );

  const [selectedLang, setSelectedLang] = useState<SupportedLanguage>("en");
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [soil, setSoil] = useState<SoilData | null>(null);
  const [history, setHistory] = useState<HistoricalClimatePoint[]>([]);
  const [riskData, setRiskData] = useState<FarmRiskData | null>(null);
  const [riskHistory, setRiskHistory] = useState<RiskHistoryItem[]>([]);
  const [advisory, setAdvisory] = useState<AdvisoryData | null>(null);
  const [activeScenario, setActiveScenario] = useState<string>("LIVE");

  const [loadingFarms, setLoadingFarms] = useState(true);
  const [loadingData, setLoadingData] = useState(false);
  const [loadingAdvisory, setLoadingAdvisory] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initial load: Auth check & get farmer's farms
  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push("/login");
      return;
    }
    setCurrentUser(authService.getUser());

    const fetchFarms = async () => {
      setLoadingFarms(true);
      try {
        const list = await farmService.getFarms();
        setFarms(list);
        if (list.length > 0) {
          if (initialFarmId && list.some((f) => f.id === parseInt(initialFarmId))) {
            setSelectedFarmId(parseInt(initialFarmId));
          } else {
            setSelectedFarmId(list[0].id);
          }
        }
      } catch (err: any) {
        setError(err.message || "Failed to load farms list");
      } finally {
        setLoadingFarms(false);
      }
    };

    fetchFarms();
  }, [router, initialFarmId]);

  // Load telemetry & risk assessment when selectedFarmId changes
  useEffect(() => {
    if (!selectedFarmId) return;

    const fetchTelemetryAndRisk = async () => {
      setLoadingData(true);
      setError(null);
      try {
        const [wData, sData, hData, rData, histList] = await Promise.all([
          climateService.getWeather(selectedFarmId),
          climateService.getSoil(selectedFarmId),
          climateService.getHistorical(selectedFarmId),
          climateService.getRiskAssessment(selectedFarmId),
          climateService.getRiskHistory(selectedFarmId),
        ]);
        setWeather(wData);
        setSoil(sData);
        setHistory(hData);
        setRiskData(rData);
        setRiskHistory(histList);
      } catch (err: any) {
        setError(err.message || "Failed to fetch telemetry data for selected farm");
      } finally {
        setLoadingData(false);
      }
    };

    fetchTelemetryAndRisk();
  }, [selectedFarmId]);

  // Load personalized multilingual advisory when farm or language changes
  useEffect(() => {
    if (!selectedFarmId) return;

    const fetchAdvisory = async () => {
      setLoadingAdvisory(true);
      try {
        const adv = await advisoryService.getAdvisory(selectedFarmId, selectedLang);
        setAdvisory(adv);
        setActiveScenario("LIVE");
      } catch (err: any) {
        console.error("Failed to load advisory", err);
      } finally {
        setLoadingAdvisory(false);
      }
    };

    fetchAdvisory();
  }, [selectedFarmId, selectedLang]);

  const handleScenarioChange = async (scenario: string, crop?: string, risk?: string) => {
    if (!selectedFarmId) return;
    setLoadingAdvisory(true);
    setActiveScenario(scenario);
    try {
      const adv = await advisoryService.generateAdvisory(
        selectedFarmId,
        selectedLang,
        crop,
        risk,
        crop ? "HIGH" : undefined
      );
      setAdvisory(adv);
    } catch (err: any) {
      setError(err.message || "Failed to switch advisory scenario");
    } finally {
      setLoadingAdvisory(false);
    }
  };

  const selectedFarm = farms.find((f) => f.id === selectedFarmId);

  const getLevelBadgeClass = (level: string) => {
    if (level === "HIGH") {
      return "bg-rose-100 text-rose-800 border-rose-200";
    } else if (level === "MEDIUM") {
      return "bg-amber-100 text-amber-800 border-amber-200";
    }
    return "bg-emerald-100 text-emerald-800 border-emerald-200";
  };

  const getLevelProgressBarClass = (level: string) => {
    if (level === "HIGH") {
      return "bg-rose-600";
    } else if (level === "MEDIUM") {
      return "bg-amber-500";
    }
    return "bg-emerald-500";
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header Bar */}
      <header className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <Link
                href="/farmer/farms"
                className="p-2 rounded-xl text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
                title="Back to Farms"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <Link href="/" className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center">
                  <Sprout className="w-4 h-4 text-emerald-100" />
                </div>
                <span className="text-lg font-black text-gray-900 tracking-tight">
                  Krushi<span className="text-emerald-700">Rakshak</span>
                </span>
              </Link>
              <span className="hidden sm:inline-block text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                Climate &amp; AI Risk Engine
              </span>
            </div>

            {/* Language Selector & Navigation */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 bg-gray-100 px-2 py-1.5 rounded-xl border border-gray-200">
                <Languages className="w-4 h-4 text-emerald-700 shrink-0" />
                <select
                  value={selectedLang}
                  onChange={(e) => setSelectedLang(e.target.value as SupportedLanguage)}
                  className="bg-transparent text-xs font-bold text-gray-800 focus:outline-none cursor-pointer pr-1"
                  aria-label="Select Advisory Language"
                >
                  {LANGUAGES.map((l) => (
                    <option key={l.code} value={l.code}>
                      {l.native} ({l.label})
                    </option>
                  ))}
                </select>
              </div>

              <Link
                href="/farmer/dashboard"
                className="inline-block text-xs font-semibold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 px-2.5 py-1 rounded-lg border border-emerald-200"
              >
                Dashboard
              </Link>
              <Link
                href="/farmer/farms"
                className="hidden sm:inline-block text-xs font-semibold text-emerald-700 hover:text-emerald-900"
              >
                Manage Farms →
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-grow max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-center gap-3 text-rose-800 text-sm">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Farm Selector Bar */}
        <div className="bg-white p-5 sm:p-6 rounded-2xl border border-gray-200/90 shadow-sm mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">
              Select Monitored Farm Parcel
            </label>
            {loadingFarms ? (
              <div className="h-10 w-64 bg-gray-100 animate-pulse rounded-xl" />
            ) : farms.length === 0 ? (
              <div className="text-sm text-gray-500">
                No farms registered.{" "}
                <Link href="/farmer/farms" className="text-emerald-700 font-semibold underline">
                  Add a farm first
                </Link>
              </div>
            ) : (
              <select
                value={selectedFarmId || ""}
                onChange={(e) => setSelectedFarmId(parseInt(e.target.value))}
                className="w-full sm:w-80 px-4 py-2.5 text-sm font-semibold text-gray-900 border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none bg-white shadow-sm"
              >
                {farms.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.farm_name} ({f.crop} - {f.area} acres)
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Farm Quick Summary Pill */}
          {selectedFarm && (
            <div className="flex flex-wrap items-center gap-3 text-xs text-gray-600 bg-gray-50 p-3 rounded-xl border border-gray-100">
              <span className="font-semibold text-gray-900">{selectedFarm.crop}</span>
              <span className="text-gray-300">•</span>
              <span>{selectedFarm.area} acres</span>
              <span className="text-gray-300">•</span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-emerald-600" />
                {selectedFarm.latitude && selectedFarm.longitude
                  ? `${selectedFarm.latitude.toFixed(4)}°, ${selectedFarm.longitude.toFixed(4)}°`
                  : "Coordinates unset"}
              </span>
            </div>
          )}
        </div>

        {/* Telemetry & Risk Grid */}
        {loadingData ? (
          <div className="space-y-6 animate-pulse">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-44 bg-white rounded-2xl border border-gray-200 p-6" />
              ))}
            </div>
            <div className="h-72 bg-white rounded-2xl border border-gray-200 p-6" />
          </div>
        ) : weather && soil && riskData ? (
          <div className="space-y-8">
            {/* AI CLIMATE RISK PREDICTION ENGINE SECTION */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-emerald-700" />
                    <span>AI Climate Risk Assessment</span>
                  </h2>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Continuous ensemble random forest risk modeling based on current telemetry and 14-day trends.
                  </p>
                </div>
                <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-100/70 px-2.5 py-1 rounded-full border border-emerald-200">
                  Model: Random Forest Ensemble v1.0
                </span>
              </div>

              {/* RISK EXPLANATION OVERVIEW BANNER */}
              <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 rounded-2xl p-6 text-white shadow-md border border-slate-700/60 mb-6">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2.5">
                      <span className="text-xs uppercase font-bold tracking-wider text-emerald-400 bg-emerald-950/70 border border-emerald-800/80 px-2.5 py-0.5 rounded-full">
                        AI Risk Explanation
                      </span>
                      {riskData.id && (
                        <span className="text-[11px] text-slate-300 flex items-center gap-1.5 bg-slate-800/80 px-2.5 py-0.5 rounded-full border border-slate-700">
                          <Database className="w-3 h-3 text-emerald-400" />
                          Logged in PostgreSQL (Prediction #{riskData.id})
                        </span>
                      )}
                    </div>

                    <div className="flex flex-wrap items-baseline gap-3">
                      <h3 className="text-2xl font-black tracking-tight text-white">
                        Dominant Threat: <span className="text-emerald-300">{riskData.highest_risk_type}</span>
                      </h3>
                      <span className={`text-xs font-black px-2.5 py-1 rounded-full border uppercase ${getLevelBadgeClass(riskData.overall_risk)}`}>
                        {riskData.overall_risk} OVERALL ({riskData.risk_score}/100)
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
                      Farm vulnerability status: <strong className="text-white">{riskData.overall_risk}</strong>. The leading driver is{" "}
                      <strong className="text-white">{riskData.highest_risk_type}</strong> scoring{" "}
                      <strong className="text-white">{riskData.risk_score}/100</strong> ({riskData.risk_level}). Real-time telemetry was processed by the Scikit-learn Random Forest ensemble and stored in database.
                    </p>
                  </div>

                  {/* Meter Card */}
                  <div className="shrink-0 bg-slate-800/90 border border-slate-700 p-4 rounded-xl flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Hazard Index</div>
                      <div className="text-3xl font-black text-white">{riskData.risk_score}<span className="text-xs font-normal text-slate-400">/100</span></div>
                    </div>
                    <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-xl">
                      {riskData.overall_risk === "HIGH" ? "⚠️" : riskData.overall_risk === "MEDIUM" ? "⚡" : "🛡️"}
                    </div>
                  </div>
                </div>

                {/* Main Contributing Factors */}
                <div className="mt-5 pt-4 border-t border-slate-700/80">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
                    Primary Contributing Factors:
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {riskData.main_contributing_factors.map((factor, i) => (
                      <div key={i} className="flex items-start gap-2 text-xs text-slate-200 bg-slate-800/60 p-2.5 rounded-lg border border-slate-700/60">
                        <span className="text-emerald-400 font-bold mt-0.5">•</span>
                        <span>{factor}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* 4 Risk Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* 1. DROUGHT RISK */}
                <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center">
                        <Sun className="w-5 h-5" />
                      </div>
                      <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${getLevelBadgeClass(riskData.drought.level)}`}>
                        {riskData.drought.level} RISK
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-gray-900 mt-2">Drought</h3>
                    <div className="flex items-baseline gap-1 mt-1">
                      <span className="text-3xl font-black text-gray-900">{riskData.drought.score}</span>
                      <span className="text-xs font-semibold text-gray-400">/ 100</span>
                    </div>

                    <div className="w-full bg-gray-100 h-2 rounded-full mt-3 overflow-hidden">
                      <div
                        className={`h-2 rounded-full transition-all duration-700 ${getLevelProgressBarClass(riskData.drought.level)}`}
                        style={{ width: `${riskData.drought.score}%` }}
                      />
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-gray-100">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
                      Contributing Factors:
                    </span>
                    <ul className="space-y-1 text-xs text-gray-600">
                      {riskData.drought.contributing_factors.map((f, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <span className="text-amber-500 font-bold">•</span>
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* 2. FLOOD RISK */}
                <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="w-10 h-10 rounded-xl bg-cyan-50 text-cyan-700 flex items-center justify-center">
                        <Waves className="w-5 h-5" />
                      </div>
                      <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${getLevelBadgeClass(riskData.flood.level)}`}>
                        {riskData.flood.level} RISK
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-gray-900 mt-2">Flood / Inundation</h3>
                    <div className="flex items-baseline gap-1 mt-1">
                      <span className="text-3xl font-black text-gray-900">{riskData.flood.score}</span>
                      <span className="text-xs font-semibold text-gray-400">/ 100</span>
                    </div>

                    <div className="w-full bg-gray-100 h-2 rounded-full mt-3 overflow-hidden">
                      <div
                        className={`h-2 rounded-full transition-all duration-700 ${getLevelProgressBarClass(riskData.flood.level)}`}
                        style={{ width: `${riskData.flood.score}%` }}
                      />
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-gray-100">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
                      Contributing Factors:
                    </span>
                    <ul className="space-y-1 text-xs text-gray-600">
                      {riskData.flood.contributing_factors.map((f, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <span className="text-cyan-600 font-bold">•</span>
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* 3. HEAT STRESS RISK */}
                <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="w-10 h-10 rounded-xl bg-rose-50 text-rose-700 flex items-center justify-center">
                        <Flame className="w-5 h-5" />
                      </div>
                      <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${getLevelBadgeClass(riskData.heat.level)}`}>
                        {riskData.heat.level} RISK
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-gray-900 mt-2">Heat Stress</h3>
                    <div className="flex items-baseline gap-1 mt-1">
                      <span className="text-3xl font-black text-gray-900">{riskData.heat.score}</span>
                      <span className="text-xs font-semibold text-gray-400">/ 100</span>
                    </div>

                    <div className="w-full bg-gray-100 h-2 rounded-full mt-3 overflow-hidden">
                      <div
                        className={`h-2 rounded-full transition-all duration-700 ${getLevelProgressBarClass(riskData.heat.level)}`}
                        style={{ width: `${riskData.heat.score}%` }}
                      />
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-gray-100">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
                      Contributing Factors:
                    </span>
                    <ul className="space-y-1 text-xs text-gray-600">
                      {riskData.heat.contributing_factors.map((f, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <span className="text-rose-500 font-bold">•</span>
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* 4. EXTREME RAINFALL RISK */}
                <div className="bg-white p-5 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center">
                        <CloudLightning className="w-5 h-5" />
                      </div>
                      <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${getLevelBadgeClass(riskData.extreme_rainfall.level)}`}>
                        {riskData.extreme_rainfall.level} RISK
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-gray-900 mt-2">Extreme Rainfall</h3>
                    <div className="flex items-baseline gap-1 mt-1">
                      <span className="text-3xl font-black text-gray-900">{riskData.extreme_rainfall.score}</span>
                      <span className="text-xs font-semibold text-gray-400">/ 100</span>
                    </div>

                    <div className="w-full bg-gray-100 h-2 rounded-full mt-3 overflow-hidden">
                      <div
                        className={`h-2 rounded-full transition-all duration-700 ${getLevelProgressBarClass(riskData.extreme_rainfall.level)}`}
                        style={{ width: `${riskData.extreme_rainfall.score}%` }}
                      />
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-gray-100">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400 block mb-1">
                      Contributing Factors:
                    </span>
                    <ul className="space-y-1 text-xs text-gray-600">
                      {riskData.extreme_rainfall.contributing_factors.map((f, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <span className="text-blue-500 font-bold">•</span>
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            {/* PERSONALIZED MULTILINGUAL ADVISORY SECTION (STEPS 8 & 9) */}
            <div className="bg-white rounded-2xl border-2 border-emerald-600/30 p-6 sm:p-7 shadow-sm">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-gray-100">
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 bg-emerald-100 px-3 py-1 rounded-full flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-emerald-700" />
                      {selectedLang === "mr"
                        ? "एआय वैयक्तिक पीक सल्ला"
                        : selectedLang === "hi"
                        ? "एआई व्यक्तिगत फसल परामर्श"
                        : selectedLang === "kn"
                        ? "ವೈಯಕ್ತಿಕ ಬೆಳೆ ಕೃಷಿ ಸಲಹೆ"
                        : "AI Personalized Crop Advisory"}
                    </span>
                    {advisory?.id && (
                      <span className="text-[11px] font-semibold text-gray-500 bg-gray-100 px-2.5 py-1 rounded-full border border-gray-200 flex items-center gap-1">
                        <Database className="w-3 h-3 text-emerald-600" />
                        Log #{advisory.id} (PostgreSQL)
                      </span>
                    )}
                  </div>
                  <h2 className="text-xl font-black text-gray-900 tracking-tight">
                    {advisory ? advisory.title : "Generating Tailored Advisory..."}
                  </h2>
                </div>

                {/* Multilingual Quick Switcher & Urgency Pill */}
                <div className="flex flex-wrap items-center gap-2">
                  <div className="flex items-center bg-gray-100 p-1 rounded-xl border border-gray-200">
                    {LANGUAGES.map((lang) => (
                      <button
                        key={lang.code}
                        type="button"
                        onClick={() => setSelectedLang(lang.code)}
                        className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                          selectedLang === lang.code
                            ? "bg-white text-emerald-800 shadow-sm border border-emerald-200"
                            : "text-gray-500 hover:text-gray-900"
                        }`}
                      >
                        {lang.native}
                      </button>
                    ))}
                  </div>

                  {advisory && (
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-black px-3 py-1.5 rounded-xl border uppercase ${getLevelBadgeClass(advisory.risk_level)}`}>
                        {advisory.urgency}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Advisory Body */}
              {loadingAdvisory ? (
                <div className="py-8 space-y-3 animate-pulse">
                  <div className="h-4 bg-gray-100 rounded-full w-3/4" />
                  <div className="h-4 bg-gray-100 rounded-full w-5/6" />
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
                    <div className="h-36 bg-gray-50 rounded-xl" />
                    <div className="h-36 bg-gray-50 rounded-xl" />
                  </div>
                </div>
              ) : advisory ? (
                <div className="mt-5 space-y-6">
                  {/* Context Explanation */}
                  <div className="p-4 rounded-xl bg-emerald-50/60 border border-emerald-100 text-xs text-emerald-950 leading-relaxed">
                    <p>{advisory.explanation}</p>
                    <div className="mt-2.5 flex flex-wrap items-center gap-4 text-[11px] font-semibold text-emerald-800">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-emerald-600" />
                        {selectedLang === "mr" ? "योग्य वेळ:" : selectedLang === "hi" ? "उपयुक्त समय सीमा:" : selectedLang === "kn" ? "ಸೂಕ್ತ ಸಮಯ:" : "Execution Window:"}{" "}
                        <strong className="text-gray-900 ml-1">{advisory.time_window}</strong>
                      </span>
                      <span>•</span>
                      <span>
                        {selectedLang === "mr" ? "लक्षित पीक:" : selectedLang === "hi" ? "लक्षित फसल:" : selectedLang === "kn" ? "ಗುರಿ ಬೆಳೆ:" : "Target Crop:"}{" "}
                        <strong className="text-gray-900">{advisory.crop}</strong>
                      </span>
                      <span>•</span>
                      <span>
                        {selectedLang === "mr" ? "धोका प्रकार:" : selectedLang === "hi" ? "जोखिम प्रकार:" : selectedLang === "kn" ? "ಅಪಾಯದ ವಿಧ:" : "Threat Mode:"}{" "}
                        <strong className="text-gray-900">{advisory.risk_type} ({advisory.risk_score}/100)</strong>
                      </span>
                    </div>
                  </div>

                  {/* Recommendations & Preventive Actions Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Recommendations */}
                    <div className="p-5 rounded-2xl bg-white border border-gray-200 shadow-sm">
                      <h4 className="text-sm font-bold text-gray-900 flex items-center gap-2 mb-3">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        <span>
                          {selectedLang === "mr"
                            ? "पिकासाठी विशेष कृषी शिफारशी"
                            : selectedLang === "hi"
                            ? "फसल-विशिष्ट कृषि सिफारिशें"
                            : selectedLang === "kn"
                            ? "ಬೆಳೆ-ನಿರ್ದಿಷ್ಟ ಕೃಷಿ ಶಿಫಾರಸುಗಳು"
                            : "Crop-Specific Action Recommendations"}
                        </span>
                      </h4>
                      <ul className="space-y-2.5 text-xs text-gray-700 leading-relaxed">
                        {advisory.recommendations.map((rec, i) => (
                          <li key={i} className="flex items-start gap-2.5">
                            <span className="w-5 h-5 rounded-full bg-emerald-50 text-emerald-700 font-bold flex items-center justify-center shrink-0 mt-0.5 text-[10px]">
                              {i + 1}
                            </span>
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Preventive Actions */}
                    <div className="p-5 rounded-2xl bg-white border border-gray-200 shadow-sm">
                      <h4 className="text-sm font-bold text-gray-900 flex items-center gap-2 mb-3">
                        <ShieldCheck className="w-4 h-4 text-sky-600" />
                        <span>
                          {selectedLang === "mr"
                            ? "प्रतिबंधात्मक उपाययोजना व शेत संरक्षण"
                            : selectedLang === "hi"
                            ? "निवारक उपाय एवं खेत सुरक्षा"
                            : selectedLang === "kn"
                            ? "ಮುನ್ನೆಚ್ಚರಿಕೆ ಕ್ರಮಗಳು ಮತ್ತು ಸಂರಕ್ಷಣೆ"
                            : "Preventive Interventions & Field Protection"}
                        </span>
                      </h4>
                      <ul className="space-y-2.5 text-xs text-gray-700 leading-relaxed">
                        {advisory.preventive_actions.map((act, i) => (
                          <li key={i} className="flex items-start gap-2.5">
                            <span className="w-5 h-5 rounded-full bg-sky-50 text-sky-700 font-bold flex items-center justify-center shrink-0 mt-0.5 text-[10px]">
                              ✓
                            </span>
                            <span>{act}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Dynamic Scenario Tester Bar */}
                  <div className="pt-4 border-t border-gray-100 flex flex-wrap items-center justify-between gap-3 text-xs">
                    <span className="text-gray-500 font-semibold">
                      {selectedLang === "mr"
                        ? "पीक किंवा हवामान धोका बदलून सल्ला तपासा:"
                        : selectedLang === "hi"
                        ? "फसल या मौसम जोखिम बदलकर परामर्श जांचें:"
                        : selectedLang === "kn"
                        ? "ಬೆಳೆ ಅಥವಾ ಹವಾಮಾನ ಅಪಾಯ ಬದಲಾಯಿಸಿ ಸಲಹೆ ಪರೀಕ್ಷಿಸಿ:"
                        : "Test dynamic advisory response across crop & risk combinations:"}
                    </span>
                    <div className="flex flex-wrap items-center gap-2">
                      <button
                        type="button"
                        onClick={() => handleScenarioChange("SOY_DROUGHT", "Soybean", "Drought")}
                        className={`px-3 py-1 rounded-lg border text-xs font-semibold transition-colors ${
                          activeScenario === "SOY_DROUGHT"
                            ? "bg-amber-100 text-amber-900 border-amber-300"
                            : "bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100"
                        }`}
                      >
                        Soybean + Drought
                      </button>
                      <button
                        type="button"
                        onClick={() => handleScenarioChange("COTTON_FLOOD", "Cotton", "Flood")}
                        className={`px-3 py-1 rounded-lg border text-xs font-semibold transition-colors ${
                          activeScenario === "COTTON_FLOOD"
                            ? "bg-cyan-100 text-cyan-900 border-cyan-300"
                            : "bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100"
                        }`}
                      >
                        Cotton + Flood
                      </button>
                      <button
                        type="button"
                        onClick={() => handleScenarioChange("WHEAT_HEAT", "Wheat", "Heat Stress")}
                        className={`px-3 py-1 rounded-lg border text-xs font-semibold transition-colors ${
                          activeScenario === "WHEAT_HEAT"
                            ? "bg-rose-100 text-rose-900 border-rose-300"
                            : "bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100"
                        }`}
                      >
                        Wheat + Heat
                      </button>
                      <button
                        type="button"
                        onClick={() => handleScenarioChange("LIVE")}
                        className={`px-3 py-1 rounded-lg border text-xs font-semibold transition-colors flex items-center gap-1 ${
                          activeScenario === "LIVE"
                            ? "bg-emerald-100 text-emerald-900 border-emerald-300"
                            : "bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100"
                        }`}
                      >
                        <RefreshCw className="w-3 h-3 text-emerald-700" />
                        Sync Farm Live Telemetry
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-6 text-center text-xs text-gray-500">
                  Select a farm to generate personalized multilingual advisories.
                </div>
              )}
            </div>

            {/* TELEMETRY READINGS SECTION */}
            <div>
              <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-emerald-700" />
                <span>Micro-Climate &amp; Soil Telemetry Readings</span>
              </h2>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Temperature */}
                <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
                      <Thermometer className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded">
                      Temperature
                    </span>
                  </div>
                  <div>
                    <div className="flex items-baseline gap-1">
                      <span className="text-3xl font-black text-gray-900">{weather.temperature}</span>
                      <span className="text-lg font-bold text-gray-400">°C</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1 font-medium">{weather.condition}</p>
                  </div>
                  <div className="mt-3 pt-2 border-t border-gray-100 text-[11px] text-gray-400 flex items-center gap-1">
                    <Wind className="w-3.5 h-3.5" /> {weather.wind_speed} km/h wind
                  </div>
                </div>

                {/* Rainfall */}
                <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center">
                      <CloudRain className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-semibold text-sky-700 bg-sky-50 px-2 py-0.5 rounded">
                      Rainfall
                    </span>
                  </div>
                  <div>
                    <div className="flex items-baseline gap-1">
                      <span className="text-3xl font-black text-gray-900">{weather.rainfall}</span>
                      <span className="text-lg font-bold text-gray-400">mm</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1 font-medium">Current precip</p>
                  </div>
                  <div className="mt-3 pt-2 border-t border-gray-100 text-[11px] text-sky-800 font-semibold">
                    24h Forecast: {weather.forecast_rainfall} mm
                  </div>
                </div>

                {/* Humidity */}
                <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-600 flex items-center justify-center">
                      <Droplets className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-semibold text-teal-700 bg-teal-50 px-2 py-0.5 rounded">
                      Humidity
                    </span>
                  </div>
                  <div>
                    <div className="flex items-baseline gap-1">
                      <span className="text-3xl font-black text-gray-900">{weather.humidity}</span>
                      <span className="text-lg font-bold text-gray-400">%</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1 font-medium">Relative humidity</p>
                  </div>
                  <div className="mt-3 pt-2 border-t border-gray-100">
                    <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                      <div className="bg-teal-500 h-1.5 rounded-full" style={{ width: `${weather.humidity}%` }} />
                    </div>
                  </div>
                </div>

                {/* Soil Moisture */}
                <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                      <Layers className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                      Soil Moisture
                    </span>
                  </div>
                  <div>
                    <div className="flex items-baseline gap-1">
                      <span className="text-3xl font-black text-gray-900">{soil.soil_moisture}</span>
                      <span className="text-lg font-bold text-gray-400">%</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1 font-medium">{soil.water_availability}</p>
                  </div>
                  <div className="mt-3 pt-2 border-t border-gray-100">
                    <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                      <div className="bg-emerald-600 h-1.5 rounded-full" style={{ width: `${soil.soil_moisture}%` }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Historical Trends & Soil Health Card */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Soil Profile Card */}
              <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm flex flex-col justify-between">
                <div>
                  <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2 mb-3">
                    <Droplets className="w-4 h-4 text-emerald-600" />
                    <span>Soil Health &amp; Water Availability</span>
                  </h3>

                  <div className="my-3">
                    <span
                      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
                        soil.water_availability === "Adequate"
                          ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                          : soil.water_availability.includes("Deficit")
                          ? "bg-amber-100 text-amber-800 border border-amber-200"
                          : "bg-cyan-100 text-cyan-800 border border-cyan-200"
                      }`}
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      {soil.water_availability}
                    </span>
                  </div>

                  <p className="text-xs text-gray-600 leading-relaxed mt-2">
                    {soil.soil_condition}
                  </p>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-100 text-xs text-gray-500 space-y-1.5">
                  <p>• Soil Classification: <strong className="text-gray-800">{soil.soil_type}</strong></p>
                  <p>• Estimated pH: <strong className="text-gray-800">{soil.ph_level}</strong></p>
                  <p>• Organic Matter: <strong className="text-gray-800">{soil.organic_matter_pct}%</strong></p>
                </div>
              </div>

              {/* Historical Climate Trends Chart */}
              <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
                <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2 mb-1">
                  <Calendar className="w-4 h-4 text-emerald-600" />
                  <span>Historical Observations (Past 14 Days)</span>
                </h3>
                <p className="text-xs text-gray-500 mb-4">
                  Past precipitation and temperature variations feeding the risk ensemble.
                </p>

                <div className="h-60 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4} />
                          <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0} />
                        </linearGradient>
                        <linearGradient id="rainGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#0284c7" stopOpacity={0.5} />
                          <stop offset="95%" stopColor="#0284c7" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#64748b" }} tickFormatter={(d) => d.slice(5)} />
                      <YAxis tick={{ fontSize: 10, fill: "#64748b" }} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#ffffff",
                          borderRadius: "0.75rem",
                          border: "1px solid #e2e8f0",
                          fontSize: "12px",
                        }}
                      />
                      <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "6px" }} />
                      <Area type="monotone" dataKey="temp_max_c" name="Max Temp (°C)" stroke="#f59e0b" strokeWidth={2} fill="url(#tempGrad)" />
                      <Area type="monotone" dataKey="rainfall_mm" name="Rainfall (mm)" stroke="#0284c7" strokeWidth={2} fill="url(#rainGrad)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* AI RISK PREDICTION HISTORY (POSTGRESQL) */}
            <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
                <div>
                  <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                    <Clock className="w-4 h-4 text-emerald-600" />
                    <span>AI Risk Prediction History (PostgreSQL)</span>
                  </h3>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Chronological audit log of all model inferences evaluated and stored for this parcel.
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 flex items-center gap-1.5">
                    <Database className="w-3 h-3 text-emerald-600" />
                    {riskHistory.length} Stored Run{riskHistory.length !== 1 ? "s" : ""}
                  </span>
                </div>
              </div>

              {riskHistory.length === 0 ? (
                <div className="text-xs text-gray-400 py-8 text-center bg-gray-50/50 rounded-xl border border-dashed border-gray-200">
                  No historical predictions recorded for this farm parcel yet.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-gray-200 bg-gray-50 text-gray-500 uppercase tracking-wider text-[10px]">
                        <th className="py-2.5 px-3 font-bold">Run</th>
                        <th className="py-2.5 px-3 font-bold">Timestamp</th>
                        <th className="py-2.5 px-3 font-bold">Overall Risk</th>
                        <th className="py-2.5 px-3 font-bold">Dominant Threat</th>
                        <th className="py-2.5 px-3 font-bold">Drought</th>
                        <th className="py-2.5 px-3 font-bold">Flood</th>
                        <th className="py-2.5 px-3 font-bold">Heat</th>
                        <th className="py-2.5 px-3 font-bold">Rainfall</th>
                        <th className="py-2.5 px-3 font-bold">Main Contributing Factors</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 font-normal">
                      {riskHistory.map((h) => (
                        <tr key={h.id} className="hover:bg-emerald-50/30 transition-colors">
                          <td className="py-3 px-3 font-mono font-bold text-gray-700">#{h.id}</td>
                          <td className="py-3 px-3 text-gray-500 whitespace-nowrap">
                            {new Date(h.created_at).toLocaleString("en-IN", {
                              month: "short",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </td>
                          <td className="py-3 px-3 whitespace-nowrap">
                            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getLevelBadgeClass(h.overall_risk)}`}>
                              {h.overall_risk} ({h.risk_score}/100)
                            </span>
                          </td>
                          <td className="py-3 px-3 font-semibold text-gray-900 whitespace-nowrap">
                            {h.highest_risk_type}
                          </td>
                          <td className="py-3 px-3 font-mono text-gray-600">{h.drought_score}</td>
                          <td className="py-3 px-3 font-mono text-gray-600">{h.flood_score}</td>
                          <td className="py-3 px-3 font-mono text-gray-600">{h.heat_score}</td>
                          <td className="py-3 px-3 font-mono text-gray-600">{h.extreme_rainfall_score}</td>
                          <td className="py-3 px-3 text-gray-600 max-w-sm truncate" title={h.main_contributing_factors?.join(", ")}>
                            {h.main_contributing_factors && h.main_contributing_factors.length > 0
                              ? h.main_contributing_factors.slice(0, 2).join("; ")
                              : "Safe operating limits"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Demo Notice */}
            <div className="p-4 rounded-xl bg-amber-50/80 border border-amber-200/80 text-xs text-amber-900 flex items-start gap-3">
              <Info className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
              <div>
                <strong className="block font-semibold">
                  ML Prototype Notice: Calibrated RandomForest Risk Engine Active
                </strong>
                <p className="mt-0.5 text-amber-800 leading-relaxed">
                  The risk predictions above are dynamically evaluated by an ensemble of trained Scikit-learn RandomForestClassifiers. In this prototype stage, models were trained on a calibrated physics-informed agro-climatic synthetic dataset and are architected to seamlessly retrain on regional ground meteorological records.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white p-12 text-center rounded-2xl border border-gray-200 text-gray-500">
            Select a farm above to calculate real-time AI climate risk scores and view telemetry.
          </div>
        )}
      </main>
    </div>
  );
}

export default function ClimatePage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-50 p-8 text-center text-gray-500 text-sm">Loading Climate Intelligence...</div>}>
      <ClimateDataContent />
    </Suspense>
  );
}
