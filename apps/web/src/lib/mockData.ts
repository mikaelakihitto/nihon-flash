export type StudyCard = {
  id: number;
  symbol: string;
  romaji: string;
  reading?: string;
};

export type DeckName = "hiragana" | "katakana";

const hiragana: StudyCard[] = [
  { id: 1, symbol: "あ", romaji: "a" },
  { id: 2, symbol: "い", romaji: "i" },
  { id: 3, symbol: "う", romaji: "u" },
  { id: 4, symbol: "え", romaji: "e" },
  { id: 5, symbol: "お", romaji: "o" },
  { id: 6, symbol: "か", romaji: "ka" },
  { id: 7, symbol: "き", romaji: "ki" },
  { id: 8, symbol: "く", romaji: "ku" },
  { id: 9, symbol: "け", romaji: "ke" },
  { id: 10, symbol: "こ", romaji: "ko" },
  { id: 11, symbol: "さ", romaji: "sa" },
  { id: 12, symbol: "し", romaji: "shi" },
  { id: 13, symbol: "す", romaji: "su" },
  { id: 14, symbol: "せ", romaji: "se" },
  { id: 15, symbol: "そ", romaji: "so" },
  { id: 16, symbol: "た", romaji: "ta" },
  { id: 17, symbol: "ち", romaji: "chi" },
  { id: 18, symbol: "つ", romaji: "tsu" },
  { id: 19, symbol: "て", romaji: "te" },
  { id: 20, symbol: "と", romaji: "to" },
  { id: 21, symbol: "な", romaji: "na" },
  { id: 22, symbol: "に", romaji: "ni" },
  { id: 23, symbol: "ぬ", romaji: "nu" },
  { id: 24, symbol: "ね", romaji: "ne" },
  { id: 25, symbol: "の", romaji: "no" },
  { id: 26, symbol: "は", romaji: "ha" },
  { id: 27, symbol: "ひ", romaji: "hi" },
  { id: 28, symbol: "ふ", romaji: "fu" },
  { id: 29, symbol: "へ", romaji: "he" },
  { id: 30, symbol: "ほ", romaji: "ho" },
  { id: 31, symbol: "ま", romaji: "ma" },
  { id: 32, symbol: "み", romaji: "mi" },
  { id: 33, symbol: "む", romaji: "mu" },
  { id: 34, symbol: "め", romaji: "me" },
  { id: 35, symbol: "も", romaji: "mo" },
  { id: 36, symbol: "や", romaji: "ya" },
  { id: 37, symbol: "ゆ", romaji: "yu" },
  { id: 38, symbol: "よ", romaji: "yo" },
  { id: 39, symbol: "ら", romaji: "ra" },
  { id: 40, symbol: "り", romaji: "ri" },
  { id: 41, symbol: "る", romaji: "ru" },
  { id: 42, symbol: "れ", romaji: "re" },
  { id: 43, symbol: "ろ", romaji: "ro" },
  { id: 44, symbol: "わ", romaji: "wa" },
  { id: 45, symbol: "を", romaji: "wo" },
  { id: 46, symbol: "ん", romaji: "n" }
];

const katakana: StudyCard[] = [
  { id: 1, symbol: "ア", romaji: "a" },
  { id: 2, symbol: "イ", romaji: "i" },
  { id: 3, symbol: "ウ", romaji: "u" },
  { id: 4, symbol: "エ", romaji: "e" },
  { id: 5, symbol: "オ", romaji: "o" },
  { id: 6, symbol: "カ", romaji: "ka" },
  { id: 7, symbol: "キ", romaji: "ki" },
  { id: 8, symbol: "ク", romaji: "ku" },
  { id: 9, symbol: "ケ", romaji: "ke" },
  { id: 10, symbol: "コ", romaji: "ko" },
  { id: 11, symbol: "サ", romaji: "sa" },
  { id: 12, symbol: "シ", romaji: "shi" },
  { id: 13, symbol: "ス", romaji: "su" },
  { id: 14, symbol: "セ", romaji: "se" },
  { id: 15, symbol: "ソ", romaji: "so" },
  { id: 16, symbol: "タ", romaji: "ta" },
  { id: 17, symbol: "チ", romaji: "chi" },
  { id: 18, symbol: "ツ", romaji: "tsu" },
  { id: 19, symbol: "テ", romaji: "te" },
  { id: 20, symbol: "ト", romaji: "to" },
  { id: 21, symbol: "ナ", romaji: "na" },
  { id: 22, symbol: "ニ", romaji: "ni" },
  { id: 23, symbol: "ヌ", romaji: "nu" },
  { id: 24, symbol: "ネ", romaji: "ne" },
  { id: 25, symbol: "ノ", romaji: "no" },
  { id: 26, symbol: "ハ", romaji: "ha" },
  { id: 27, symbol: "ヒ", romaji: "hi" },
  { id: 28, symbol: "フ", romaji: "fu" },
  { id: 29, symbol: "ヘ", romaji: "he" },
  { id: 30, symbol: "ホ", romaji: "ho" },
  { id: 31, symbol: "マ", romaji: "ma" },
  { id: 32, symbol: "ミ", romaji: "mi" },
  { id: 33, symbol: "ム", romaji: "mu" },
  { id: 34, symbol: "メ", romaji: "me" },
  { id: 35, symbol: "モ", romaji: "mo" },
  { id: 36, symbol: "ヤ", romaji: "ya" },
  { id: 37, symbol: "ユ", romaji: "yu" },
  { id: 38, symbol: "ヨ", romaji: "yo" },
  { id: 39, symbol: "ラ", romaji: "ra" },
  { id: 40, symbol: "リ", romaji: "ri" },
  { id: 41, symbol: "ル", romaji: "ru" },
  { id: 42, symbol: "レ", romaji: "re" },
  { id: 43, symbol: "ロ", romaji: "ro" },
  { id: 44, symbol: "ワ", romaji: "wa" },
  { id: 45, symbol: "ヲ", romaji: "wo" },
  { id: 46, symbol: "ン", romaji: "n" }
];

export const decks = {
  hiragana,
  katakana
};

export function getDeck(deck: DeckName): StudyCard[] {
  return decks[deck];
}

export const mockStats = {
  studiedToday: 20,
  reviewsPending: 12,
  progress: {
    hiragana: `${hiragana.length}/${hiragana.length}`,
    katakana: `${katakana.length}/${katakana.length}`
  }
};
