"""Polish text normalizer — pure Python, zero dependencies."""

from .polish_text_normalizer import normalize_polish_text as normalize
from .polish_text_normalizer import normalize_polish_text

__all__ = ["normalize", "normalize_polish_text"]
