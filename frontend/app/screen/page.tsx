"use client";

import { useState } from "react";
import { apiPost } from "@/lib/api";

type ScreenResult = {
  count: number;
  results: Array<{
    company: { symbol: string; name: string; sector: string | null; roce: string | null };
    matched_rules: string[];
  }>;
};

export default function ScreenPage() {
  const [minRoce, setMinRoce] = useState("20");
  const [maxDe, setMaxDe] = useState("0.5");
  const [result, setResult] = useState<ScreenResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function runScreen() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiPost<ScreenResult>("/api/v1/screen", {
        min_roce: Number(minRoce) || null,
        max_debt_to_equity: Number(maxDe) || null,
        limit: 25,
      });
      setResult(data);
    } catch (e) {
      setError(String((e as Error).message || e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Screen</h1>
      <div className="flex flex-wrap items-end gap-4 rounded-xl border border-slate-200 bg-white p-4">
        <label className="text-sm">
          <span className="text-slate-600">Min ROCE %</span>
          <input
            className="mt-1 block w-28 rounded border border-slate-300 px-2 py-1.5"
            value={minRoce}
            onChange={(e) => setMinRoce(e.target.value)}
          />
        </label>
        <label className="text-sm">
          <span className="text-slate-600">Max D/E</span>
          <input
            className="mt-1 block w-28 rounded border border-slate-300 px-2 py-1.5"
            value={maxDe}
            onChange={(e) => setMaxDe(e.target.value)}
          />
        </label>
        <button
          onClick={runScreen}
          disabled={loading}
          className="rounded-lg bg-astra-600 px-4 py-2 text-sm font-medium text-white hover:bg-astra-700 disabled:opacity-50"
        >
          {loading ? "Running…" : "Run screen"}
        </button>
      </div>
      {error && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          {error}
        </div>
      )}
      {result && (
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <p className="mb-3 text-sm text-slate-600">{result.count} matches</p>
          <ul className="space-y-2">
            {result.results.map((r, i) => (
              <li key={i} className="flex justify-between border-b border-slate-100 py-2 text-sm">
                <span>
                  <strong>{r.company.symbol}</strong> — {r.company.name}
                </span>
                <span className="text-slate-500">{r.matched_rules.join(", ")}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
