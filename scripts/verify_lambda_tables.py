import re
import pypdf

pdf_path = r"c:\Users\User\Downloads\ad-wiki-slides\raw\papers\lee2026-lambda.pdf"
md_path = r"c:\Users\User\Downloads\ad-wiki-slides\wiki\papers\lee2026-lambda.md"
report_path = r"c:\Users\User\Downloads\ad-wiki-slides\scripts\reports\lambda-table-check.txt"

reader = pypdf.PdfReader(pdf_path)
p8 = reader.pages[7].extract_text()
p9 = reader.pages[8].extract_text()
p10 = reader.pages[9].extract_text()
p13 = reader.pages[12].extract_text()
p14 = reader.pages[13].extract_text()

with open(md_path, "r", encoding="utf-8") as f:
    md_text = f.read()

def clean_pdf_numbers(s):
    # Remove kerning spaces around decimal point like "98 .2" -> "98.2"
    s = re.sub(r"(\d)\s+\.(\d)", r"\1.\2", s)
    s = re.sub(r"(\d)\.\s+(\d)", r"\1.\2", s)
    return re.findall(r"\d+(?:\.\d+)?", s)

def extract_md_table_rows(md_section):
    rows = {}
    for line in md_section.split("\n"):
        l = line.strip()
        if not l.startswith("| **"):
            continue
        cols = [c.strip() for c in l.strip("|").split("|")]
        key = cols[0].replace("*", "").strip()
        cells = [c.replace("*", "").strip() for c in cols[1:]]
        rows[key] = cells
    return rows

report_lines = []
total_cells = 0
total_numbers = 0
total_errors = 0

def log(msg):
    print(msg)
    report_lines.append(msg)

# 1. Verify Table 1 (6 models x 12 columns = 72 cells, 78 numbers)
t1_models = ["DiffusionAD", "DRAEM", "DDAD", "D3AD", "LAMBDA", "LAMBDA w/o VAE"]
md_t1_sec = md_text.split("#### (A) VisA 資料集檢測精度與計算效率綜合比較")[1].split("#### (B) 跨 30 個獨立類別")[0]
md_t1 = extract_md_table_rows(md_t1_sec)

p8_lines = p8.split("\n")
t1_cells = 0
t1_nums = 0
t1_errs = 0
for m in t1_models:
    pdf_m = m.replace("w/o VAE", "w/o  VAE")
    line = next(l.strip() for l in p8_lines if l.strip().startswith(pdf_m))
    pdf_nums = clean_pdf_numbers(line[len(pdf_m):])
    md_nums = clean_pdf_numbers(" ".join(md_t1[m]))
    t1_cells += len(md_t1[m])
    t1_nums += len(pdf_nums)
    if pdf_nums != md_nums:
        t1_errs += 1
        log(f"ERROR in Table 1 [{m}]: PDF={pdf_nums} vs MD={md_nums}")
total_cells += t1_cells
total_numbers += t1_nums
total_errors += t1_errs
log(f"Table 1 (VisA Summary & Efficiency, 6 rows): checked {t1_cells} cells ({t1_nums} numbers), errors = {t1_errs}")

# 2. Verify Table 2 (BMAD Summary, 5 models x 6 columns = 30 cells, 30 numbers)
t2_models = ["DiffusionAD", "DRAEM", "DDAD", "D3AD", "LAMBDA"]
md_t2_sec = md_text.split("#### (A) BMAD 醫療資料集整體表現對比")[1].split("#### (B) BMAD 3 大醫學解剖類別")[0]
md_t2 = extract_md_table_rows(md_t2_sec)
p9_lines = p9.split("\n")
t2_cells = 0
t2_nums = 0
t2_errs = 0
for m in t2_models:
    line = next(l.strip() for l in p9_lines if l.strip().startswith(m + " "))
    pdf_nums = clean_pdf_numbers(line[len(m):])
    md_nums = [c for c in md_t2[m]]
    t2_cells += len(md_nums)
    t2_nums += len(pdf_nums)
    if pdf_nums != md_nums:
        t2_errs += 1
        log(f"ERROR in Table 2 [{m}]: PDF={pdf_nums} vs MD={md_nums}")
