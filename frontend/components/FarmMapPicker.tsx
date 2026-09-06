"use client";

import React, { useEffect, useRef } from "react";
import { MapPin } from "lucide-react";

interface FarmMapPickerProps {
  latitude?: number | null;
  longitude?: number | null;
  onChange: (lat: number, lng: number) => void;
}

export const FarmMapPicker: React.FC<FarmMapPickerProps> = ({
  latitude,
  longitude,
  onChange,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markerRef = useRef<any>(null);

  useEffect(() => {
    if (typeof window === "undefined" || !mapContainerRef.current) return;

    // Dynamically import leaflet to avoid SSR issues
    let isMounted = true;

    import("leaflet").then((L) => {
      if (!isMounted || !mapContainerRef.current) return;

      // Fix default marker icons in Leaflet when bundled with Webpack / Next.js
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      const defaultLat = latitude || 19.7515; // India Central/Maharashtra default
      const defaultLng = longitude || 75.7139;
      const initialZoom = latitude && longitude ? 13 : 5;

      if (!mapInstanceRef.current) {
        const map = L.map(mapContainerRef.current).setView(
          [defaultLat, defaultLng],
          initialZoom
        );

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          maxZoom: 19,
        }).addTo(map);

        mapInstanceRef.current = map;

        // Click listener on map to select coordinates
        map.on("click", (e: any) => {
          const { lat, lng } = e.latlng;
          const roundedLat = parseFloat(lat.toFixed(6));
          const roundedLng = parseFloat(lng.toFixed(6));
          onChange(roundedLat, roundedLng);

          if (markerRef.current) {
            markerRef.current.setLatLng([roundedLat, roundedLng]);
          } else {
            const marker = L.marker([roundedLat, roundedLng], { draggable: true }).addTo(map);
            marker.on("dragend", (event: any) => {
              const pos = event.target.getLatLng();
              onChange(parseFloat(pos.lat.toFixed(6)), parseFloat(pos.lng.toFixed(6)));
            });
            markerRef.current = marker;
          }
        });
      }

      // Update marker if lat/lng are provided externally
      if (latitude && longitude && mapInstanceRef.current) {
        if (markerRef.current) {
          markerRef.current.setLatLng([latitude, longitude]);
        } else {
          const marker = L.marker([latitude, longitude], { draggable: true }).addTo(mapInstanceRef.current);
          marker.on("dragend", (event: any) => {
            const pos = event.target.getLatLng();
            onChange(parseFloat(pos.lat.toFixed(6)), parseFloat(pos.lng.toFixed(6)));
          });
          markerRef.current = marker;
        }
      }
    });

    return () => {
      isMounted = false;
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
        markerRef.current = null;
      }
    };
  }, []);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-gray-600">
        <span className="flex items-center gap-1 font-medium">
          <MapPin className="w-3.5 h-3.5 text-emerald-600" />
          Click on map to pick parcel coordinates (or drag pin)
        </span>
        {latitude && longitude ? (
          <span className="bg-emerald-50 text-emerald-800 font-mono px-2 py-0.5 rounded border border-emerald-200">
            {latitude.toFixed(4)}°, {longitude.toFixed(4)}°
          </span>
        ) : (
          <span className="text-gray-400 italic">No coordinates selected</span>
        )}
      </div>

      <div
        ref={mapContainerRef}
        className="w-full h-64 rounded-xl border border-gray-300 shadow-inner overflow-hidden z-0"
        style={{ minHeight: "240px" }}
      />
    </div>
  );
};
