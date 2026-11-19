import re
import pypdf

pdf_path = r"c:\Users\User\Downloads\ad-wiki-slides\raw\papers\zhang2023-diffusionad.pdf"
md_path = r"c:\Users\User\Downloads\ad-wiki-slides\wiki\papers\zhang2023-diffusionad.md"

reader = pypdf.PdfReader(pdf_path)
p7 = reader.pages[6].extract_text()
p8 = reader.pages[7].extract_text()
p9 = reader.pages[8].extract_text()
p10 = reader.pages[9].extract_text()

with open(md_path, "r", encoding="utf-8") as f:
    md_text = f.read()

def extract_pdf_pair_table(text, header, cats):
    lines = text.split("\n")
    idx = next(i for i, l in enumerate(lines) if header in l)
    data = {}
    for l in lines[idx+1:]:
        l_strip = l.strip()
        for c in cats:
            if l_strip.startswith(c + " ") and c not in data:
                pairs = re.findall(r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)", l_strip[len(c):])
                assert len(pairs) == 8, f"PDF {header} {c}: got {len(pairs)}"
                data[c] = [(p[0], p[1]) for p in pairs]
    assert len(data) == len(cats), f"PDF {header}: missing cats {set(cats) - set(data.keys())}"
    return data

def extract_md_pair_table(md_section, cats):
    data = {}
    for line in md_section.split("\n"):
        if not line.strip().startswith("| **"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        cat = cols[0].replace("*", "").strip()
        if cat in cats:
            row_pairs = []
            for cell in cols[1:]:
                clean_cell = cell.replace("*", "").strip()
                m = re.match(r"^(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)$", clean_cell)
                assert m, f"MD cell format error: {cell}"
                row_pairs.append((m.group(1), m.group(2)))
            assert len(row_pairs) == 8
            data[cat] = row_pairs
    assert len(data) == len(cats), f"MD missing cats: {set(cats) - set(data.keys())}"
    return data

visa_cats = [
    "candle", "capsules", "cashew", "chewinggum", "fryum",
    "macaroni1", "macaroni2", "pcb1", "pcb2", "pcb3", "pcb4", "pipe fryum", "Average"
]
mvtec_cats = [
    "Carpet", "Grid", "Leather", "Tile", "Wood",
    "Bottle", "Cable", "Capsule", "Hazelnut", "Metal nut",
    "Pill", "Screw", "Toothbrush", "Transistor", "Zipper", "Average"
]

pdf_t1 = extract_pdf_pair_table(p7, "TABLE I:", visa_cats)
pdf_t2 = extract_pdf_pair_table(p8, "TABLE II:", visa_cats)
pdf_t3 = extract_pdf_pair_table(p8, "TABLE III:", mvtec_cats)
pdf_t4 = extract_pdf_pair_table(p9, "TABLE IV:", mvtec_cats)

sec_t3 = md_text.split("#### (A) MVTec AD")[1].split("#### (B) MVTec AD")[0]
sec_t4 = md_text.split("#### (B) MVTec AD")[1].split("### 5.4 VisA")[0]
sec_t1 = md_text.split("#### (A) VisA")[1].split("#### (B) VisA")[0]
sec_t2 = md_text.split("#### (B) VisA")[1].split("### 5.5")[0]

md_t1 = extract_md_pair_table(sec_t1, visa_cats)
md_t2 = extract_md_pair_table(sec_t2, visa_cats)
md_t3 = extract_md_pair_table(sec_t3, mvtec_cats)
md_t4 = extract_md_pair_table(sec_t4, mvtec_cats)

total_cells = 0
total_nums = 0
errors = 0

for name, pdf_t, md_t, cats in [
    ("Table I (VisA I/O)", pdf_t1, md_t1, visa_cats),
    ("Table II (VisA P/A)", pdf_t2, md_t2, visa_cats),
    ("Table III (MVTec I/P)", pdf_t3, md_t3, mvtec_cats),
    ("Table IV (MVTec O/A)", pdf_t4, md_t4, mvtec_cats),
]:
    t_cells = 0
    t_errs = 0
    for c in cats:
        for m_idx in range(8):
            t_cells += 1
            total_cells += 1
            total_nums += 2
            if pdf_t[c][m_idx] != md_t[c][m_idx]:
                t_errs += 1
                errors += 1
                print(f"ERROR in {name} [{c}][col {m_idx}]: PDF={pdf_t[c][m_idx]} vs MD={md_t[c][m_idx]}")
    print(f"{name}: checked {t_cells} cells ({t_cells*2} numbers), errors = {t_errs}")

print(f"=== TOTAL Table I-IV: checked {total_cells} cells ({total_nums} numbers), errors = {errors} ===")
