# src/utils_text.py
import re
import unicodedata
import pandas as pd

_ws_re = re.compile(r"\s+")

def basic_text_normalize(
    s: str,
    lowercase: bool = True,
    strip_accents: bool = True,
    remove_punct: bool = True,
    collapse_whitespace: bool = True,
) -> str:
    if not isinstance(s, str):
        s = "" if pd.isna(s) else str(s)

    if lowercase:
        s = s.lower()

    if strip_accents:
        s = unicodedata.normalize("NFKD", s)
        s = "".join([c for c in s if not unicodedata.combining(c)])

    if remove_punct:
        s = "".join(ch for ch in s if ch.isalnum() or ch.isspace())

    if collapse_whitespace:
        s = _ws_re.sub(" ", s).strip()

    return s
