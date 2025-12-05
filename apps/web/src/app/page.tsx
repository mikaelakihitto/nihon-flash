import { apiFetch, getApiBaseUrl } from "../lib/api";

export default async function HomePage() {
  const health = await apiFetch<{ status: string }>("/health").catch(() => ({ status: "offline" }));

  return (
    <section className="space-y-3">
      <h1 className="text-3xl font-semibold">Nihon Flash - MVP iniciado 🎌</h1>
      <p className="text-slate-700">Base inicial do app Next.js pronta para receber os primeiros componentes.</p>
      <div className="rounded border border-slate-200 bg-white p-4 shadow-sm">
        <p className="font-medium">API status: <span className="text-green-700">{health.status}</span></p>
        <p className="text-sm text-slate-600">Fonte: {getApiBaseUrl()}/health</p>
      </div>
    </section>
  );
}
