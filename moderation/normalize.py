import re
import unicodedata

ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"))

HOMOGLYPHS = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x", "у": "y",
    "ѕ": "s", "і": "i", "ј": "j", "ν": "v", "υ": "u", "ο": "o", "α": "a",
})

def normalize(text: str) -> str:
    t = unicodedata.normalize("NFKC", text)
    t = t.translate(ZERO_WIDTH)
    t = t.translate(HOMOGLYPHS)
    t = t.casefold()
    t = re.sub(r"(.)\1{2,}", r"\1\1", t)     # fuuuuck -> fuuck
    t = re.sub(r"\s+", " ", t).strip()
    return t

def deleet(text: str) -> str:
    return text.translate(str.maketrans({
        "4": "a", "3": "e", "1": "i", "0": "o", "5": "s", "7": "t", "$": "s", "@": "a",
    }))