"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

type Company = {
  id: string;
  symbol: string;
  exchange: string;
  name: string;
  sector: string | null;
  pe_ratio: string | null;
  roce: string | null;
};

type CompanyList = {
  items: Company[];
  total: number;
};

export default function CompaniesPage() {
  const [data, setData] = useState<CompanyList | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<CompanyList>("/api/v1/companies?page_size=50")
      .then(setData)
      .catch((e) => setError(String(e.message || e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Companies</h1>
      {loading && <p className="text-slate-500">Loading…</p>}
      {error && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
          Could not load companies. Is the backend running at localhost:8000?
          <br />
          <span className="font-mono text-xs">{error}</span>
        </div>
      )}
      {data && (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Symbol</th>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Sector</th>
                <th className="px-4 py-3 font-medium">PE</th>
                <th className="px-4 py-3 font-medium">ROCE</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((c) => (
                <tr key={c.id} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">
                    {c.symbol}
                    <span className="ml-1 text-xs text-slate-400">{c.exchange}</span>
                  </td>
                  <td className="px-4 py-3">{c.name}</td>
                  <td className="px-4 py-3 text-slate-600">{c.sector ?? "—"}</td>
                  <td className="px-4 py-3">{c.pe_ratio ?? "—"}</td>
                  <td className="px-4 py-3">{c.roce ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="px-4 py-2 text-xs text-slate-500">{data.total} companies</div>
        </div>
      )}
    </div>
  );
}
