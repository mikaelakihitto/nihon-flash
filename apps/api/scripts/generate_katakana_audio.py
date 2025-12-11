"""
Gera arquivos de áudio (MP3) para cada caractere do Katakana usando gTTS.
Saída: apps/web/public/audio/katakana/<romaji>.mp3

Execute a partir da raiz do repositório:
    python apps/api/scripts/generate_katakana_audio.py
"""

from pathlib import Path

try:
    from gtts import gTTS
except ImportError:
    raise SystemExit("Instale gTTS primeiro: pip install gTTS")

from utils.common import KATAKANA_PAIRS, get_repo_root


def main() -> None:
    repo_root = get_repo_root()
    out_dir = repo_root / "apps" / "web" / "public" / "audio" / "katakana"
    out_dir.mkdir(parents=True, exist_ok=True)

    for kana, romaji in KATAKANA_PAIRS:
        path = out_dir / f"{romaji}.mp3"
        print(f"Gerando {path.name} ({kana})...")
        tts = gTTS(text=kana, lang="ja")
        tts.save(path)
        print(f"✔ salvo em {path}")

    print(f"Concluído. Arquivos disponíveis em {out_dir}")


if __name__ == "__main__":
    main()

