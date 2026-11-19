#!/usr/bin/env python3
"""
Gate ② Programmatic Checker for slides/evolution-of-anomaly-detection/drafts/01.md .. 16.md.
Enforces:
1. AGENTS.md §5 Slide Density Rules on '## 投影片內容':
   - Body character count <= 130 chars (after stripping Markdown syntax, link URLs, tables, formulas, and image/caption lines)
   - Key number count <= 3 (excluding numbers inside tables and fixed proper names MVTec AD 2, A100, AU-PRO0.05/0.30 prefix)
   - Figure count + Table count <= 1
   - If Table present: <= 4 data rows, <= 3 data columns (<= 4 total columns), and NO parenthetical diffs like (-4.0) or (+263.4%)
   - Formula count <= 1
2. Plain-language & Terminology Rules:
   - No colloquial/exaggerated terms ('顯存', '暴增')
3. Every number appearing in the draft's visible body text and visible table MUST correspond to at least one claim in that slide's '## 主張記錄表'.
4. Full Claim Verification (reusing check_outline.py):
   - Per-claim wiki file & section heading existence
   - Table cell lookup & strict positional correspondence for table-backed claims
   - Section-scoped number existence check for '數字存在性已查、語意待 AI 審查' claims
   - '（AI 整理）' marker check for AI-inferred claims
   - Relative link & #anchor existence check across the draft
"""

import argparse
import json
import os
import re
import sys
import urllib.parse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from check_outline import (  # noqa: E402
    CLAIM_HEADERS,
    METHOD_QUESTIONS,
    METHOD_SLIDES,
    NUM_TOKEN_RE,
    REQUIRED_SLIDE_TITLES,
    TABLE_BACKED_CLAIMS,
    VALID_CLAIM_TYPES,
    clean_md_cell,
    extract_wiki_section,
    load_wiki_file,
    parse_markdown_tables,
    verify_claim_against_table,
    verify_pending_ai_claim_numbers,
)

DRAFTS_DIR = os.path.join(ROOT, "slides", "evolution-of-anomaly-detection", "drafts")
OUTLINE_PATH = os.path.join(ROOT, "slides", "evolution-of-anomaly-detection", "outline.md")
REPORT_DIR = os.path.join(ROOT, "slides", "evolution-of-anomaly-detection", "reports")
DEFAULT_REPORT_PATH = os.path.join(REPORT_DIR, "drafts-check.txt")
REWRITE_LOG_PATH = os.path.join(REPORT_DIR, "drafts-rewrites.json")

FORBIDDEN_TERMS = ["顯存", "暴增"]
WIKI_REF_PATTERN = re.compile(r"`(wiki/[a-z0-9\-/]+\.md)`\s*`(##+ [^`]+)`")


def github_slug(heading_line: str) -> str:
    """Convert a Markdown heading line ('## 4. 方法架構...') into a GitHub-compatible anchor slug."""
    h = re.sub(r"^#+\s*", "", heading_line.strip())
    # Remove backticks and LaTeX command backslashes
    h = h.replace("`", "")
    h = h.lower()
    # Keep alphanumeric, CJK characters, spaces, hyphens, and underscores; drop punctuation
    cleaned = []
    for ch in h:
        if ch.isalnum() or "\u4e00" <= ch <= "\u9fff" or ch in ("-", "_"):
            cleaned.append(ch)
        elif ch == " ":
            cleaned.append("-")
        # other punctuation (., (), （）, /, ：, $, \, {, }, &, etc.) is dropped
    return "".join(cleaned).strip("-")


def get_valid_anchors(md_full_path: str) -> set[str]:
    if not os.path.isfile(md_full_path):
        return set()
    with open(md_full_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    slugs = set()
    for ln in lines:
        if ln.startswith("#"):
            slugs.add(github_slug(ln))
    return slugs


def load_outline_claim_ids() -> dict[int, list[str]]:
    """Return {slide_num: [claim_id, ...]} from outline.md."""
    if not os.path.isfile(OUTLINE_PATH):
        return {}
    text = open(OUTLINE_PATH, "r", encoding="utf-8").read()
    slide_pattern = re.compile(r"^## 第 (\d+) 頁：(.+)$", re.MULTILINE)
    matches = list(slide_pattern.finditer(text))
    out = {}
    for idx, m in enumerate(matches):
        p = int(m.group(1))
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end]
        cids = re.findall(r"^\|\s*`(C\d{2}-\d{2})`", body, re.MULTILINE)
        out[p] = cids
    return out


