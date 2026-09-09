"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { authService } from "@/services/auth";
import { Sprout, Lock, Phone, ArrowRight, AlertCircle, CheckCircle2 } from "lucide-react";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [mobile, setMobile] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (searchParams.get("registered") === "true") {
      setSuccess("Account registered successfully! Please log in with your credentials.");
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const cleanMobile = mobile.replace(/\D/g, "");
    if (!cleanMobile) {
      setError("Please enter your registered mobile number.");
      return;
    }
    if (!password) {
      setError("Please enter your password.");
      return;
    }

    setLoading(true);
    try {
      const auth = await authService.login(cleanMobile, password);
      if (auth.role === "ADMIN") {
        router.push("/admin/dashboard");
      } else {
        router.push("/farmer/dashboard");
      }
    } catch (err: any) {
      const msg = err.message || "";
     if (msg.toLowerCase().includes("failed to fetch") || msg.toLowerCase().includes("networkerror")) {
         setError("Unable to connect to the backend server. Please try again.");
    } else {
        setError(msg || "Invalid mobile number or password.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white py-8 px-5 sm:px-8 shadow-xl shadow-gray-200/50 rounded-2xl border border-gray-100">
      {success && (
        <div className="mb-5 p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 flex items-start gap-2.5 text-emerald-800 text-xs sm:text-sm">
          <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-emerald-600" />
          <span>{success}</span>
        </div>
      )}

      {error && (
        <div className="mb-5 p-3.5 rounded-xl bg-rose-50 border border-rose-200 flex items-start gap-2.5 text-rose-800 text-xs sm:text-sm">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      <form className="space-y-4" onSubmit={handleSubmit}>
        {/* Mobile input */}
        <div>
          <label className="block text-xs font-semibold text-gray-700 mb-1">
            Registered Mobile Number
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              <Phone className="w-4 h-4" />
            </div>
            <input
              type="tel"
              required
              placeholder="Enter 10-digit mobile"
              value={mobile}
              onChange={(e) => setMobile(e.target.value)}
              className="w-full pl-9 pr-3.5 py-2.5 text-sm border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all"
            />
          </div>
        </div>

        {/* Password input */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="block text-xs font-semibold text-gray-700">
              Password
            </label>
          </div>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
              <Lock className="w-4 h-4" />
            </div>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-9 pr-3.5 py-2.5 text-sm border border-gray-300 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all"
            />
          </div>
        </div>

        <div className="pt-2">
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl text-white bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 font-semibold text-sm shadow-md shadow-emerald-700/20 transition-all disabled:opacity-70"
          >
            {loading ? "Signing In..." : "Sign In"}
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </form>

      {/* Quick Test Credentials Helper */}
      <div className="mt-5 p-3 rounded-xl bg-slate-50 border border-gray-200">
        <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider block mb-2">
          Quick Demo Credentials:
        </span>
        <div className="flex flex-col sm:flex-row gap-2 text-xs">
          <button
            type="button"
            onClick={() => {
              setMobile("9876500001");
              setPassword("SecurePassword123");
            }}
            className="flex-1 text-left p-2 rounded-lg bg-white border border-gray-200 hover:border-emerald-500 hover:bg-emerald-50/50 transition-colors"
          >
            <strong className="text-emerald-800 block">Farmer Account</strong>
            <span className="text-gray-500 text-[10px]">9876500001 / SecurePassword123</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setMobile("9999900000");
              setPassword("AdminPassword123");
            }}
            className="flex-1 text-left p-2 rounded-lg bg-white border border-gray-200 hover:border-indigo-500 hover:bg-indigo-50/50 transition-colors"
          >
            <strong className="text-indigo-800 block">Admin Account</strong>
            <span className="text-gray-500 text-[10px]">9999900000 / AdminPassword123</span>
          </button>
        </div>
      </div>

      <div className="mt-5 text-center text-xs text-gray-500">
        Don&apos;t have an account yet?{" "}
        <Link href="/register" className="font-semibold text-emerald-700 hover:underline">
          Register as Farmer
        </Link>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-50/50 via-gray-50 to-white flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link href="/" className="inline-flex items-center gap-2.5 group">
          <div className="w-11 h-11 rounded-2xl bg-emerald-600 text-white flex items-center justify-center shadow-md shadow-emerald-700/20 group-hover:scale-105 transition-transform">
            <Sprout className="w-6 h-6 text-emerald-100" />
          </div>
          <span className="text-2xl font-black text-gray-900 tracking-tight">
            Krushi<span className="text-emerald-700">Rakshak</span>
          </span>
        </Link>
        <h2 className="mt-4 text-2xl font-bold tracking-tight text-gray-900">
          Farmer &amp; Admin Sign In
        </h2>
        <p className="mt-1 text-xs sm:text-sm text-gray-600">
          Access your personalized crop advisories and farm management portal
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <Suspense fallback={<div className="bg-white p-8 rounded-2xl border text-center text-xs text-gray-400">Loading login form...</div>}>
          <LoginForm />
        </Suspense>
      </div>
    </div>
  );
}
