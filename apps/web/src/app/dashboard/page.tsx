"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearToken, useAuthGuard } from "../../lib/auth";
import { apiFetch } from "../../lib/api";

type Deck = {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
  description_md?: string | null;
  cover_image_url?: string | null;
  instructions_md?: string | null;
  is_public?: boolean;
  tags?: string[];
  note_types?: { template_count: number; field_count: number }[];
  available?: boolean;
};

const placeholders: Deck[] = [
  {
    id: 10_001,
    name: "Katakana - Básico",
    slug: "katakana",
    description: "46 caracteres para palavras estrangeiras e ênfase.",
    cover_image_url: null,
    note_types: [],
    available: false
  },
  {
    id: 10_002,
    name: "Vocabulário N5",
    slug: "vocabulario-n5",
    description: "Vocabulário essencial do JLPT N5.",
    cover_image_url: null,
    note_types: [],
    available: false
  },
  {
    id: 10_003,
    name: "Kanji N5",
    slug: "kanji-n5",
    description: "Primeiros kanji com leituras e significados.",
    cover_image_url: null,
    note_types: [],
    available: false
  }
];

export default function DashboardPage() {
  const router = useRouter();
  const { ready } = useAuthGuard(router);
  const [decks, setDecks] = useState<Deck[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ready) return;
    apiFetch<Deck[]>("/decks")
      .then((data) => {
        setDecks(data.map((d) => ({ ...d, available: true })));
      })
      .catch((err) => setError(err?.message || "Erro ao carregar decks"));
  }, [ready]);

  if (!ready) return null;

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
        <div>
          <p className="text-sm text-slate-600">Olá, estudante 👋</p>
          <h1 className="text-xl font-semibold text-slate-900">Pronto para estudar japonês hoje?</h1>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/decks"
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-800 transition hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
            aria-label="Ver decks"
          >
            Ver decks
          </Link>
          <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm">
            <p className="font-semibold">🔥 Streak: --</p>
            <p className="text-xs text-slate-500">Cards para hoje: --</p>
          </div>
          <Link
            href="/profile"
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-800 transition hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
            aria-label="Ir para perfil e preferências"
          >
            Perfil
          </Link>
          <button
            onClick={() => {
              clearToken();
              router.replace("/login");
            }}
            className="text-sm font-medium text-indigo-600 hover:underline"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8 space-y-8">
        {/* Bloco 1 - Próxima ação */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm md:p-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="space-y-2">
              <p className="text-sm uppercase tracking-[0.2em] text-indigo-600">Próxima ação</p>
              <h2 className="text-3xl font-semibold text-slate-900">Você tem cards para revisar hoje</h2>
              <p className="text-slate-600">
                Comece pela revisão para consolidar sua memória antes de ver novos símbolos.
              </p>
            </div>
            <div className="flex flex-col gap-3 md:w-64">
              <Link
                href="/study/hiragana"
                className="w-full rounded-lg bg-indigo-600 px-4 py-3 text-center text-white shadow hover:bg-indigo-700"
              >
                Começar revisão agora
              </Link>
              <Link
                href="/review/hiragana"
                className="w-full rounded-lg border border-indigo-200 bg-indigo-50 px-4 py-3 text-center text-indigo-700 hover:bg-indigo-100"
              >
                Revisar cards devidos
              </Link>
            </div>
          </div>
        </section>

        {/* Bloco 2 - Trilhas */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-slate-900">Trilhas</h3>
            {error && <span className="text-sm text-red-600">{error}</span>}
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {[...decks, ...placeholders].map((deck) => (
              <DeckCard
                key={deck.id}
                title={deck.name}
                description={deck.description || ""}
                cover={deck.cover_image_url}
                href={deck.available ? `/study/${deck.slug}` : undefined}
                noteTypes={deck.note_types?.length ?? 0}
                available={deck.available ?? false}
              />
            ))}
          </div>
        </section>

        {/* Bloco 3 - Mini estatísticas */}
        <section className="grid gap-4 sm:grid-cols-3">
          <StatCard title="Streak" value="--" />
          <StatCard title="Cards estudados" value="--" />
          <StatCard title="Taxa de acerto (7d)" value="--" />
        </section>

        {/* Bloco 4 - Dica */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm uppercase tracking-[0.2em] text-indigo-600">Dica rápida</p>
          <h4 className="mt-2 text-lg font-semibold text-slate-900">Estude um pouco todo dia</h4>
          <p className="mt-2 text-slate-600">
            Em vez de tentar decorar tudo de uma vez, estude alguns minutos diariamente. O segredo é a repetição
            espaçada, não o esforço pontual.
          </p>
        </section>
      </main>
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: number | string | JSX.Element }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm text-slate-600">{title}</p>
      <div className="mt-2 text-2xl font-semibold text-slate-900">
        {typeof value === "number" ? value : value}
      </div>
    </div>
  );
}

function DeckCard({
  title,
  description,
  cover,
  href,
  noteTypes,
  available
}: {
  title: string;
  description: string;
  cover?: string | null;
  href?: string;
  noteTypes: number;
  available: boolean;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-center justify-between gap-2">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
          <p className="text-sm text-slate-600">{description}</p>
        </div>
        {cover && <img src={cover} alt="" className="h-12 w-20 rounded object-cover" />}
      </div>
      <div className="mt-2 text-xs uppercase tracking-wide text-slate-500">
        {available ? "Disponível" : "Em breve"}
      </div>
      <div className="mt-4 text-sm text-slate-600">Modelos de nota: {noteTypes}</div>
      {available && href ? (
        <Link
          href={href}
          className="mt-4 inline-flex items-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow hover:bg-indigo-700"
        >
          Estudar
        </Link>
      ) : (
        <button className="mt-4 inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 opacity-60">
          Indisponível
        </button>
      )}
    </div>
  );
}
