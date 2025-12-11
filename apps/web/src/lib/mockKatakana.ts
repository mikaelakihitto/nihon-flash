export type MockDeck = {
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

export type MockNoteFieldValue = {
  value_text?: string | null;
  field?: { name: string };
  media_asset?: { url?: string | null };
};

export type MockRenderedCard = {
  id: number;
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
  note?: { field_values: MockNoteFieldValue[] } | null;
  template_name?: string | null;
};

const now = new Date();
const iso = (date: Date) => date.toISOString();

export const KATAKANA_DECK: MockDeck = {
  id: 2_001,
  name: "Katakana - Básico",
  slug: "katakana-basico",
  description: "Mock do deck de Katakana para testar o frontend.",
  description_md: "Deck fictício para pré-visualizar o fluxo de Katakana.",
  cover_image_url: null,
  instructions_md: "Revise os 46 caracteres básicos do Katakana com áudio e mnemônicos.",
  is_public: true,
  tags: ["katakana", "mock", "kana"],
  note_types: [{ template_count: 1, field_count: 5 }],
  available: true
};

export const KATAKANA_DECK_ID = KATAKANA_DECK.id;

const mockCards: MockRenderedCard[] = [
  {
    id: 200_101,
    note_id: 200_101,
    card_template_id: 2_001,
    mnemonic: "Parece um poste com telhado: som aberto, 'a'.",
    status: "new",
    stage: "curto_prazo",
    srs_interval: 0,
    srs_ease: 2.5,
    due_at: iso(new Date(now.getTime() - 60 * 60 * 1000)),
    last_reviewed_at: null,
    lapses: 0,
    reps: 0,
    front: '<div class="text-[10rem] leading-none">ア</div>',
    back: "a\nExemplo: アイス (aisu)",
    note: {
      field_values: [
        { field: { name: "kana" }, value_text: "ア" },
        { field: { name: "romaji" }, value_text: "a" },
        { field: { name: "exemplo" }, value_text: "アイス (aisu)" },
        { field: { name: "dica" }, value_text: "Pense em um poste com telhado para lembrar o som 'a'." },
        { field: { name: "audio" }, value_text: "" }
      ]
    },
    template_name: "Reconhecer kana"
  },
  {
    id: 200_102,
    note_id: 200_102,
    card_template_id: 2_001,
    mnemonic: "Linha reta com gancho, lembra o som 'i'.",
    status: "new",
    stage: "curto_prazo",
    srs_interval: 0,
    srs_ease: 2.5,
    due_at: iso(new Date(now.getTime() + 30 * 60 * 1000)),
    last_reviewed_at: null,
    lapses: 0,
    reps: 0,
    front: '<div class="text-[10rem] leading-none">イ</div>',
    back: "i\nExemplo: イギリス (igirisu)",
    note: {
      field_values: [
        { field: { name: "kana" }, value_text: "イ" },
        { field: { name: "romaji" }, value_text: "i" },
        { field: { name: "exemplo" }, value_text: "イギリス (igirisu)" },
        { field: { name: "dica" }, value_text: "Duas linhas inclinadas que soam como 'i'." },
        { field: { name: "audio" }, value_text: "" }
      ]
    },
    template_name: "Reconhecer kana"
  },
  {
    id: 200_103,
    note_id: 200_103,
    card_template_id: 2_001,
    mnemonic: "Curva lembra uma onda sonora: 'u'.",
    status: "learning",
    stage: "transicao",
    srs_interval: 30,
    srs_ease: 2.6,
    due_at: iso(new Date(now.getTime() + 2 * 60 * 60 * 1000)),
    last_reviewed_at: iso(new Date(now.getTime() - 12 * 60 * 60 * 1000)),
    lapses: 0,
    reps: 2,
    front: '<div class="text-[10rem] leading-none">ウ</div>',
    back: "u\nExemplo: ウイルス (uirusu)",
    note: {
      field_values: [
        { field: { name: "kana" }, value_text: "ウ" },
        { field: { name: "romaji" }, value_text: "u" },
        { field: { name: "exemplo" }, value_text: "ウイルス (uirusu)" },
        { field: { name: "dica" }, value_text: "Linha curva que lembra o som 'u' saindo de uma boca." },
        { field: { name: "audio" }, value_text: "" }
      ]
    },
    template_name: "Reconhecer kana"
  },
  {
    id: 200_104,
    note_id: 200_104,
    card_template_id: 2_001,
    mnemonic: "Forma de canto/ângulo: som 'ka'.",
    status: "learning",
    stage: "consolidacao",
    srs_interval: 120,
    srs_ease: 2.7,
    due_at: iso(new Date(now.getTime() + 6 * 60 * 60 * 1000)),
    last_reviewed_at: iso(new Date(now.getTime() - 24 * 60 * 60 * 1000)),
    lapses: 1,
    reps: 3,
    front: '<div class="text-[10rem] leading-none">カ</div>',
    back: "ka\nExemplo: カメラ (kamera)",
    note: {
      field_values: [
        { field: { name: "kana" }, value_text: "カ" },
        { field: { name: "romaji" }, value_text: "ka" },
        { field: { name: "exemplo" }, value_text: "カメラ (kamera)" },
        { field: { name: "dica" }, value_text: "Lembra um canto: use-o para lembrar o som 'ka'." },
        { field: { name: "audio" }, value_text: "" }
      ]
    },
    template_name: "Reconhecer kana"
  },
  {
    id: 200_105,
    note_id: 200_105,
    card_template_id: 2_001,
    mnemonic: "Pincelada reta com gancho suave: som 'ki'.",
    status: "review",
    stage: "longo_prazo",
    srs_interval: 240,
    srs_ease: 2.8,
    due_at: iso(new Date(now.getTime() + 18 * 60 * 60 * 1000)),
    last_reviewed_at: iso(new Date(now.getTime() - 72 * 60 * 60 * 1000)),
    lapses: 1,
    reps: 4,
    front: '<div class="text-[10rem] leading-none">キ</div>',
    back: "ki\nExemplo: キウイ (kiui)",
    note: {
      field_values: [
        { field: { name: "kana" }, value_text: "キ" },
        { field: { name: "romaji" }, value_text: "ki" },
        { field: { name: "exemplo" }, value_text: "キウイ (kiui)" },
        { field: { name: "dica" }, value_text: "Parece um 'K' angular para lembrar 'ki'." },
        { field: { name: "audio" }, value_text: "" }
      ]
    },
    template_name: "Reconhecer kana"
  },
  {
    id: 200_106,
    note_id: 200_106,
    card_template_id: 2_001,
    mnemonic: "Três traços como garfos de salada: 'sa'.",
    status: "review",
    stage: "consolidacao",
    srs_interval: 180,
    srs_ease: 2.6,
    due_at: iso(new Date(now.getTime() + 4 * 60 * 60 * 1000)),
    last_reviewed_at: iso(new Date(now.getTime() - 48 * 60 * 60 * 1000)),
    lapses: 0,
    reps: 3,
    front: '<div class="text-[10rem] leading-none">サ</div>',
    back: "sa\nExemplo: サラダ (sarada)",
    note: {
      field_values: [
        { field: { name: "kana" }, value_text: "サ" },
        { field: { name: "romaji" }, value_text: "sa" },
        { field: { name: "exemplo" }, value_text: "サラダ (sarada)" },
        { field: { name: "dica" }, value_text: "Três traços lembram garfos de salada: 'sa'." },
        { field: { name: "audio" }, value_text: "" }
      ]
    },
    template_name: "Reconhecer kana"
  },
  {
    id: 200_107,
    note_id: 200_107,
    card_template_id: 2_001,
    mnemonic: "Parece um peixe estilizado, mas soa 'shi'.",
    status: "review",
    stage: "longo_prazo",
    srs_interval: 360,
    srs_ease: 2.9,
    due_at: iso(new Date(now.getTime() + 22 * 60 * 60 * 1000)),
    last_reviewed_at: iso(new Date(now.getTime() - 96 * 60 * 60 * 1000)),
    lapses: 1,
    reps: 5,
    front: '<div class="text-[10rem] leading-none">シ</div>',
    back: "shi\nExemplo: システム (shisutemu)",
    note: {
      field_values: [
        { field: { name: "kana" }, value_text: "シ" },
        { field: { name: "romaji" }, value_text: "shi" },
        { field: { name: "exemplo" }, value_text: "システム (shisutemu)" },
        { field: { name: "dica" }, value_text: "Três gotas para lembrar o som 'shi'." },
        { field: { name: "audio" }, value_text: "" }
      ]
    },
    template_name: "Reconhecer kana"
  },
  {
    id: 200_108,
    note_id: 200_108,
    card_template_id: 2_001,
    mnemonic: "Curva com gancho: som 'tsu'.",
    status: "learning",
    stage: "transicao",
    srs_interval: 90,
    srs_ease: 2.6,
    due_at: iso(new Date(now.getTime() + 8 * 60 * 60 * 1000)),
    last_reviewed_at: iso(new Date(now.getTime() - 24 * 60 * 60 * 1000)),
    lapses: 0,
    reps: 2,
    front: '<div class="text-[10rem] leading-none">ツ</div>',
    back: "tsu\nExemplo: ツナ (tsuna)",
    note: {
      field_values: [
        { field: { name: "kana" }, value_text: "ツ" },
        { field: { name: "romaji" }, value_text: "tsu" },
        { field: { name: "exemplo" }, value_text: "ツナ (tsuna)" },
        { field: { name: "dica" }, value_text: "Dois pontos verticais lembram respingos: 'tsu'." },
        { field: { name: "audio" }, value_text: "" }
      ]
    },
    template_name: "Reconhecer kana"
  },
  {
    id: 200_109,
    note_id: 200_109,
    card_template_id: 2_001,
    mnemonic: "Traço com curva baixa: 'na'.",
    status: "review",
    stage: "memoria_estavel",
    srs_interval: 720,
    srs_ease: 3.0,
    due_at: iso(new Date(now.getTime() + 36 * 60 * 60 * 1000)),
    last_reviewed_at: iso(new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)),
    lapses: 0,
    reps: 6,
    front: '<div class="text-[10rem] leading-none">ナ</div>',
    back: "na\nExemplo: ナイフ (naifu)",
    note: {
      field_values: [
        { field: { name: "kana" }, value_text: "ナ" },
        { field: { name: "romaji" }, value_text: "na" },
        { field: { name: "exemplo" }, value_text: "ナイフ (naifu)" },
        { field: { name: "dica" }, value_text: "Traço e curva simples lembram a letra 'n' para 'na'." },
        { field: { name: "audio" }, value_text: "" }
      ]
    },
    template_name: "Reconhecer kana"
  },
  {
    id: 200_110,
    note_id: 200_110,
    card_template_id: 2_001,
    mnemonic: "Linha com gancho arredondado: 'ma'.",
    status: "review",
    stage: "memoria_estavel",
    srs_interval: 1440,
    srs_ease: 2.9,
    due_at: iso(new Date(now.getTime() + 72 * 60 * 60 * 1000)),
    last_reviewed_at: iso(new Date(now.getTime() - 10 * 24 * 60 * 60 * 1000)),
    lapses: 1,
    reps: 7,
    front: '<div class="text-[10rem] leading-none">マ</div>',
    back: "ma\nExemplo: マンガ (manga)",
    note: {
      field_values: [
        { field: { name: "kana" }, value_text: "マ" },
        { field: { name: "romaji" }, value_text: "ma" },
        { field: { name: "exemplo" }, value_text: "マンガ (manga)" },
        { field: { name: "dica" }, value_text: "Forma arredondada lembra a letra 'm' em itálico: 'ma'." },
        { field: { name: "audio" }, value_text: "" }
      ]
    },
    template_name: "Reconhecer kana"
  }
];

