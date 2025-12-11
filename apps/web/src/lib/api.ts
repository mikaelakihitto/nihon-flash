import {
  KATAKANA_DECK_ID,
  ensureKatakanaDeckInList,
  getMockKatakanaCardStatus,
  getMockKatakanaCardsWithStats,
  getMockKatakanaDeckStats,
  getMockKatakanaDueCards,
  getMockKatakanaReviewStats,
  getMockKatakanaStudyBatch,
  isKatakanaCard,
  isKatakanaDeckId
} from "./mockKatakana";

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

export type DeckSummary = {
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

export async function fetchDecksWithMock(): Promise<DeckSummary[]> {
  try {
    const decks = await apiFetch<DeckSummary[]>("/decks");
    const withAvailability = decks.map((d) => ({ ...d, available: true }));
    return ensureKatakanaDeckInList(withAvailability) as DeckSummary[];
  } catch (err) {
    // Se a API não estiver disponível, ainda retornamos o mock de Katakana
    return ensureKatakanaDeckInList([]) as DeckSummary[];
  }
}

// Study/Review helpers
export async function fetchStudyBatch<T>(deckId: number, limit = 5): Promise<T[]> {
  if (isKatakanaDeckId(deckId)) {
    return getMockKatakanaStudyBatch(limit) as unknown as T[];
  }
  const batch = await apiFetch<{ cards: T[] }>(`/decks/${deckId}/study?limit=${limit}`);
  return batch.cards;
}

export async function submitStudyResults(payload: {
  deck_id: number;
  results: { card_id: number; correct: boolean }[];
}) {
  if (isKatakanaDeckId(payload.deck_id)) {
    return Promise.resolve({ updated: payload.results.length });
  }
  return apiFetch<{ updated: number }>("/study/submit", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function fetchDueCards<T>(deckId: number, limit = 20): Promise<T[]> {
  if (isKatakanaDeckId(deckId)) {
    return getMockKatakanaDueCards(limit) as unknown as T[];
  }
  return apiFetch<T[]>(`/decks/${deckId}/reviews?due_only=true&limit=${limit}`);
}

export async function submitReview(cardId: number, result: { correct: boolean }) {
  if (isKatakanaCard(cardId)) {
    return Promise.resolve({ ok: true, card_id: cardId, status: "mocked" });
  }
  return apiFetch(`/cards/${cardId}/review`, {
    method: "POST",
    body: JSON.stringify(result)
  });
}

export async function fetchDeckReviewStats(deckId: number): Promise<{ due_count_today: number; next_due_at: string | null }> {
  if (isKatakanaDeckId(deckId)) {
    return getMockKatakanaReviewStats();
  }
  return apiFetch(`/decks/${deckId}/review-stats`);
}

export async function fetchDeckStats(deckId: number) {
  if (isKatakanaDeckId(deckId)) {
    return getMockKatakanaDeckStats();
  }
  return apiFetch(`/decks/${deckId}/stats`);
}

export async function fetchCardsWithStats<T>(deckId: number) {
  if (isKatakanaDeckId(deckId)) {
    return getMockKatakanaCardsWithStats() as unknown as T[];
  }
  return apiFetch<T[]>(`/decks/${deckId}/cards-with-stats`);
}

export async function fetchCardStatus<T>(deckId: number, cardId: number): Promise<T> {
  if (isKatakanaDeckId(deckId) || isKatakanaCard(cardId)) {
    const card = getMockKatakanaCardStatus(cardId);
    if (!card) {
      throw new Error("Card not found");
    }
    return card as T;
  }
  return apiFetch<T>(`/decks/${deckId}/cards/${cardId}/status`);
}
