"use client";

import React from "react";
import { useHealthCheck } from "@/hooks/useHealthCheck";
import { CheckCircle2, AlertCircle, RefreshCw, Server } from "lucide-react";

export const BackendStatusBadge: React.FC = () => {
  const { data, status, lastChecked, refetch } = useHealthCheck();

  return (
    <div className="inline-flex items-center gap-3 px-3.5 py-1.5 rounded-full text-xs font-medium border transition-all backdrop-blur-md bg-white/80 shadow-sm border-gray-200">
      <div className="flex items-center gap-1.5">
        <Server className="w-3.5 h-3.5 text-gray-500" />
        <span className="text-gray-600 font-medium">FastAPI Backend:</span>
      </div>

      {status === "checking" && (
        <span className="flex items-center gap-1 text-amber-600 font-semibold">
          <RefreshCw className="w-3 h-3 animate-spin" />
          Connecting...
        </span>
      )}

      {status === "connected" && (
        <span className="flex items-center gap-1 text-emerald-700 font-semibold">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          Healthy ({data?.service})
        </span>
      )}

      {status === "disconnected" && (
        <span className="flex items-center gap-1 text-rose-600 font-semibold">
          <AlertCircle className="w-3.5 h-3.5 text-rose-500" />
          Disconnected (Port 8000)
        </span>
      )}

      <button
        onClick={() => refetch()}
        title="Check Backend Connection"
        className="text-gray-400 hover:text-emerald-700 transition-colors p-0.5 ml-1"
      >
        <RefreshCw className="w-3 h-3" />
      </button>

      {lastChecked && (
        <span className="text-[10px] text-gray-400 hidden sm:inline">
          {lastChecked.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
        </span>
      )}
    </div>
  );
};
