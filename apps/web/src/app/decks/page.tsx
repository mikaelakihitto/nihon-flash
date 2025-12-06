"use client";

import { useEffect, useState } from "react";
import { apiFetch, getApiBaseUrl } from "../../lib/api";

type Deck = {
  id: number;
  name: string;
  description?: string | null;
};

export default function DecksPage() {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Deck[]>("/decks")
      .then(setDecks)
      .catch((err) => setError(err?.message || "Erro ao carregar decks"));
  }, []);

  return (
    <section className="space-y-3">
      <div>
        <h2 className="text-2xl font-semibold">Decks</h2>
        <p className="text-slate-700">Consumindo da API: {getApiBaseUrl()}/decks</p>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {decks.length === 0 ? (
        <p className="text-slate-600">Nenhum deck encontrado.</p>
      ) : (
        <ul className="space-y-2">
          {decks.map((deck) => (
            <li key={deck.id} className="rounded border border-slate-200 bg-white p-3 shadow-sm">
              <p className="font-medium">{deck.name}</p>
              {deck.description && <p className="text-sm text-slate-600">{deck.description}</p>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
