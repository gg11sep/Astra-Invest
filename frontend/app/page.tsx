export default function HomePage() {
  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
        <p className="mt-2 text-slate-600">
          AI-native investment research platform — MVP shell
        </p>
      </section>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Companies", href: "/companies", desc: "Master list & research" },
          { label: "Portfolio", href: "/portfolio", desc: "Holdings & transactions" },
          { label: "Screen", href: "/screen", desc: "Rule-based screening" },
          { label: "API Docs", href: "http://localhost:8000/docs", desc: "OpenAPI (backend)" },
        ].map((card) => (
          <a
            key={card.label}
            href={card.href}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-astra-500 hover:shadow"
          >
            <h2 className="font-semibold text-slate-900">{card.label}</h2>
            <p className="mt-1 text-sm text-slate-500">{card.desc}</p>
          </a>
        ))}
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <h2 className="font-semibold text-slate-900">Getting started</h2>
        <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-slate-600">
          <li>
            Start backend: <code className="rounded bg-slate-100 px-1">docker compose up</code>
          </li>
          <li>
            Migrate & seed: <code className="rounded bg-slate-100 px-1">make migrate && make seed</code>
          </li>
          <li>
            Run frontend: <code className="rounded bg-slate-100 px-1">cd frontend && npm install && npm run dev</code>
          </li>
          <li>Open http://localhost:3000</li>
        </ol>
      </section>
    </div>
  );
}
