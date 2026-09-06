import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "KrushiRakshak | AI-Powered Climate-Resilient Agriculture Platform",
  description:
    "Predict farm-level climate risks and deliver personalized, crop-specific and multilingual advisories to farmers, with institutional vulnerability mapping.",
  keywords: [
    "KrushiRakshak",
    "Climate-Resilient Agriculture",
    "AgriTech AI",
    "Farm Climate Risk",
    "Farmer Advisory",
    "Drought Prediction",
    "Government Agriculture Dashboard",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="min-h-screen flex flex-col bg-white text-gray-900 antialiased">
        {children}
      </body>
    </html>
  );
}
