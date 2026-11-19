import pathlib
import re
import tokenize
import pypdf

NL = chr(10)
CR = chr(13)
TAB = chr(9)

pdf_path = r"c:\Users\User\Downloads\ad-wiki-slides\raw\papers\hecklerkram2025-mvtec-ad-2.pdf"
md_path = r"c:\Users\User\Downloads\ad-wiki-slides\wiki\papers\hecklerkram2025-mvtec-ad-2.md"
report_path = r"c:\Users\User\Downloads\ad-wiki-slides\scripts\reports\mvtec-ad-2-table-check.txt"

reader = pypdf.PdfReader(pdf_path)
p2 = reader.pages[1].extract_text()
p3 = reader.pages[2].extract_text()
p5 = reader.pages[4].extract_text()
p6 = reader.pages[5].extract_text()
p10 = reader.pages[9].extract_text()
p15 = reader.pages[14].extract_text()

with open(md_path, "r", encoding="utf-8") as f:
    md_text = f.read()

METHODS = ["PatchCore", "RD", "RD++", "EfficientAD", "MSFlow", "SimpleNet", "DSR"]
OBJECTS = ["Can", "Fabric", "Fruit Jelly", "Rice", "Sheet Metal", "Vial", "Wall Plugs", "Walnuts"]
OBJECTS_WITH_MEAN = OBJECTS + ["Mean"]

report_lines = []
total_cells = 0
total_numbers = 0
total_errors = 0


def log(msg):
    print(msg)
    report_lines.append(msg)


def extract_md_table_rows(md_section):
    rows = {}
    for line in md_section.splitlines():
        l = line.strip()
        if not l.startswith("| **"):
            continue
        cols = [c.strip() for c in l.strip("|").split("|")]
        raw_key = cols[0].replace(r"\*", "__AST__").replace("*", "").replace("__AST__", "*").strip()
        # Normalize key like "RD (即 RD4AD)" -> "RD"
        if raw_key.startswith("RD "):
            raw_key = "RD"
        elif raw_key.startswith("Total "):
            raw_key = "Total"
        cells = [c.replace("*", "").strip() for c in cols[1:]]
        rows[raw_key] = cells
    return rows


def find_nums(s):
    return re.findall(r"\d+(?:\.\d+)?", s)


# 1. Verify Table 1 (8 rows x 3 cols = 24 cells, 24 numbers)
sec_t1 = md_text.split("### 5.2 跨資料集分割表現對比：Table 1")[1].split("### 5.3 MVTec AD 2 標準解析度")[0]
md_t1 = extract_md_table_rows(sec_t1)
p2_lines = [l.strip() for l in p2.splitlines()]
t1_start = next(i for i, l in enumerate(p2_lines) if l == "TABLE 1")
t1_cells = 0
t1_nums = 0
t1_errs = 0
for rk in METHODS + ["Mean"]:
    pdf_line = next(l for l in p2_lines[t1_start:] if l.startswith(rk + " "))
    pdf_nums = find_nums(pdf_line[len(rk):])
    md_nums = find_nums(" ".join(md_t1[rk]))
    t1_cells += len(md_t1[rk])
    t1_nums += len(pdf_nums)
    if pdf_nums != md_nums:
        t1_errs += 1
        log(f"ERROR in Table 1 [{rk}]: PDF={pdf_nums} vs MD={md_nums}")
total_cells += t1_cells
total_numbers += t1_nums
total_errors += t1_errs
log(f"Table 1 (Cross-Dataset AU-PRO0.30, 8 rows x 3 cols): checked {t1_cells} cells ({t1_nums} numbers), errors = {t1_errs}")

