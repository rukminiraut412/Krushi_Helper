import React from "react";
import { Sprout } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-gray-300 border-t border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Col */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white">
                <Sprout className="w-5 h-5" />
              </div>
              <span className="text-xl font-bold text-white tracking-tight">
                Krushi<span className="text-emerald-400">Rakshak</span>
              </span>
            </div>
            <p className="text-sm text-gray-400 max-w-md leading-relaxed mb-4">
              AI-powered climate-resilient agriculture platform that predicts farm-level climate risks and delivers personalized, crop-specific, multilingual advisories, paired with institutional risk mapping for governmental decision-makers.
            </p>
            <p className="text-xs text-emerald-400 font-medium">
              Tagline: &quot;Predict. Prepare. Protect.&quot;
            </p>
          </div>

          {/* Technology Stack Info */}
          <div>
            <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-4">
              Platform Architecture
            </h4>
            <ul className="space-y-2 text-xs text-gray-400">
              <li>Next.js, React & TypeScript</li>
              <li>Tailwind CSS & Lucide Icons</li>
              <li>Python & FastAPI Microservices</li>
              <li>PostgreSQL & SQLAlchemy ORM</li>
              <li>Scikit-learn, Pandas & NumPy</li>
              <li>Leaflet Maps & Recharts Visualizations</li>
            </ul>
          </div>

          {/* Direct Portals */}
          <div>
            <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-4">
              System Portals
            </h4>
            <ul className="space-y-2 text-xs text-gray-400">
              <li>
                <span className="text-gray-300 font-medium">Farmer Advisory Portal</span> (Crop stage & risk feeds)
              </li>
              <li>
                <span className="text-gray-300 font-medium">Government Risk Dashboard</span> (Spatial hazard maps)
              </li>
              <li>
                <a 
                  href="http://localhost:8000/docs" 
                  target="_blank" 
                  rel="noreferrer"
                  className="hover:text-emerald-400 underline underline-offset-2"
                >
                  FastAPI Interactive Swagger Docs
                </a>
              </li>
              <li>
                <a 
                  href="http://localhost:8000/api/health" 
                  target="_blank" 
                  rel="noreferrer"
                  className="hover:text-emerald-400 underline underline-offset-2"
                >
                  Backend /api/health Status Endpoint
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-800 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-500">
          <p>© {new Date().getFullYear()} KrushiRakshak. Built for Climate-Resilient Agriculture.</p>
          <p className="mt-2 sm:mt-0">Initial Project Architecture &amp; Foundation</p>
        </div>
      </div>
    </footer>
  );
};
