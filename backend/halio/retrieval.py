"""T1 local retrieval: match a claim against known debunks.

Pure-Python TF-IDF over word n-grams + character trigrams, so it runs on a
laptop with no model download and survives typos and chat spelling. Small
corpus by design; swap for embeddings once the corpus grows.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache
from pathlib import Path

from .textnorm import fold, normalized, tokens

_NEGATION = re.compile(r"\b(tidak|tak|tanpa|bukan|gak|nggak|belum|jangan)\b[\w\s]{0,10}$")
# "biaya gratis", "uang: tidak dipungut" -- the cost word is there, but it says the opposite.
_DEFUSED = re.compile(r"^[\s:,-]{0,3}(\w+\s){0,1}(gratis|nol rupiah|rp ?0\b|tidak dipungut|tanpa (biaya|dipungut))")
# The message talks ABOUT a hoax or scam instead of making the claim: a warning or a correction.
_CORRECTION = re.compile(
    r"\b(hoaks|hoax|kabar bohong|berita bohong|disinformasi|misinformasi|tidak benar|membantah|dibantah|bantahan|"
    r"(meng|di)?klarifikasi(kan)?|(me|di)?luruskan|pelurusan|menepis|ditepis|menyangkal|disangkal|"
    r"(isu|kabar|informasi|video|pesan)( itu| tersebut)? (adalah |itu )?(tidak benar|hoaks|hoax|bohong|palsu)|"
    r"tidak ada bukti|tidak terbukti|belum terbukti|modus penipuan|adalah (penipu|penipuan|calo)|itu (penipu|penipuan)|waspada (calo|penipu|penipuan|modus)|"
    # Warnings people forward ("hati-hati penipuan bansos memakai video palsu", "jangan percaya calo", "polisi menangkap calo").
    r"(hati-hati|hati hati|awas|waspadai) (terhadap )?(penipuan|penipu|calo|modus|hoaks|hoax|video palsu|akun palsu|tautan palsu)|"
    r"(memakai|menggunakan|pakai|berupa) (video|foto|akun|suara) (palsu|rekayasa|deepfake)|"
    r"jangan (mudah )?(percaya|tertipu|terkecoh)( (pada|kepada|dengan|sama))? (calo|penipu|oknum|tautan|link|pesan berantai)|"
    r"(menangkap|meringkus|membekuk|memburu|menindak) (oknum |para |seorang )?(calo|penipu|pelaku penipuan|komplotan penipu))\b")
_NOT_A_CORRECTION = re.compile(r"\b(bukan|tidak|gak|nggak|bkn) (hoaks|hoax)\b")


def is_correction(text: str) -> bool:
    """True if the message warns about or corrects a hoax rather than spreading it."""
    low = fold(text)
    return bool(_CORRECTION.search(low)) and not _NOT_A_CORRECTION.search(low)


@dataclass
class Debunk:
    id: str
    kategori: str
    klaim: str
    varian: list[str]
    fakta: str
    sederhana: str
    sumber: list[dict]
    syarat: list[str] = field(default_factory=list)
    jenis: str = "bantahan"
    kutipan_sumber: str = ""
    valid_from: str | None = None
    valid_until: str | None = None
    wilayah: str = ""

    def __post_init__(self) -> None:
        if self.jenis not in {"bantahan", "verifikasi_positif"}:
            raise ValueError(f"Jenis bukti tidak dikenal: {self.jenis}")
        for value in (self.valid_from, self.valid_until):
            if value:
                date.fromisoformat(value)
        if self.valid_from and self.valid_until and self.valid_from > self.valid_until:
            raise ValueError(f"Masa berlaku terbalik pada bukti {self.id}")

    @property
    def is_positive(self) -> bool:
        return self.jenis == "verifikasi_positif"

    def is_current(self, today: date) -> bool:
        return (
            bool(self.valid_from)
            and date.fromisoformat(self.valid_from) <= today
            and (not self.valid_until or today <= date.fromisoformat(self.valid_until))
        )

    @property
    def texts(self) -> list[str]:
        return [self.klaim, *self.varian]

    def core_present(self, text: str) -> bool:
        """True if every 'syarat' group appears in the text, not negated and not defused."""
        low = fold(text)
        for group in self.syarat:
            hits = [
                m for m in re.finditer(group, low)
                if not _NEGATION.search(low[max(0, m.start() - 16) : m.start()]) and not _DEFUSED.match(low[m.end() : m.end() + 24])
            ]
            if not hits:
                return False
        return True


@dataclass
class Match:
    debunk: Debunk
    score: float
    matched_text: str


def _word_feats(text: str) -> Counter:
    toks = tokens(text)
    return Counter(toks + [f"{a}_{b}" for a, b in zip(toks, toks[1:])])


def _char_feats(text: str) -> Counter:
    s = f" {normalized(text)} "
    return Counter(s[i : i + 3] for i in range(len(s) - 2))


class _TfIdf:
    def __init__(self, docs: list[Counter]):
        n = len(docs)
        df = Counter(f for d in docs for f in d)
        self.idf = {f: math.log((1 + n) / (1 + c)) + 1 for f, c in df.items()}
        self.vecs = [self._vec(d) for d in docs]

    def _vec(self, feats: Counter) -> dict[str, float]:
        v = {f: (1 + math.log(c)) * self.idf.get(f, 0.0) for f, c in feats.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {f: x / norm for f, x in v.items()}

    def scores(self, feats: Counter) -> list[float]:
        q = self._vec(feats)
        return [sum(w * d.get(f, 0.0) for f, w in q.items()) for d in self.vecs]


class Index:
    def __init__(self, debunks: list[Debunk]):
        self.debunks = debunks
        self.rows = [(d, t) for d in debunks for t in d.texts]
        self.word = _TfIdf([_word_feats(t) for _, t in self.rows])
        self.char = _TfIdf([_char_feats(t) for _, t in self.rows])

    def search(self, query: str, k: int = 3) -> list[Match]:
        ws = self.word.scores(_word_feats(query))
        cs = self.char.scores(_char_feats(query))
        best: dict[str, Match] = {}
        for (deb, text), w, c in zip(self.rows, ws, cs):
            score = 0.5 * w + 0.5 * c
            if deb.id not in best or score > best[deb.id].score:
                best[deb.id] = Match(deb, round(score, 3), text)
        return sorted(best.values(), key=lambda m: m.score, reverse=True)[:k]

    def get(self, debunk_id: str) -> Debunk | None:
        return next((d for d in self.debunks if d.id == debunk_id), None)


def load_debunks(path: Path) -> list[Debunk]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Debunk(**{k: d[k] for k in Debunk.__dataclass_fields__ if k in d}) for d in raw["debunks"]]


@lru_cache(maxsize=4)
def get_index(path: Path) -> Index:
    return Index(load_debunks(path))
