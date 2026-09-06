"use client";

import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { authService } from "@/services/auth";
import {
  adminService,
  AdminDashboardStats,
  RiskMapPoint,
  VulnerabilityAssessment,
  PriorityInterventionItem,
} from "@/services/admin";
import { User } from "@/types";
import {
  Building2,
  Users,
  Sprout,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  LogOut,
  Sun,
  Waves,
  Flame,
  CloudLightning,
  MapPin,
  Search,
  ExternalLink,
  HelpCircle,
  FileSpreadsheet,
  Layers,
  ArrowUpRight,
  TrendingUp,
  Map,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

// Dynamically import GovernmentRiskMap with SSR disabled
const GovernmentRiskMap = dynamic(
  () => import("@/components/GovernmentRiskMap").then((mod) => mod.GovernmentRiskMap),
  {
    ssr: false,
    loading: () => (
      <div className="h-[460px] bg-gray-100 animate-pulse rounded-2xl flex items-center justify-center text-xs text-gray-400">
        Loading Government Geographic Risk Map...
      </div>
    ),
  }
);

const RISK_COLORS = {
  HIGH: "#ef4444",
  MEDIUM: "#f59e0b",
  LOW: "#10b981",
};

export default function AdminDashboardPage() {
  const router = useRouter();

  const [adminUser, setAdminUser] = useState<User | null>(null);
  const [stats, setStats] = useState<AdminDashboardStats | null>(null);
  const [riskMapPoints, setRiskMapPoints] = useState<RiskMapPoint[]>([]);
  const [vulnerability, setVulnerability] = useState<VulnerabilityAssessment | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [errorNotice, setErrorNotice] = useState<string | null>(null);

  // 1. Role Guard & Initial Data Fetch
  const loadDashboardData = useCallback(async () => {
    try {
      const [statsData, mapData, vulnData] = await Promise.all([
        adminService.getDashboardStats(),
        adminService.getRiskMapPoints(),
        adminService.getVulnerabilityAssessment(),
      ]);

      setStats(statsData);
      setRiskMapPoints(mapData);
      setVulnerability(vulnData);
      setErrorNotice(null);
    } catch (err: any) {
      setErrorNotice(err.message || "Failed to load government dashboard data");
    }
  }, []);

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push("/login?redirect=/admin/dashboard");
      return;
    }

    const user = authService.getUser();
    if (!user || user.role !== "ADMIN") {
      router.push("/login?redirect=/admin/dashboard");
      return;
    }

    setAdminUser(user);

    setLoading(true);
    loadDashboardData().finally(() => setLoading(false));
  }, [router, loadDashboardData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleLogout = () => {
    authService.clearSession();
    router.push("/login");
  };

  // Filter priority interventions by user search
  const filteredInterventions = (stats?.priority_intervention_list || []).filter((item) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      item.farmer_name.toLowerCase().includes(term) ||
      item.farm_name.toLowerCase().includes(term) ||
      item.crop.toLowerCase().includes(term) ||
      (item.district && item.district.toLowerCase().includes(term)) ||
      (item.village && item.village.toLowerCase().includes(term)) ||
      item.risk_type.toLowerCase().includes(term)
    );
  });

  // Prepare Recharts Data
  const riskPieData = stats
    ? [
        { name: "Low Risk", value: stats.low_risk_farms, color: RISK_COLORS.LOW },
        { name: "Medium Risk", value: stats.medium_risk_farms, color: RISK_COLORS.MEDIUM },
        { name: "High Risk", value: stats.high_risk_farms, color: RISK_COLORS.HIGH },
      ]
    : [];

  const hazardBarData = stats
    ? [
        { hazard: "Drought", count: stats.drought_risk_farms, fill: "#f59e0b" },
        { hazard: "Flood", count: stats.flood_risk_farms, fill: "#3b82f6" },
        { hazard: "Heat Stress", count: stats.heat_stress_farms, fill: "#ef4444" },
        { hazard: "Extreme Rain", count: stats.extreme_rainfall_farms, fill: "#06b6d4" },
      ]
    : [];

  const cropBarData = (stats?.crop_distribution || []).map((c) => ({
    crop: c.crop,
    farms: c.count,
    acres: c.area_acres,
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

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
        <div className="text-center space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-indigo-600 text-white flex items-center justify-center mx-auto shadow-md animate-pulse">
            <Building2 className="w-6 h-6" />
          </div>
          <h2 className="text-base font-bold text-gray-900">
            Initializing Government Command Center...
          </h2>
          <p className="text-xs text-gray-500">
            Retrieving state-wide geospatial telemetry and PostgreSQL hazard analytics.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 font-sans pb-20">
      {/* Top Banner / Government Identity */}
      <header className="bg-white border-b border-gray-200 shadow-xs sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-700 to-indigo-900 flex items-center justify-center text-white shadow-md shadow-indigo-900/20">
              <Building2 className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold text-gray-900 leading-tight">
                  Government &amp; Department Command Center
                </h1>
                <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 border border-indigo-200">
                  ADMIN PORTAL
                </span>
              </div>
              <p className="text-xs text-gray-500">
                Officer: <strong className="text-gray-700">{adminUser?.name || "System Admin"}</strong> &bull; Contact: {adminUser?.mobile} &bull; State Agricultural Directorate
              </p>
            </div>
          </div>

          {/* Actions & Portal Switcher */}
          <div className="flex items-center gap-2 sm:gap-3">
            <Link
              href="/farmer/dashboard"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg transition-colors"
            >
              <Sprout className="w-3.5 h-3.5" />
              <span>Farmer Portal View</span>
            </Link>

            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 rounded-lg transition-colors"
              title="Refresh all metrics from database"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} />
              <span>{refreshing ? "Syncing..." : "Sync Database"}</span>
            </button>

            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-rose-600 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Error alert if any */}
      {errorNotice && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs sm:text-sm flex items-center justify-between">
            <span>{errorNotice}</span>
            <button onClick={() => setErrorNotice(null)} className="text-xs text-rose-600 underline">
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6 space-y-6">
        {/* =========================================================================
            SECTION 1: High-Level Database Statistics (Step 12)
           ========================================================================= */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-gray-800 uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-600" />
              Aggregated Agricultural Overview
            </h2>
            <span className="text-xs text-gray-400">Database-driven real-time statistics</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
            {/* Total Farmers */}
            <div className="p-4 rounded-2xl bg-white border border-gray-200 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-gray-500 mb-1">
                <span className="text-xs font-semibold">Total Farmers</span>
                <Users className="w-4 h-4 text-indigo-600" />
              </div>
              <div className="text-2xl font-black text-gray-900">
                {stats?.total_farmers || 0}
              </div>
              <span className="text-[10px] text-gray-400 mt-1">Registered accounts</span>
            </div>

            {/* Total Farms */}
            <div className="p-4 rounded-2xl bg-white border border-gray-200 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-gray-500 mb-1">
                <span className="text-xs font-semibold">Total Farms</span>
                <Sprout className="w-4 h-4 text-emerald-600" />
              </div>
              <div className="text-2xl font-black text-gray-900">
                {stats?.total_farms || 0}
              </div>
              <span className="text-[10px] text-gray-400 mt-1">Geo-mapped parcels</span>
            </div>

            {/* High-Risk Farms */}
            <div className="p-4 rounded-2xl bg-rose-50/70 border border-rose-200 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-rose-700 mb-1">
                <span className="text-xs font-bold">High-Risk Farms</span>
                <ShieldAlert className="w-4 h-4 text-rose-600" />
              </div>
              <div className="text-2xl font-black text-rose-900">
                {stats?.high_risk_farms || 0}
              </div>
              <span className="text-[10px] text-rose-600 mt-1 font-semibold">
                Score &ge; 71 (Priority Alert)
              </span>
            </div>

            {/* Medium-Risk Farms */}
            <div className="p-4 rounded-2xl bg-amber-50/70 border border-amber-200 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-amber-800 mb-1">
                <span className="text-xs font-bold">Medium-Risk Farms</span>
                <AlertTriangle className="w-4 h-4 text-amber-600" />
              </div>
              <div className="text-2xl font-black text-amber-900">
                {stats?.medium_risk_farms || 0}
              </div>
              <span className="text-[10px] text-amber-700 mt-1 font-medium">
                Score 31–70 (Monitoring)
              </span>
            </div>

            {/* Low-Risk Farms */}
            <div className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200 shadow-xs flex flex-col justify-between">
              <div className="flex items-center justify-between text-emerald-800 mb-1">
                <span className="text-xs font-bold">Low-Risk Farms</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              </div>
              <div className="text-2xl font-black text-emerald-900">
                {stats?.low_risk_farms || 0}
              </div>
              <span className="text-[10px] text-emerald-700 mt-1 font-medium">
                Score 0–30 (Safe bounds)
              </span>
            </div>
          </div>

          {/* 4 Hazard Breakdown Pills */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-white border border-gray-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-amber-100 rounded-lg text-amber-700">
                  <Sun className="w-4 h-4" />
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">Drought Risk</span>
                  <strong className="text-sm text-gray-900">{stats?.drought_risk_farms || 0} farms</strong>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white border border-gray-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-blue-100 rounded-lg text-blue-700">
                  <Waves className="w-4 h-4" />
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">Flood Risk</span>
                  <strong className="text-sm text-gray-900">{stats?.flood_risk_farms || 0} farms</strong>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white border border-gray-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-rose-100 rounded-lg text-rose-700">
                  <Flame className="w-4 h-4" />
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">Heat Stress</span>
                  <strong className="text-sm text-gray-900">{stats?.heat_stress_farms || 0} farms</strong>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white border border-gray-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-cyan-100 rounded-lg text-cyan-700">
                  <CloudLightning className="w-4 h-4" />
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">Extreme Rainfall</span>
                  <strong className="text-sm text-gray-900">{stats?.extreme_rainfall_farms || 0} farms</strong>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* =========================================================================
            SECTION 2: Analytics & Charts (Step 12)
           ========================================================================= */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chart 1: Risk Level Distribution (Pie) */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-xs flex flex-col justify-between">
            <div className="mb-2">
              <h3 className="text-sm font-bold text-gray-900 flex items-center gap-1.5">
                <TrendingUp className="w-4 h-4 text-indigo-600" />
                Risk Level Distribution
              </h3>
              <p className="text-xs text-gray-500">
                Categorization of all registered farms by severity.
              </p>
            </div>

            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskPieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={75}
                    paddingAngle={4}
                  >
                    {riskPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val: any, name: any) => [`${val} farms`, name]}
                    contentStyle={{ borderRadius: "10px", fontSize: "12px" }}
                  />
                  <Legend verticalAlign="bottom" height={36} iconType="circle" />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Chart 2: Climate Hazards Breakdown (Bar) */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-xs flex flex-col justify-between">
            <div className="mb-2">
              <h3 className="text-sm font-bold text-gray-900 flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4 text-amber-600" />
                Specific Hazard Exposure
              </h3>
              <p className="text-xs text-gray-500">
                Number of farms vulnerable to specific environmental hazards.
              </p>
            </div>

            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={hazardBarData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="hazard" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                  <Tooltip
                    formatter={(val: any) => [`${val} farms`, "Exposed Farms"]}
                    contentStyle={{ borderRadius: "10px", fontSize: "12px" }}
                  />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {hazardBarData.map((entry, index) => (
                      <Cell key={`cell-hazard-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Chart 3: Crop Distribution (Bar) */}
          <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-xs flex flex-col justify-between">
            <div className="mb-2">
              <h3 className="text-sm font-bold text-gray-900 flex items-center gap-1.5">
                <Sprout className="w-4 h-4 text-emerald-600" />
                Crop Cultivation Distribution
              </h3>
              <p className="text-xs text-gray-500">
                Farms and total acreage across cultivated crops.
              </p>
            </div>

            <div className="h-56 w-full">
              {cropBarData.length === 0 ? (
                <div className="h-full flex items-center justify-center text-xs text-gray-400">
                  No crop data recorded yet.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={cropBarData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="crop" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                    <Tooltip
                      formatter={(val: any, name: any) => [
                        name === "farms" ? `${val} farms` : `${val} acres`,
                        name === "farms" ? "Farms" : "Total Acreage",
                      ]}
                      contentStyle={{ borderRadius: "10px", fontSize: "12px" }}
                    />
                    <Bar dataKey="farms" fill="#059669" radius={[6, 6, 0, 0]} name="farms" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </section>

        {/* =========================================================================
            SECTION 3: Government Risk Map (Step 13)
           ========================================================================= */}
        <section className="space-y-2">
          <GovernmentRiskMap points={riskMapPoints} />
        </section>

        {/* =========================================================================
            SECTION 4: Vulnerability Assessment & Priority Hotspots (Step 13)
           ========================================================================= */}
        <section className="bg-white rounded-2xl border border-gray-200 p-5 shadow-xs space-y-4">
          <div className="border-b border-gray-100 pb-3 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-indigo-700" />
                Regional Vulnerability Assessment &amp; Systemic Risks
              </h3>
              <p className="text-xs text-gray-500">
                Composite evaluation identifying vulnerable districts, risk drivers, and targeted agricultural relief.
              </p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-800 border border-indigo-200">
              {vulnerability?.total_vulnerable_farms || 0} Vulnerable Farms Flagged
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Vulnerable District Clusters Table */}
            <div className="bg-slate-50 rounded-xl p-4 border border-gray-200">
              <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-2.5">
                Vulnerable District Clusters
              </h4>
              <div className="overflow-x-auto">
                <table className="min-w-full text-xs text-left">
                  <thead>
                    <tr className="border-b border-gray-200 text-gray-500">
                      <th className="pb-2 font-semibold">District / State</th>
                      <th className="pb-2 font-semibold">Farms</th>
                      <th className="pb-2 font-semibold">Avg Risk</th>
                      <th className="pb-2 font-semibold">Dominant Hazard</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200/60">
                    {(vulnerability?.vulnerable_areas || []).length === 0 ? (
                      <tr>
                        <td colSpan={4} className="py-4 text-center text-gray-400 italic">
                          No distinct regional clusters formed.
                        </td>
                      </tr>
                    ) : (
                      (vulnerability?.vulnerable_areas || []).map((area, idx) => (
                        <tr key={idx} className="hover:bg-white/50 transition-colors">
                          <td className="py-2.5 font-semibold text-gray-900">
                            {area.district}, {area.state}
                          </td>
                          <td className="py-2.5 text-gray-700">{area.farm_count}</td>
                          <td className="py-2.5">
                            <span className="font-bold text-gray-900">
                              {Math.round(area.avg_risk_score)}
                            </span>
                            <span className="text-[10px] text-gray-400">/100</span>
                          </td>
                          <td className="py-2.5">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-white border border-gray-200 text-gray-800">
                              {area.dominant_hazard}
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Main Systemic Risk Factors & Interventions */}
            <div className="space-y-3">
              <div className="bg-slate-50 rounded-xl p-4 border border-gray-200">
                <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-2">
                  Key Systemic Risk Factors
                </h4>
                <div className="flex flex-wrap gap-2">
                  {(vulnerability?.main_risk_factors || []).length === 0 ? (
                    <span className="text-xs text-gray-400 italic">No systemic factors identified</span>
                  ) : (
                    (vulnerability?.main_risk_factors || []).map((factor, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 rounded-lg bg-white border border-gray-200 text-xs font-medium text-gray-800 shadow-2xs"
                      >
                        &bull; {factor}
                      </span>
                    ))
                  )}
                </div>
              </div>

              <div className="bg-gradient-to-br from-indigo-50 to-blue-50/50 rounded-xl p-4 border border-indigo-100">
                <h4 className="text-xs font-bold text-indigo-900 uppercase tracking-wider mb-1.5">
                  Recommended Department Policy Interventions
                </h4>
                <ul className="text-xs text-indigo-950 space-y-1.5 list-disc list-inside">
                  <li>Deploy PMKSY drip &amp; micro-irrigation subsidies in drought-exposed clusters.</li>
                  <li>Ensure district canal release schedules align with forecasted precipitation deficits.</li>
                  <li>Mobilize PMFBY parametric crop insurance adjusters for flood-logged river basins.</li>
                  <li>Issue regional SMS advisory broadcasts in Marathi, Hindi, and Kannada.</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* =========================================================================
            SECTION 5: Priority Intervention List & Farmer Registry (Step 12)
           ========================================================================= */}
        <section className="bg-white rounded-2xl border border-gray-200 shadow-xs overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-rose-600" />
                Priority Intervention List &amp; Farm Registry
              </h3>
              <p className="text-xs text-gray-500">
                Actionable roster of farms ranked by climate hazard severity.
              </p>
            </div>

            {/* Search Input */}
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search farmer, farm, crop, district..."
                className="w-full pl-9 pr-3 py-1.5 bg-white border border-gray-300 rounded-xl text-xs font-medium text-gray-800 outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-xs text-left">
              <thead className="bg-gray-50 text-gray-600 uppercase font-semibold text-[10px] tracking-wider">
                <tr>
                  <th className="px-4 py-3">Farmer &amp; Contact</th>
                  <th className="px-4 py-3">Farm &amp; Crop</th>
                  <th className="px-4 py-3">Location</th>
                  <th className="px-4 py-3">Risk Type</th>
                  <th className="px-4 py-3">Risk Score &amp; Level</th>
                  <th className="px-4 py-3">Recommended Intervention Action</th>
                  <th className="px-4 py-3">Evaluated At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 bg-white">
                {filteredInterventions.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                      No farms match the current filter or criteria.
                    </td>
                  </tr>
                ) : (
                  filteredInterventions.map((item) => (
                    <tr key={item.farm_id} className="hover:bg-slate-50 transition-colors">
                      {/* Farmer */}
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="font-bold text-gray-900">{item.farmer_name}</div>
                        <div className="text-[11px] text-gray-500">{item.mobile}</div>
                      </td>

                      {/* Farm & Crop */}
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="font-semibold text-gray-900">{item.farm_name}</div>
                        <div className="text-[11px] text-emerald-700 font-medium">
                          {item.crop} &bull; {item.area} acres
                        </div>
                      </td>

                      {/* Location */}
                      <td className="px-4 py-3 whitespace-nowrap text-gray-600">
                        <div>
                          {item.village ? `${item.village}, ` : ""}
                          {item.district || "—"}
                        </div>
                        <div className="text-[10px] text-gray-400">{item.state || "India"}</div>
                      </td>

                      {/* Risk Type */}
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className="font-semibold text-gray-900">{item.risk_type}</span>
                      </td>

                      {/* Risk Score & Badge */}
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="flex items-center gap-1.5">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[11px] font-extrabold border ${getRiskBadge(
                              item.risk_level
                            )}`}
                          >
                            {item.risk_level}
                          </span>
                          <span className="font-mono text-xs font-bold text-gray-800">
                            {Math.round(item.risk_score)}/100
                          </span>
                        </div>
                      </td>

                      {/* Recommended Action */}
                      <td className="px-4 py-3 max-w-xs">
                        <div className="text-gray-800 line-clamp-2" title={item.recommended_action}>
                          {item.recommended_action}
                        </div>
                      </td>

                      {/* Timestamp */}
                      <td className="px-4 py-3 whitespace-nowrap text-[11px] text-gray-400">
                        {new Date(item.timestamp).toLocaleDateString()}{" "}
                        {new Date(item.timestamp).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
}
