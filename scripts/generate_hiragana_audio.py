"""
Gera arquivos de áudio (MP3) para cada caractere do hiragana usando gTTS.
Saída: apps/web/public/audio/hiragana/<romaji>.mp3

Observação: gTTS precisa de acesso à internet para sintetizar a voz.
Execute a partir da raiz do repositório:
    python scripts/generate_hiragana_audio.py
"""

from pathlib import Path

try:
    from gtts import gTTS
except ImportError:
    raise SystemExit("Instale gTTS primeiro: pip install gTTS")


HIRAGANA_PAIRS: list[tuple[str, str]] = [
    ("あ", "a"), ("い", "i"), ("う", "u"), ("え", "e"), ("お", "o"),
    ("か", "ka"), ("き", "ki"), ("く", "ku"), ("け", "ke"), ("こ", "ko"),
    ("さ", "sa"), ("し", "shi"), ("す", "su"), ("せ", "se"), ("そ", "so"),
    ("た", "ta"), ("ち", "chi"), ("つ", "tsu"), ("て", "te"), ("と", "to"),
    ("な", "na"), ("に", "ni"), ("ぬ", "nu"), ("ね", "ne"), ("の", "no"),
    ("は", "ha"), ("ひ", "hi"), ("ふ", "fu"), ("へ", "he"), ("ほ", "ho"),
    ("ま", "ma"), ("み", "mi"), ("む", "mu"), ("め", "me"), ("も", "mo"),
    ("や", "ya"), ("ゆ", "yu"), ("よ", "yo"),
    ("ら", "ra"), ("り", "ri"), ("る", "ru"), ("れ", "re"), ("ろ", "ro"),
    ("わ", "wa"), ("を", "wo"), ("ん", "n"),
]


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    out_dir = base_dir / "apps" / "web" / "public" / "audio" / "hiragana"
    out_dir.mkdir(parents=True, exist_ok=True)

    for kana, romaji in HIRAGANA_PAIRS:
        path = out_dir / f"{romaji}.mp3"
        print(f"Gerando {path.name} ({kana})...")
        tts = gTTS(text=kana, lang="ja")
        tts.save(path)
        print(f"✔ salvo em {path}")

    print(f"Concluído. Arquivos disponíveis em {out_dir}")


if __name__ == "__main__":
    main()
