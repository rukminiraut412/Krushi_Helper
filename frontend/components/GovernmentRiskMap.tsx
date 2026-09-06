"use client";

import React, { useEffect, useRef, useState } from "react";
import { RiskMapPoint } from "@/services/admin";
import { MapPin, Filter, Layers, Info } from "lucide-react";

interface GovernmentRiskMapProps {
  points: RiskMapPoint[];
}

export const GovernmentRiskMap: React.FC<GovernmentRiskMapProps> = ({ points }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersLayerRef = useRef<any>(null);

  const [levelFilter, setLevelFilter] = useState<string>("ALL");
  const [hazardFilter, setHazardFilter] = useState<string>("ALL");

  // Filter points based on user selection
  const filteredPoints = points.filter((p) => {
    if (!p.latitude || !p.longitude) return false;
    if (levelFilter !== "ALL" && p.risk_level?.toUpperCase() !== levelFilter) {
      return false;
    }
    if (hazardFilter !== "ALL") {
      const hazardLower = hazardFilter.toLowerCase();
      const ptHazardLower = (p.risk_type || "").toLowerCase();
      if (!ptHazardLower.includes(hazardLower)) return false;
    }
    return true;
  });

  useEffect(() => {
    if (typeof window === "undefined" || !mapContainerRef.current) return;

    let isMounted = true;

    import("leaflet").then((L) => {
      if (!isMounted || !mapContainerRef.current) return;

      // Fix default marker icon assets in Leaflet with Next.js
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      // Initialize map instance if not already created
      if (!mapInstanceRef.current) {
        const defaultLat = 19.7515; // Maharashtra / Central India center
        const defaultLng = 75.7139;

        const map = L.map(mapContainerRef.current, {
          zoomControl: true,
          scrollWheelZoom: true,
        }).setView([defaultLat, defaultLng], 6);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | KrushiRakshak GeoSpatial',
          maxZoom: 18,
        }).addTo(map);

        const markersLayer = L.layerGroup().addTo(map);
        markersLayerRef.current = markersLayer;
        mapInstanceRef.current = map;
      }

      const map = mapInstanceRef.current;
      const markersLayer = markersLayerRef.current;
      markersLayer.clearLayers();

      const getPinColor = (level?: string) => {
        switch (level?.toUpperCase()) {
          case "HIGH":
            return "#ef4444"; // Red
          case "MEDIUM":
            return "#f59e0b"; // Amber
          case "LOW":
          default:
            return "#10b981"; // Emerald Green
        }
      };

      const getPinBadgeBg = (level?: string) => {
        switch (level?.toUpperCase()) {
          case "HIGH":
            return "#fee2e2";
          case "MEDIUM":
            return "#fef3c7";
          case "LOW":
          default:
            return "#d1fae5";
        }
      };

      const getPinBadgeColor = (level?: string) => {
        switch (level?.toUpperCase()) {
          case "HIGH":
            return "#991b1b";
          case "MEDIUM":
            return "#92400e";
          case "LOW":
          default:
            return "#065f46";
        }
      };

      const latLngList: [number, number][] = [];

      filteredPoints.forEach((point) => {
        const color = getPinColor(point.risk_level);
        const badgeBg = getPinBadgeBg(point.risk_level);
        const badgeColor = getPinBadgeColor(point.risk_level);

        latLngList.push([point.latitude, point.longitude]);

        // Custom SVG DivIcon marker
        const pinHtml = `
          <div style="position: relative; width: 32px; height: 38px; transform: translate(-50%, -100%); cursor: pointer; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">
            <svg viewBox="0 0 32 40" width="32" height="40" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M16 0C7.163 0 0 7.163 0 16c0 10.5 14 22.5 15.2 23.5.5.4 1.1.4 1.6 0C18 38.5 32 26.5 32 16c0-8.837-7.163-16-16-16z" fill="${color}"/>
              <circle cx="16" cy="15" r="7" fill="#ffffff"/>
              <circle cx="16" cy="15" r="3.5" fill="${color}"/>
            </svg>
            <div style="position: absolute; top: -8px; right: -6px; background: ${color}; color: white; font-weight: 800; font-size: 9px; padding: 1px 4px; border-radius: 9999px; border: 1.5px solid white;">
              ${Math.round(point.risk_score)}
            </div>
          </div>
        `;

        const icon = L.divIcon({
          className: "custom-farm-risk-pin",
          html: pinHtml,
          iconSize: [32, 40],
          iconAnchor: [16, 40],
          popupAnchor: [0, -36],
        });

        const factorsHtml =
          point.contributing_factors && point.contributing_factors.length > 0
            ? point.contributing_factors
                .map(
                  (f) =>
                    `<span style="display:inline-block; background:#f3f4f6; color:#374151; font-size:10px; padding:1px 5px; border-radius:4px; margin:2px 2px 0 0;">${f}</span>`
                )
                .join("")
            : `<span style="font-size:10px; color:#9ca3af;">Nominal conditions</span>`;

        const popupContent = `
          <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; min-width: 230px; max-width: 280px; padding: 4px;">
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #e5e7eb; padding-bottom: 6px; margin-bottom: 8px;">
              <strong style="font-size: 14px; color: #111827;">${point.farm_name}</strong>
              <span style="background: ${badgeBg}; color: ${badgeColor}; font-weight: 700; font-size: 10px; padding: 2px 7px; border-radius: 9999px; text-transform: uppercase;">
                ${point.risk_level} (${Math.round(point.risk_score)})
              </span>
            </div>
            
            <div style="font-size: 11px; color: #4b5563; line-height: 1.5; margin-bottom: 8px;">
              <div><strong>Farmer:</strong> ${point.farmer_name} &bull; <span style="color:#6b7280;">${point.mobile}</span></div>
              <div><strong>Crop:</strong> <span style="color:#065f46; font-weight:600;">${point.crop}</span> &bull; <strong>Area:</strong> ${point.area} acres</div>
              <div><strong>Location:</strong> ${point.village ? point.village + ", " : ""}${point.district || ""}${point.state ? " (" + point.state + ")" : ""}</div>
              <div><strong>Coordinates:</strong> ${point.latitude.toFixed(4)}°N, ${point.longitude.toFixed(4)}°E</div>
              <div><strong>Irrigation:</strong> ${point.irrigation_available ? "Available" : "Rainfed / None"}</div>
            </div>

            <div style="background: #f9fafb; border: 1px solid #f3f4f6; border-radius: 6px; padding: 6px; margin-bottom: 8px;">
              <div style="font-size: 10px; font-weight: 700; color: #374151; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">
                Dominant Hazard
              </div>
              <div style="font-size: 12px; font-weight: 700; color: ${color};">
                ${point.risk_type || "General Agricultural Risk"}
              </div>
              <div style="font-size: 10px; color: #6b7280; margin-top: 2px;">
                Vulnerability: <strong style="color:#1f2937;">${point.vulnerability_level || "MODERATE"}</strong> (${Math.round(point.vulnerability_score || 50)}/100)
              </div>
            </div>

            <div>
              <div style="font-size: 10px; font-weight: 600; color: #6b7280; margin-bottom: 2px;">Contributing Factors:</div>
              <div>${factorsHtml}</div>
            </div>
          </div>
        `;

        L.marker([point.latitude, point.longitude], { icon })
          .bindPopup(popupContent)
          .addTo(markersLayer);
      });

      // Fit map bounds if points are available
      if (latLngList.length > 0) {
        const bounds = L.latLngBounds(latLngList);
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 13 });
      }
    });

    return () => {
      isMounted = false;
    };
  }, [filteredPoints]);

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Map Header & Filter Controls */}
      <div className="p-4 bg-slate-50 border-b border-gray-200 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-sm">
            <MapPin className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm sm:text-base font-bold text-gray-900 flex items-center gap-2">
              Government Geographic Risk Map
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                {filteredPoints.length} of {points.length} Farms Plotted
              </span>
            </h3>
            <p className="text-xs text-gray-500">
              Interactive satellite &amp; parcel hazard layer color-coded by AI risk level.
            </p>
          </div>
        </div>

        {/* Filter Toolbar */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Risk Level Filter */}
          <div className="flex items-center gap-1 bg-white p-1 rounded-xl border border-gray-200 text-xs">
            <Filter className="w-3.5 h-3.5 text-gray-400 ml-1" />
            <button
              onClick={() => setLevelFilter("ALL")}
              className={`px-2 py-1 rounded-lg font-medium transition-all ${
                levelFilter === "ALL" ? "bg-gray-900 text-white" : "text-gray-600 hover:text-gray-900"
              }`}
            >
              All
            </button>
            <button
              onClick={() => setLevelFilter("HIGH")}
              className={`px-2 py-1 rounded-lg font-medium transition-all ${
                levelFilter === "HIGH" ? "bg-rose-600 text-white" : "text-gray-600 hover:text-rose-600"
              }`}
            >
              High
            </button>
            <button
              onClick={() => setLevelFilter("MEDIUM")}
              className={`px-2 py-1 rounded-lg font-medium transition-all ${
                levelFilter === "MEDIUM" ? "bg-amber-500 text-white" : "text-gray-600 hover:text-amber-600"
              }`}
            >
              Medium
            </button>
            <button
              onClick={() => setLevelFilter("LOW")}
              className={`px-2 py-1 rounded-lg font-medium transition-all ${
                levelFilter === "LOW" ? "bg-emerald-600 text-white" : "text-gray-600 hover:text-emerald-600"
              }`}
            >
              Low
            </button>
          </div>

          {/* Hazard Filter */}
          <select
            value={hazardFilter}
            onChange={(e) => setHazardFilter(e.target.value)}
            className="px-2.5 py-1.5 bg-white border border-gray-200 rounded-xl text-xs font-semibold text-gray-700 outline-none focus:ring-1 focus:ring-emerald-500"
          >
            <option value="ALL">All Hazards</option>
            <option value="DROUGHT">Drought</option>
            <option value="FLOOD">Flood / Waterlogging</option>
            <option value="HEAT">Heat Stress</option>
            <option value="RAINFALL">Extreme Rainfall</option>
          </select>
        </div>
      </div>

      {/* Map Container */}
      <div className="relative">
        <div ref={mapContainerRef} className="w-full h-[460px] z-0" />

        {/* Interactive Floating Legend */}
        <div className="absolute bottom-4 left-4 z-[400] bg-white/95 backdrop-blur-sm p-3 rounded-xl border border-gray-200 shadow-md text-xs space-y-1.5 max-w-[220px]">
          <div className="font-bold text-gray-800 text-[11px] uppercase tracking-wider mb-1 flex items-center gap-1">
            <Layers className="w-3.5 h-3.5 text-gray-500" />
            Risk Index Legend
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-full bg-emerald-500 border border-white shadow-xs inline-block" />
            <span className="text-gray-700"><strong>LOW</strong> (0–30 Score)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-full bg-amber-500 border border-white shadow-xs inline-block" />
            <span className="text-gray-700"><strong>MEDIUM</strong> (31–70 Score)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-full bg-rose-500 border border-white shadow-xs inline-block" />
            <span className="text-gray-700"><strong>HIGH</strong> (71–100 Score)</span>
          </div>
          <div className="pt-1 text-[10px] text-gray-500 border-t border-gray-100 flex items-center gap-1">
            <Info className="w-3 h-3 text-gray-400" /> Click any pin for farm details.
          </div>
        </div>
      </div>
    </div>
  );
};
