"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiGet, apiPost } from "@/lib/api";
import { clearToken, getToken } from "@/lib/auth";

type Portfolio = {
  id: string;
  name: string;
  description: string | null;
  base_currency: string;
  is_default: boolean;
};

type PortfolioList = { items: Portfolio[]; total: number };

type Holding = {
  id: string;
  company_id: string;
  quantity: string;
  average_cost: string;
};

type HoldingList = { items: Holding[]; total: number };

export default function PortfolioPage() {
  const [token, setTok] = useState<string | null>(null);
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [newName, setNewName] = useState("My Portfolio");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = getToken();
    setTok(t);
    if (!t) {
      setLoading(false);
      return;
    }
    apiGet<PortfolioList>("/api/v1/portfolios")
      .then((data) => {
        setPortfolios(data.items);
        if (data.items.length) setSelected(data.items[0].id);
      })
      .catch((e) => setError(String(e.message || e)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selected || !getToken()) return;
    apiGet<HoldingList>(`/api/v1/portfolios/${selected}/holdings`)
      .then((d) => setHoldings(d.items))
      .catch((e) => setError(String(e.message || e)));
  }, [selected]);

  async function createPortfolio() {
    try {
      const p = await apiPost<Portfolio>("/api/v1/portfolios", {
        name: newName,
        base_currency: "INR",
        is_default: portfolios.length === 0,
      });
      setPortfolios((prev) => [...prev, p]);
      setSelected(p.id);
    } catch (e) {
      setError(String((e as Error).message || e));
    }
  }

  function logout() {
    clearToken();
    setTok(null);
    setPortfolios([]);
    setHoldings([]);
  }

  if (!token) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-slate-900">Portfolio</h1>
        <p className="text-slate-600">Sign in to manage portfolios and holdings.</p>
        <Link
          href="/login"
          className="inline-block rounded-lg bg-astra-600 px-4 py-2 text-sm font-medium text-white hover:bg-astra-700"
        >
          Sign in
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Portfolio</h1>
        <button onClick={logout} className="text-sm text-slate-500 hover:text-slate-800">
          Sign out
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          {error}
        </div>
      )}

      {loading ? (
        <p className="text-slate-500">Loading…</p>
      ) : (
        <>
          <div className="flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-white p-4">
            <label className="text-sm">
              <span className="text-slate-600">New portfolio</span>
              <input
                className="mt-1 block rounded border border-slate-300 px-2 py-1.5"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
              />
            </label>
            <button
              onClick={createPortfolio}
              className="rounded-lg bg-astra-600 px-3 py-2 text-sm text-white hover:bg-astra-700"
            >
              Create
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {portfolios.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelected(p.id)}
                className={`rounded-full px-3 py-1 text-sm ${
                  selected === p.id
                    ? "bg-astra-600 text-white"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                }`}
              >
                {p.name}
              </button>
            ))}
            {!portfolios.length && (
              <p className="text-sm text-slate-500">No portfolios yet — create one above.</p>
            )}
          </div>

          {selected && (
            <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
              <div className="border-b bg-slate-50 px-4 py-2 text-sm font-medium text-slate-700">
                Holdings
              </div>
              {holdings.length === 0 ? (
                <p className="p-4 text-sm text-slate-500">
                  No holdings. Record BUY transactions via API:
                  <code className="ml-1 rounded bg-slate-100 px-1">
                    POST /api/v1/portfolios/{selected}/transactions
                  </code>
                </p>
              ) : (
                <table className="min-w-full text-left text-sm">
                  <thead className="border-b text-slate-600">
                    <tr>
                      <th className="px-4 py-2">Company ID</th>
                      <th className="px-4 py-2">Qty</th>
                      <th className="px-4 py-2">Avg cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {holdings.map((h) => (
                      <tr key={h.id} className="border-b border-slate-100">
                        <td className="px-4 py-2 font-mono text-xs">{h.company_id.slice(0, 8)}…</td>
                        <td className="px-4 py-2">{h.quantity}</td>
                        <td className="px-4 py-2">{h.average_cost}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
