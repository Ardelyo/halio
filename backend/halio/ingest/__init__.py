"""Sensor ingest: poll open, public news and fact-check feeds and measure our own coverage.

Scope is deliberate (docs/ARCHITECTURE_SENSOR.md): institutional and media sources only,
metadata only, no accounts of private citizens. Every source reports whether it is live,
stale or dead, so the dashboard can say what Halio does NOT see.
"""

# modul sensor rss publik: cuma nyimpen metadata judul + link, ga pernah simpen isi artikel penuh
# status tiap sumber dipantau terus biar di dashboard keliatan jelas mana yg hidup sm mana yg titik buta
