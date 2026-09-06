"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { authService } from "@/services/auth";
import { farmService } from "@/services/farms";
import { Farm, FarmCreatePayload, FarmUpdatePayload, User } from "@/types";
import { 
  Sprout, 
  Plus, 
  Edit3, 
  Trash2, 
  MapPin, 
  Calendar, 
  Droplets, 
  Layers, 
  Maximize2, 
  LogOut, 
  User as UserIcon, 
  X, 
  AlertCircle, 
  CheckCircle2, 
  Info,
  ShieldCheck,
  Building2,
  LayoutDashboard
} from "lucide-react";

// Dynamically import Leaflet Map Picker with SSR disabled
const FarmMapPicker = dynamic(
  () => import("@/components/FarmMapPicker").then((mod) => mod.FarmMapPicker),
  { ssr: false, loading: () => <div className="h-64 bg-gray-100 animate-pulse rounded-xl flex items-center justify-center text-xs text-gray-400">Loading interactive map...</div> }
);

export default function FarmerFarmsPage() {
  const router = useRouter();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Modal states
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingFarm, setEditingFarm] = useState<Farm | null>(null);
  const [viewingFarm, setViewingFarm] = useState<Farm | null>(null);
  const [deletingFarmId, setDeletingFarmId] = useState<number | null>(null);
  const [formSubmitting, setFormSubmitting] = useState(false);

  // Form input state
  const [formData, setFormData] = useState<{
    farm_name: string;
    area: string;
    crop: string;
    sowing_date: string;
    soil_type: string;
    irrigation_available: boolean;
    latitude: number | null;
    longitude: number | null;
  }>({
    farm_name: "",
    area: "",
    crop: "",
    sowing_date: "",
    soil_type: "Black Soil",
    irrigation_available: true,
    latitude: 18.5204,
    longitude: 73.8567,
  });

  // Auth check & load farms
  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push("/login");
      return;
    }

    const user = authService.getUser();
    setCurrentUser(user);
    loadFarms();
  }, [router]);

  const loadFarms = async () => {
    setLoading(true);
    setError(null);
    try {
      const list = await farmService.getFarms();
      setFarms(list);
    } catch (err: any) {
      setError(err.message || "Could not load farms");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authService.clearSession();
    router.push("/login");
  };

  const openAddModal = () => {
    setFormData({
      farm_name: "",
      area: "",
      crop: "",
      sowing_date: new Date().toISOString().split("T")[0],
      soil_type: "Black Soil",
      irrigation_available: true,
      latitude: currentUser?.latitude || 18.5204,
      longitude: currentUser?.longitude || 73.8567,
    });
    setEditingFarm(null);
    setIsAddModalOpen(true);
    setError(null);
  };

  const openEditModal = (farm: Farm) => {
    setFormData({
      farm_name: farm.farm_name,
      area: farm.area.toString(),
      crop: farm.crop,
      sowing_date: farm.sowing_date || "",
      soil_type: farm.soil_type || "Black Soil",
      irrigation_available: farm.irrigation_available,
      latitude: farm.latitude,
      longitude: farm.longitude,
    });
    setEditingFarm(farm);
    setIsAddModalOpen(true);
    setError(null);
  };

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    if (type === "checkbox") {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleLocationChange = (lat: number, lng: number) => {
    setFormData((prev) => ({ ...prev, latitude: lat, longitude: lng }));
  };

  const handleSaveFarm = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    const trimmedName = formData.farm_name.trim();
    if (!trimmedName) {
      setError("Farm name is required.");
      return;
    }
    const numArea = parseFloat(formData.area);
    if (isNaN(numArea) || numArea <= 0) {
      setError("Area must be a positive number greater than 0.");
      return;
    }
    const trimmedCrop = formData.crop.trim();
    if (!trimmedCrop) {
      setError("Crop name cannot be empty.");
      return;
    }

    setFormSubmitting(true);
    try {
      if (editingFarm) {
        // Edit Farm
        const payload: FarmUpdatePayload = {
          farm_name: trimmedName,
          area: numArea,
          crop: trimmedCrop,
          sowing_date: formData.sowing_date || undefined,
          soil_type: formData.soil_type || undefined,
          irrigation_available: formData.irrigation_available,
          latitude: formData.latitude ?? undefined,
          longitude: formData.longitude ?? undefined,
        };
        await farmService.updateFarm(editingFarm.id, payload);
        setSuccess(`Farm '${trimmedName}' updated successfully!`);
      } else {
        // Add Farm
        const payload: FarmCreatePayload = {
          farm_name: trimmedName,
          area: numArea,
          crop: trimmedCrop,
          sowing_date: formData.sowing_date || undefined,
          soil_type: formData.soil_type || undefined,
          irrigation_available: formData.irrigation_available,
          latitude: formData.latitude ?? undefined,
          longitude: formData.longitude ?? undefined,
        };
        await farmService.createFarm(payload);
        setSuccess(`Farm '${trimmedName}' registered successfully!`);
      }

      setIsAddModalOpen(false);
      setEditingFarm(null);
      await loadFarms();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to save farm.");
    } finally {
      setFormSubmitting(false);
    }
  };

  const confirmDeleteFarm = async (id: number) => {
    try {
      await farmService.deleteFarm(id);
      setSuccess("Farm deleted successfully.");
      setDeletingFarmId(null);
      await loadFarms();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to delete farm.");
      setDeletingFarmId(null);
    }
  };

  const totalAcreage = farms.reduce((sum, f) => sum + (f.area || 0), 0);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-40 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-sm">
                <Sprout className="w-5 h-5 text-emerald-100" />
              </div>
              <div>
                <span className="text-lg font-black text-gray-900 tracking-tight">
                  Krushi<span className="text-emerald-700">Rakshak</span>
                </span>
                <span className="ml-2 text-[10px] font-semibold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  Farmer Portal
                </span>
              </div>
            </Link>

            <div className="flex items-center gap-3 sm:gap-4">
              <Link
                href="/farmer/dashboard"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-emerald-800 bg-emerald-50 hover:bg-emerald-100 rounded-lg border border-emerald-200 transition-colors"
              >
                <LayoutDashboard className="w-3.5 h-3.5 text-emerald-700" />
                <span>Dashboard</span>
              </Link>

              <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-700 font-medium">
                <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
                  {currentUser?.name ? currentUser.name.charAt(0).toUpperCase() : "F"}
                </div>
                <div className="hidden sm:block text-left">
                  <p className="font-semibold text-gray-900 leading-tight">{currentUser?.name || "Farmer"}</p>
                  <p className="text-[11px] text-gray-500 font-normal">{currentUser?.mobile}</p>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-rose-700 hover:bg-rose-50 rounded-lg border border-rose-200 transition-colors"
                title="Log Out"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-grow max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Banner Alert Messages */}
        {success && (
          <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-between text-emerald-800 text-sm animate-fade-in">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
              <span>{success}</span>
            </div>
            <button onClick={() => setSuccess(null)} className="text-emerald-700 hover:text-emerald-900">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-center justify-between text-rose-800 text-sm">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
              <span>{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-rose-700 hover:text-rose-900">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Dashboard Header Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-gray-200">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight">
              My Farm Parcels
            </h1>
            <p className="mt-1 text-xs sm:text-sm text-gray-500">
              Manage your agricultural holdings, crop varieties, and geo-coordinates for downscaled climate alerts.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={openAddModal}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-sm text-white bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 shadow-md shadow-emerald-700/20 transition-all"
            >
              <Plus className="w-4 h-4" />
              <span>Add New Farm</span>
            </button>
          </div>
        </div>

        {/* Summary Metrics Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 my-6">
          <div className="bg-white p-4 rounded-xl border border-gray-200/80 shadow-sm">
            <p className="text-xs text-gray-500 font-medium">Registered Farms</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{farms.length}</p>
            <p className="text-[11px] text-emerald-600 mt-0.5">Multiple parcels supported</p>
          </div>

          <div className="bg-white p-4 rounded-xl border border-gray-200/80 shadow-sm">
            <p className="text-xs text-gray-500 font-medium">Total Cultivated Area</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{totalAcreage.toFixed(2)} <span className="text-sm font-normal text-gray-500">acres</span></p>
            <p className="text-[11px] text-gray-400 mt-0.5">Active monitoring</p>
          </div>

          <div className="col-span-2 sm:col-span-1 bg-white p-4 rounded-xl border border-gray-200/80 shadow-sm">
            <p className="text-xs text-gray-500 font-medium">Climate Intelligence</p>
            <p className="text-2xl font-bold text-emerald-700 mt-1">Ready</p>
            <p className="text-[11px] text-gray-400 mt-0.5">FastAPI &amp; PostgreSQL synced</p>
          </div>
        </div>

        {/* Farms Grid / Empty State */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-56 bg-white rounded-2xl border border-gray-200 p-6" />
            ))}
          </div>
        ) : farms.length === 0 ? (
          <div className="bg-white rounded-2xl border border-dashed border-gray-300 p-12 text-center max-w-lg mx-auto my-8">
            <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto mb-4">
              <Sprout className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-gray-900">No farms registered yet</h3>
            <p className="text-sm text-gray-500 mt-1 max-w-sm mx-auto">
              Add your first agricultural parcel using the interactive map to start receiving tailored crop advisories.
            </p>
            <button
              onClick={openAddModal}
              className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm text-white bg-emerald-600 hover:bg-emerald-700 shadow-sm"
            >
              <Plus className="w-4 h-4" />
              <span>Add Your First Farm</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {farms.map((farm) => (
              <div
                key={farm.id}
                className="bg-white rounded-2xl border border-gray-200/90 shadow-sm hover:shadow-md hover:border-emerald-300 transition-all flex flex-col justify-between overflow-hidden"
              >
                <div className="p-5 sm:p-6">
                  {/* Card Header */}
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                        {farm.crop}
                      </span>
                      <h3 className="text-lg font-bold text-gray-900 mt-1 leading-snug">
                        {farm.farm_name}
                      </h3>
                    </div>

                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => openEditModal(farm)}
                        className="p-1.5 text-gray-400 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg transition-colors"
                        title="Edit Farm"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeletingFarmId(farm.id)}
                        className="p-1.5 text-gray-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                        title="Delete Farm"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Attributes Grid */}
                  <div className="space-y-2 mt-4 text-xs text-gray-600">
                    <div className="flex items-center justify-between py-1 border-b border-gray-100">
                      <span className="text-gray-400 flex items-center gap-1.5">
                        <Maximize2 className="w-3.5 h-3.5 text-gray-400" />
                        Cultivated Area:
                      </span>
                      <span className="font-semibold text-gray-800">{farm.area} acres</span>
                    </div>

                    <div className="flex items-center justify-between py-1 border-b border-gray-100">
                      <span className="text-gray-400 flex items-center gap-1.5">
                        <Layers className="w-3.5 h-3.5 text-gray-400" />
                        Soil Type:
                      </span>
                      <span className="font-medium text-gray-700">{farm.soil_type || "Unspecified"}</span>
                    </div>

                    <div className="flex items-center justify-between py-1 border-b border-gray-100">
                      <span className="text-gray-400 flex items-center gap-1.5">
                        <Droplets className="w-3.5 h-3.5 text-gray-400" />
                        Irrigation:
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${farm.irrigation_available ? "bg-cyan-50 text-cyan-800 border border-cyan-200" : "bg-gray-100 text-gray-600"}`}>
                        {farm.irrigation_available ? "Available" : "Rainfed"}
                      </span>
                    </div>

                    <div className="flex items-center justify-between py-1 border-b border-gray-100">
                      <span className="text-gray-400 flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5 text-gray-400" />
                        Sowing Date:
                      </span>
                      <span className="font-medium text-gray-700">{farm.sowing_date || "Not recorded"}</span>
                    </div>

                    <div className="flex items-center justify-between pt-1">
                      <span className="text-gray-400 flex items-center gap-1.5">
                        <MapPin className="w-3.5 h-3.5 text-emerald-600" />
                        Coordinates:
                      </span>
                      <span className="font-mono text-[11px] text-gray-600">
                        {farm.latitude && farm.longitude ? (
                          `${farm.latitude.toFixed(4)}°, ${farm.longitude.toFixed(4)}°`
                        ) : (
                          "Unset"
                        )}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Card Footer */}
                <div className="p-4 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
                  <button
                    onClick={() => setViewingFarm(farm)}
                    className="text-xs font-semibold text-gray-600 hover:text-gray-900 inline-flex items-center gap-1"
                  >
                    <Info className="w-3.5 h-3.5" />
                    <span>View Details</span>
                  </button>

                  <Link
                    href={`/farmer/climate?farmId=${farm.id}`}
                    className="text-xs font-semibold text-emerald-700 hover:text-emerald-900 inline-flex items-center gap-1 bg-emerald-50 hover:bg-emerald-100 px-2.5 py-1 rounded-lg border border-emerald-200 transition-colors"
                  >
                    <Sprout className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Climate &amp; Soil</span>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* ADD / EDIT FARM MODAL */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6">
          <div className="bg-white rounded-2xl max-w-xl w-full shadow-2xl border border-gray-200 overflow-hidden animate-fade-in my-8">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50/50">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Sprout className="w-5 h-5 text-emerald-600" />
                <span>{editingFarm ? "Edit Farm Parcel" : "Register New Farm Parcel"}</span>
              </h3>
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="text-gray-400 hover:text-gray-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveFarm} className="p-6 space-y-4">
              {/* Farm Name */}
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Farm Name *
                </label>
                <input
                  type="text"
                  name="farm_name"
                  required
                  placeholder="e.g. North Field Parcel #1"
                  value={formData.farm_name}
                  onChange={handleFormChange}
                  className="w-full px-3.5 py-2 text-sm border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                />
              </div>

              {/* Area & Crop */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Area in Acres * (Positive)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    name="area"
                    required
                    placeholder="e.g. 3.5"
                    value={formData.area}
                    onChange={handleFormChange}
                    className="w-full px-3.5 py-2 text-sm border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Primary Crop *
                  </label>
                  <input
                    type="text"
                    name="crop"
                    required
                    placeholder="e.g. Cotton, Wheat, Paddy"
                    value={formData.crop}
                    onChange={handleFormChange}
                    className="w-full px-3.5 py-2 text-sm border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                  />
                </div>
              </div>

              {/* Sowing Date & Soil Type */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Sowing Date
                  </label>
                  <input
                    type="date"
                    name="sowing_date"
                    value={formData.sowing_date}
                    onChange={handleFormChange}
                    className="w-full px-3.5 py-2 text-sm border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 mb-1">
                    Soil Type
                  </label>
                  <select
                    name="soil_type"
                    value={formData.soil_type}
                    onChange={handleFormChange}
                    className="w-full px-3.5 py-2 text-sm border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none bg-white"
                  >
                    <option value="Black Soil">Black Soil (Regur)</option>
                    <option value="Alluvial Soil">Alluvial Soil</option>
                    <option value="Red Soil">Red Soil</option>
                    <option value="Laterite Soil">Laterite Soil</option>
                    <option value="Clayey Loam">Clayey Loam</option>
                    <option value="Sandy Loam">Sandy Loam</option>
                  </select>
                </div>
              </div>

              {/* Irrigation Toggle */}
              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="irrigation_available"
                  name="irrigation_available"
                  checked={formData.irrigation_available}
                  onChange={handleFormChange}
                  className="w-4 h-4 text-emerald-600 rounded border-gray-300 focus:ring-emerald-500"
                />
                <label htmlFor="irrigation_available" className="text-xs font-medium text-gray-700">
                  Irrigation facility available on this parcel
                </label>
              </div>

              {/* Interactive Leaflet Map Location Picker */}
              <div className="pt-2">
                <label className="block text-xs font-semibold text-gray-700 mb-1">
                  Farm Parcel Geographical Location
                </label>
                <FarmMapPicker
                  latitude={formData.latitude}
                  longitude={formData.longitude}
                  onChange={handleLocationChange}
                />
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={formSubmitting}
                  className="px-5 py-2.5 text-xs font-semibold text-white bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 rounded-xl shadow-md transition-all disabled:opacity-70"
                >
                  {formSubmitting ? "Saving..." : editingFarm ? "Update Farm" : "Save Farm Parcel"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* VIEW FARM DETAILS MODAL */}
      {viewingFarm && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-gray-200 space-y-4">
            <div className="flex items-start justify-between border-b border-gray-100 pb-3">
              <div>
                <span className="text-[10px] font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100 uppercase">
                  {viewingFarm.crop}
                </span>
                <h3 className="text-xl font-bold text-gray-900 mt-1">
                  {viewingFarm.farm_name}
                </h3>
              </div>
              <button
                onClick={() => setViewingFarm(null)}
                className="text-gray-400 hover:text-gray-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-gray-50 p-3 rounded-xl">
                <span className="text-gray-400 block mb-1">Cultivated Area</span>
                <span className="text-base font-bold text-gray-900">{viewingFarm.area} acres</span>
              </div>
              <div className="bg-gray-50 p-3 rounded-xl">
                <span className="text-gray-400 block mb-1">Irrigation Mode</span>
                <span className="text-base font-bold text-gray-900">
                  {viewingFarm.irrigation_available ? "Irrigated" : "Rainfed"}
                </span>
              </div>
              <div className="bg-gray-50 p-3 rounded-xl">
                <span className="text-gray-400 block mb-1">Soil Classification</span>
                <span className="font-semibold text-gray-800">{viewingFarm.soil_type || "Standard"}</span>
              </div>
              <div className="bg-gray-50 p-3 rounded-xl">
                <span className="text-gray-400 block mb-1">Sowing Date</span>
                <span className="font-semibold text-gray-800">{viewingFarm.sowing_date || "Not set"}</span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-100 text-xs text-gray-700">
              <div className="flex items-center gap-1.5 font-semibold text-emerald-800 mb-1">
                <MapPin className="w-4 h-4 text-emerald-600" />
                <span>Geospatial Coordinates</span>
              </div>
              <p className="font-mono text-[11px]">
                Latitude: {viewingFarm.latitude ?? "N/A"} | Longitude: {viewingFarm.longitude ?? "N/A"}
              </p>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setViewingFarm(null)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold rounded-xl"
              >
                Close Details
              </button>
            </div>
          </div>
        </div>
      )}

      {/* DELETE CONFIRMATION MODAL */}
      {deletingFarmId && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-gray-200 text-center">
            <div className="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto mb-3">
              <Trash2 className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-gray-900">Delete Farm Parcel?</h3>
            <p className="text-xs text-gray-500 mt-1 mb-6">
              Are you sure you want to delete this farm parcel? This action cannot be undone.
            </p>
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={() => setDeletingFarmId(null)}
                className="px-4 py-2 text-xs font-semibold text-gray-600 hover:bg-gray-100 rounded-xl"
              >
                Cancel
              </button>
              <button
                onClick={() => confirmDeleteFarm(deletingFarmId)}
                className="px-4 py-2 text-xs font-semibold text-white bg-rose-600 hover:bg-rose-700 rounded-xl shadow-sm"
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
