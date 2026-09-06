import React from "react";
import { 
  CloudSunRain, 
  Languages, 
  Map, 
  Cpu, 
  Layers, 
  BellRing,
  Leaf,
  Activity
} from "lucide-react";

interface FeatureItem {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  badge: string;
  description: string;
  points: string[];
}

const features: FeatureItem[] = [
  {
    icon: CloudSunRain,
    title: "Farm-Level Climate Risk Prediction",
    badge: "Predictive AI",
    description:
      "Advanced machine learning models analyze high-resolution satellite, meteorological, and soil telemetry to forecast extreme weather hazards before they strike.",
    points: [
      "Early warning for droughts, unseasonal rainfall, and heatwaves",
      "Soil moisture and evapotranspiration risk indexes",
      "Localized pest and disease outbreak vulnerability",
    ],
  },
  {
    icon: Leaf,
    title: "Crop-Specific Personalized Advisories",
    badge: "Agronomy Engine",
    description:
      "Actionable recommendations tailored to specific crop stages, planting dates, soil types, and irrigation methods to safeguard crop yield and minimize losses.",
    points: [
      "Sowing, irrigation, and harvest window optimization",
      "Nutrient and bio-pesticide timing adjustments",
      "Contingency crop planning for aberrant monsoons",
    ],
  },
  {
    icon: Languages,
    title: "Multilingual Farmer Interface",
    badge: "Inclusive Access",
    description:
      "Breaking linguistic barriers by delivering real-time alerts and clear agronomist advisories in regional languages tailored for easy comprehension.",
    points: [
      "Intuitive localized terminology",
      "Voice and simple visual advisory cues",
      "Seamless mobile-first access for field use",
    ],
  },
  {
    icon: Map,
    title: "Government Risk Mapping & Vulnerability",
    badge: "Macro Analytics",
    description:
      "Equipping agricultural departments and disaster management authorities with interactive spatial maps to identify climate hot-spots and prioritize interventions.",
    points: [
      "District and taluk level vulnerability heatmaps",
      "Crop damage exposure and relief planning",
      "Targeted subsidization and resource mobilization",
    ],
  },
  {
    icon: Activity,
    title: "Integrated Agro-Telemetry",
    badge: "Data Fusion",
    description:
      "Multi-source data ingestion pipeline merging weather sensors, satellite remote sensing, and historical yield data into a single coherent truth.",
    points: [
      "Automated sensor & IMD weather ingestion",
      "Vegetation index (NDVI/NDWI) tracking",
      "Continuous model validation and retraining",
    ],
  },
  {
    icon: BellRing,
    title: "Proactive Disaster Warning Alerts",
    badge: "Actionable Insights",
    description:
      "Automated alerting triggers proactive measures days ahead of severe meteorological anomalies, enabling timely harvest or protective irrigation.",
    points: [
      "Pre-event defensive advisory broadcasts",
      "Frost and hail storm defensive protocols",
      "Direct communication channel to extension officers",
    ],
  },
];

export const Features: React.FC = () => {
  return (
    <section id="features" className="py-20 sm:py-28 bg-gray-50/60 border-t border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-3xl mx-auto text-center mb-16">
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-700 bg-emerald-100/70 px-3 py-1 rounded-full">
            Core Architecture & Capabilities
          </span>
          <h2 className="mt-4 text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight">
            Designed for Farmers, Engineered for Impact
          </h2>
          <p className="mt-3 text-base sm:text-lg text-gray-600">
            A unified ecosystem connecting grassroots farmers with predictive intelligence and enabling governmental bodies to build climate-resilient agricultural policies.
          </p>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <div
                key={idx}
                className="bg-white rounded-2xl p-6 sm:p-7 border border-gray-200/80 shadow-sm hover:shadow-md hover:border-emerald-300 transition-all flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between mb-5">
                    <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-100 text-emerald-700 flex items-center justify-center group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-100">
                      {feature.badge}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-gray-900 mb-2">
                    {feature.title}
                  </h3>

                  <p className="text-sm text-gray-600 leading-relaxed mb-5">
                    {feature.description}
                  </p>
                </div>

                <div className="pt-4 border-t border-gray-100">
                  <ul className="space-y-2">
                    {feature.points.map((pt, pIdx) => (
                      <li key={pIdx} className="text-xs text-gray-500 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
                        <span>{pt}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