def extract_section(md_text: str, section_heading: str) -> str | None:
    """Extract content under `## <section_heading>` until the next `## ` heading."""
    pattern = re.compile(
        rf"^##\s+{re.escape(section_heading)}\s*\n(.*?)(?=\n##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(md_text)
    return m.group(1).strip() if m else None


def compute_slide_density_and_numbers(slide_content: str):
    """
    Analyze `## 投影片內容` and return:
    - body_chars: int (character count after stripping Markdown symbols, link URLs, tables, formulas, and image/caption lines)
    - cleaned_body_text: str
    - key_numbers: list[str]
    - all_prose_numbers: list[str]
    - table_numbers: list[str]
    - figure_count: int
    - figures: list[tuple[str, str]]
    - table_count: int
    - table_info: list[dict] (rows, data_cols, has_paren_diff)
    - formula_count: int
    """
    work = slide_content

    # 1. Count and remove display formulas $$...$$
    disp_formulas = re.findall(r"\$\$.*?\$\$", work, flags=re.DOTALL)
    formula_count = len(disp_formulas)
    work = re.sub(r"\$\$.*?\$\$", "", work, flags=re.DOTALL)

    # 2. Extract and remove Markdown image lines and figure caption lines
    figures = []
    remaining_lines = []
    for ln in work.splitlines():
        s = ln.strip()
        img_m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", s)
        if img_m:
            figures.append((img_m.group(1), img_m.group(2)))
            continue
        if re.match(r"^\*示意圖，依論文 Fig\.[^*]+\*$", s):
            continue
        remaining_lines.append(ln)
    figure_count = len(figures)
    work_no_fig = "\n".join(remaining_lines)

    # 3. Parse and remove Markdown tables
    tables = parse_markdown_tables(work_no_fig)
    table_count = len(tables)
    table_info = []
    table_numbers = []
    for tbl in tables:
        n_rows = len(tbl["rows"])
        n_data_cols = max(0, len(tbl["headers"]) - 1)
        paren_diffs = []
        for r in tbl["rows"]:
            for cell in r["clean"][1:]:
                if re.search(r"\([+-]?\d+(?:\.\d+)?%?\)", cell):
                    paren_diffs.append(cell)
                table_numbers.extend(NUM_TOKEN_RE.findall(cell))
        table_info.append(
            {
                "rows": n_rows,
                "data_cols": n_data_cols,
                "total_cols": len(tbl["headers"]),
                "paren_diffs": paren_diffs,
            }
        )

    prose_lines = [ln for ln in work_no_fig.splitlines() if not ln.strip().startswith("|")]
    prose_text = "\n".join(prose_lines)

    # Remove inline math $...$ and \(...\)
    prose_no_math = re.sub(r"\$[^$\n]+\$", "", prose_text)
    prose_no_math = re.sub(r"\\\([^)]+\\\)", "", prose_no_math)

    # Replace Markdown links [text](url) with text
    prose_no_links = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", prose_no_math)

    # Extract ALL numbers appearing in the prose text (for claim backing verification)
    all_prose_numbers = NUM_TOKEN_RE.findall(prose_no_links)

    # Extract KEY numbers (masking out proper names MVTec AD 2, NVIDIA A100 / A100, and metric name prefixes AU-PRO0.05 / AU-PRO0.30)
    prose_for_key_nums = prose_no_links
    prose_for_key_nums = re.sub(r"MVTec\s+AD\s+2", "MVTec AD", prose_for_key_nums)
    prose_for_key_nums = re.sub(r"\bA100\b", "GPU", prose_for_key_nums)
    prose_for_key_nums = re.sub(r"AU-PRO_?\{?0\.(?:05|30)\}?", "AU-PRO", prose_for_key_nums)
    key_numbers = NUM_TOKEN_RE.findall(prose_for_key_nums)

    # Clean Markdown formatting for character count
    lines_cleaned = []
    for ln in prose_no_links.splitlines():
        # Strip leading bullet or ordered list markers
        ln_c = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", ln)
        lines_cleaned.append(ln_c)
    text_for_count = "".join(lines_cleaned)
    # Remove Markdown syntax symbols (*, `, #, >, whitespace)
    for sym in ["**", "*", "`", "#", ">", "\n", "\r", "\t", " "]:
        text_for_count = text_for_count.replace(sym, "")
    body_chars = len(text_for_count)

    return {
        "body_chars": body_chars,
        "cleaned_body_text": text_for_count,
        "key_numbers": key_numbers,
        "all_prose_numbers": all_prose_numbers,
        "table_numbers": table_numbers,
        "figure_count": figure_count,
        "figures": figures,
        "table_count": table_count,
        "table_info": table_info,
        "formula_count": formula_count,
    }


def check_single_draft(page_num: int, outline_claim_ids: dict[int, list[str]]):
    """
    Validate `slides/evolution-of-anomaly-detection/drafts/{page_num:02d}.md`.
    Returns dict with `passed`, `errors`, `stats`, `cell_checked`, `pending_ai`, `unchecked`.
    """
    draft_path = os.path.join(DRAFTS_DIR, f"{page_num:02d}.md")
    errors = []
    cell_checked = []
    pending_ai = []
    unchecked = []

    if not os.path.isfile(draft_path):
        return {
            "page": page_num,
            "passed": False,
            "errors": [f"Draft file not found: {draft_path}"],
            "stats": None,
            "cell_checked": [],
            "pending_ai": [],
            "unchecked": [],
        }

    text = open(draft_path, "r", encoding="utf-8").read()

    # 1. Check Title
    expected_title = REQUIRED_SLIDE_TITLES.get(page_num, "")
    title_m = re.search(r"^#\s+第\s*(\d+)\s*頁：(.+)$", text, re.MULTILINE)
    if not title_m:
        errors.append(f"Slide {page_num:02d}: missing top-level heading '# 第 {page_num} 頁：<標題>'")
    else:
        got_num = int(title_m.group(1))
        got_title = title_m.group(2).strip()
        if got_num != page_num or got_title != expected_title:
            errors.append(
                f"Slide {page_num:02d}: heading mismatch: got '第 {got_num} 頁：{got_title}', expected '第 {page_num} 頁：{expected_title}'"
            )

    # 2. Check forbidden colloquial/exaggerated terms
    for bad_term in FORBIDDEN_TERMS:
        if bad_term in text:
            errors.append(
                f"Slide {page_num:02d}: contains forbidden colloquial/exaggerated term '{bad_term}' (use 'GPU 記憶體' / '增加' instead)"
            )

    # 3. Check required sections exist
    lo_sec = extract_section(text, "學習目標")
    if not lo_sec or len(lo_sec.strip()) < 10:
        errors.append(f"Slide {page_num:02d}: missing or too short '## 學習目標'")

    slide_sec = extract_section(text, "投影片內容")
    if not slide_sec:
        errors.append(f"Slide {page_num:02d}: missing '## 投影片內容'")
        return {
            "page": page_num,
            "passed": False,
            "errors": errors,
            "stats": None,
            "cell_checked": [],
            "pending_ai": [],
            "unchecked": [],
        }

    further_sec = extract_section(text, "延伸閱讀")
    if not further_sec:
        errors.append(f"Slide {page_num:02d}: missing '## 延伸閱讀'")

    claim_sec = extract_section(text, "主張記錄表")
    if not claim_sec:
        errors.append(f"Slide {page_num:02d}: missing '## 主張記錄表'")

    # 4. Compute density metrics on ## 投影片內容
    stats = compute_slide_density_and_numbers(slide_sec)

    if stats["body_chars"] > 130:
        errors.append(
            f"Slide {page_num:02d}: body character count = {stats['body_chars']} (exceeds 130-char limit)"
        )

    if len(stats["key_numbers"]) > 3:
        errors.append(
            f"Slide {page_num:02d}: key number count = {len(stats['key_numbers'])} {stats['key_numbers']} (exceeds 3-number limit)"
        )

    if stats["figure_count"] + stats["table_count"] > 1:
        errors.append(
            f"Slide {page_num:02d}: has {stats['figure_count']} figure(s) and {stats['table_count']} table(s) in '## 投影片內容' (at most 1 figure OR 1 small table allowed)"
        )

    if stats["formula_count"] > 1:
        errors.append(
            f"Slide {page_num:02d}: has {stats['formula_count']} display formulas in '## 投影片內容' (at most 1 allowed)"
        )

    # Check figure file existence and caption
    for alt, url in stats["figures"]:
        img_full = os.path.normpath(os.path.join(DRAFTS_DIR, url))
        if not os.path.isfile(img_full):
            errors.append(f"Slide {page_num:02d}: figure file does not exist: {url}")
        if not re.search(r"\*示意圖，依論文 Fig\.[^*]+\*", slide_sec):
            errors.append(f"Slide {page_num:02d}: figure missing '*示意圖，依論文 Fig. X 重繪*' caption")

    # Check table rows, columns, and absence of parenthetical diffs
    for tinfo in stats["table_info"]:
        if tinfo["rows"] > 4:
            errors.append(f"Slide {page_num:02d}: visible table has {tinfo['rows']} data rows (max 4 allowed)")
        if tinfo["data_cols"] > 3:
            errors.append(
                f"Slide {page_num:02d}: visible table has {tinfo['data_cols']} metric/data columns (max 3 allowed)"
            )
        if tinfo["paren_diffs"]:
            errors.append(
                f"Slide {page_num:02d}: visible table contains parenthetical diff(s) {tinfo['paren_diffs']} (must not put parenthetical diffs on slide)"
            )

    # 5. Method slides (5, 6, 8, 9) must include the 4 standardized questions in ## 投影片內容
    if page_num in METHOD_SLIDES:
        missing_q = [q for q in METHOD_QUESTIONS if q not in slide_sec]
        if missing_q:
            errors.append(f"Slide {page_num:02d}: method slide missing required question(s): {missing_q}")

    # 6. Check all Markdown links & #anchors in the draft
    for label, raw_url in re.findall(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", text):
        if raw_url.startswith(("http://", "https://", "/")):
            errors.append(f"Slide {page_num:02d}: non-relative link '{raw_url}' in [{label}]")
            continue
        if "#" in raw_url:
            rel_file, anchor = raw_url.split("#", 1)
            anchor = urllib.parse.unquote(anchor)
        else:
            rel_file, anchor = raw_url, None
        target_full = os.path.normpath(os.path.join(DRAFTS_DIR, rel_file))
        if not os.path.isfile(target_full):
            errors.append(f"Slide {page_num:02d}: broken relative link '{raw_url}' (file not found)")
            continue
        if anchor and target_full.endswith(".md"):
            valid_slugs = get_valid_anchors(target_full)
            if anchor.lower() not in valid_slugs:
                errors.append(
                    f"Slide {page_num:02d}: broken link anchor '#{anchor}' in '{raw_url}' (valid slugs: {sorted(valid_slugs)})"
                )

    # 7. Parse and verify '## 主張記錄表'
    claim_numbers_pool = set()
    draft_claim_ids = []
    if claim_sec:
        tlines = [ln.strip() for ln in claim_sec.splitlines() if ln.strip().startswith("|")]
        if len(tlines) < 3:
            errors.append(f"Slide {page_num:02d}: claim table has no data rows")
        else:
            headers = [c.strip() for c in tlines[0].strip("|").split("|")]
            if headers != CLAIM_HEADERS:
                errors.append(f"Slide {page_num:02d}: claim table headers mismatch: {headers}")
            for rline in tlines[2:]:
                cols = [c.strip() for c in rline.strip("|").split("|")]
                if len(cols) != 9:
                    errors.append(f"Slide {page_num:02d}: claim row has {len(cols)} cols (expected 9): {rline}")
                    unchecked.append(rline)
                    continue
                cid, content, method, dataset, metric, val_cond, wiki_src, raw_loc, ctype = cols
                cid_clean = cid.strip("`")
                draft_claim_ids.append(cid_clean)

                # Add all numbers from this claim's content, method, dataset, metric, and val_cond to the slide's claim_numbers_pool
                for field_txt in (content, method, dataset, metric, val_cond):
                    for n_tok in NUM_TOKEN_RE.findall(field_txt):
                        claim_numbers_pool.add(n_tok)

                if ctype not in VALID_CLAIM_TYPES:
                    errors.append(f"Slide {page_num:02d} claim {cid_clean}: invalid claim type '{ctype}'")
                if ctype == "AI 推論" and "（AI 整理）" not in content and "（AI 整理）" not in wiki_src:
                    errors.append(f"Slide {page_num:02d} claim {cid_clean}: AI 推論 missing '（AI 整理）'")

                claim_wiki_refs = WIKI_REF_PATTERN.findall(wiki_src)
                if not claim_wiki_refs:
                    errors.append(
                        f"Slide {page_num:02d} claim {cid_clean}: 'wiki 頁與段落' has no valid '`wiki/...` `## ...`' reference"
                    )
                    unchecked.append(cid_clean)
                    continue

                claim_sections = []
                ref_err = False
                for wpath, wsec in claim_wiki_refs:
                    wtext, _ = load_wiki_file(wpath)
                    if wtext is None:
                        errors.append(
                            f"Slide {page_num:02d} claim {cid_clean}: references non-existent file '{wpath}'"
                        )
                        ref_err = True
                        continue
                    matched_h, sec_text = extract_wiki_section(wtext, wsec)
                    if matched_h is None:
                        errors.append(
                            f"Slide {page_num:02d} claim {cid_clean}: references non-existent heading '{wsec}' in '{wpath}'"
                        )
                        ref_err = True
                        continue
                    claim_sections.append((wpath, matched_h, sec_text))

                if ref_err:
                    unchecked.append(cid_clean)
                    continue

                claim_obj = {
                    "id": cid_clean,
                    "slide": page_num,
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
                    or (page_num == 10 and cid_clean != "C10-05")
                    or page_num == 14
                )

                if is_table_claim:
                    passed_tbl, tbl_msg = verify_claim_against_table(
                        claim_obj, claim_wiki_refs, claim_sections
                    )
                    if passed_tbl:
                        cell_checked.append(cid_clean)
                    else:
                        errors.append(f"Slide {page_num:02d} {tbl_msg}")
                else:
                    passed_num, num_msg = verify_pending_ai_claim_numbers(claim_obj, claim_sections)
                    if passed_num:
                        pending_ai.append(cid_clean)
                    else:
                        errors.append(f"Slide {page_num:02d} {num_msg}")

    # Check claim IDs match outline.md for this page
    expected_cids = outline_claim_ids.get(page_num, [])
    if expected_cids and draft_claim_ids != expected_cids:
        errors.append(
            f"Slide {page_num:02d}: claim IDs {draft_claim_ids} do not match outline.md claim IDs {expected_cids}"
        )

    # 8. Verify EVERY number in the draft's visible body text and visible table is backed by this slide's claim table
    unbacked_prose_nums = [n for n in stats["all_prose_numbers"] if n not in claim_numbers_pool]
    if unbacked_prose_nums:
        errors.append(
            f"Slide {page_num:02d}: number(s) {unbacked_prose_nums} in draft body text do not correspond to any claim in '## 主張記錄表' (pool: {sorted(claim_numbers_pool)})"
        )

    unbacked_table_nums = [n for n in stats["table_numbers"] if n not in claim_numbers_pool]
    if unbacked_table_nums:
        errors.append(
            f"Slide {page_num:02d}: number(s) {unbacked_table_nums} in draft visible table do not correspond to any claim in '## 主張記錄表'"
        )

    return {
        "page": page_num,
        "passed": len(errors) == 0,
        "errors": errors,
        "stats": stats,
        "cell_checked": cell_checked,
        "pending_ai": pending_ai,
        "unchecked": unchecked,
    }


def load_rewrite_log() -> dict[str, dict]:
    if os.path.isfile(REWRITE_LOG_PATH):
        try:
            with open(REWRITE_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def main():
    parser = argparse.ArgumentParser(description="Gate ② Drafts Checker")
    parser.add_argument("--page", type=int, help="Check a single slide draft (1..16)")
    parser.add_argument("--report", default=DEFAULT_REPORT_PATH, help="Output report path")
    args = parser.parse_args()

    outline_claim_ids = load_outline_claim_ids()
    rewrite_log = load_rewrite_log()

    if args.page is not None:
        res = check_single_draft(args.page, outline_claim_ids)
        st = res["stats"]
        if res["passed"]:
            print(
                f"[PASS] draft {args.page:02d}.md | 字數={st['body_chars']}/130 | 關鍵數字={len(st['key_numbers'])}/3 {st['key_numbers']} | 圖={st['figure_count']} | 表={st['table_count']} | 公式={st['formula_count']} | 儲存格核對={len(res['cell_checked'])} | 數字存在性已查、語意待AI審查={len(res['pending_ai'])}"
            )
            sys.exit(0)
        else:
            print(f"[FAIL] draft {args.page:02d}.md:")
            for err in res["errors"]:
                print(f"  - {err}")
            sys.exit(1)

    # Full check across 01.md .. 16.md
    report_lines = []
    report_lines.append("=" * 88)
    report_lines.append("Gate ② Drafts Programmatic Check Report: slides/evolution-of-anomaly-detection/drafts/")
    report_lines.append("=" * 88)
    report_lines.append("")
    report_lines.append(
        "頁碼 | 標題 | 正文字數 (<=130) | 關鍵數字個數 (<=3) | 圖/表/公式 | 重寫次數與原因 | 主張統計（儲存格/待AI/未查） | 狀態"
    )
    report_lines.append("-" * 88)

    all_errors = []
    all_cell_checked = []
    all_pending_ai = []
    all_unchecked = []

    for p in range(1, 17):
        res = check_single_draft(p, outline_claim_ids)
        st = res["stats"]
        all_cell_checked.extend(res["cell_checked"])
        all_pending_ai.extend(res["pending_ai"])
        all_unchecked.extend(res["unchecked"])

        rw_info = rewrite_log.get(f"{p:02d}", {"count": 0, "reasons": []})
        rw_count = rw_info.get("count", 0)
        rw_reasons = "；".join(rw_info.get("reasons", [])) if rw_count > 0 else "無"
        rw_str = f"{rw_count} 次（{rw_reasons}）" if rw_count > 0 else "0 次（一次通過）"

        title = REQUIRED_SLIDE_TITLES.get(p, "")
        if st:
            chars_str = f"{st['body_chars']} 字"
            knums_str = f"{len(st['key_numbers'])} 個 {st['key_numbers']}"
            media_str = f"圖{st['figure_count']}/表{st['table_count']}/式{st['formula_count']}"
        else:
            chars_str = "N/A"
            knums_str = "N/A"
            media_str = "N/A"

        claim_str = f"{len(res['cell_checked'])} / {len(res['pending_ai'])} / {len(res['unchecked'])}"
        status_str = "PASS" if res["passed"] else "FAIL"

        report_lines.append(
            f"{p:02d} | {title} | {chars_str} | {knums_str} | {media_str} | {rw_str} | {claim_str} | {status_str}"
        )
        if not res["passed"]:
            all_errors.extend(res["errors"])
            for err in res["errors"]:
                report_lines.append(f"   [FAIL] {err}")

    total_claims = len(all_cell_checked) + len(all_pending_ai) + len(all_unchecked)
    report_lines.append("-" * 88)
    report_lines.append(
        f"三類主張總計（共 {total_claims} 筆）：已由程式核對儲存格 {len(all_cell_checked)} 筆｜數字存在性已查、語意待 AI 審查 {len(all_pending_ai)} 筆｜尚未檢查 {len(all_unchecked)} 筆"
    )
    report_lines.append(f"  - 已由程式核對儲存格（{len(all_cell_checked)} 筆）：{', '.join(all_cell_checked)}")
    report_lines.append(
        f"  - 數字存在性已查、語意待 AI 審查（{len(all_pending_ai)} 筆）：{', '.join(all_pending_ai)}"
    )
    report_lines.append(
        f"  - 尚未檢查（{len(all_unchecked)} 筆）：{', '.join(all_unchecked) if all_unchecked else '無'}"
    )

    if all_errors:
        report_lines.append(f"OVERALL RESULT: FAILED ({len(all_errors)} error(s) found)")
    else:
        report_lines.append("OVERALL RESULT: PASSED (All 16 drafts passed density, number-backing, link/anchor, and claim checks)")
    report_lines.append("=" * 88)

    report_content = "\n".join(report_lines) + "\n"
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(report_content)
    sys.exit(0 if not all_errors else 1)


if __name__ == "__main__":
    main()
