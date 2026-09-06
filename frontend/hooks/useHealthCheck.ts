"use client";

import { useEffect, useState, useCallback } from "react";
import { apiService } from "@/services/api";
import { HealthResponse } from "@/types";

export type HealthState = "checking" | "connected" | "disconnected";

export function useHealthCheck() {
  const [data, setData] = useState<HealthResponse | null>(null);
  const [status, setStatus] = useState<HealthState>("checking");
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const checkHealth = useCallback(async () => {
    setStatus("checking");
    try {
      const result = await apiService.getHealth();
      if (result && result.status === "healthy") {
        setData(result);
        setStatus("connected");
      } else {
        setStatus("disconnected");
      }
    } catch {
      setStatus("disconnected");
      setData(null);
    } finally {
      setLastChecked(new Date());
    }
  }, []);

  useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  return { data, status, lastChecked, refetch: checkHealth };
}
