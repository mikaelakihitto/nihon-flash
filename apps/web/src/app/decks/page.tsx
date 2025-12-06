"use client";

import Link from "next/link";
import { deckMeta } from "../../lib/mockData";

export default function DecksPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">Decks disponíveis</h1>
            <p className="text-slate-600">Escolha um deck para estudar ou veja o que está por vir.</p>
          </div>
          <Link
            href="/dashboard"
            className="inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100"
          >
            Voltar ao dashboard
          </Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {deckMeta.map((deck) => {
            const progress = Math.round((deck.completedCards / deck.totalCards) * 100);
            const remaining = deck.totalCards - deck.completedCards;
            return (
              <div key={deck.id} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center justify-between gap-2">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">{deck.name}</h3>
                    <p className="text-sm text-slate-600">{deck.description}</p>
                  </div>
                  {deck.status === "soon" && (
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                      Em breve
                    </span>
                  )}
                </div>
                <div className="mt-4">
                  <div className="flex items-center justify-between text-sm text-slate-600">
                    <span>Progresso</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="mt-2 h-2 rounded-full bg-slate-100">
                    <div className="h-2 rounded-full bg-indigo-500" style={{ width: `${progress}%` }} />
                  </div>
                  <p className="mt-2 text-xs text-slate-500">
                    {deck.status === "available"
                      ? `Faltam ${remaining} cartões`
                      : "Este deck estará disponível em breve."}
                  </p>
                </div>
                {deck.status === "available" ? (
                  <Link
                    href={`/study/${deck.key}`}
                    className="mt-4 inline-flex items-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow hover:bg-indigo-700"
                  >
                    Estudar
                  </Link>
                ) : (
                  <button className="mt-4 inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 opacity-60">
                    Em breve
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </main>
  );
}
