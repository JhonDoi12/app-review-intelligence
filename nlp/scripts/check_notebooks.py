"""Gagal jika ada notebook di folder notebooks/ yang masih menyimpan output.

Output notebook memuat cuplikan teks ulasan, jadi tidak boleh ikut ke repositori.
"""

import json
import sys
from pathlib import Path


def count_outputs(path: Path) -> int:
    nb = json.loads(path.read_text(encoding="utf-8"))
    return sum(
        len(cell.get("outputs", []))
        for cell in nb.get("cells", [])
        if cell.get("cell_type") == "code"
    )


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    notebooks = sorted((root / "notebooks").glob("*.ipynb"))
    kotor = {nb.name: n for nb in notebooks if (n := count_outputs(nb))}
    if kotor:
        for nama, n in kotor.items():
            print(f"{nama}: {n} output. Jalankan 'Clear All Outputs' lalu simpan.")
        return 1
    print(f"OK: {len(notebooks)} notebook tanpa output.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