const stageKey = (stage: string | null | undefined) => stage || "unknown";

const computeStats = () => {
  const endOfDay = new Date();
  endOfDay.setHours(23, 59, 59, 999);

  const dueToday = mockCards.filter((card) => card.due_at && new Date(card.due_at) <= endOfDay);
  const nextDue = dueToday.length
    ? dueToday.reduce<string | null>((acc, card) => {
        if (!card.due_at) return acc;
        if (!acc) return card.due_at;
        return new Date(card.due_at) < new Date(acc) ? card.due_at : acc;
      }, null)
    : null;

  const sumReps = mockCards.reduce((acc, card) => acc + (card.reps || 0), 0);
  const sumLapses = mockCards.reduce((acc, card) => acc + (card.lapses || 0), 0);
  const stageDistribution: Record<string, number> = {};
  mockCards.forEach((card) => {
    const key = stageKey(card.stage);
    stageDistribution[key] = (stageDistribution[key] || 0) + 1;
  });

  return {
    total_cards: mockCards.length,
    due_today: dueToday.length,
    next_due_at: nextDue,
    avg_reps: mockCards.length ? sumReps / mockCards.length : null,
    total_lapses: sumLapses,
    accuracy_estimate: sumReps ? Math.max(0, (sumReps - sumLapses) / sumReps) : null,
    stage_distribution: stageDistribution,
    new_available: mockCards.filter((card) => card.status === "new").length
  };
};