# 2. Verify Table 2 (Qualitative comparison, 10 rows x 7 cols = 70 symbol cells)
sec_t2 = md_text.split("### 4.1 跨資料集定性特徵比較")[1].split("### 4.2 八大工業檢測場景")[0]
md_t2 = extract_md_table_rows(sec_t2)
p3_lines = [l.strip() for l in p3.splitlines()]
t2_criteria = [
    "Real images", "High Variability*", "Defects at Image Borders",
    "Variation in #Objects/image*", "Structural Defects", "Logical Defects",
    "2D Data", "3D Data", "Different Lighting Conditions", "Transparent Objects"
]
t2_cells = 0
t2_errs = 0
for crit in t2_criteria:
    pdf_line = next(l for l in p3_lines if l.startswith(crit + " "))
    pdf_syms = re.findall(r"[✓✗]", pdf_line)
    md_syms = md_t2[crit]
    t2_cells += len(md_syms)
    if pdf_syms != md_syms:
        t2_errs += 1
        log(f"ERROR in Table 2 [{crit}]: PDF={pdf_syms} vs MD={md_syms}")
total_cells += t2_cells
total_errors += t2_errs
log(f"Table 2 (Dataset Qualitative Comparison, 10 rows x 7 cols): checked {t2_cells} symbol cells, errors = {t2_errs}")

# 2b. Verify Table 3 (Acquisition setting, defects, and challenges, 8 rows x 3 cols = 24 text cells)
sec_t3 = md_text.split("以下完整抄錄論文 `Table 3`（p. 5）")[1].split("### 4.3 資料集統計規模")[0]
md_t3 = extract_md_table_rows(sec_t3)
p5_norm = re.sub(r"-\s+", "", " ".join(l.strip() for l in p5.splitlines()))
p5_norm = re.sub(r"\s+", " ", p5_norm)
t3_cells = 0
t3_errs = 0
for obj in OBJECTS:
    assert len(md_t3[obj]) == 3, f"Table 3 {obj}: expected 3 cols"
    for col_val in md_t3[obj]:
        t3_cells += 1
        # Split by <br> and verify each bullet / phrase exists in PDF Page 5 text
        for part in col_val.split("<br>"):
            p_clean = re.sub(r"\s+", " ", part.strip())
            if p_clean not in p5_norm:
                t3_errs += 1
                log(f"ERROR in Table 3 [{obj}]: '{p_clean}' not found in PDF page 5")
total_cells += t3_cells
total_errors += t3_errs
log(f"Table 3 (Acquisition Setting, Defects & Challenges, 8 rows x 3 cols): checked {t3_cells} text cells, errors = {t3_errs}")

# 3. Verify Table 4 (Statistical overview, 8 object rows x 7 cols = 56 cells, 128 numbers + Total row = 7 cells, 15 numbers)
sec_t4 = md_text.split("### 4.3 資料集統計規模與三大測試子集設計")[1].split("### 4.4 取像硬體")[0]
md_t4 = extract_md_table_rows(sec_t4)
p6_lines = [l.strip() for l in p6.splitlines()]
t4_start = next(i for i, l in enumerate(p6_lines) if l == "TABLE 4")
t4_cells = 0
t4_nums = 0
t4_errs = 0
for obj in OBJECTS:
    pdf_line = next(l for l in p6_lines[t4_start:] if l.startswith(obj + " "))
    pdf_nums = find_nums(pdf_line[len(obj):])
    md_nums = find_nums(" ".join(md_t4[obj]))
    t4_cells += len(md_t4[obj])
    t4_nums += len(pdf_nums)
    if pdf_nums != md_nums:
        t4_errs += 1
        log(f"ERROR in Table 4 [{obj}]: PDF={pdf_nums} vs MD={md_nums}")

# Also verify AI-computed Total row in Table 4
expected_total_nums = ["2528", "302", "1084", "379", "705", "2045", "748", "1297", "2045", "748", "1297", "5174", "1875", "3299", "8004"]
md_total_nums = find_nums(" ".join(md_t4["Total"]).replace("Table 4", "").replace("8,004", "8004"))
t4_cells += len(md_t4["Total"])
t4_nums += len(expected_total_nums)
if md_total_nums != expected_total_nums:
    t4_errs += 1
    log(f"ERROR in Table 4 [Total]: expected={expected_total_nums} vs MD={md_total_nums}")
