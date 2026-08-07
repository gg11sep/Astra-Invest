import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Astra-Invest",
  description: "AI-native investment research platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        <header className="border-b border-slate-200 bg-white">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
            <a href="/" className="text-xl font-semibold tracking-tight text-astra-900">
              Astra-Invest
            </a>
            <nav className="flex gap-6 text-sm text-slate-600">
              <a href="/" className="hover:text-astra-600">
                Dashboard
              </a>
              <a href="/companies" className="hover:text-astra-600">
                Companies
              </a>
              <a href="/portfolio" className="hover:text-astra-600">
                Portfolio
              </a>
              <a href="/screen" className="hover:text-astra-600">
                Screen
              </a>
              <a href="/login" className="hover:text-astra-600">
                Login
              </a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