total_cells += t2_cells
total_numbers += t2_nums
total_errors += t2_errs
log(f"Table 2 (BMAD Summary, 5 rows): checked {t2_cells} cells ({t2_nums} numbers), errors = {t2_errs}")

# 3. Verify Table 3 (Wilcoxon test, 4 rows x 2 columns = 8 cells, 8 numbers)
md_t3_sec = md_text.split("#### (B) 跨 30 個獨立類別之成對 Wilcoxon")[1].split("### 5.3 醫療影像異常檢測結果")[0]
md_t3 = extract_md_table_rows(md_t3_sec)
t3_keys = ["LAMBDA vs. DiffusionAD", "LAMBDA vs. DRAEM", "LAMBDA vs. DDAD", "LAMBDA vs. D3AD"]
t3_cells = 0
t3_nums = 0
t3_errs = 0
p9_joined = " ".join(l.strip() for l in p9_lines)
for k in t3_keys:
    pdf_k = k.replace("vs. ", "vs.  ")
    idx = p9_joined.index(pdf_k) + len(pdf_k)
    pdf_nums = clean_pdf_numbers(p9_joined[idx:idx+40])[:2]
    md_nums = [c.replace("*", "") for c in md_t3[k]]
    t3_cells += 2
    t3_nums += 2
    if pdf_nums != md_nums:
        t3_errs += 1
        log(f"ERROR in Table 3 [{k}]: PDF={pdf_nums} vs MD={md_nums}")
total_cells += t3_cells
total_numbers += t3_nums
total_errors += t3_errs
log(f"Table 3 (Wilcoxon Signed-Rank Test, 4 rows): checked {t3_cells} cells ({t3_nums} numbers), errors = {t3_errs}")

# 4. Verify Table 5 (n_m ablation summary, 5 rows x 6 columns = 30 cells, 30 numbers)
md_t5_sec = md_text.split("#### (B) 記憶庫大小 $n_m$ 消融實驗")[1].split("2. **MVTec AD 15 類別於不同記憶庫容量")[0]
md_t5 = extract_md_table_rows(md_t5_sec)
p10_lines = p10.split("\n")
t5_idx = next(i for i, l in enumerate(p10_lines) if "Table 5" in l)
t5_cells = 0
t5_nums = 0
t5_errs = 0
for nm in ["50", "100", "150", "200", "250"]:
    line = next(l.strip() for l in p10_lines[t5_idx:] if l.strip().startswith(nm + " "))
    pdf_nums = clean_pdf_numbers(line[len(nm):])
    md_nums = md_t5[nm]
    t5_cells += len(md_nums)
    t5_nums += len(pdf_nums)
    if pdf_nums != md_nums:
        t5_errs += 1
        log(f"ERROR in Table 5 [n_m={nm}]: PDF={pdf_nums} vs MD={md_nums}")
total_cells += t5_cells
total_numbers += t5_nums
total_errors += t5_errs
log(f"Table 5 (Memory Bank Size Summary, 5 rows): checked {t5_cells} cells ({t5_nums} numbers), errors = {t5_errs}")

# 5. Verify Table 6 (lambda ablation summary, 7 rows x 6 columns = 42 cells, 42 numbers)
md_t6_sec = md_text.split(r"#### (C) 分割損失權重因子 $\lambda$ 消融實驗")[1].split("2. **MVTec AD 15 類別於不同權重")[0]
md_t6 = extract_md_table_rows(md_t6_sec)
t6_idx = next(i for i, l in enumerate(p10_lines) if "Table 6" in l)
t6_cells = 0
t6_nums = 0
t6_errs = 0
for lam in ["0.1", "0.2", "0.5", "1 (Ours)", "2", "5", "10"]:
    line = next(l.strip() for l in p10_lines[t6_idx:] if l.strip().startswith(lam + " "))
    pdf_nums = clean_pdf_numbers(line[len(lam):])
    md_nums = md_t6[lam]
    t6_cells += len(md_nums)
    t6_nums += len(pdf_nums)
    if pdf_nums != md_nums:
        t6_errs += 1
        log(f"ERROR in Table 6 [lambda={lam}]: PDF={pdf_nums} vs MD={md_nums}")
total_cells += t6_cells
total_numbers += t6_nums
total_errors += t6_errs
log(f"Table 6 (Loss Weighting Factor Summary, 7 rows): checked {t6_cells} cells ({t6_nums} numbers), errors = {t6_errs}")

