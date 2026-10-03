import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "CodeFort Dashboard",
  description: "Build with confidence.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} font-sans dark`}>
      <body className="flex h-screen bg-surface text-text-primary overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-24">
          {children}
        </main>
      </body>
    </html>
  );
}
