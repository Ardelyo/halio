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
    "pak": "bapak", "bu": "ibu", "wa": "whatsapp", "japri": "whatsapp", "chat": "whatsapp",
    "lwt": "lewat", "lewat2": "lewat", "klo": "kalau", "kalo": "kalau", "dlm": "dalam", "tmn": "teman", "trf": "transfer", "tf": "transfer",
    "covid19": "covid", "covid-19": "covid", "rb": "ribu", "jt": "juta",
}

# frasa/slang domain Indonesia -> satu token kanonik (huruf saja, biar lolos pemecah token). Dipakai korpus DAN kueri,
# jadi parafrase berat ("kenalan perwira", "ordal", "uang pelicin") nyambung ke varian bantahan yg bunyinya beda.
# Batas kata pake lookaround [a-z0-9] (bukan ) supaya hasilnya identik di Python dan JS. Urutan penting.
_B, _E = r"(?<![a-z0-9])", r"(?![a-z0-9])"
PHRASES: list[tuple[str, str]] = [
    (_B + r"(?:orang\s+dalam|ordal|kenalan\s+(?:di\s+)?(?:perwira|kodam|korem|kodim|tni|jenderal|petinggi|pejabat|panitia)|kenalan\s+orang\s+dalam|"
     r"relasi\s+(?:di\s+)?(?:kodam|tni|panitia)|jalur\s+(?:belakang|dalam|khusus|titipan)|titipan)" + _E, "caloordal"),
    (_B + r"(?:(?:dijamin|jamin|pasti|100\s*%|seratus\s+persen)\s+(?:lulus|masuk|diterima|lolos)|lulus\s+(?:pasti|dijamin|100\s*%))" + _E, "jaminlulus"),
    (_B + r"(?:uang\s+pelicin|pelicin|uang\s+rokok|uang\s+lelah|uang\s+muka|uang\s+jasa|uang\s+administrasi\s+khusus|mahar|setoran)" + _E, "biayailegal"),
]
_PHRASES = [(re.compile(p), repl) for p, repl in PHRASES]

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


def canon(low: str) -> str:
    """Tambahkan token kanonik di samping frasa domain (frasa asli tetap ada) pada teks yang SUDAH di-fold."""
    for rx, repl in _PHRASES:
        low = rx.sub(lambda m: f" {m.group(0)} {repl} ", low)
    return low


def tokens(text: str, drop_stopwords: bool = True) -> list[str]:
    out = []
    for tok in _TOKEN.findall(canon(fold(text))):
        tok = SLANG.get(tok, tok)
        # kempesin huruf berulang panjang khas chat: "bahayaaaa" -> "bahaya"
        tok = re.sub(r"(.)\1{2,}", r"\1", tok)
        if drop_stopwords and (tok in STOPWORDS or len(tok) < 2):
            continue
        out.append(tok)
    return out


def normalized(text: str) -> str:
    return " ".join(tokens(text))