total_cells += t4_cells
total_numbers += t4_nums
total_errors += t4_errs
log(f"Table 4 (Dataset Statistical Overview, 8 rows + Total row): checked {t4_cells} cells ({t4_nums} numbers), errors = {t4_errs}")

# 4. Verify Table 5 (Cameras and lenses, 8 rows x 2 cols = 16 text cells) and Table 6 (Lights, 8 rows x 4 cols = 32 cells)
sec_t5 = md_text.split("#### (A) 相機與鏡頭硬體規格")[1].split("#### (B) 測試集各光照條件使用之光源配置")[0]
md_t5 = extract_md_table_rows(sec_t5)
t5_start = next(i for i, l in enumerate(p6_lines) if l == "TABLE 5")
t5_cells = 0
t5_errs = 0
for obj in OBJECTS:
    pdf_line = next(l for l in p6_lines[t5_start:] if l.startswith(obj + " "))
    rest = pdf_line[len(obj):].strip()
    md_joined = " ".join(md_t5[obj])
    t5_cells += len(md_t5[obj])
    if rest != md_joined:
        t5_errs += 1
        log(f"ERROR in Table 5 [{obj}]: PDF='{rest}' vs MD='{md_joined}'")
total_cells += t5_cells
total_errors += t5_errs
log(f"Table 5 (Cameras and Lenses, 8 rows x 2 cols): checked {t5_cells} text cells, errors = {t5_errs}")

sec_t6 = md_text.split("#### (B) 測試集各光照條件使用之光源配置")[1].split("#### (C) 各場景打光細節")[0]
md_t6 = extract_md_table_rows(sec_t6)
t6_start = next(i for i, l in enumerate(p6_lines) if l == "TABLE 6")
t6_cells = 0
t6_errs = 0
for obj in OBJECTS:
    pdf_line = next(l for l in p6_lines[t6_start:] if l.startswith(obj + " "))
    rest = pdf_line[len(obj):].strip()
    md_joined = " ".join(md_t6[obj])
    t6_cells += len(md_t6[obj])
    if rest != md_joined:
        t6_errs += 1
        log(f"ERROR in Table 6 [{obj}]: PDF='{rest}' vs MD='{md_joined}'")
total_cells += t6_cells
total_errors += t6_errs
log(f"Table 6 (Lighting Conditions, 8 rows x 4 cols): checked {t6_cells} text/symbol cells, errors = {t6_errs}")


# 5. Helper to verify dual-value numeric tables (Tables 7, 8, 9, 10, 11, 12)
def verify_dual_table(table_name, page_str, pdf_header, md_section):
    global total_cells, total_numbers, total_errors
    p_lines = [l.strip() for l in page_str.splitlines()]
    start = next(i for i, l in enumerate(p_lines) if l == pdf_header)
    md_rows = extract_md_table_rows(md_section)
    c_count = 0
    n_count = 0
    err_count = 0
    cell_pat = re.compile(r"\d+\.\d+\s*/\s*\d+\.\d+|-")
    for rk in OBJECTS_WITH_MEAN:
        pdf_line = next(l for l in p_lines[start:] if l.startswith(rk + " "))
        rest = pdf_line[len(rk):].strip()
        pdf_cells = [re.sub(r"\s*/\s*", " / ", c.strip()) for c in cell_pat.findall(rest)]
        md_cells = md_rows[rk]
        assert len(pdf_cells) == 7 and len(md_cells) == 7, f"{table_name} {rk}: col count mismatch"
        for col_i in range(7):
            c_count += 1
            p_nums = find_nums(pdf_cells[col_i])
            m_nums = find_nums(md_cells[col_i])
            n_count += len(p_nums)
            if pdf_cells[col_i] != md_cells[col_i] or p_nums != m_nums:
                err_count += 1
                log(f"ERROR in {table_name} [{rk}][col {col_i}]: PDF='{pdf_cells[col_i]}' vs MD='{md_cells[col_i]}'")
    total_cells += c_count
    total_numbers += n_count
    total_errors += err_count
    log(f"{table_name} (9 rows x 7 cols): checked {c_count} cells ({n_count} numbers), errors = {err_count}")
    return md_rows


