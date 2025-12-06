"use client";

import Link from "next/link";
import { notFound, useParams, useRouter } from "next/navigation";
import { useEffect, useRef, useState, type FormEvent } from "react";
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
  note?: {
    field_values: {
      value_text?: string | null;
      field?: { name: string };
    }[];
  };
};

export default function StudyPage() {
  const router = useRouter();
  const params = useParams();
  const deckParam = (params?.deck as string | undefined) || "";

  const { ready } = useAuthGuard(router);
  const [deck, setDeck] = useState<Deck | null>(null);
  const [cards, setCards] = useState<RenderedCard[]>([]);
  const [index, setIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState("");
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

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
        setAnswer("");
        setIsCorrect(null);
        setShowDetails(false);
      } catch (err: any) {
        setError(err?.message || "Erro ao carregar cartas");
      } finally {
        setLoading(false);
      }
    })();
  }, [deckParam, ready]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, [index, loading]);

  if (!ready) return null;
  if (!deckParam) return null;

  const current = cards[index];
  const total = cards.length;
  const finished = index >= total;

  function nextCard() {
    setIndex((prev) => prev + 1);
    setAnswer("");
    setIsCorrect(null);
    setShowDetails(false);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }

  function normalize(value: string): string {
    return value.trim().toLowerCase();
  }

  function expectedAnswer(card: RenderedCard): string {
    const romaji = card.note?.field_values?.find((fv) => fv.field?.name === "romaji")?.value_text;
    if (romaji) return romaji;
    // fallback para primeira linha do back
    return card.back.split("\n")[0] || card.back;
  }

  function checkAnswer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!current) return;
    if (isCorrect !== null) {
      nextCard();
      return;
    }
    const expected = normalize(expectedAnswer(current));
    const received = normalize(answer);
    const ok = received === expected;
    setIsCorrect(ok);
    setShowDetails(false);
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
            <form className="mt-6 space-y-3" onSubmit={checkAnswer}>
              <label className="block text-center text-sm text-slate-500">Digite a resposta e pressione Enter</label>
              <input
                ref={inputRef}
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                className={`w-full rounded-lg border px-4 py-3 text-center text-lg shadow-sm focus:outline-none focus:ring-2 ${
                  isCorrect === null
                    ? "border-slate-300 focus:ring-indigo-500"
                    : isCorrect
                    ? "border-emerald-500 ring-emerald-500"
                    : "border-red-400 ring-red-400"
                }`}
                placeholder="Digite aqui"
                autoComplete="off"
                readOnly={isCorrect !== null}
              />
              <div className="flex justify-center">
                <button
                  type="submit"
                  className={`rounded-lg px-4 py-2 text-white shadow ${
                    isCorrect === null
                      ? "bg-indigo-600 hover:bg-indigo-700"
                      : "bg-emerald-600 hover:bg-emerald-700"
                  } disabled:opacity-60`}
                  disabled={isCorrect === null && !answer.trim()}
                >
                  {isCorrect === null ? "Verificar" : "Próximo (Enter)"}
                </button>
              </div>
            </form>

            {isCorrect === true && (
              <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-center text-emerald-800">
                Acertou! Pressione Enter ou clique em “Próximo” para continuar.
              </div>
            )}
            {isCorrect === false && (
              <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-center text-red-700">
                Resposta correta: <span className="font-semibold">{expectedAnswer(current)}</span>. Pressione Enter para avançar.
              </div>
            )}

            <div className="mt-6 flex justify-center gap-3">
              {isCorrect !== null && (
                <>
                  <button
                    onClick={() => setShowDetails((prev) => !prev)}
                    className="rounded-lg border border-slate-300 px-4 py-2 text-slate-800 hover:bg-slate-100"
                  >
                    {showDetails ? "Ocultar detalhes" : "Ver detalhes"}
                  </button>
                  <button
                    onClick={nextCard}
                    className="rounded-lg bg-emerald-600 px-4 py-2 text-white shadow hover:bg-emerald-700"
                  >
                    Próximo
                  </button>
                </>
              )}
            </div>

            {showDetails && isCorrect !== null && (
              <div className="mt-4 rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-700 shadow-sm">
                <p className="font-semibold text-slate-900">Resposta completa:</p>
                <div className="mt-2 whitespace-pre-wrap">{current.back}</div>
                {current.mnemonic && (
                  <p className="mt-2 text-slate-600">
                    <span className="font-semibold text-slate-800">Mnemônico:</span> {current.mnemonic}
                  </p>
                )}
              </div>
            )}
          </div>
        ) : null}
      </main>
    </div>
  );
}
