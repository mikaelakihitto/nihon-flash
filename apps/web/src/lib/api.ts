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
    if (res.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("nf_auth_token");
        window.location.href = "/login";
      }
      throw new Error("Não autenticado");
    }
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function getApiBaseUrl() {
  return baseUrl;
}

// Study/Review helpers
export async function fetchStudyBatch<T>(deckId: number, limit = 5): Promise<T[]> {
  const batch = await apiFetch<{ cards: T[] }>(`/decks/${deckId}/study?limit=${limit}`);
  return batch.cards;
}

export async function submitStudyResults(payload: {
  deck_id: number;
  results: { card_id: number; correct: boolean }[];
}) {
  return apiFetch<{ updated: number }>("/study/submit", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function fetchDueCards<T>(deckId: number, limit = 20): Promise<T[]> {
  return apiFetch<T[]>(`/decks/${deckId}/reviews?due_only=true&limit=${limit}`);
}

export async function submitReview(cardId: number, result: { correct: boolean }) {
  return apiFetch(`/cards/${cardId}/review`, {
    method: "POST",
    body: JSON.stringify(result)
  });
}

export async function fetchDeckReviewStats(deckId: number): Promise<{ due_count_today: number; next_due_at: string | null }> {
  return apiFetch(`/decks/${deckId}/review-stats`);
}

export async function fetchDeckStats(deckId: number) {
  return apiFetch(`/decks/${deckId}/stats`);
}

export async function fetchCardsWithStats<T>(deckId: number) {
  return apiFetch<T[]>(`/decks/${deckId}/cards-with-stats`);
}

export async function fetchCardStatus<T>(deckId: number, cardId: number): Promise<T> {
  return apiFetch<T>(`/decks/${deckId}/cards/${cardId}/status`);
}
