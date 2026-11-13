"""Indonesian text normalisation shared by claim extraction and retrieval."""

from __future__ import annotations

import re
import unicodedata

# kamus singkatan ketikan chat sehari-hari yg sering bgt muncul di pesan terusannya grup WA
SLANG = {
    "yg": "yang", "dgn": "dengan", "utk": "untuk", "krn": "karena", "tdk": "tidak",
    "gak": "tidak", "ga": "tidak", "gk": "tidak", "nggak": "tidak", "engga": "tidak",
    "sdh": "sudah", "udah": "sudah", "blm": "belum", "bs": "bisa", "bisa2": "bisa",
    "org": "orang", "skrg": "sekarang", "hr": "hari", "jg": "juga", "aja": "saja",
    "dr": "dari", "pd": "pada", "sm": "sama", "bgt": "banget", "tsb": "tersebut",
    "pak": "bapak", "bu": "ibu", "wa": "whatsapp",
    "covid19": "covid", "covid-19": "covid", "rb": "ribu", "jt": "juta",
}

# kata sambung/umum yg dibuang pas ngitung kemiripan biar ga ngaburin kata kunci inti
STOPWORDS = set(
    """
    yang dan di ke dari untuk pada dengan ini itu adalah akan juga sudah telah atau
    tidak bisa dapat ada karena oleh sebagai dalam para kita kami saya anda kamu mereka
    nya lah kah pun saja hanya agar supaya jika kalau bila maka lalu kemudian serta
    bahwa tersebut sangat lebih paling semua setiap banyak sedikit sini sana mau ingin
    hari ini besok kemarin tolong mohon info berita kabar ya yah dong deh sih kok nih tuh
    """.split()
)

_TOKEN = re.compile(r"[a-z0-9]+")


def fold(text: str) -> str:
    # ratain karakter unicode beraksen terus ubah jadi huruf kecil semua
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower()


def tokens(text: str, drop_stopwords: bool = True) -> list[str]:
    out = []
    for tok in _TOKEN.findall(fold(text)):
        tok = SLANG.get(tok, tok)
        # kempesin huruf berulang panjang khas chat: "bahayaaaa" -> "bahaya"
        tok = re.sub(r"(.)\1{2,}", r"\1", tok)
        if drop_stopwords and (tok in STOPWORDS or len(tok) < 2):
            continue
        out.append(tok)
    return out


def normalized(text: str) -> str:
    return " ".join(tokens(text))
