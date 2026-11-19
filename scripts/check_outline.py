import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_OUTLINE_PATH = os.path.join(ROOT, "slides", "evolution-of-anomaly-detection", "outline.md")
REPORT_DIR = os.path.join(ROOT, "slides", "evolution-of-anomaly-detection", "reports")
DEFAULT_REPORT_PATH = os.path.join(REPORT_DIR, "outline-check.txt")
AGENTS_PATH = os.path.join(ROOT, "AGENTS.md")

SEVEN_PAPERS = [
    "bergmann2019-mvtec-ad",
    "ho2020-ddpm",
    "zavrtanik2021-riad",
    "roth2022-patchcore",
    "zhang2023-diffusionad",
    "lee2026-lambda",
    "hecklerkram2025-mvtec-ad-2",
]

REQUIRED_SLIDE_TITLES = {
    1: "封面＋學習目標",
    2: "任務設定：只用正常品訓練、影像級與像素級輸出",
    3: "MVTec AD 與基本評估",
    4: "兩條基本路線：重建正常外觀／比對正常特徵",
    5: "RIAD",
    6: "PatchCore",
    7: "DDPM 入門",
    8: "DiffusionAD",
    9: "LAMBDA",
    10: "效果與成本",
    11: "MVTec AD 2：舊基準沒涵蓋的難題",
    12: "PRO vs. TPR",
    13: "AU-PRO0.05：0.05 是 FPR 積分上限",
    14: "新基準結果",
    15: "方法脈絡＋一題情境判斷題",
    16: "參考資料：7 篇各支援哪幾頁",
}

METHOD_SLIDES = [5, 6, 8, 9]
METHOD_QUESTIONS = ["輸入什麼", "保存或學到什麼", "怎麼產生異常分數", "主要限制"]

CLAIM_HEADERS = [
    "主張 ID",
    "內容",
    "方法",
    "資料集",
    "指標",
    "數值與條件",
    "wiki 頁與段落",
    "原文位置",
    "原文事實／依原文數據計算／AI 推論",
]

VALID_CLAIM_TYPES = {"原文事實", "依原文數據計算", "AI 推論"}

# Claims whose numerical values come from Markdown tables in their referenced wiki section
TABLE_BACKED_CLAIMS = {
    "C05-02",
    "C05-03",
    "C06-02",
    "C06-03",
    "C08-02",
    "C09-02",
    "C09-03",
    "C10-01",
    "C10-02",
    "C10-03",
    "C10-04",
    "C11-03",
    "C13-03",
    "C14-01",
    "C14-02",
    "C14-03",
    "C14-04",
    "C14-05",
    "C14-06",
    "C14-07",
    "C14-08",
    "C15-01",
    "C15-02",
}

# Regex matching every number token (including comma-formatted thousands integers, decimals, and integers)
NUM_TOKEN_RE = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?")