sec_t7 = md_text.split("#### (A) 主力嚴格指標：")[1].split("#### (B) 傳統寬鬆指標對照：")[0]
sec_t9 = md_text.split("#### (B) 傳統寬鬆指標對照：")[1].split("- **無閾值分割與光照強健性關鍵發現")[0]
sec_t8 = md_text.split("#### (A) 像素級二值化分割")[1].split("#### (B) 影像級二值化分類")[0]
sec_t12 = md_text.split("#### (B) 影像級二值化分類")[1].split("- **有閾值評估與 `PatchCore` 標準化失效分析")[0]
sec_t10 = md_text.split(r"#### (A) 輸入影像尺寸 $512 \times 512$ 之分割表現")[1].split(r"#### (B) 輸入影像尺寸為原始影像寬高 $1/2$ 之分割表現")[0]
sec_t11 = md_text.split(r"#### (B) 輸入影像尺寸為原始影像寬高 $1/2$ 之分割表現")[1].split("- **高解析度擴展性與計算成本權衡結論")[0]

md_t7_rows = verify_dual_table("Table 7 (256x256 AU-PRO0.05)", p10, "TABLE 7", sec_t7)
md_t8_rows = verify_dual_table("Table 8 (256x256 Pixel Seg F1)", p10, "TABLE 8", sec_t8)
md_t9_rows = verify_dual_table("Table 9 (256x256 AU-PRO0.30)", p15, "TABLE 9", sec_t9)
md_t10_rows = verify_dual_table("Table 10 (512x512 AU-PRO0.05)", p15, "TABLE 10", sec_t10)
md_t11_rows = verify_dual_table("Table 11 (Half Size AU-PRO0.05)", p15, "TABLE 11", sec_t11)
md_t12_rows = verify_dual_table("Table 12 (256x256 Image Cls F1)", p15, "TABLE 12", sec_t12)

# 6. Cross-page verification (datasets/mvtec-ad-2.md, datasets/mvtec-ad.md, comparisons/embedding-vs-reconstruction.md, wiki/index.md, index.html)
ds_ad2_path = r"c:\Users\User\Downloads\ad-wiki-slides\wiki\datasets\mvtec-ad-2.md"
ds_ad1_path = r"c:\Users\User\Downloads\ad-wiki-slides\wiki\datasets\mvtec-ad.md"
comp_path = r"c:\Users\User\Downloads\ad-wiki-slides\wiki\comparisons\embedding-vs-reconstruction.md"
w_idx_path = r"c:\Users\User\Downloads\ad-wiki-slides\wiki\index.md"
html_path = r"c:\Users\User\Downloads\ad-wiki-slides\index.html"

cross_checks = 0
cross_errs = 0


def assert_in_file(fpath, expected_substr, desc):
    global cross_checks, cross_errs
    cross_checks += 1
    txt = pathlib.Path(fpath).read_text(encoding="utf-8")
    if expected_substr not in txt:
        cross_errs += 1
        log(f"ERROR in cross-page check [{desc}] in {fpath}: missing '{expected_substr}'")


# Check all 8 object rows of Table 4 in datasets/mvtec-ad-2.md against PDF Table 4
for obj in OBJECTS:
    c = md_t4[obj]
    sub = f"| {c[0]} | {c[1]} | {c[2]} | {c[3]} | {c[4]} | {c[5]} | {c[6]} |"
    assert_in_file(ds_ad2_path, sub, f"datasets/mvtec-ad-2.md Table 4 row [{obj}] vs PDF")

