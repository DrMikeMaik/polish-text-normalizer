"""
Polish TTS using Coqui TTS (tts_models/pl/mai_female/vits).
Adapted from Mike's implementation — chunked synthesis with concatenation.
"""

import re
import os
import torch
import numpy as np
import soundfile as sf
from TTS.api import TTS
from polish_text_normalizer import normalize_polish_text

MODEL_NAME = "tts_models/pl/mai_female/vits"
MAX_CHUNK_SIZE = 150
PAUSE_BETWEEN_SENTENCES_MS = 300  # silence between chunks
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

_tts_model = None


def _get_model():
    global _tts_model
    if _tts_model is None:
        print(f"Loading Polish TTS model on {DEVICE}...")
        _tts_model = TTS(model_name=MODEL_NAME, progress_bar=False).to(DEVICE)
    return _tts_model


def _split_text(text: str) -> list[str]:
    """Split text into chunks at sentence/clause boundaries, preserving punctuation."""
    # Common abbreviations that end with a period but aren't sentence endings
    ABBREVS = {
        'np', 'dr', 'prof', 'mgr', 'inż', 'ul', 'al', 'pl', 'wg', 'tzn',
        'tj', 'itd', 'itp', 'ok', 'godz', 'tel', 'nr', 'pkt', 'str',
        'przyp', 'red', 'wyd', 'tys', 'mln', 'mld', 'św',
    }

    # First pass: split on sentence-ending punctuation followed by space
    raw_parts = re.split(r'(?<=[.!?;])\s+|\n+', text)

    # Second pass: re-join splits that were after abbreviations or numbers
    parts = []
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        if parts:
            prev = parts[-1]
            # Check if previous chunk ends with an abbreviation or number-period
            prev_stripped = prev.rstrip('.')
            last_word = prev_stripped.split()[-1].lower() if prev_stripped.split() else ''
            if (prev.endswith('.') and last_word in ABBREVS) or \
               re.search(r'\d\.$', prev):
                parts[-1] = prev + ' ' + part
                continue
        parts.append(part)
    chunks = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) <= MAX_CHUNK_SIZE:
            chunks.append(part)
        else:
            # Long chunk: split at commas/dashes first, then by word count
            sub_parts = re.split(r'(?<=[,;:–—])\s+', part)
            for sub in sub_parts:
                sub = sub.strip()
                if not sub:
                    continue
                if len(sub) <= MAX_CHUNK_SIZE:
                    chunks.append(sub)
                else:
                    words = sub.split()
                    current = ""
                    for word in words:
                        if len(current) + len(word) + 1 <= MAX_CHUNK_SIZE:
                            current = f"{current} {word}" if current else word
                        else:
                            if current:
                                chunks.append(current)
                            current = word
                    if current:
                        chunks.append(current)
    return chunks


def generate_polish_tts(text: str, output_file: str = "output.wav") -> str | None:
    """Generate Polish TTS audio from text, saving to output_file."""
    text = text.strip()
    if not text:
        print("Error: Empty input text")
        return None

    # Normalize text: expand abbreviations, convert numbers to words
    text = normalize_polish_text(text)
    print(f"After normalization: {text[:100]}{'...' if len(text) > 100 else ''}")

    tts = _get_model()
    chunks = _split_text(text)
    print(f"Text split into {len(chunks)} chunks")

    temp_dir = "/tmp/polish_tts_chunks"
    os.makedirs(temp_dir, exist_ok=True)

    all_audio = []
    sample_rate = None

    for i, chunk in enumerate(chunks):
        if len(chunk) < 2:
            continue
        preview = chunk[:50] + ("..." if len(chunk) > 50 else "")
        print(f"  [{i+1}/{len(chunks)}] {preview}")

        temp_file = os.path.join(temp_dir, f"chunk_{i}.wav")
        tts.tts_to_file(text=chunk, file_path=temp_file)

        audio_data, sr = sf.read(temp_file)
        if sample_rate is None:
            sample_rate = sr
        all_audio.append(audio_data)
        os.remove(temp_file)

    if not all_audio:
        print("Error: No audio generated")
        return None

    # Insert short silence between chunks for natural pacing
    pause_samples = int(sample_rate * PAUSE_BETWEEN_SENTENCES_MS / 1000)
    silence = np.zeros(pause_samples, dtype=all_audio[0].dtype)
    interleaved = []
    for i, audio in enumerate(all_audio):
        if i > 0:
            interleaved.append(silence)
        interleaved.append(audio)
    combined = np.concatenate(interleaved)
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    sf.write(output_file, combined, sample_rate)
    print(f"Saved to {output_file}")
    return output_file


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Polish TTS using Coqui VITS")
    parser.add_argument("text", nargs="?", help="Text to synthesize (or use --file)")
    parser.add_argument("-f", "--file", help="Read text from file")
    parser.add_argument(
        "-o", "--output",
        default="/Users/clawdia/random_audio/polish_tts_output.wav",
        help="Output WAV path",
    )
    parser.add_argument(
        "--pause", type=int, default=PAUSE_BETWEEN_SENTENCES_MS,
        help=f"Pause between sentences in ms (default: {PAUSE_BETWEEN_SENTENCES_MS})",
    )
    args = parser.parse_args()

    if args.file:
        with open(args.file) as fh:
            text = fh.read()
    elif args.text:
        text = args.text
    else:
        parser.error("Provide text as argument or use --file")

    PAUSE_BETWEEN_SENTENCES_MS = args.pause
    generate_polish_tts(text, output_file=args.output)
