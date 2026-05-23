import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Islamic Research Agent",
  description:
    "AI-powered research assistant with Quranic references, prayer times, live weather and web research.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
