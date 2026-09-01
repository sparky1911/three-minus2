import ahocorasick
from normalize import normalize, deleet

HARD_BLOCK = ["slur1", "slur2"]          # instant REJECT
SOFT_FLAG  = ["fuck", "shit", "bitch"]   # signal only
ALLOWLIST  = ["scunthorpe", "assassin", "analysis", "cockburn", "class"]


def _build(terms):
    a = ahocorasick.Automaton()
    for t in terms:
        a.add_word(t, t)
    a.make_automaton()
    return a


_hard = _build(HARD_BLOCK)
_soft = _build(SOFT_FLAG)
_allow = _build(ALLOWLIST)


def _spans(automaton, text):
    return [(end - len(word) + 1, end, word) for end, word in automaton.iter(text)]


def _hits(automaton, text):
    allowed = _spans(_allow, text)
    out = []
    for start, end, word in _spans(automaton, text):
        # skip if this match sits inside an allowlisted word
        if any(a <= start and end <= b for a, b, _ in allowed):
            continue
        out.append(word)
    return out


def check(text: str):
    """Returns ('BLOCK'|'FLAG'|'CLEAN', matched_terms)."""
    norm = normalize(text)
    variants = {norm, deleet(norm)}

    for v in variants:
        if hits := _hits(_hard, v):
            return "BLOCK", hits

    flags = set()
    for v in variants:
        flags.update(_hits(_soft, v))

    return ("FLAG", sorted(flags)) if flags else ("CLEAN", [])