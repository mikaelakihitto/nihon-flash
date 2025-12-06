"use client";

import Link from "next/link";
import { notFound, useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuthGuard } from "../../../lib/auth";
import { DeckName, StudyCard, getDeck } from "../../../lib/mockData";
import { apiFetch } from "../../../lib/api";

export default function StudyPage() {
  const router = useRouter();
  const params = useParams();
  const deckParam = params?.deck as DeckName | undefined;

  const { ready } = useAuthGuard(router);
  const [cards, setCards] = useState<StudyCard[]>([]);
  const [index, setIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);

  useEffect(() => {
    if (!ready) return;
    if (!deckParam || (deckParam !== "hiragana" && deckParam !== "katakana")) {
      notFound();
      return;
    }
    setCards(getDeck(deckParam));
    setIndex(0);
    setShowAnswer(false);

    // Exemplo de chamada real para /decks/{id}/cards (ids fictícios 1 e 2)
    const deckId = deckParam === "hiragana" ? 1 : 2;
    apiFetch(`/decks/${deckId}/cards`)
      .then((data) => console.log("Cards recebidos da API:", data))
      .catch((err) => console.warn("Erro ao buscar cards reais:", err?.message));
  }, [deckParam, ready]);

  if (!ready) return null;
  if (!deckParam || (deckParam !== "hiragana" && deckParam !== "katakana")) return null;

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
        <div className="flex items-center justify-between text-sm text-slate-600">
          <span>Progresso: {Math.min(index, total)}/{total}</span>
          <span>Deck: {deckParam}</span>
        </div>

        {finished ? (
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
        ) : current ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="text-center text-sm uppercase tracking-wide text-indigo-600">Flashcard</div>
            <div className="mt-4 flex items-center justify-center text-7xl font-semibold text-slate-900">
              {current.symbol}
            </div>
            {showAnswer ? (
              <div className="mt-6 text-center text-2xl font-semibold text-slate-700">{current.romaji}</div>
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
