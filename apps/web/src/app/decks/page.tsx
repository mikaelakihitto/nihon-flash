import { apiFetch, getApiBaseUrl } from "../../lib/api";

type Deck = {
  id: number;
  name: string;
  description?: string | null;
};

export default async function DecksPage() {
  const decks = await apiFetch<Deck[]>("/decks").catch(() => []);

  return (
    <section className="space-y-3">
      <div>
        <h2 className="text-2xl font-semibold">Decks</h2>
        <p className="text-slate-700">Consumindo da API: {getApiBaseUrl()}/decks</p>
      </div>

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