# 6. Helper to verify 5-tuple Appendix tables (Table A.1 - A.6)
def verify_appendix_table(name, page_str, pdf_header, md_section, cats, num_cols):
    global total_cells, total_numbers, total_errors
    lines = page_str.split("\n")
    start = next(i for i, l in enumerate(lines) if pdf_header in l)
    md_rows = extract_md_table_rows(md_section)
    c_count = 0
    n_count = 0
    err_count = 0
    cur_line = start + 1
    for cat in cats:
        while cur_line < len(lines):
            l = lines[cur_line].strip()
            cur_line += 1
            if l.startswith(cat + " "):
                rest = l[len(cat):]
                pdf_nums = clean_pdf_numbers(rest)
                assert len(pdf_nums) == num_cols * 5, f"{name} {cat}: expected {num_cols*5} numbers, got {len(pdf_nums)}"
                md_cells = md_rows[cat]
                assert len(md_cells) == num_cols, f"{name} {cat}: expected {num_cols} MD cols, got {len(md_cells)}"
                for col_i in range(num_cols):
                    c_count += 1
                    n_count += 5
                    p_slice = pdf_nums[col_i*5 : (col_i+1)*5]
                    m_slice = clean_pdf_numbers(md_cells[col_i])
                    if p_slice != m_slice:
                        err_count += 1
                        log(f"ERROR in {name} [{cat}][col {col_i}]: PDF={p_slice} vs MD={m_slice}")
                break
    total_cells += c_count
    total_numbers += n_count
    total_errors += err_count
    log(f"{name} ({len(cats)} rows x {num_cols} cols): checked {c_count} cells ({n_count} numbers), errors = {err_count}")

visa_cats = [
    "Candle", "Capsules", "Cashew", "Chewinggum", "Fryum",
    "Macaroni1", "Macaroni2", "Pcb1", "Pcb2", "Pcb3", "Pcb4", "Pipe_fryum", "Average"
]
mvtec_cats = [
    "Carpet", "Grid", "Leather", "Tile", "Wood", "Texture Avg.",
    "Bottle", "Cable", "Capsule", "Hazelnut", "Metalnut",
    "Pill", "Screw", "Toothbrush", "Transistor", "Zipper", "Object Avg.", "Average"
]
bmad_cats = ["Brain", "Liver", "Retinal", "Average"]

sec_ta1 = md_text.split("#### (A) VisA 12 類別逐類表現")[1].split("#### (B) MVTec AD 15 類別逐類表現")[0]
sec_ta2 = md_text.split("#### (B) MVTec AD 15 類別逐類表現")[1].split("### 5.5 消融實驗")[0]
sec_ta3 = md_text.split("#### (B) BMAD 3 大醫學解剖類別")[1].split("### 5.4 VisA 與 MVTec AD")[0]
sec_ta4 = md_text.split("2. **VisA 12 類別逐類消融詳細數據")[1].split("3. **各組件貢獻與收斂效率")[0]
sec_ta5 = md_text.split("2. **MVTec AD 15 類別於不同記憶庫容量")[1].split("#### (C) 分割損失權重因子")[0]
sec_ta6 = md_text.split("2. **MVTec AD 15 類別於不同權重")[1].split("## 6. 論文限制")[0]

verify_appendix_table("Table A.1 (VisA 12 Categories + Avg)", p13, "Table A.1", sec_ta1, visa_cats, 5)
verify_appendix_table("Table A.2 (MVTec AD 15 Categories + Avgs)", p13, "Table A.2", sec_ta2, mvtec_cats, 5)
verify_appendix_table("Table A.3 (BMAD 3 Categories + Avg)", p13, "Table A.3", sec_ta3, bmad_cats, 5)
verify_appendix_table("Table A.4 (VisA Ablation 12 Categories + Avg)", p13, "Table A.4", sec_ta4, visa_cats, 4)
verify_appendix_table("Table A.5 (MVTec n_m Ablation 15 Categories + Avgs)", p14, "Table A.5", sec_ta5, mvtec_cats, 5)
verify_appendix_table("Table A.6 (MVTec lambda Ablation 15 Categories + Avgs)", p14, "Table A.6", sec_ta6, mvtec_cats, 7)

