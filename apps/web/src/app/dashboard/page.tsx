"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearToken, useAuthGuard } from "../../lib/auth";
import { apiFetch } from "../../lib/api";
import { mockStats } from "../../lib/mockData";

type Deck = { id: number; name: string; description?: string | null };

export default function DashboardPage() {
  const router = useRouter();
  const { ready } = useAuthGuard(router);
  const [decks, setDecks] = useState<Deck[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ready) return;
    apiFetch<Deck[]>("/decks")
      .then((data) => {
        setDecks(data);
        console.log("Decks carregados:", data);
      })
      .catch((err) => setError(err?.message || "Erro ao carregar decks"));
  }, [ready]);

  if (!ready) return null;

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
        <div className="text-lg font-semibold text-slate-900">Nihon Flash</div>
        <button
          onClick={() => {
            clearToken();
            router.replace("/login");
          }}
          className="text-sm font-medium text-indigo-600 hover:underline"
        >
          Logout
        </button>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8 space-y-8">
        <div className="grid gap-4 sm:grid-cols-3">
          <StatCard title="Cartas estudadas hoje" value={mockStats.studiedToday} />
          <StatCard title="Revisões pendentes" value={mockStats.reviewsPending} />
          <StatCard
            title="Progresso geral"
            value={
              <div className="space-y-1 text-sm text-slate-700">
                <p>Hiragana: {mockStats.progress.hiragana}</p>
                <p>Katakana: {mockStats.progress.katakana}</p>
              </div>
            }
          />
        </div>

        <section className="grid gap-4 sm:grid-cols-2">
          <DeckCard
            title="Estudar Hiragana"
            description="46 caracteres básicos. Revisão estilo flashcard."
            href="/study/hiragana"
          />
          <DeckCard
            title="Estudar Katakana"
            description="46 caracteres usados para empréstimos e ênfase."
            href="/study/katakana"
          />
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-900">Decks da API (GET /decks)</h3>
            {error && <span className="text-sm text-red-600">{error}</span>}
          </div>
          {decks.length === 0 ? (
            <p className="text-sm text-slate-600">Nenhum deck retornado.</p>
          ) : (
            <ul className="space-y-2 text-sm text-slate-700">
              {decks.map((deck) => (
                <li key={deck.id} className="rounded border border-slate-200 px-3 py-2">
                  <p className="font-medium">{deck.name}</p>
                  {deck.description && <p className="text-slate-600">{deck.description}</p>}
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: number | JSX.Element }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm text-slate-600">{title}</p>
      <div className="mt-2 text-2xl font-semibold text-slate-900">
        {typeof value === "number" ? value : value}
      </div>
    </div>
  );
}

function DeckCard({ title, description, href }: { title: string; description: string; href: string }) {
  return (
    <Link
      href={href}
      className="block rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
    >
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm text-slate-600">{description}</p>
      <span className="mt-4 inline-flex items-center text-sm font-medium text-indigo-600">
        Começar → 
      </span>
    </Link>
  );
}
