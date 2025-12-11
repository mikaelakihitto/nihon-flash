"use client";

import Link from "next/link";
import { notFound, useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuthGuard } from "../../../../../lib/auth";
import { fetchCardStatus, fetchDecksWithMock } from "../../../../../lib/api";

type Deck = {
  id: number;
  name: string;
  slug: string;
};

type NoteFieldValue = {
  value_text?: string | null;
  field?: { name: string };
  media_asset?: { url?: string | null };
};

type Note = {
  field_values: NoteFieldValue[];
};

type CardStatus = {
  id: number;
  deck_id: number;
  note_id: number;
  card_template_id: number;
  mnemonic?: string | null;
  status: string;
  stage?: string | null;
  srs_interval?: number | null;
  srs_ease?: number | null;
  due_at?: string | null;
  last_reviewed_at?: string | null;
  lapses?: number | null;
  reps?: number | null;
  front: string;
  back: string;
  note?: Note | null;
  template_name?: string | null;
};

export default function CardDetailPage() {
  const params = useParams();
  const router = useRouter();
  const deckParam = (params?.deck as string | undefined) || "";
  const cardParam = params?.cardId as string | undefined;
  const cardId = Number(cardParam);
  const { ready } = useAuthGuard(router);

  const [deck, setDeck] = useState<Deck | null>(null);
  const [card, setCard] = useState<CardStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ready || !deckParam || Number.isNaN(cardId)) return;
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ready, deckParam, cardId]);

  if (!ready) return null;
  if (!deckParam || Number.isNaN(cardId)) {
    notFound();
  }

  async function fetchData() {
    setLoading(true);
    setError(null);
    try {
      const decks = await fetchDecksWithMock();
      const found = decks.find((d) => d.slug === deckParam || d.slug === `${deckParam}-basico`);
      if (!found) {
        notFound();
        return;
      }
      setDeck(found);
      const status = await fetchCardStatus<CardStatus>(found.id, cardId);
      setCard(status);
    } catch (err: any) {
      const message = err?.message || "Erro ao carregar card";
      if (typeof message === "string" && message.toLowerCase().includes("not found")) {
        notFound();
        return;
      }
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  const formattedDue =
    card?.due_at &&
    new Date(card.due_at).toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
  const formattedLast =
    card?.last_reviewed_at &&
    new Date(card.last_reviewed_at).toLocaleString("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });

  const audioUrl =
    card?.note?.field_values?.find((fv) => fv.field?.name === "audio")?.media_asset?.url ||
    card?.note?.field_values?.find((fv) => fv.field?.name === "audio")?.value_text ||
    "";
  const cleanBack =
    card?.back && audioUrl
      ? card.back.replaceAll(audioUrl, "").trim()
      : card?.back || "";

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
        <div>
          <p className="text-sm text-slate-600">Detalhe do card</p>
          <h1 className="text-xl font-semibold text-slate-900">{deck?.name || deckParam}</h1>
        </div>
        <div className="flex items-center gap-3">
          <Link href={`/decks/${deckParam}`} className="text-sm font-medium text-indigo-600 hover:underline">
            Voltar ao deck
          </Link>
          <Link href={`/study/${deckParam}`} className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white shadow hover:bg-indigo-700">
            Estudar
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-8 space-y-6">
        {loading && (
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm text-slate-600">Carregando card...</div>
        )}
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 shadow-sm">
            <p>{error}</p>
            <button
              onClick={fetchData}
              className="mt-3 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100"
            >
              Tentar novamente
            </button>
          </div>
        )}

        {!loading && !error && card && (
          <>
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500">Template</p>
                  <p className="text-base font-semibold text-slate-900">{card.template_name || "—"}</p>
                </div>
                {card.mnemonic && <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700">Mnemônico disponível</span>}
              </div>
              <div
                className="flex flex-col items-center justify-center gap-2 text-center text-6xl font-semibold leading-none text-slate-900 [&_img]:mt-0"
                dangerouslySetInnerHTML={{ __html: card.front }}
              />
              <div
                className="mt-2 text-center text-lg text-slate-700 [&_img]:mt-2 [&_img]:!h-auto [&_img]:!max-w-[200px] [&_img]:rounded-lg [&_img]:shadow-sm"
                dangerouslySetInnerHTML={{ __html: cleanBack }}
              />
              {audioUrl && (
                <div className="mt-3 flex justify-center">
                  <audio controls src={audioUrl} className="w-full max-w-sm" />
                </div>
              )}
            </section>

            <section className="grid gap-4 sm:grid-cols-2">
              <StatBox label="Status" value={card.status} />
              <StatBox label="Estágio" value={card.stage || "—"} />
              <StatBox label="Reps" value={card.reps ?? "—"} />
              <StatBox label="Erros (lapses)" value={card.lapses ?? "—"} />
              <StatBox label="Intervalo (srs_interval)" value={card.srs_interval ?? "—"} />
              <StatBox label="SRS ease" value={card.srs_ease ?? "—"} />
              <StatBox label="Próxima revisão" value={formattedDue || "—"} />
              <StatBox label="Última revisão" value={formattedLast || "—"} />
            </section>

            <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <h3 className="text-sm font-semibold text-slate-900">Campos da nota</h3>
              <div className="mt-3 space-y-3">
                {card.note?.field_values?.length ? (
                  card.note.field_values.map((fv, idx) => (
                    <div key={idx} className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-800 space-y-1">
                      <p className="font-semibold">{fv.field?.name || "Campo"}</p>
                      {fv.media_asset?.url ? (
                        <img src={fv.media_asset.url} alt={fv.field?.name || "media"} className="max-h-40 rounded-md shadow-sm" />
                      ) : (
                        <p className="text-slate-700">{fv.value_text || "—"}</p>
                      )}
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-slate-600">Sem campos para exibir.</p>
                )}
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm text-slate-600">{label}</p>
      <div className="mt-1 text-lg font-semibold text-slate-900">{value}</div>
    </div>
  );
}
