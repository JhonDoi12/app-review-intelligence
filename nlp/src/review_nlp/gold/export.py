from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.datavalidation import DataValidation

HEADER = ["id", "teks", "label", "tipe", "ragu", "catatan"]
LABELS = ["negatif", "netral", "positif"]
TIPE = ["biasa", "saran", "pertanyaan", "campuran", "spam", "tidak_jelas"]


def tulis_xlsx(path: Path, sampel: pd.DataFrame) -> None:
    """Tulis lembar pelabelan: id dan teks terisi, sisanya untuk diisi pelabel."""
    wb = Workbook()
    ws = wb.active
    ws.title = "label"
    ws.append(HEADER)
    for _, baris in sampel.iterrows():
        teks = ILLEGAL_CHARACTERS_RE.sub("", str(baris["text_raw"]))
        ws.append([int(baris["id"]), teks, None, "biasa", None, None])

    akhir = len(sampel) + 1
    for kolom, lebar in zip("ABCDEF", [6, 90, 12, 14, 6, 35], strict=True):
        ws.column_dimensions[kolom].width = lebar
    for sel in ws[1]:
        sel.font = Font(bold=True)
    for baris in ws.iter_rows(min_row=2, max_row=akhir):
        for sel in baris:
            sel.alignment = Alignment(wrap_text=sel.column == 2, vertical="top")
    ws.freeze_panes = "A2"

    for kolom, pilihan in {"C": LABELS, "D": TIPE, "E": ["y"]}.items():
        dv = DataValidation(type="list", formula1='"' + ",".join(pilihan) + '"', allow_blank=True)
        dv.error = "Pilih salah satu nilai dari daftar"
        ws.add_data_validation(dv)
        dv.add(f"{kolom}2:{kolom}{akhir}")
    wb.save(path)
