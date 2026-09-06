"use client";

import React, { useEffect, useRef } from "react";
import { MapPin } from "lucide-react";

interface FarmDisplayMapProps {
  latitude?: number | null;
  longitude?: number | null;
  farmName: string;
  crop?: string | null;
  area?: number | null;
}

export const FarmDisplayMap: React.FC<FarmDisplayMapProps> = ({
  latitude,
  longitude,
  farmName,
  crop,
  area,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markerRef = useRef<any>(null);

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

      const lat = latitude || 18.5204; // Pune / Maharashtra default
      const lng = longitude || 73.8567;
      const zoomLevel = latitude && longitude ? 14 : 7;

      if (!mapInstanceRef.current) {
        const map = L.map(mapContainerRef.current, {
          zoomControl: true,
          scrollWheelZoom: false,
        }).setView([lat, lng], zoomLevel);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          maxZoom: 19,
        }).addTo(map);

        mapInstanceRef.current = map;

        if (latitude && longitude) {
          const marker = L.marker([lat, lng]).addTo(map);
          marker.bindPopup(`
            <div style="font-family: sans-serif; padding: 4px;">
              <strong style="font-size: 13px; color: #065f46;">${farmName}</strong>
              <div style="font-size: 11px; color: #4b5563; margin-top: 2px;">
                Crop: <strong>${crop || "Not set"}</strong> | Area: <strong>${area || 0} acres</strong>
              </div>
              <div style="font-size: 10px; color: #6b7280; margin-top: 2px;">
                Coordinates: ${lat.toFixed(4)}°, ${lng.toFixed(4)}°
              </div>
            </div>
          `).openPopup();
          markerRef.current = marker;
        }
      } else {
        // Map instance already exists; update view and marker
        mapInstanceRef.current.setView([lat, lng], zoomLevel);

        if (markerRef.current) {
          markerRef.current.remove();
          markerRef.current = null;
        }

        if (latitude && longitude) {
          const marker = L.marker([lat, lng]).addTo(mapInstanceRef.current);
          marker.bindPopup(`
            <div style="font-family: sans-serif; padding: 4px;">
              <strong style="font-size: 13px; color: #065f46;">${farmName}</strong>
              <div style="font-size: 11px; color: #4b5563; margin-top: 2px;">
                Crop: <strong>${crop || "Not set"}</strong> | Area: <strong>${area || 0} acres</strong>
              </div>
              <div style="font-size: 10px; color: #6b7280; margin-top: 2px;">
                Coordinates: ${lat.toFixed(4)}°, ${lng.toFixed(4)}°
              </div>
            </div>
          `).openPopup();
          markerRef.current = marker;
        }
      }
    });

    return () => {
      isMounted = false;
    };
  }, [latitude, longitude, farmName, crop, area]);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span className="flex items-center gap-1 font-semibold text-gray-700">
          <MapPin className="w-3.5 h-3.5 text-emerald-600" />
          Farm Geographic Location &amp; Parcel Pin
        </span>
        {latitude && longitude ? (
          <span className="font-mono text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            {latitude.toFixed(4)}° N, {longitude.toFixed(4)}° E
          </span>
        ) : (
          <span className="text-gray-400 italic">No coordinates registered</span>
        )}
      </div>

      <div
        ref={mapContainerRef}
        className="w-full h-72 rounded-2xl border border-gray-200 shadow-sm overflow-hidden z-0"
      />
    </div>
  );
};
