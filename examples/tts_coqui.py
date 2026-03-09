#!/usr/bin/env python3
"""
End-to-end example: Polish text → normalization → Coqui VITS TTS → WAV file.

Requirements:
    pip install polish-text-normalizer TTS soundfile numpy torch

Usage:
    python tts_coqui.py
    python tts_coqui.py "Twój tekst tutaj"
    python tts_coqui.py -f input.txt -o output.wav

Model info:
    - tts_models/pl/mai_female/vits (BSD-3-Clause)
    - Single female voice, no cloning
    - ~0.5x real-time on CPU, 22050 Hz
    - Max ~150 chars per inference — this script handles chunking automatically
"""

import argparse
import os
import re
import sys

import numpy as np
import soundfile as sf
import torch
from TTS.api import TTS

from polish_text_normalizer import normalize

MODEL_NAME = "tts_models/pl/mai_female/vits"
MAX_CHUNK_CHARS = 150
PAUSE_BETWEEN_CHUNKS_MS = 300

DEMO_TEXT = (
    "Dr Nowak mieszka przy ul. Długiej 15 w Krakowie. "
    "Spotkanie zaplanowano na 27.03.2026 o godz. 14:30. "
    "Cena biletu to 42,50 zł, tj. ok. $12. "
    "Jan III Sobieski rządził w XVII wieku. "
    "Kontakt: jan@example.pl, tel. 512 345 678."
)


def split_into_chunks(text: str, max_len: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split normalized text into chunks that fit the model's character limit.

    Since normalize() already expands abbreviations, we only need naive
    sentence splitting — no abbreviation-awareness required.
    """
    sentences = [s.strip() for s in re.split(r"(?<=[.!?;])\s+|\n+", text) if s.strip()]

    chunks: list[str] = []
    for sentence in sentences:
        if len(sentence) <= max_len:
            chunks.append(sentence)
            continue
        # Split at commas/semicolons/dashes, then by words as last resort
        for sub in re.split(r"(?<=[,;:–—])\s+", sentence):
            sub = sub.strip()
            if not sub:
                continue
            if len(sub) <= max_len:
                chunks.append(sub)
                continue
            current = ""
            for word in sub.split():
                if len(current) + len(word) + 1 <= max_len:
                    current = f"{current} {word}" if current else word
                else:
                    if current:
                        chunks.append(current)
                    current = word
            if current:
                chunks.append(current)
    return chunks


def synthesize(text: str, output_path: str = "output.wav") -> str:
    """Normalize, chunk, synthesize, and concatenate into a single WAV."""
    normalized = normalize(text)
    print(f"\n── Normalized ──\n{normalized}\n")

    chunks = split_into_chunks(normalized)
    print(f"Split into {len(chunks)} chunk(s)\n")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Coqui VITS on {device}...")
    tts = TTS(model_name=MODEL_NAME, progress_bar=False).to(device)

    audio_segments: list[np.ndarray] = []
    sample_rate = None

    for i, chunk in enumerate(chunks):
        if len(chunk) < 2:
            continue
        preview = chunk[:60] + ("…" if len(chunk) > 60 else "")
        print(f"  [{i + 1}/{len(chunks)}] {preview}")

        tmp = f"/tmp/_polish_tts_chunk_{i}.wav"
        tts.tts_to_file(text=chunk, file_path=tmp)
        audio, sr = sf.read(tmp)
        sample_rate = sr
        audio_segments.append(audio)
        os.remove(tmp)

    if not audio_segments:
        print("Error: no audio generated", file=sys.stderr)
        sys.exit(1)

    pause = np.zeros(int(sample_rate * PAUSE_BETWEEN_CHUNKS_MS / 1000))
    combined: list[np.ndarray] = []
    for i, seg in enumerate(audio_segments):
        if i > 0:
            combined.append(pause)
        combined.append(seg)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    sf.write(output_path, np.concatenate(combined), sample_rate)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n✓ Saved: {output_path} ({size_kb:.0f} KB)")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Polish TTS: text → normalize → Coqui VITS → WAV",
    )
    parser.add_argument("text", nargs="?", help="Text to speak (or use -f)")
    parser.add_argument("-f", "--file", help="Read text from file")
    parser.add_argument("-o", "--output", default="output.wav", help="Output WAV path")
    args = parser.parse_args()

    if args.file:
        with open(args.file) as fh:
            text = fh.read().strip()
        print(f"Read {len(text)} chars from {args.file}")
    elif args.text:
        text = args.text
    else:
        text = DEMO_TEXT
        print("No input — running demo.\n")

    print(f"── Input ──\n{text}")
    synthesize(text, args.output)


if __name__ == "__main__":
    main()
