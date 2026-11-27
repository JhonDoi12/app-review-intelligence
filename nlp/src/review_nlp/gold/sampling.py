import numpy as np
import pandas as pd

QUOTAS = {1: 80, 2: 70, 3: 100, 4: 80, 5: 120}


def text_key(text: str) -> str:
    return " ".join(text.lower().split())


def dedupe_texts(df: pd.DataFrame) -> pd.DataFrame:
    """Buang teks yang sama persis (setelah huruf kecil dan spasi dirapikan)."""
    out = df.sort_values("external_id").copy()
    out["_key"] = out["text_raw"].map(text_key)
    return out.drop_duplicates("_key").drop(columns="_key")


def allocate(counts: pd.Series, quota: int) -> pd.Series:
    """Bagi kuota ke tiap kelompok secara proporsional (sisa ke pecahan terbesar)."""
    total = int(counts.sum())
    if quota >= total:
        return counts.astype(int)
    raw = counts * quota / total
    alloc = np.floor(raw).astype(int)
    sisa = quota - int(alloc.sum())
    urutan = (raw - alloc).sort_values(ascending=False, kind="stable").index
    for idx in urutan[:sisa]:
        alloc.loc[idx] += 1
    return alloc


def stratified_sample(df: pd.DataFrame, quotas: dict[int, int], seed: int = 42) -> pd.DataFrame:
    """Ambil sampel per bintang sesuai kuota, tersebar proporsional antar minggu.

    Menambahkan kolom peluang_terpilih dan bobot (kebalikan peluang) per bintang.
    """
    rng = np.random.default_rng(seed)
    hasil = []
    for rating, quota in sorted(quotas.items()):
        grup = df[df["rating"] == rating]
        if len(grup) < quota:
            raise ValueError(f"bintang {rating}: tersedia {len(grup)}, kuota {quota}")
        alokasi = allocate(grup.groupby("week_index").size(), quota)
        dipilih: list[str] = []
        for minggu, k in alokasi.items():
            kandidat = np.sort(grup.loc[grup["week_index"] == minggu, "external_id"].to_numpy())
            dipilih.extend(rng.choice(kandidat, size=int(k), replace=False).tolist())
        bagian = grup[grup["external_id"].isin(dipilih)].copy()
        bagian["peluang_terpilih"] = len(bagian) / len(grup)
        bagian["bobot"] = len(grup) / len(bagian)
        hasil.append(bagian)
    return pd.concat(hasil).sample(frac=1, random_state=seed).reset_index(drop=True)