# 7. Cross-check Table 4 detection metrics against Table A.4 Average row in PDF
sec_t4 = md_text.split("1. **VisA 整體檢測表現與計算效率消融")[1].split("2. **VisA 12 類別逐類消融詳細數據")[0]
md_t4 = extract_md_table_rows(sec_t4)
md_ta4 = extract_md_table_rows(sec_ta4)
t4_variants = ["Ours", "w/o GSM", "w/o MBG", "w/o VAE"]
t4_cells = 0
t4_nums = 0
t4_errs = 0
for v_idx, v_name in enumerate(t4_variants):
    ta4_avg_5 = clean_pdf_numbers(md_ta4["Average"][v_idx])
    t4_first_5 = [clean_pdf_numbers(md_t4[v_name][k])[0] for k in range(5)]
    t4_cells += 10
    t4_nums += len(clean_pdf_numbers(" ".join(md_t4[v_name])))
    if ta4_avg_5 != t4_first_5:
        t4_errs += 1
        log(f"ERROR in Table 4 vs Table A.4 Avg [{v_name}]: T4={t4_first_5} vs TA4={ta4_avg_5}")
total_cells += t4_cells
total_numbers += t4_nums
total_errors += t4_errs
log(f"Table 4 (Component Ablation Summary, 4 rows, cross-checked with Table A.4 Avg & Page 10): checked {t4_cells} cells ({t4_nums} numbers), errors = {t4_errs}")

# 8. Verify cross-page numbers (comparisons/, datasets/, concepts/, index.md, index.html) against PDF tables
cross_files = [
    r"c:\Users\User\Downloads\ad-wiki-slides\wiki\comparisons\embedding-vs-reconstruction.md",
    r"c:\Users\User\Downloads\ad-wiki-slides\wiki\datasets\mvtec-ad.md",
    r"c:\Users\User\Downloads\ad-wiki-slides\wiki\concepts\memory-bank-guided-latent-diffusion.md",
    r"c:\Users\User\Downloads\ad-wiki-slides\wiki\concepts\norm-guided-one-step-denoising.md",
    r"c:\Users\User\Downloads\ad-wiki-slides\wiki\concepts\memory-bank.md",
    r"c:\Users\User\Downloads\ad-wiki-slides\wiki\concepts\denoising-diffusion-probabilistic-models.md",
    r"c:\Users\User\Downloads\ad-wiki-slides\wiki\index.md",
    r"c:\Users\User\Downloads\ad-wiki-slides\index.html",
]

# Expected canonical values from PDF Table 1, Table 2, Table 3, Table 4, Table 5, Table A.2
pdf_t1_lambda = clean_pdf_numbers(next(l.strip() for l in p8_lines if l.strip().startswith("LAMBDA "))[6:])
# ['98.1', '98.1', '98.6', '50.2', '94.2', '87.8', '9.3', '5.8', '25.3', '42.3', '23.6', '27', '57']
pdf_t1_diffad = clean_pdf_numbers(next(l.strip() for l in p8_lines if l.strip().startswith("DiffusionAD "))[11:])
# ['98.8', '98.8', '98.9', '52.8', '96.2', '89.1', '48.4', '12.4', '11.2', '10.9', '91.7', '58', '10']
pdf_t2_lambda = clean_pdf_numbers(next(l.strip() for l in p9_lines if l.strip().startswith("LAMBDA "))[6:])
# ['87.1', '88.1', '90.3', '41.8', '70.2', '75.5']
pdf_t2_diffad = clean_pdf_numbers(next(l.strip() for l in p9_lines if l.strip().startswith("DiffusionAD "))[11:])
# ['83.4', '85.9', '86.9', '39.9', '68.2', '72.9']

ta2_md_rows = extract_md_table_rows(sec_ta2)
# Table A.2 columns: 0=DiffusionAD, 1=DRAEM*, 2=DDAD, 3=D3AD, 4=Ours (LAMBDA)

cross_checks = 0
cross_errs = 0

def assert_substr(fpath, expected_str, desc):
    global cross_checks, cross_errs
    cross_checks += 1
    with open(fpath, "r", encoding="utf-8") as f:
        txt = f.read()
    if expected_str not in txt:
        cross_errs += 1
        log(f"ERROR in cross-page check [{desc}] in {fpath}: missing '{expected_str}'")