# Check all 7 methods in datasets/mvtec-ad-2.md Section 5 summary table against PDF Mean rows of Tables 9, 7, 10, 11, 8, 12
for m_idx, m_name in enumerate(METHODS):
    t9_m = md_t9_rows["Mean"][m_idx]
    t7_m = md_t7_rows["Mean"][m_idx]
    t10_m = md_t10_rows["Mean"][m_idx]
    t11_m = md_t11_rows["Mean"][m_idx]
    if m_name == "DSR":
        t11_m = f"- *(僅 Rice: {md_t11_rows['Rice'][m_idx]})*"
    t8_m = md_t8_rows["Mean"][m_idx]
    t12_m = md_t12_rows["Mean"][m_idx]
    sub_ad2 = f"| {t9_m} | {t7_m} | {t10_m} | {t11_m} | {t8_m} | {t12_m} |"
    assert_in_file(ds_ad2_path, sub_ad2, f"datasets/mvtec-ad-2.md Sec 5 row [{m_name}] vs PDF Tables 7-12")

    # Check datasets/mvtec-ad.md Section 5.3 table against PDF Table 1, Table 9, Table 7
    t1_c = md_t1[m_name]
    sub_ad1 = f"| {t1_c[0]} | {t1_c[1]} | {t9_m} | {t7_m} |"
    assert_in_file(ds_ad1_path, sub_ad1, f"datasets/mvtec-ad.md Sec 5.3 row [{m_name}] vs PDF Tables 1, 7, 9")

    # Check comparisons/embedding-vs-reconstruction.md Section 4.2 table against PDF Tables 1, 9, 7, 11, 8, 12
    sub_comp = f"| {t1_c[0]} | {t1_c[1]} | {t9_m} | {t7_m} | {t11_m} | {t8_m} | {t12_m} |"
    assert_in_file(comp_path, sub_comp, f"comparisons/embedding-vs-reconstruction.md Sec 4.2 row [{m_name}] vs PDF Tables 1, 7-9, 11-12")

# Check Mean row of Table 1 in datasets/mvtec-ad.md and comparisons/embedding-vs-reconstruction.md
t1_mean = md_t1["Mean"]
assert_in_file(ds_ad1_path, f"| {t1_mean[0]} | {t1_mean[1]} | {t1_mean[2]} / - *(Table 1 僅報 TESTpriv)* |", "datasets/mvtec-ad.md Mean row vs PDF Table 1")
assert_in_file(comp_path, f"| {t1_mean[0]} | {t1_mean[1]} | {t1_mean[2]} / - *(Table 1 僅報 TESTpriv)* |", "comparisons Mean row vs PDF Table 1")

# Check prose numbers in datasets/mvtec-ad-2.md and comparisons/embedding-vs-reconstruction.md against PDF
assert_in_file(ds_ad2_path, f"| 2528 | 302 | 1084 (379/705) | 2045 (748/1297) | 2045 (748/1297) | 5174 (1875/3299) | **總計 8,004 張** |", "datasets/mvtec-ad-2.md Total row vs PDF Table 4 sums")
assert_in_file(comp_path, rf"`{md_t7_rows['Mean'][3].split(' / ')[0]}%` $\text{{AU-PRO}}_{{0.05}}$**（**`{md_t9_rows['Mean'][3].split(' / ')[0]}%` $\text{{AU-PRO}}_{{0.30}}$**）", "comparisons Sec 5 EfficientAD TESTpriv vs PDF Table 7 & 9")
assert_in_file(comp_path, f"`{md_t11_rows['Mean'][0].split(' / ')[0]}% / {md_t11_rows['Mean'][0].split(' / ')[1]}%`", "comparisons Sec 5 PatchCore Table 11 Mean vs PDF Table 11")
assert_in_file(comp_path, f"`{md_t8_rows['Mean'][0].split(' / ')[0]}% / {md_t8_rows['Mean'][0].split(' / ')[1]}%`", "comparisons Sec 5 PatchCore Table 8 Mean vs PDF Table 8")
assert_in_file(comp_path, f"`{md_t12_rows['Mean'][0].split(' / ')[0]}% / {md_t12_rows['Mean'][0].split(' / ')[1]}%`", "comparisons Sec 5 PatchCore Table 12 Mean vs PDF Table 12")

