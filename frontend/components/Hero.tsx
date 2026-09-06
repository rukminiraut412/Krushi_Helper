import React from "react";
import Link from "next/link";
import { BackendStatusBadge } from "./BackendStatusBadge";
import { ShieldCheck, ArrowRight, Sprout, MapPin, Compass, Globe2 } from "lucide-react";

export const Hero: React.FC = () => {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-emerald-50/60 via-white to-white pt-12 pb-20 sm:pt-16 sm:pb-28">
      {/* Decorative background grid & glow */}
      <div className="absolute inset-0 pointer-events-none opacity-40 [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black)]">
        <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-gradient-to-tr from-emerald-300 to-teal-200 blur-3xl opacity-30 rounded-full" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div className="max-w-3xl mx-auto text-center">
          {/* Status Badge & Backend Indicator */}
          <div className="flex flex-wrap items-center justify-center gap-3 mb-6">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100/90 text-emerald-900 border border-emerald-200">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
              Next-Gen Agri-Tech Intelligence
            </span>
            <BackendStatusBadge />
          </div>

          {/* Tagline */}
          <div className="inline-block mb-3">
            <span className="text-sm sm:text-base font-semibold uppercase tracking-widest text-emerald-700 bg-emerald-50 px-3 py-1 rounded-md border border-emerald-200/60">
              Predict. Prepare. Protect.
            </span>
          </div>

          {/* Main Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-gray-900 tracking-tight leading-[1.15] mb-6">
            Climate Resilience for Every Farm, Powered by AI
          </h1>

          {/* Project Purpose / Explanation */}
          <p className="text-base sm:text-lg text-gray-600 leading-relaxed mb-8 sm:mb-10 font-normal">
            <strong>KrushiRakshak</strong> is an AI-powered climate-resilient agriculture platform that predicts farm-level climate risks and delivers personalized, crop-specific, and multilingual advisories to farmers. Simultaneously, it equips government authorities with comprehensive risk mapping and vulnerability assessments for proactive planning.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 sm:gap-5">
            {/* Farmer Portal CTA */}
            <Link
              href="/login"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-white bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 shadow-lg shadow-emerald-700/25 transition-all text-sm sm:text-base hover:-translate-y-0.5"
            >
              <Sprout className="w-5 h-5 text-emerald-100" />
              <span>Farmer Login / Register</span>
              <ArrowRight className="w-4 h-4 ml-1 opacity-80" />
            </Link>

            {/* Government Dashboard CTA */}
            <Link
              href="/login"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl font-semibold text-gray-800 bg-white hover:bg-gray-50 border border-gray-300 shadow-sm transition-all text-sm sm:text-base hover:border-emerald-500 hover:text-emerald-800 hover:-translate-y-0.5"
            >
              <MapPin className="w-5 h-5 text-emerald-700" />
              <span>Government &amp; Admin Portal</span>
            </Link>
          </div>

          {/* Value Highlights Pill Bar (No Fake Statistics) */}
          <div className="mt-12 pt-8 border-t border-gray-100 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
            <div className="flex items-start gap-3 p-3 rounded-lg bg-gray-50/70 border border-gray-100">
              <div className="p-2 rounded-lg bg-emerald-100 text-emerald-800 shrink-0">
                <Compass className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-gray-900">Hyper-Local Forecasting</h4>
                <p className="text-[11px] text-gray-500">Downscaled risk detection at the individual farm parcel level.</p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 rounded-lg bg-gray-50/70 border border-gray-100">
              <div className="p-2 rounded-lg bg-emerald-100 text-emerald-800 shrink-0">
                <Globe2 className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-gray-900">Multilingual Accessibility</h4>
                <p className="text-[11px] text-gray-500">Actionable advisories delivered in native regional languages.</p>
              </div>
            </div>

            <div className="flex items-start gap-3 p-3 rounded-lg bg-gray-50/70 border border-gray-100">
              <div className="p-2 rounded-lg bg-emerald-100 text-emerald-800 shrink-0">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-gray-900">Institutional Mapping</h4>
                <p className="text-[11px] text-gray-500">Regional climate vulnerability and proactive resource allocation.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