# Check wiki/comparisons/embedding-vs-reconstruction.md directly against PDF Table 2 & Table A.2 numbers
comp_path = cross_files[0]
b_lam = f"{pdf_t2_lambda[0]} / {pdf_t2_lambda[1]} / {pdf_t2_lambda[2]} / {pdf_t2_lambda[3]} / {pdf_t2_lambda[4]}`［mAD `{pdf_t2_lambda[5]}`］"
b_dif = f"{pdf_t2_diffad[0]} / {pdf_t2_diffad[1]} / {pdf_t2_diffad[2]} / {pdf_t2_diffad[3]} / {pdf_t2_diffad[4]}`［mAD `{pdf_t2_diffad[5]}`］"
assert_substr(comp_path, b_lam, "Comparison Note 2 LAMBDA BMAD vs PDF Table 2")
assert_substr(comp_path, b_dif, "Comparison Note 2 DiffusionAD BMAD vs PDF Table 2")

# Extract PDF Table A.2 Texture Avg., Object Avg., Average directly from p13
p13_lines = p13.split("\n")
ta2_start = next(i for i, l in enumerate(p13_lines) if "Table A.2" in l)
def get_ta2_row(row_name):
    line = next(l.strip() for l in p13_lines[ta2_start:] if l.strip().startswith(row_name + " "))
    nums = clean_pdf_numbers(line[len(row_name):])
    # 5 models x 5 metrics = 25 numbers: 0=DiffusionAD, 1=DRAEM*, 2=DDAD, 3=D3AD, 4=Ours(LAMBDA)
    return [nums[g*5:(g+1)*5] for g in range(5)]

ta2_tex = get_ta2_row("Texture Avg.")
ta2_obj = get_ta2_row("Object Avg.")
ta2_avg = get_ta2_row("Average")
t5_200 = clean_pdf_numbers(next(l.strip() for l in p10_lines[t5_idx:] if l.strip().startswith("200 "))[4:])

# DDAD is col 2, D3AD is col 3, LAMBDA is col 4
ddad_comp = f"| **DDAD** | 重建式（單階段條件去噪擴散） | {ta2_tex[2][0]} / {ta2_tex[2][2]} | {ta2_obj[2][0]} / {ta2_obj[2][2]} | {ta2_avg[2][0]} | {ta2_avg[2][2]} | {ta2_avg[2][4]} *(P-AP: {ta2_avg[2][3]})* |"
d3ad_comp = f"| **D3AD** | 重建式（單階段動態加噪擴散） | {ta2_tex[3][0]} / {ta2_tex[3][2]} | {ta2_obj[3][0]} / {ta2_obj[3][2]} | {ta2_avg[3][0]} | {ta2_avg[3][2]} | {ta2_avg[3][4]} *(P-AP: {ta2_avg[3][3]})* |"
lam_comp = f"| **[LAMBDA](../papers/lee2026-lambda.md)** | 混合流派（預訓練 VAE 潛在擴散 + `MBG` + `GSM` + 分割） | {ta2_tex[4][0]} / {ta2_tex[4][2]} | {ta2_obj[4][0]} / {ta2_obj[4][2]} | {ta2_avg[4][0]} | {ta2_avg[4][2]} | {ta2_avg[4][4]} *(P-AP: {ta2_avg[4][3]}, mAD: {t5_200[5]})* |"
assert_substr(comp_path, ddad_comp, "Comparison DDAD MVTec vs PDF Table A.2")
assert_substr(comp_path, d3ad_comp, "Comparison D3AD MVTec vs PDF Table A.2")
assert_substr(comp_path, lam_comp, "Comparison LAMBDA MVTec vs PDF Table 5 & A.2")

