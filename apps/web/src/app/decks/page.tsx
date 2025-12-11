"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { fetchDecksWithMock } from "../../lib/api";

type Deck = {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  cover_image_url?: string | null;
  instructions_md?: string | null;
  note_types?: { template_count: number; field_count: number }[];
  available?: boolean;
};

const placeholders: Deck[] = [
  {
    id: 10_002,
    name: "Vocabulário N5",
    slug: "vocabulario-n5",
    description: "Vocabulário essencial do JLPT N5.",
    cover_image_url: null,
    available: false
  },
  {
    id: 10_003,
    name: "Kanji N5",
    slug: "kanji-n5",
    description: "Primeiros kanji com leituras e significados.",
    cover_image_url: null,
    available: false
  }
];

export default function DecksPage() {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchDecksWithMock()
      .then((data) => {
        const extras = placeholders.filter((p) => !data.some((deck) => deck.slug === p.slug));
        setDecks([...data, ...extras]);
      })
      .catch((err) => setError(err?.message || "Erro ao carregar decks"))
      .finally(() => setLoading(false));
  }, []);

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

        {loading && <div className="text-sm text-slate-600">Carregando decks...</div>}
        {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        <div className="grid gap-4 md:grid-cols-2">
          {decks.map((deck) => (
            <div key={deck.id} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between gap-2">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900">{deck.name}</h3>
                  <p className="text-sm text-slate-600">{deck.description}</p>
                </div>
                {deck.cover_image_url && (
                  <img src={deck.cover_image_url} alt="" className="h-12 w-20 rounded object-cover" />
                )}
              </div>
              <p className="mt-3 text-xs text-slate-500">
                {deck.note_types?.length ?? 0} modelos de nota | slug: {deck.slug}
              </p>
              {deck.available ? (
                <div className="mt-4 flex flex-wrap gap-2">
                  <Link
                    href={`/study/${deck.slug}`}
                    className="inline-flex items-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow hover:bg-indigo-700"
                  >
                    Estudar
                  </Link>
                  <Link
                    href={`/decks/${deck.slug}`}
                    className="inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100"
                  >
                    Ver estatísticas
                  </Link>
                </div>
              ) : (
                <button className="mt-4 inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 opacity-60">
                  Em breve
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