# Check wiki/index.md and index.html numbers against PDF Table 1 (58.7), Table 4 (8,004), Table 7 (30.8)
assert_in_file(w_idx_path, rf"{md_t1['EfficientAD'][2]}% $\text{{AU-PRO}}_{{0.30}}$（出自 Table 1 & Table 9）與 {md_t7_rows['Mean'][3].split(' / ')[0]}% $\text{{AU-PRO}}_{{0.05}}$（出自 Table 7）", "wiki/index.md numbers vs PDF Table 1, 7, 9")
assert_in_file(html_path, f"{md_t1['EfficientAD'][2]}% AU-PRO0.30（出自 Table 1 &amp; Table 9）與 {md_t7_rows['Mean'][3].split(' / ')[0]}% AU-PRO0.05（出自 Table 7）", "index.html numbers vs PDF Table 1, 7, 9")

total_errors += cross_errs
log(f"Cross-page number verification (datasets/mvtec-ad-2.md, datasets/mvtec-ad.md, comparisons, index.md, index.html vs PDF): checked {cross_checks} assertions, errors = {cross_errs}")

# 7. Verify zero control characters across all files in wiki/
ctrl_errors = 0
wiki_files_checked = 0
for p in sorted(pathlib.Path(r"c:\Users\User\Downloads\ad-wiki-slides\wiki").rglob("*.md")):
    wiki_files_checked += 1
    content = p.read_text(encoding="utf-8")
    for line_no, line_str in enumerate(content.splitlines(), 1):
        for ch in line_str:
            if (ord(ch) < 32 and ch not in (NL, CR, TAB)) or ord(ch) == 127:
                ctrl_errors += 1
                log(f"Control char {repr(ch)} found in {p} line {line_no}")
total_errors += ctrl_errors
log(f"Control character scan across {wiki_files_checked} wiki/*.md files: errors = {ctrl_errors}")

# 8. Verify raw-string compliance in scripts/generate_mvtec_ad_2_tables.py and scripts/verify_mvtec_ad_2_tables.py
raw_str_errors = 0
for sp in [
    r"c:\Users\User\Downloads\ad-wiki-slides\scripts\generate_mvtec_ad_2_tables.py",
    r"c:\Users\User\Downloads\ad-wiki-slides\scripts\verify_mvtec_ad_2_tables.py",
]:
    with tokenize.open(sp) as sf:
        for tok in tokenize.generate_tokens(sf.readline):
            if tok.type == tokenize.STRING and chr(92) in tok.string:
                prefix = tok.string.split(chr(34))[0].split(chr(39))[0].lower()
                if "r" not in prefix:
                    raw_str_errors += 1
                    log(f"Non-raw string with backslash in {sp} line {tok.start[0]}: {tok.string[:40]}")
total_errors += raw_str_errors
log(f"Python script raw-string check across MVTec AD 2 scripts: errors = {raw_str_errors}")

# 9. Verify all Markdown relative links in wiki/ resolve to existing files
link_errors = 0
links_checked = 0
link_pat = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
for p in sorted(pathlib.Path(r"c:\Users\User\Downloads\ad-wiki-slides\wiki").rglob("*.md")):
    content = p.read_text(encoding="utf-8")
    for m in link_pat.finditer(content):
        target = m.group(1).split("#")[0].strip()
        if not target or target.startswith("http://") or target.startswith("https://"):
            continue
        links_checked += 1
        resolved = (p.parent / target).resolve()
        if not resolved.exists():
            link_errors += 1
            log(f"Broken relative link in {p}: {target} -> {resolved}")
total_errors += link_errors
log(f"Markdown relative link check across {wiki_files_checked} wiki/*.md files: checked {links_checked} links, errors = {link_errors}")

log("=" * 80)
log(f"=== TOTAL across all 12 tables (Table 1-12): checked {total_cells} cells ({total_numbers} numbers), cross-page assertions = {cross_checks}, control-char errors = {ctrl_errors}, raw-string errors = {raw_str_errors}, link errors = {link_errors}, total errors = {total_errors} ===")

with open(report_path, "w", encoding="utf-8") as f:
    f.write(NL.join(report_lines) + NL)