def clean_md_cell(s):
    """Strip Markdown links, bold/italics, and inline code from a table cell or header."""
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = s.replace("**", "").replace("*", "").replace("`", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def load_wiki_file(wiki_rel_path):
    full_path = os.path.join(ROOT, *wiki_rel_path.split("/"))
    if not os.path.isfile(full_path):
        return None, []
    with open(full_path, "r", encoding="utf-8") as f:
        text = f.read()
    headings = []
    for line in text.splitlines():
        if line.startswith("#"):
            headings.append(line.strip())
    return text, headings


def extract_wiki_section(text, heading_prefix):
    """Extract the markdown content of the section starting with heading_prefix."""
    lines = text.splitlines()
    norm_prefix = heading_prefix.replace("`", "").strip()
    start_idx = None
    start_level = None
    matched_heading = None

    for i, line in enumerate(lines):
        if line.startswith("#"):
            norm_line = line.replace("`", "").strip()
            if norm_line.startswith(norm_prefix):
                start_idx = i
                start_level = len(line) - len(line.lstrip("#"))
                matched_heading = line.strip()
                break

    if start_idx is None:
        return None, None

    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        line = lines[j]
        if line.startswith("#"):
            lvl = len(line) - len(line.lstrip("#"))
            if lvl <= start_level:
                end_idx = j
                break

    # If start_level is #### (level 4), prepend its immediate ### (level 3) parent heading line for table context
    parent_heading_line = ""
    if start_level == 4:
        for k in range(start_idx - 1, -1, -1):
            if lines[k].startswith("### "):
                parent_heading_line = lines[k] + "\n"
                break

    return matched_heading, parent_heading_line + "\n".join(lines[start_idx:end_idx])


def parse_markdown_tables(section_text):
    """Parse all Markdown tables inside section_text into [{'headers': [...], 'rows': [...]}]."""
    tables = []
    lines = section_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("|") and i + 1 < len(lines):
            sep_line = lines[i + 1].strip()
            if sep_line.startswith("|") and re.search(r":?-{3,}:?", sep_line):
                raw_headers = [c.strip() for c in line.strip("|").split("|")]
                headers = [clean_md_cell(c) for c in raw_headers]
                rows = []
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith("|"):
                    r_raw = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                    r_clean = [clean_md_cell(c) for c in r_raw]
                    if len(r_clean) == len(headers):
                        rows.append({"raw": r_raw, "clean": r_clean})
                    j += 1
                tables.append({"headers": headers, "raw_headers": raw_headers, "rows": rows})
                i = j
                continue
        i += 1
    return tables


def split_top_level_slashes(s):
    """Split a string by ' / ' outside parentheses '()' and '（）'."""
    parts = []
    depth = 0
    current = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch in "（(":
            depth += 1
            current.append(ch)
            i += 1
        elif ch in "）)":
            depth = max(0, depth - 1)
            current.append(ch)
            i += 1
        elif depth == 0 and s[i : i + 3] == " / ":
            parts.append(clean_md_cell("".join(current)))
            current = []
            i += 3
        else:
            current.append(ch)
            i += 1
    if current:
        parts.append(clean_md_cell("".join(current)))
    return [p for p in parts if p]


def split_metric_columns(metric_str):
    """Split a claim's 指標 field into column names while preserving slashes inside parentheses or compound metric names."""
    if "<br>" in metric_str and "] / " in metric_str:
        parts = metric_str.split("] / ")
        out = []
        for idx, p in enumerate(parts):
            if idx < len(parts) - 1:
                out.append(clean_md_cell(p + "]"))
            else:
                out.append(clean_md_cell(p))
        return out

    if "Image / Pixel ROC AUC" in metric_str:
        parts = re.split(r"\)\s*/\s*(?=(?:紋理|物件|全 15 類))", metric_str)
        out = []
        for idx, p in enumerate(parts):
            if idx < len(parts) - 1 and not p.endswith(")"):
                p = p + ")"
            out.append(clean_md_cell(p))
        return out

    return split_top_level_slashes(metric_str)


def extract_decimals(s):
    """Extract decimal numbers for numeric comparison, ignoring section/equation/metric-name numbers."""
    s_clean = re.sub(r"AU-PRO_?\{?0\.\d+\}?", "", s)
    s_clean = re.sub(r"(?:Sec\.|Fig\.|Table|Appendix)\s*[A-Z0-9.\-–]+", "", s_clean)
    s_clean = re.sub(r"0\.01%", "", s_clean)
    s_clean = re.sub(r"v\d+\.\d+", "", s_clean)
    return re.findall(r"[-+]?\d+\.\d+", s_clean)


def cell_matches_val_item(cell_val, val_item, col_name):
    """Check exact equality between a table cell and the positional value item in 數值與條件."""
    c_clean = clean_md_cell(cell_val)
    v_clean = clean_md_cell(val_item)
    if c_clean == v_clean:
        return True
    if "(秒)" in col_name and v_clean.endswith(" s"):
        v_clean = v_clean[:-2].strip()
    return c_clean == v_clean


def verify_claim_against_table(claim, wiki_refs, full_section_texts):
    """
    Locate the Markdown table in the claim's referenced wiki section,
    match the row using 方法, match the column(s) using 指標,
    verify dataset context, and check strict positional correspondence
    between the i-th metric column and the i-th value in 數值與條件.
    Returns (passed: bool, detail_msg: str).
    """
    cid = claim["id"]
    method_str = claim["method"]
    dataset_str = claim["dataset"]
    metric_str = claim["metric"]
    val_cond = claim["val_cond"]
    content = claim["content"]

    all_tables = []
    combined_section_text = ""
    for wpath, wsec, sec_text in full_section_texts:
        combined_section_text += "\n" + sec_text
        for tbl in parse_markdown_tables(sec_text):
            all_tables.append((wpath, wsec, tbl))

    if not all_tables:
        return False, f"Claim {cid}: no Markdown table found in referenced wiki section(s)"

    # 1. Verify Dataset matches the referenced wiki section / table context
    ds_tokens = [clean_md_cell(d) for d in re.split(r"\s*/\s*", dataset_str) if d.strip()]
    norm_sec = clean_md_cell(combined_section_text)
    for ds in ds_tokens:
        base_ds = re.sub(r"\s*\([^)]*\)", "", ds).strip()
        if base_ds and base_ds not in norm_sec:
            return False, f"Claim {cid}: dataset '{base_ds}' (from '{dataset_str}') not found in referenced wiki section"

    # 2. Parse target row names from 方法 and target column names from 指標
    target_methods = [clean_md_cell(m) for m in method_str.split(" / ") if m.strip()]
    target_metrics = split_metric_columns(metric_str)

    if not target_methods:
        return False, f"Claim {cid}: empty 方法 field"
    if not target_metrics:
        return False, f"Claim {cid}: empty 指標 field"

    looked_up_cells = []
    looked_up_matrix = []  # looked_up_matrix[m_idx][k_idx] = (tm, col_name, cell_val)

    for tm in target_methods:
        row_found = False
        matched_table = None
        matched_row = None

        for wpath, wsec, tbl in all_tables:
            for r in tbl["rows"]:
                row_header = r["clean"][0]
                if row_header == tm:
                    row_found = True
                    matched_table = tbl
                    matched_row = r
                    break
            if row_found:
                break

        if not row_found:
            return False, f"Claim {cid}: row for method '{tm}' not found in Markdown table of referenced wiki section"

        method_cells = []
        for col_name in target_metrics:
            col_idx = None
            for idx, h in enumerate(matched_table["headers"]):
                if h == col_name:
                    col_idx = idx
                    break
            if col_idx is None:
                return (
                    False,
                    f"Claim {cid}: column for metric '{col_name}' not found in Markdown table headers {matched_table['headers']}",
                )

            cell_val = matched_row["clean"][col_idx]
            looked_up_cells.append((tm, col_name, cell_val))
            method_cells.append((tm, col_name, cell_val))
        looked_up_matrix.append(method_cells)

    # 3. Strict Positional Correspondence Check between 指標 and 數值與條件
    # Strip trailing full-width parenthetical condition notes like （硬體：...）
    val_cond_main = re.sub(r"（[^）]*）\s*$", "", clean_md_cell(val_cond)).strip()
    M = len(target_methods)
    K = len(target_metrics)

    if M > 1 and K > 1:
        m_blocks = [b.strip() for b in val_cond_main.split("｜") if b.strip()]
        if len(m_blocks) != M:
            return (
                False,
                f"Claim {cid}: expected {M} method blocks separated by '｜' in 數值與條件, got {len(m_blocks)} ('{val_cond}')",
            )
        for m_idx, m_block in enumerate(m_blocks):
            # Strip trailing method/parameter tag like (n_m=200) or (DiffusionAD)
            m_block_clean = re.sub(r"\s*\((?:n_m=\d+|DiffusionAD|LAMBDA)\)\s*$", "", m_block).strip()
            val_items = split_top_level_slashes(m_block_clean)
            if len(val_items) != K:
                return (
                    False,
                    f"Claim {cid}: method '{target_methods[m_idx]}' has {len(val_items)} '/'-separated values in 數值與條件, expected {K} for metrics {target_metrics}",
                )
            for k_idx, val_item in enumerate(val_items):
                tm, col_name, cell_val = looked_up_matrix[m_idx][k_idx]
                if not cell_matches_val_item(cell_val, val_item, col_name):
                    return (
                        False,
                        f"Claim {cid}: positional mismatch for method '{tm}' at metric #{k_idx + 1} ('{col_name}'): table cell is '{cell_val}', but 數值與條件 item #{k_idx + 1} is '{val_item}' (full: '{val_cond}')",
                    )
    elif M > 1 and K == 1:
        val_items = split_top_level_slashes(val_cond_main)
        if len(val_items) != M:
            return (
                False,
                f"Claim {cid}: expected {M} '/'-separated values for methods {target_methods}, got {len(val_items)} ('{val_cond}')",
            )
        for m_idx, val_item in enumerate(val_items):
            tm, col_name, cell_val = looked_up_matrix[m_idx][0]
            if not cell_matches_val_item(cell_val, val_item, col_name):
                return (
                    False,
                    f"Claim {cid}: positional mismatch at method #{m_idx + 1} ('{tm}', metric='{col_name}'): table cell is '{cell_val}', but 數值與條件 item #{m_idx + 1} is '{val_item}'",
                )
    elif M == 1 and K > 1:
        if "｜" in val_cond_main:
            val_items = [b.strip() for b in val_cond_main.split("｜") if b.strip()]
        else:
            val_items = split_top_level_slashes(val_cond_main)
        if len(val_items) != K:
            return (
                False,
                f"Claim {cid}: expected {K} positional values in 數值與條件 for metrics {target_metrics}, got {len(val_items)} ('{val_cond}')",
            )
        for k_idx, val_item in enumerate(val_items):
            tm, col_name, cell_val = looked_up_matrix[0][k_idx]
            if not cell_matches_val_item(cell_val, val_item, col_name):
                return (
                    False,
                    f"Claim {cid}: positional mismatch at metric #{k_idx + 1} (row='{tm}', col='{col_name}'): table cell value '{cell_val}' does not match 數值與條件 item #{k_idx + 1} '{val_item}' (full: '{val_cond}')",
                )
    else:
        tm, col_name, cell_val = looked_up_matrix[0][0]
        if not cell_matches_val_item(cell_val, val_cond_main, col_name):
            return (
                False,
                f"Claim {cid}: table cell value '{cell_val}' (row='{tm}', col='{col_name}') does not match claim 數值與條件 '{val_cond}'",
            )

    # 4. Also verify that every decimal number in 數值與條件 and 內容 is backed by the looked-up cells
    all_cell_strings = " | ".join(f"{c[0]} {c[1]} {c[2]}" for c in looked_up_cells)
    cell_decimals = set(extract_decimals(all_cell_strings))
    claim_decimals = extract_decimals(val_cond) + extract_decimals(content)
    for dec in claim_decimals:
        if dec not in cell_decimals:
            return (
                False,
                f"Claim {cid}: number '{dec}' in claim does not match any looked-up table cell value ({all_cell_strings})",
            )

    summary_pairs = [f"[{tm} | {col}] = {val}" for tm, col, val in looked_up_cells]
    return True, f"Claim {cid}（已由程式核對儲存格）：{'; '.join(summary_pairs)}"


def verify_pending_ai_claim_numbers(claim, full_section_texts):
    """
    For a '待 AI 審查' claim, verify that EVERY number token (including comma-formatted
    thousands integers like 5,354 or 8,004, decimals, and integers) in 內容 and 數值與條件
    appears inside the referenced wiki section(s) ONLY (not searching the whole file).
    Returns (passed: bool, detail_msg: str).
    """
    cid = claim["id"]
    content = claim["content"]
    val_cond = claim["val_cond"]
    wiki_src = claim["wiki_src"]

    combined_section_text = "\n".join(sec_text for _, _, sec_text in full_section_texts)
    sec_num_tokens = set(NUM_TOKEN_RE.findall(combined_section_text))
    claim_num_tokens = NUM_TOKEN_RE.findall(content + " " + val_cond)

    missing_nums = [num for num in claim_num_tokens if num not in sec_num_tokens]
    if missing_nums:
        return (
            False,
            f"Claim {cid}（待 AI 審查）：數字 {missing_nums} 未出現在所引 wiki 段落內（{wiki_src}）",
        )

    return (
        True,
        f"Claim {cid}（數字存在性已查、語意待 AI 審查）：共核對 {len(claim_num_tokens)} 個數字皆存在於所引段落（{wiki_src}），語意關係留待關卡 ③ AI 審查",
    )


def run_check(outline_path=DEFAULT_OUTLINE_PATH, report_path=DEFAULT_REPORT_PATH, verbose=True):
    lines_out = []
    errors = []

    def log(msg):
        lines_out.append(msg)

    def fail(msg):
        errors.append(msg)
        lines_out.append(f"  [FAIL] {msg}")

    def ok(msg):
        lines_out.append(f"  [PASS] {msg}")

    log("======================================================================")
    log(f"Gate ① Programmatic Check Report: {os.path.relpath(outline_path, ROOT)}")
    log("======================================================================")

    # 0. Check AGENTS.md character count & slide density rule presence
    with open(AGENTS_PATH, "r", encoding="utf-8") as f:
        agents_text = f.read()
    agents_chars = len(agents_text)
    log("\n[0] AGENTS.md Character Count & Density Rule Check")
    if agents_chars <= 12000:
        ok(f"AGENTS.md length = {agents_chars} chars (<= 12,000 limit)")
    else:
        fail(f"AGENTS.md length = {agents_chars} chars (exceeds 12,000 limit)")

    if "投影片密度規則" in agents_text and "1366×768" in agents_text:
        ok("AGENTS.md §5 includes '投影片密度規則' (1366×768 single-screen rule)")
    else:
        fail("AGENTS.md §5 missing '投影片密度規則'")

    # 1. Read outline.md and check base wiki commit
    if not os.path.isfile(outline_path):
        fail(f"Outline file not found: {outline_path}")
        return False, "\n".join(lines_out), errors

    with open(outline_path, "r", encoding="utf-8") as f:
        outline_text = f.read()

    log("\n[1] Base Wiki Commit & Cover Declaration Check")
    try:
        git_out = subprocess.check_output(
            ["git", "log", "-1", "--format=%h %H", "--", "wiki"],
            cwd=ROOT,
            text=True,
        ).strip()
        short_hash, full_hash = git_out.split()
    except Exception as e:
        short_hash, full_hash = "", ""
        fail(f"Failed to query git log for wiki/: {e}")

    if short_hash and (short_hash in outline_text or full_hash in outline_text):
        ok(f"Outline records current wiki commit: {short_hash} ({full_hash})")
    else:
        fail(f"Outline header missing current wiki commit {short_hash}")

    if "這是選定 7 篇論文的發展脈絡，不代表後面的方法全面取代前面的" in outline_text:
        ok("Cover note present: '這是選定 7 篇論文的發展脈絡，不代表後面的方法全面取代前面的'")
    else:
        fail("Cover note missing")

    # 2. Split slides and check numbering, titles, learning objectives, and sections
    log("\n[2] Slide Count, Sequential Numbering, Learning Objectives & Density Sections Check")
    slide_pattern = re.compile(r"^## 第 (\d+) 頁：(.+)$", re.MULTILINE)
    matches = list(slide_pattern.finditer(outline_text))

    if len(matches) == 16:
        ok(f"Total slide count = {len(matches)} (expected 16)")
    else:
        fail(f"Total slide count = {len(matches)} (expected 16)")

    slides = {}
    for idx, m in enumerate(matches):
        page_num = int(m.group(1))
        title = m.group(2).strip()
        start_pos = m.end()
        end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(outline_text)
        body = outline_text[start_pos:end_pos]
        slides[page_num] = {"title": title, "body": body}

        expected_num = idx + 1
        if page_num != expected_num:
            fail(f"Slide position {expected_num} has wrong number: 第 {page_num} 頁")
        expected_title = REQUIRED_SLIDE_TITLES.get(page_num, "")
        if title == expected_title:
            ok(f"Slide {page_num:02d} title matches: '{title}'")
        else:
            fail(f"Slide {page_num:02d} title mismatch: got '{title}', expected '{expected_title}'")

        lo_match = re.search(r"### 學習目標\s*\n+([^\n#]+)", body)
        if lo_match and len(lo_match.group(1).strip()) >= 10:
            ok(f"Slide {page_num:02d} has 1-sentence learning objective ({len(lo_match.group(1).strip())} chars)")
        else:
            fail(f"Slide {page_num:02d} missing or empty '### 學習目標'")

        if "### 投影片可見內容" in body and "### 查證資料與講稿備註" in body:
            ok(f"Slide {page_num:02d} includes '### 投影片可見內容' and '### 查證資料與講稿備註'")
        else:
            fail(f"Slide {page_num:02d} missing '### 投影片可見內容' or '### 查證資料與講稿備註'")

    # 3. Check slide-level Wiki section list (Slides 1–16)
    log("\n[3] Slide-Level Wiki Section List Existence Check (Slides 1–16)")
    wiki_ref_pattern = re.compile(r"`(wiki/[a-z0-9\-/]+\.md)`\s*`(##+ [^`]+)`")
    for p in range(1, 17):
        if p not in slides:
            continue
        body = slides[p]["body"]
        sec_block_match = re.search(r"### 用到的 Wiki 頁與段落\s*\n(.*?)(?=\n### |\Z)", body, re.DOTALL)
        if not sec_block_match:
            fail(f"Slide {p:02d} missing '### 用到的 Wiki 頁與段落'")
            continue
        refs = wiki_ref_pattern.findall(sec_block_match.group(1))
        if not refs:
            fail(f"Slide {p:02d} has no valid '`wiki/...` `## ...`' pairs in '### 用到的 Wiki 頁與段落'")
            continue
        all_ok = True
        for wpath, wsec in refs:
            text, _ = load_wiki_file(wpath)
            if text is None:
                fail(f"Slide {p:02d} slide-level source references non-existent file: {wpath}")
                all_ok = False
                continue
            matched_h, _ = extract_wiki_section(text, wsec)
            if matched_h is None:
                fail(f"Slide {p:02d} slide-level source references non-existent heading '{wsec}' in {wpath}")
                all_ok = False
        if all_ok:
            ok(f"Slide {p:02d}: all {len(refs)} slide-level wiki file & heading path(s) exist")

    # 4. Check planned diagram files exist on disk
    log("\n[4] Planned Diagram Files Existence Check")
    diag_pattern = re.compile(r"`(assets/diagrams/(?:slides/)?[a-z0-9\-]+\.(?:svg|html))`")
    diag_refs = []
    for p in range(1, 17):
        if p not in slides:
            continue
        body = slides[p]["body"]
        diag_block_match = re.search(r"### 預計使用的圖檔\s*\n(.*?)(?=\n### |\Z)", body, re.DOTALL)
        if not diag_block_match:
            fail(f"Slide {p:02d} missing '### 預計使用的圖檔'")
            continue
        for drel in diag_pattern.findall(diag_block_match.group(1)):
            dfull = os.path.join(ROOT, *drel.split("/"))
            diag_refs.append((p, drel, os.path.isfile(dfull)))
            if os.path.isfile(dfull):
                ok(f"Slide {p:02d} diagram file exists: {drel}")
            else:
                fail(f"Slide {p:02d} diagram file NOT found: {drel}")
    if not diag_refs:
        fail("No diagrams referenced across any slides")

    # 5. Check Method Slides (5, 6, 8, 9) standardized 4-question structure
    log("\n[5] Method Slides (5, 6, 8, 9) Standardized 4-Question Check")
    for p in METHOD_SLIDES:
        if p not in slides:
            continue
        body = slides[p]["body"]
        missing_q = [q for q in METHOD_QUESTIONS if q not in body]
        if not missing_q:
            ok(f"Slide {p:02d} ({slides[p]['title']}) contains all 4 required questions: {', '.join(METHOD_QUESTIONS)}")
        else:
            fail(f"Slide {p:02d} missing required questions: {missing_q}")

    # 6. Per-Claim Wiki Source Check & Table Cell Lookup vs. AI Review Classification
    log("\n[6] Per-Claim Wiki Source Check, Table Cell Lookup & Claim Classification")
    paper_support_pages = {paper: set() for paper in SEVEN_PAPERS}
    paper_support_claims = {paper: [] for paper in SEVEN_PAPERS}

    cell_checked_claims = []
    pending_ai_claims = []
    unchecked_claims = []

    for p in range(1, 17):
        if p not in slides:
            continue
        body = slides[p]["body"]
        table_match = re.search(r"### 預計的主張記錄表\s*\n(.*?)(?=\n---|\n## |\Z)", body, re.DOTALL)
        if not table_match:
            fail(f"Slide {p:02d} missing '### 預計的主張記錄表'")
            continue
        tlines = [ln.strip() for ln in table_match.group(1).strip().splitlines() if ln.strip().startswith("|")]
        if len(tlines) < 3:
            fail(f"Slide {p:02d} claim table has no data rows")
            continue
        headers = [c.strip() for c in tlines[0].strip("|").split("|")]
        if headers != CLAIM_HEADERS:
            fail(f"Slide {p:02d} claim table headers mismatch: {headers}")

        for rline in tlines[2:]:
            cols = [c.strip() for c in rline.strip("|").split("|")]
            if len(cols) != 9:
                fail(f"Slide {p:02d} claim row has {len(cols)} cols (expected 9): {rline}")
                unchecked_claims.append(rline)
                continue

            cid, content, method, dataset, metric, val_cond, wiki_src, raw_loc, ctype = cols
            cid_clean = cid.strip("`")

            if any(bad in rline for bad in ["待補", "TBD", "TODO"]):
                fail(f"Slide {p:02d} claim {cid_clean} contains placeholder ('待補'/'TBD'/'TODO')")
            if ctype not in VALID_CLAIM_TYPES:
                fail(f"Slide {p:02d} claim {cid_clean} has invalid type '{ctype}'")
            if ctype == "AI 推論" and "（AI 整理）" not in content and "（AI 整理）" not in wiki_src:
                fail(f"Slide {p:02d} AI-inferred claim {cid_clean} missing '（AI 整理）' marker")

            # Every claim MUST have its own valid wiki file and heading in cols[6] (wiki_src)
            claim_wiki_refs = wiki_ref_pattern.findall(wiki_src)
            if not claim_wiki_refs:
                fail(
                    f"Slide {p:02d} claim {cid_clean}: 'wiki 頁與段落' column ('{wiki_src}') has no valid '`wiki/...` `## ...`' reference"
                )
                unchecked_claims.append(cid_clean)
                continue

            claim_sections = []
            ref_error = False
            for wpath, wsec in claim_wiki_refs:
                text, _ = load_wiki_file(wpath)
                if text is None:
                    fail(
                        f"Slide {p:02d} claim {cid_clean}: 'wiki 頁與段落' references non-existent file '{wpath}'"
                    )
                    ref_error = True
                    continue
                matched_h, sec_text = extract_wiki_section(text, wsec)
                if matched_h is None:
                    fail(
                        f"Slide {p:02d} claim {cid_clean}: 'wiki 頁與段落' references non-existent heading '{wsec}' in '{wpath}'"
                    )
                    ref_error = True
                    continue
                claim_sections.append((wpath, matched_h, sec_text))

            if ref_error:
                unchecked_claims.append(cid_clean)
                continue

            claim_obj = {
                "id": cid_clean,
                "slide": p,
                "content": content,
                "method": method,
                "dataset": dataset,
                "metric": metric,
                "val_cond": val_cond,
                "wiki_src": wiki_src,
                "raw_loc": raw_loc,
                "ctype": ctype,
            }

            is_table_claim = (
                cid_clean in TABLE_BACKED_CLAIMS
                or (p == 10 and cid_clean != "C10-05")
                or p == 14
            )

            if is_table_claim:
                passed_tbl, tbl_msg = verify_claim_against_table(claim_obj, claim_wiki_refs, claim_sections)
                if passed_tbl:
                    cell_checked_claims.append(cid_clean)
                    ok(f"Slide {p:02d} {tbl_msg}")
                else:
                    fail(f"Slide {p:02d} {tbl_msg}")
            else:
                passed_num, num_msg = verify_pending_ai_claim_numbers(claim_obj, claim_sections)
                if passed_num:
                    pending_ai_claims.append(cid_clean)
                    lines_out.append(f"  [INFO] Slide {p:02d} {num_msg}")
                else:
                    fail(f"Slide {p:02d} {num_msg}")

            # Track 7-paper support on teaching slides 2..15
            if 2 <= p <= 15 and ctype in {"原文事實", "依原文數據計算"}:
                for paper in SEVEN_PAPERS:
                    if f"{paper}.pdf" in raw_loc or f"wiki/papers/{paper}.md" in wiki_src:
                        paper_support_pages[paper].add(p)
                        paper_support_claims[paper].append(cid_clean)

    # 7. Check 7-Paper Teaching Claim Coverage on Slides 2–15
    log("\n[7] 7-Paper Teaching Claim Coverage Check (Slides 2–15)")
    for paper in SEVEN_PAPERS:
        pages = sorted(paper_support_pages[paper])
        claims = paper_support_claims[paper]
        if pages:
            ok(f"Paper '{paper}' supports {len(claims)} teaching claim(s) on Slide(s) {pages}: {', '.join(claims)}")
        else:
            fail(f"Paper '{paper}' does NOT support any actual teaching claim on Slides 2–15")

    # 8. Check Slide 10 '未記載' test conditions & Slide 14/15 boundary statements
    log("\n[8] Slide 10, 14 & 15 Specific Boundary & Framing Check")
    if 10 in slides:
        s10_body = slides[10]["body"]
        for unrec in ["評估 Batch Size：未記載", "影像解析度：未記載", "計時範圍：未記載"]:
            if unrec not in s10_body:
                fail(f"Slide 10 missing explicit '{unrec}'")
        if "論文所列差值" in s10_body:
            ok("Slide 10 explicitly notes '論文所列差值' and marks missing test conditions as '未記載'")
        else:
            fail("Slide 10 missing '論文所列差值' note")

    if 14 in slides:
        s14_body = slides[14]["body"]
        if "非單一已訓練模型直接跨資料集測試的退化幅度" in s14_body and "僅涵蓋表中" in s14_body:
            ok("Slide 14 explicitly states 7-method average boundary and restricts conclusions to the 7 listed methods")
        else:
            fail("Slide 14 missing required interpretation boundary statement")

    if 15 in slides:
        s15_body = slides[15]["body"]
        if (
            "哪個方法值得優先測試？現有證據還缺哪些條件才能確認部署需求？" in s15_body
            and "不需訓練網路權重，但仍需擷取正常特徵、建立記憶庫並選取核心集" in s15_body
            and "不得從 A100 上的記憶體與 FPS 推論其他顯卡能達到的速度" in s15_body.replace("`", "")
        ):
            ok("Slide 15 scenario question and C15-03 follow strict candidate-testing & no-hardware-extrapolation framing")
        else:
            fail("Slide 15 missing updated scenario question or C15-03 framing")

    # 9. Check Layout Template in slides/_templates/
    log("\n[9] Layout Template Check (slides/_templates/)")
    tpl_dir = os.path.join(ROOT, "slides", "_templates")
    tpl_files = sorted(os.listdir(tpl_dir)) if os.path.isdir(tpl_dir) else []
    if tpl_files == ["template-2-top-figure.html"]:
        ok("slides/_templates/ contains only 'template-2-top-figure.html' (template-1 and template-3 removed)")
    else:
        fail(f"slides/_templates/ file list mismatch: got {tpl_files}, expected ['template-2-top-figure.html']")

    tpl2_path = os.path.join(tpl_dir, "template-2-top-figure.html")
    if os.path.isfile(tpl2_path):
        with open(tpl2_path, "r", encoding="utf-8") as f:
            tcontent = f.read()
        if "overflow: hidden" in tcontent or "overflow-x: hidden" in tcontent or "overflow-y: hidden" in tcontent:
            fail("template-2-top-figure.html uses overflow: hidden")
        else:
            ok("template-2-top-figure.html does NOT use overflow: hidden")

        q_positions = [tcontent.find(f"{i}. ") for i in range(1, 5)]
        if all(pos != -1 for pos in q_positions) and q_positions == sorted(q_positions):
            ok("template-2-top-figure.html orders the 4 question cards strictly as 1 -> 2 -> 3 -> 4")
        else:
            fail(f"template-2-top-figure.html question order invalid: {q_positions}")

        if "示範內容，尚未經正式草稿審查" in tcontent and "0.17 s" in tcontent and "PatchCore-25%" not in tcontent:
            ok("template-2-top-figure.html contains draft notice and cites Table 5 (0.17 s for PatchCore-1%) without PatchCore-25% time")
        else:
            fail("template-2-top-figure.html failed Table 5 or draft notice check")

    # Summary with 3-category claim counts
    total_claims = len(cell_checked_claims) + len(pending_ai_claims) + len(unchecked_claims)
    log("\n======================================================================")
    log(
        f"主張分類統計：已由程式核對儲存格 {len(cell_checked_claims)} 筆｜待 AI 審查（數字存在性已查、語意待 AI 審查） {len(pending_ai_claims)} 筆｜尚未檢查 {len(unchecked_claims)} 筆（總計 {total_claims} 筆）"
    )
    log(f"  - 已由程式核對儲存格（{len(cell_checked_claims)} 筆）：{', '.join(cell_checked_claims)}")
    log(
        f"  - 數字存在性已查、語意待 AI 審查（{len(pending_ai_claims)} 筆）：{', '.join(pending_ai_claims)}"
    )
    log(f"  - 尚未檢查（{len(unchecked_claims)} 筆）：{', '.join(unchecked_claims) if unchecked_claims else '無'}")

    if errors:
        log(f"OVERALL RESULT: FAILED ({len(errors)} error(s) found)")
        for e in errors:
            log(f"  - {e}")
    else:
        log("OVERALL RESULT: PASSED (0 errors)")
    log("======================================================================")

    report_content = "\n".join(lines_out) + "\n"
    if report_path:
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

    if verbose:
        print(report_content)

    return len(errors) == 0, report_content, errors


def main():
    outline_arg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTLINE_PATH
    report_arg = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_REPORT_PATH
    passed, _, _ = run_check(outline_arg, report_arg, verbose=True)
    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