export function ensureKatakanaDeckInList<T extends { slug: string; id: number }>(decks: T[]): (T | MockDeck)[] {
  const hasKatakana = decks.some((d) => d.slug === KATAKANA_DECK.slug || d.slug === "katakana");
  return hasKatakana ? decks : [...decks, KATAKANA_DECK];
}

export function findKatakanaDeckBySlug(slug: string) {
  if (slug === KATAKANA_DECK.slug || slug === "katakana") return KATAKANA_DECK;
  return null;
}

export function isKatakanaDeckId(deckId: number) {
  return deckId === KATAKANA_DECK_ID;
}

export function isKatakanaCard(cardId: number) {
  return mockCards.some((card) => card.id === cardId);
}

export function getMockKatakanaDeckStats() {
  const stats = computeStats();
  return {
    ...stats,
    accuracy_estimate: stats.accuracy_estimate,
    stage_distribution: stats.stage_distribution
  };
}

export function getMockKatakanaReviewStats() {
  const stats = computeStats();
  return {
    due_count_today: stats.due_today,
    next_due_at: stats.next_due_at
  };
}

export function getMockKatakanaCardsWithStats() {
  return mockCards.map((card) => ({
    id: card.id,
    front: card.front.replace(/<[^>]+>/g, "").trim() || card.front,
    status: card.status,
    stage: card.stage,
    due_at: card.due_at,
    reps: card.reps,
    lapses: card.lapses,
    srs_interval: card.srs_interval,
    srs_ease: card.srs_ease,
    last_reviewed_at: card.last_reviewed_at
  }));
}

export function getMockKatakanaStudyBatch(limit = 5) {
  return mockCards.slice(0, limit);
}

export function getMockKatakanaDueCards(limit = 20) {
  const dueNow = mockCards
    .filter((card) => card.due_at && new Date(card.due_at) <= new Date())
    .sort((a, b) => new Date(a.due_at || 0).getTime() - new Date(b.due_at || 0).getTime());
  const slice = dueNow.slice(0, limit);
  return slice.length ? slice : mockCards.slice(0, Math.min(limit, mockCards.length));
}

export function getMockKatakanaCardStatus(cardId: number) {
  const card = mockCards.find((c) => c.id === cardId);
  if (!card) return null;
  return {
    ...card,
    deck_id: KATAKANA_DECK_ID
  };
}

