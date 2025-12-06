const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("nf_auth_token");
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const res = await fetch(`${baseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function getApiBaseUrl() {
  return baseUrl;
}

// Study/Review helpers (can be replaced with real endpoints quando prontos)
export async function fetchStudyBatch<T>(deckId: number, limit = 5): Promise<T[]> {
  const cards = await apiFetch<T[]>(`/decks/${deckId}/cards`);
  return cards.slice(0, limit);
}

export async function submitStudyResults(payload: {
  deck_id: number;
  results: { card_id: number; correct: boolean }[];
}) {
  // placeholder para integração futura
  console.log("submitStudyResults (stub)", payload);
  return { ok: true };
}

export async function fetchDueCards<T>(deckId: number, limit = 20): Promise<T[]> {
  const cards = await apiFetch<T[]>(`/decks/${deckId}/cards`);
  return cards.slice(0, limit);
}

export async function submitReview(cardId: number, result: { correct: boolean }) {
  // placeholder para integração futura
  console.log("submitReview (stub)", { cardId, result });
  return { ok: true };
}
