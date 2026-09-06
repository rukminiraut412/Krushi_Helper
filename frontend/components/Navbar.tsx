"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Sprout, Building2, User as UserIcon, LayoutDashboard, CloudSun } from "lucide-react";
import { authService } from "@/services/auth";

export const Navbar: React.FC = () => {
  const [isAuth, setIsAuth] = useState(false);
  const [userRole, setUserRole] = useState<string | null>(null);

  useEffect(() => {
    setIsAuth(authService.isAuthenticated());
    const user = authService.getUser();
    if (user) {
      setUserRole(user.role);
    }
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full bg-white/95 backdrop-blur border-b border-emerald-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          {/* Brand Logo & Name */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-700 flex items-center justify-center text-white shadow-md shadow-emerald-700/20 group-hover:scale-105 transition-transform">
              <Sprout className="w-5 h-5 text-emerald-100" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xl font-bold text-gray-900 tracking-tight font-sans">
                  Krushi<span className="text-emerald-700">Rakshak</span>
                </span>
                <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 text-emerald-800">
                  AI
                </span>
              </div>
              <p className="text-[10px] text-gray-500 font-medium tracking-wide uppercase">
                Climate-Resilient Agriculture
              </p>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-600">
            {userRole === "ADMIN" ? (
              <>
                <Link href="/admin/dashboard" className="hover:text-indigo-700 transition-colors">
                  Govt Dashboard
                </Link>
                <Link href="/farmer/dashboard" className="hover:text-emerald-700 transition-colors">
                  Farmer Portal View
                </Link>
                <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-emerald-700 transition-colors">
                  API Docs
                </a>
              </>
            ) : (
              <>
                <a href="/#features" className="hover:text-emerald-700 transition-colors">
                  Platform Features
                </a>
                <Link href="/farmer/farms" className="hover:text-emerald-700 transition-colors">
                  My Farms
                </Link>
                <Link href="/farmer/climate" className="hover:text-emerald-700 transition-colors flex items-center gap-1">
                  <CloudSun className="w-4 h-4 text-emerald-600" />
                  <span>Climate Data</span>
                </Link>
                <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-emerald-700 transition-colors">
                  API Docs
                </a>
              </>
            )}
          </nav>

          {/* User Action Buttons */}
          <div className="flex items-center gap-2.5 sm:gap-3">
            {isAuth ? (
              userRole === "ADMIN" ? (
                <Link
                  href="/admin/dashboard"
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs sm:text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm"
                >
                  <Building2 className="w-4 h-4" />
                  <span>Admin Portal</span>
                </Link>
              ) : (
                <Link
                  href="/farmer/dashboard"
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs sm:text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  <span>Farmer Dashboard</span>
                </Link>
              )
            ) : (
              <>
                <Link
                  href="/login"
                  className="inline-flex items-center gap-1.5 px-3 py-2 text-xs sm:text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 hover:text-emerald-800 rounded-lg border border-gray-200 transition-colors"
                >
                  <Building2 className="w-4 h-4 text-emerald-700" />
                  <span className="hidden sm:inline">Admin / Govt</span>
                  <span className="sm:hidden">Govt</span>
                </Link>

                <Link
                  href="/login"
                  className="inline-flex items-center gap-1.5 px-3 py-2 text-xs sm:text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 rounded-lg shadow-sm shadow-emerald-700/20 transition-all hover:shadow"
                >
                  <UserIcon className="w-4 h-4" />
                  <span>Farmer Login</span>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
