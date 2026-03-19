import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";

export const metadata: Metadata = {
  title: "Slalom Field Services Intelligence",
  description: "Knowledge Graph + RAG for utility FSM consulting intelligence",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 flex flex-col">
        {/* Slalom brand header bar */}
        <header className="bg-[#00A3AD] text-white shadow-md">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Logo placeholder */}
              <div className="w-8 h-8 bg-white/20 rounded flex items-center justify-center">
                <span className="text-white font-bold text-sm">S</span>
              </div>
              <span className="font-semibold text-lg tracking-tight">
                Field Services Intelligence
              </span>
            </div>
            <span className="text-white/70 text-sm hidden sm:block">
              Utilities Practice · Phase 1a
            </span>
          </div>
        </header>

        {/* Navigation */}
        <Nav />

        {/* Page content */}
        <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        <footer className="border-t border-slate-200 py-4 text-center text-xs text-slate-400">
          Slalom Field Services Intelligence Platform · Internal Use Only
        </footer>
      </body>
    </html>
  );
}