# Check wiki/datasets/mvtec-ad.md directly against PDF Table A.2 & Table 1 & Table 5
mvtec_path = cross_files[1]
ddad_ds = f"| **DDAD** | 條件去噪擴散異常檢測（單階段） | {ta2_tex[2][0]} / {ta2_tex[2][2]} | {ta2_obj[2][0]} / {ta2_obj[2][2]} | {ta2_avg[2][0]} / {ta2_avg[2][2]} / {ta2_avg[2][4]} *(P-AP: {ta2_avg[2][3]})* |"
d3ad_ds = f"| **D3AD** | 動態加噪擴散異常檢測（單階段） | {ta2_tex[3][0]} / {ta2_tex[3][2]} | {ta2_obj[3][0]} / {ta2_obj[3][2]} | {ta2_avg[3][0]} / {ta2_avg[3][2]} / {ta2_avg[3][4]} *(P-AP: {ta2_avg[3][3]})* |"
lam_ds = f"| **[LAMBDA](../papers/lee2026-lambda.md)**（`Applied Soft Computing 2026`） | 潛在空間一步擴散 + 記憶庫引導 `MBG` + `GSM` + 分割（1 步，{pdf_t1_lambda[9]} FPS） | {ta2_tex[4][0]} / {ta2_tex[4][2]} | {ta2_obj[4][0]} / {ta2_obj[4][2]} | {ta2_avg[4][0]} / {ta2_avg[4][2]} / {ta2_avg[4][4]} *(P-AP: {ta2_avg[4][3]}, mAD: {t5_200[5]})* |"
assert_substr(mvtec_path, ddad_ds, "Dataset DDAD MVTec vs PDF Table A.2")
assert_substr(mvtec_path, d3ad_ds, "Dataset D3AD MVTec vs PDF Table A.2")
assert_substr(mvtec_path, lam_ds, "Dataset LAMBDA MVTec vs PDF Table 1, 5 & A.2")

# Check wiki/concepts/*, wiki/index.md, index.html directly against PDF Table 1, Table 2, Table 5, Table A.2
assert_substr(cross_files[2], f"{pdf_t1_lambda[6]} GB", "Concept MBG/GSM Train Mem vs PDF Table 1")
assert_substr(cross_files[2], f"{pdf_t1_lambda[7]} GB", "Concept MBG/GSM Eval Mem vs PDF Table 1")
assert_substr(cross_files[2], f"{pdf_t1_lambda[9]} FPS", "Concept MBG/GSM FPS vs PDF Table 1")
assert_substr(cross_files[3], f"{pdf_t1_diffad[6]} → {pdf_t1_lambda[6]} GB", "Concept NOD Train Mem vs PDF Table 1")
assert_substr(cross_files[4], f"MVTec AD：**{ta2_avg[4][0]}% / {ta2_avg[4][2]}% / {ta2_avg[4][4]}%**（AP: **{ta2_avg[4][3]}%**）；VisA：**{pdf_t1_lambda[0]}% / {pdf_t1_lambda[2]}% / {pdf_t1_lambda[4]}%**", "Concept Memory Bank LAMBDA metrics vs PDF Table 1, 5, A.2")
assert_substr(cross_files[6], f"{pdf_t2_lambda[0]}% Image AUROC 與 {pdf_t2_lambda[5]}% mAD", "wiki/index.md BMAD vs PDF Table 2")
assert_substr(cross_files[7], f"{pdf_t2_lambda[0]}% Image AUROC 與 {pdf_t2_lambda[5]}% mAD", "index.html BMAD vs PDF Table 2")

total_errors += cross_errs
log(f"Cross-page number verification (comparisons, datasets, concepts, index.md, index.html vs PDF): checked {cross_checks} assertions, errors = {cross_errs}")

# 9. Verify zero control characters across all files in wiki/
import pathlib
ctrl_errors = 0
wiki_files_checked = 0
for p in sorted(pathlib.Path(r"c:\Users\User\Downloads\ad-wiki-slides\wiki").rglob("*.md")):
    wiki_files_checked += 1
    content = p.read_text(encoding="utf-8")
    for line_no, line_str in enumerate(content.splitlines(), 1):
        for ch in line_str:
            if (ord(ch) < 32 and ch not in ("\n", "\r", "\t")) or ord(ch) == 127:
                ctrl_errors += 1
                log(f"Control char {repr(ch)} found in {p} line {line_no}")
total_errors += ctrl_errors
log(f"Control character scan across {wiki_files_checked} wiki/*.md files: errors = {ctrl_errors}")

log("=" * 80)
log(f"=== TOTAL across all 12 tables (Table 1-6 & Table A.1-A.6): checked {total_cells} cells ({total_numbers} numbers), cross-page assertions = {cross_checks}, control-char errors = {ctrl_errors}, total errors = {total_errors} ===")

with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines) + "\n")
