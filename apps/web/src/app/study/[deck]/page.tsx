"use client";

import Link from "next/link";
import { notFound, useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuthGuard } from "../../../lib/auth";
import { apiFetch } from "../../../lib/api";

type Deck = {
  id: number;
  slug: string;
  name: string;
  description?: string | null;
  instructions_md?: string | null;
  cover_image_url?: string | null;
};

type RenderedCard = {
  id: number;
  front: string;
  back: string;
  mnemonic?: string | null;
  template_name?: string | null;
};

export default function StudyPage() {
  const router = useRouter();
  const params = useParams();
  const deckParam = (params?.deck as string | undefined) || "";

  const { ready } = useAuthGuard(router);
  const [deck, setDeck] = useState<Deck | null>(null);
  const [cards, setCards] = useState<RenderedCard[]>([]);
  const [index, setIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ready) return;
    if (!deckParam) {
      notFound();
      return;
    }
    setLoading(true);
    setError(null);
    (async () => {
      try {
        const decks = await apiFetch<Deck[]>("/decks");
        const found = decks.find((d) => d.slug === deckParam || d.slug === `${deckParam}-basico`);
        if (!found) {
          setLoading(false);
          notFound();
          return;
        }
        setDeck(found);
        const cardsResp = await apiFetch<RenderedCard[]>(`/decks/${found.id}/cards`);
        setCards(cardsResp);
        setIndex(0);
        setShowAnswer(false);
      } catch (err: any) {
        setError(err?.message || "Erro ao carregar cartas");
      } finally {
        setLoading(false);
      }
    })();
  }, [deckParam, ready]);

  if (!ready) return null;
  if (!deckParam) return null;

  const current = cards[index];
  const total = cards.length;
  const finished = index >= total;

  function nextCard() {
    setShowAnswer(false);
    setIndex((prev) => prev + 1);
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
        <div>
          <div className="text-lg font-semibold text-slate-900">Nihon Flash</div>
          <p className="text-sm text-slate-600 capitalize">{deckParam} study session</p>
        </div>
        <Link href="/dashboard" className="text-sm font-medium text-indigo-600 hover:underline">
          Voltar ao dashboard
        </Link>
      </header>

      <main className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-8">
        {deck && (
          <div className="flex items-center justify-between text-sm text-slate-600">
            <span>
              Progresso: {Math.min(index, total)}/{total}
            </span>
            <span>Deck: {deck.name}</span>
          </div>
        )}

        {loading && (
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm text-slate-600">
            Carregando cartas...
          </div>
        )}
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 shadow-sm">{error}</div>
        )}

        {!loading && !error && finished ? (
          <div className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
            <p className="text-xl font-semibold text-slate-900">Sessão concluída!</p>
            <p className="mt-2 text-sm text-slate-600">
              Você passou por todas as cartas deste deck. Volte ao dashboard ou reinicie a sessão.
            </p>
            <div className="mt-4 flex justify-center gap-3">
              <button
                onClick={() => {
                  setIndex(0);
                  setShowAnswer(false);
                }}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-white shadow hover:bg-indigo-700"
              >
                Reiniciar deck
              </button>
              <Link
                href="/dashboard"
                className="rounded-lg border border-slate-300 px-4 py-2 text-slate-800 hover:bg-slate-100"
              >
                Dashboard
              </Link>
            </div>
          </div>
        ) : !loading && !error && current ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="text-center text-sm uppercase tracking-wide text-indigo-600">Flashcard</div>
            <div className="mt-4 flex items-center justify-center text-4xl font-semibold text-slate-900 text-center whitespace-pre-wrap">
              {current.front}
            </div>
            {showAnswer ? (
              <div className="mt-6 whitespace-pre-wrap text-center text-2xl font-semibold text-slate-700">
                {current.back}
              </div>
            ) : (
              <div className="mt-6 text-center text-slate-500">Clique em &quot;Mostrar resposta&quot;</div>
            )}

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
              {!showAnswer ? (
                <button
                  onClick={() => setShowAnswer(true)}
                  className="rounded-lg bg-indigo-600 px-4 py-2 text-white shadow hover:bg-indigo-700"
                >
                  Mostrar resposta
                </button>
              ) : (
                <>
                  <button
                    onClick={nextCard}
                    className="rounded-lg bg-emerald-600 px-4 py-2 text-white shadow hover:bg-emerald-700"
                  >
                    Lembrei
                  </button>
                  <button
                    onClick={nextCard}
                    className="rounded-lg border border-slate-300 px-4 py-2 text-slate-800 hover:bg-slate-100"
                  >
                    Não lembrei
                  </button>
                </>
              )}
            </div>
          </div>
        ) : null}
      </main>
    </div>
  );
}
