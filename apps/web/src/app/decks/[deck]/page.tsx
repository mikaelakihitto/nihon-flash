"use client";

import Link from "next/link";
import { notFound, useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuthGuard } from "../../../lib/auth";
import { apiFetch, fetchCardsWithStats, fetchDeckStats } from "../../../lib/api";

type Deck = {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  cover_image_url?: string | null;
};

type DeckStats = {
  total_cards: number;
  due_today: number;
  next_due_at: string | null;
  avg_reps: number | null;
  total_lapses: number | null;
  accuracy_estimate: number | null;
  stage_distribution: Record<string, number>;
};

type CardWithStats = {
  id: number;
  front: string;
  status: string;
  stage?: string | null;
  due_at?: string | null;
  reps?: number | null;
  lapses?: number | null;
  srs_interval?: number | null;
  srs_ease?: number | null;
  last_reviewed_at?: string | null;
};

export default function DeckDetailPage() {
  const params = useParams();
  const router = useRouter();
  const deckParam = (params?.deck as string | undefined) || "";
  const { ready } = useAuthGuard(router);

  const [deck, setDeck] = useState<Deck | null>(null);
  const [stats, setStats] = useState<DeckStats | null>(null);
  const [cards, setCards] = useState<CardWithStats[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ready || !deckParam) return;
    setLoading(true);
    setError(null);
    (async () => {
      try {
        const decks = await apiFetch<Deck[]>("/decks");
        const found = decks.find((d) => d.slug === deckParam || d.slug === `${deckParam}-basico`);
        if (!found) {
          notFound();
          return;
        }
        setDeck(found);
        const [deckStats, cardStats] = await Promise.all([
          fetchDeckStats(found.id),
          fetchCardsWithStats<CardWithStats>(found.id)
        ]);
        setStats(deckStats as DeckStats);
        setCards(cardStats);
      } catch (err: any) {
        setError(err?.message || "Erro ao carregar dados do deck");
      } finally {
        setLoading(false);
      }
    })();
  }, [deckParam, ready]);

  if (!ready) return null;
  if (!deckParam) return null;

  const nextDueFormatted =
    stats?.next_due_at &&
    new Date(stats.next_due_at).toLocaleString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
      day: "2-digit",
      month: "2-digit"
    });

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
        <div>
          <p className="text-sm text-slate-600">Detalhes do deck</p>
          <h1 className="text-xl font-semibold text-slate-900">{deck?.name || deckParam}</h1>
        </div>
        <Link href="/dashboard" className="text-sm font-medium text-indigo-600 hover:underline">
          Dashboard
        </Link>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8 space-y-6">
        {loading && (
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm text-slate-600">
            Carregando informações do deck...
          </div>
        )}
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 shadow-sm">{error}</div>
        )}

        {!loading && stats && (
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <StatCard title="Total de cards" value={stats.total_cards} />
            <StatCard title="Devidos hoje" value={stats.due_today} />
            <StatCard title="Próxima revisão" value={nextDueFormatted || "—"} />
            <StatCard title="Reps médios" value={stats.avg_reps?.toFixed(1) ?? "—"} />
            <StatCard title="Erros (lapses)" value={stats.total_lapses ?? "—"} />
            <StatCard
              title="Acurácia estimada"
              value={stats.accuracy_estimate !== null && stats.accuracy_estimate !== undefined ? `${Math.round(stats.accuracy_estimate * 100)}%` : "—"}
            />
          </section>
        )}

        {!loading && stats && (
          <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-900">Distribuição por estágio</h3>
            <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {Object.entries(stats.stage_distribution || {}).map(([stage, count]) => (
                <div key={stage} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700">
                  <div className="font-semibold capitalize">{stage.replace("_", " ")}</div>
                  <div>{count} cards</div>
                </div>
              ))}
              {Object.keys(stats.stage_distribution || {}).length === 0 && (
                <p className="text-sm text-slate-600">Sem dados de estágio ainda.</p>
              )}
            </div>
          </section>
        )}

        {!loading && cards.length > 0 && (
          <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-900">Cards do deck</h3>
              <span className="text-xs text-slate-500">{cards.length} itens</span>
            </div>
            <div className="mt-4 overflow-x-auto">
              <table className="min-w-full text-left text-sm text-slate-700">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="px-3 py-2 font-semibold">Frente</th>
                    <th className="px-3 py-2 font-semibold">Estágio</th>
                    <th className="px-3 py-2 font-semibold">Próxima revisão</th>
                    <th className="px-3 py-2 font-semibold">Reps</th>
                    <th className="px-3 py-2 font-semibold">Erros</th>
                    <th className="px-3 py-2 font-semibold">Última</th>
                  </tr>
                </thead>
                <tbody>
                  {cards.map((card) => (
                    <tr key={card.id} className="border-b border-slate-100">
                      <td className="px-3 py-2 text-slate-900">{card.front}</td>
                      <td className="px-3 py-2 capitalize">{card.stage || "—"}</td>
                      <td className="px-3 py-2">
                        {card.due_at
                          ? new Date(card.due_at).toLocaleString("pt-BR", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "2-digit" })
                          : "—"}
                      </td>
                      <td className="px-3 py-2">{card.reps ?? "—"}</td>
                      <td className="px-3 py-2">{card.lapses ?? "—"}</td>
                      <td className="px-3 py-2">
                        {card.last_reviewed_at
                          ? new Date(card.last_reviewed_at).toLocaleString("pt-BR", {
                              hour: "2-digit",
                              minute: "2-digit",
                              day: "2-digit",
                              month: "2-digit"
                            })
                          : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: number | string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm text-slate-600">{title}</p>
      <div className="mt-2 text-2xl font-semibold text-slate-900">{value}</div>
    </div>
  );
}
