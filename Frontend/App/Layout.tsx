import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Providers from "./providers";
import ErrorBoundary from "@/components/common/ErrorBoundary";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SmartCropAdvisory - AI-Powered Agriculture",
  description:
    "Transform your farming with intelligent crop recommendations, disease detection, and precision irrigation management.",
  keywords:
    "agriculture, farming, AI, crop advisory, irrigation, disease detection",
  authors: [{ name: "SmartCrop Team" }],
  viewport: "width=device-width, initial-scale=1",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ErrorBoundary>
          <Providers>{children}</Providers>
        </ErrorBoundary>
      </body>
    </html>
  );
}
