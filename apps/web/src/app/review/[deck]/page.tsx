"use client";

import Link from "next/link";
import { notFound, useParams, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useAuthGuard } from "../../../lib/auth";
import { apiFetch, fetchDueCards, submitReview } from "../../../lib/api";

type Deck = {
  id: number;
  slug: string;
  name: string;
};

type RenderedCard = {
  id: number;
  front: string;
  back: string;
  mnemonic?: string | null;
  note?: {
    field_values: {
      value_text?: string | null;
      field?: { name: string };
    }[];
  };
};

export default function ReviewPage() {
  const router = useRouter();
  const params = useParams();
  const deckParam = (params?.deck as string | undefined) || "";
  const { ready } = useAuthGuard(router);

  const [deck, setDeck] = useState<Deck | null>(null);
  const [queue, setQueue] = useState<RenderedCard[]>([]);
  const [current, setCurrent] = useState<RenderedCard | null>(null);
  const [answer, setAnswer] = useState("");
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!ready) return;
    if (!deckParam) {
      notFound();
      return;
    }
    loadData();
  }, [deckParam, ready]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, [current, loading]);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const decks = await apiFetch<Deck[]>("/decks");
      const found = decks.find((d) => d.slug === deckParam);
      if (!found) {
        notFound();
        return;
      }
      setDeck(found);
      const cards = await fetchDueCards<RenderedCard>(found.id, 20);
      setQueue(cards);
      setCurrent(cards[0] ?? null);
      setAnswer("");
      setIsCorrect(null);
      setShowAnswer(false);
    } catch (err: any) {
      setError(err?.message || "Erro ao carregar cards de revisão");
    } finally {
      setLoading(false);
    }
  }

  const finished = queue.length === 0;
  const normalize = (v: string) => v.trim().toLowerCase();
  const audioUrl =
    current?.note?.field_values?.find((fv) => fv.field?.name === "audio")?.media_asset?.url ||
    current?.note?.field_values?.find((fv) => fv.field?.name === "audio")?.value_text ||
    "";

  function submit() {
    if (!current) return;
    if (isCorrect !== null) {
      nextCard();
      return;
    }
    const ok = normalize(answer) === normalize(expectedAnswer(current));
    setIsCorrect(ok);
    setShowAnswer(!ok);
    submitReview(current.id, { correct: ok }).catch((err) => console.warn("Falha ao enviar review", err));
    setQueue((prev) => {
      if (ok) return prev.slice(1);
      const [, ...rest] = prev;
      return [...rest, current];
    });
  }

  function nextCard() {
    const next = queue[0] ?? null;
    setCurrent(next);
    setAnswer("");
    setIsCorrect(null);
    setShowAnswer(false);
    if (inputRef.current) inputRef.current.focus();
  }

  function expectedAnswer(card: RenderedCard): string {
    const romaji = card.note?.field_values?.find((fv) => fv.field?.name === "romaji")?.value_text;
    if (romaji) return romaji;
    return card.back.split("\n")[0] || card.back;
  }

  const cleanBack = current?.back ? current.back.replace(/https?:\/\/[^\s"']+\.mp3/gi, "") : "";
  const frontNoImg = current?.front ? current.front.replace(/<img[^>]*>/gi, "") : "";
  const imageHtml = current?.front ? (current.front.match(/<img[^>]*>/i)?.[0] || "") : "";

  if (!ready) return null;
  if (!deckParam) return null;

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
        <div>
          <div className="text-lg font-semibold text-slate-900">Revisão {deck?.name || "..."}</div>
          <p className="text-sm text-slate-600">Cards devidos para o deck selecionado.</p>
        </div>
        <Link href="/dashboard" className="text-sm font-medium text-indigo-600 hover:underline">
          Dashboard
        </Link>
      </header>

      <main className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-8">
        <div className="flex items-center justify-between text-sm text-slate-600">
          <span>Fila: {queue.length} cards</span>
          <span>Deck: {deck?.name || deckParam}</span>
        </div>

        {loading && (
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm text-slate-600">
            Carregando cards...
          </div>
        )}
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 shadow-sm">{error}</div>
        )}

        {!loading && !error && finished && (
          <div className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
            <p className="text-xl font-semibold text-slate-900">Nada para revisar agora.</p>
            <p className="mt-2 text-sm text-slate-600">Volte depois ou recarregue a fila.</p>
            <div className="mt-4 flex justify-center gap-3">
              <button
                onClick={loadData}
                className="rounded-lg bg-indigo-600 px-4 py-2 text-white shadow hover:bg-indigo-700"
              >
                Recarregar
              </button>
              <Link
                href="/dashboard"
                className="rounded-lg border border-slate-300 px-4 py-2 text-slate-800 hover:bg-slate-100"
              >
                Dashboard
              </Link>
            </div>
          </div>
        )}

        {!loading && !error && current && (
          <div className="rounded-2xl border border-slate-200 bg-white px-8 pb-8 pt-0 shadow-sm">
            <div className="text-center text-sm uppercase tracking-wide text-indigo-600">Revisão</div>
            <div
              className="mt-4 flex flex-col items-center justify-center gap-2 text-center text-[12rem] font-semibold text-slate-900 sm:text-[15rem] [&_img]:mt-2 [&_img]:!h-auto [&_img]:!max-w-[150px] [&_img]:rounded-lg [&_img]:shadow-sm"
              dangerouslySetInnerHTML={{ __html: frontNoImg }}
            />

            <form
              className="mt-6 space-y-3"
              onSubmit={(e) => {
                e.preventDefault();
                submit();
              }}
            >
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
                  {isCorrect === null ? "Verificar" : "Próximo"}
                </button>
              </div>
            </form>

            {isCorrect === true && (
              <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-center text-emerald-800">
                Acertou! Próximo card já está na fila.
              </div>
            )}
            {isCorrect === false && (
              <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-center text-red-700">
                Resposta correta: <span className="font-semibold">{expectedAnswer(current)}</span>
              </div>
            )}

            {isCorrect !== null && (
              <div className="mt-6 flex flex-col items-center gap-3">
                <button
                  onClick={() => setShowAnswer((prev) => !prev)}
                  className="rounded-lg border border-slate-300 px-4 py-2 text-slate-800 hover:bg-slate-100"
                >
                  {showAnswer ? "Ocultar verso" : "Mostrar verso"}
                </button>
                {audioUrl && (
                  <div className="flex items-center gap-2">
                    <audio ref={audioRef} src={audioUrl} className="hidden" />
                    <button
                      type="button"
                      onClick={() => {
                        if (audioRef.current) {
                          audioRef.current.currentTime = 0;
                          audioRef.current.play().catch(() => {});
                        }
                      }}
                      className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-800 shadow-sm hover:bg-slate-100"
                    >
                      Ouvir
                    </button>
                  </div>
                )}
              </div>
            )}

            {showAnswer && (
              <div className="mt-4 text-center text-sm text-slate-600">
                <span className="font-semibold">Verso:</span>{" "}
                <span
                  className="[&_img]:mt-2 [&_img]:!h-auto [&_img]:!max-w-[150px] [&_img]:rounded-lg [&_img]:shadow-sm"
                  dangerouslySetInnerHTML={{ __html: cleanBack }}
                />
                {imageHtml && (
                  <div
                    className="mt-2 flex justify-center [&_img]:!h-auto [&_img]:!max-w-[120px] [&_img]:rounded-lg [&_img]:shadow-sm"
                    dangerouslySetInnerHTML={{ __html: imageHtml }}
                  />
                )}
                {current.mnemonic && (
                  <div className="mt-2 text-slate-500">
                    <span className="font-semibold text-slate-700">Mnemônico:</span> {current.mnemonic}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
