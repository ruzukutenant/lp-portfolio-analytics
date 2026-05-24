import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LP Portfolio Dashboard — Sample Fund",
  description: "Comp-anchored, dilution-aware marks for a sample early-stage rolling fund cohort.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
