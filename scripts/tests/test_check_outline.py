#!/usr/bin/env python3
"""
Mutation tests for scripts/check_outline.py.
Injects 9 deliberate errors into temporary copies of
slides/evolution-of-anomaly-detection/outline.md and verifies that
check_outline.py marks EVERY single mutation as FAIL.
Saves the report to slides/evolution-of-anomaly-detection/reports/outline-check-mutation-tests.txt.
"""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from check_outline import run_check  # noqa: E402

OUTLINE_PATH = ROOT / "slides" / "evolution-of-anomaly-detection" / "outline.md"
REPORT_OUT = (
    ROOT
    / "slides"
    / "evolution-of-anomaly-detection"
    / "reports"
    / "outline-check-mutation-tests.txt"
)


def replace_in_claim_row(text: str, claim_id: str, col_index: int, new_value: str) -> str:
    """
    Locate the Markdown table row starting with `| `<claim_id>` |` and replace
    column `col_index` (0-indexed: 0=ID, 1=內容, 2=方法, 3=資料集, 4=指標,
    5=數值與條件, 6=wiki 頁與段落, 7=原文位置, 8=分類) with `new_value`.
    """
    lines = text.splitlines()
    found = False
    for idx, line in enumerate(lines):
        if line.strip().startswith(f"| `{claim_id}`"):
            cells = line.split("|")
            target_idx = col_index + 1
            if target_idx >= len(cells) - 1:
                raise ValueError(f"Column index {col_index} out of range for {claim_id}")
            cells[target_idx] = f" {new_value} "
            lines[idx] = "|".join(cells)
            found = True
            break
    if not found:
        raise ValueError(f"Claim row {claim_id} not found in outline.md")
    return "\n".join(lines) + "\n"


def replace_substring_in_claim_row(text: str, claim_id: str, old_sub: str, new_sub: str) -> str:
    """Locate the Markdown table row starting with `| `<claim_id>` |` and replace `old_sub` with `new_sub`."""
    lines = text.splitlines()
    found = False
    for idx, line in enumerate(lines):
        if line.strip().startswith(f"| `{claim_id}`"):
            if old_sub not in line:
                raise ValueError(f"Substring '{old_sub}' not found in claim {claim_id}")
            lines[idx] = line.replace(old_sub, new_sub)
            found = True
            break
    if not found:
        raise ValueError(f"Claim row {claim_id} not found in outline.md")
    return "\n".join(lines) + "\n"


def main() -> int:
    original_text = OUTLINE_PATH.read_text(encoding="utf-8")

    # Baseline check: original outline must PASS
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_outline = Path(tmpdir) / "outline_baseline.md"
        tmp_report = Path(tmpdir) / "report_baseline.txt"
        tmp_outline.write_text(original_text, encoding="utf-8")
        baseline_passed, _, baseline_errors = run_check(
            outline_path=tmp_outline, report_path=tmp_report, verbose=False
        )

    mutations = [
        (
            "(a) 第 10 頁方法欄改為 RIAD",
            lambda txt: replace_in_claim_row(txt, "C10-01", 2, "RIAD"),
        ),
        (
            "(b) 第 10 頁資料集改為 MVTec AD 2",
            lambda txt: replace_in_claim_row(txt, "C10-01", 3, "MVTec AD 2"),
        ),
        (
            "(c) 第 10 頁指標欄改為 Accuracy",
            lambda txt: replace_in_claim_row(txt, "C10-01", 4, "Accuracy"),
        ),
        (
            "(d) 第 14 頁 PatchCore 的方法欄改為 LAMBDA",
            lambda txt: replace_in_claim_row(txt, "C14-01", 2, "LAMBDA"),
        ),
        (
            "(e) 第 14 頁來源改為不存在的 wiki 檔",
            lambda txt: replace_in_claim_row(
                txt,
                "C14-01",
                6,
                "`wiki/papers/nonexistent-paper.md` `### 5.2 跨資料集分割表現對比`",
            ),
        ),
        (
            "(f) 第 14 頁某個數值改掉 0.1 (92.7 -> 92.8)",
            lambda txt: replace_in_claim_row(
                txt, "C14-01", 5, "92.8 / 79.7 / 53.8"
            ),
        ),
        (
            "(g) C14-05 的數值欄 91.2 / 88.4 / 52.7 改成 88.4 / 91.2 / 52.7（位置對應測試）",
            lambda txt: replace_in_claim_row(
                txt, "C14-05", 5, "88.4 / 91.2 / 52.7"
            ),
        ),
        (
            "(h) C03-01 的 5,354 改成 5,345（待 AI 審查主張之千分位數字存在性測試）",
            lambda txt: replace_substring_in_claim_row(
                txt, "C03-01", "5,354", "5,345"
            ),
        ),
        (
            "(i) C11-02 的 8,004 改成 8,400（待 AI 審查主張之千分位數字存在性測試）",
            lambda txt: replace_substring_in_claim_row(
                txt, "C11-02", "8,004", "8,400"
            ),
        ),
    ]

    report_lines = []
    report_lines.append("=" * 76)
    report_lines.append("OUTLINE CHECKER MUTATION TEST REPORT")
    report_lines.append("Target Checker: scripts/check_outline.py")
    report_lines.append("Source Outline: slides/evolution-of-anomaly-detection/outline.md")
    report_lines.append("=" * 76)
    report_lines.append(
        f"[Baseline] Original unmodified outline.md: {'PASS (expected PASS)' if baseline_passed else 'FAIL (unexpected!)'}"
    )
    if not baseline_passed:
        for err in baseline_errors:
            report_lines.append(f"  - {err}")
    report_lines.append("-" * 76)

    all_mutations_caught = baseline_passed
    caught_count = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        for idx, (desc, mutator) in enumerate(mutations, start=1):
            mutated_text = mutator(original_text)
            assert mutated_text != original_text, f"Mutation {desc} did not change text!"
            tmp_outline = Path(tmpdir) / f"outline_mut_{idx}.md"
            tmp_report = Path(tmpdir) / f"report_mut_{idx}.txt"
            tmp_outline.write_text(mutated_text, encoding="utf-8")

            passed, _, errors = run_check(
                outline_path=tmp_outline, report_path=tmp_report, verbose=False
            )
            if not passed:
                caught_count += 1
                status_str = "Checker returned FAIL [EXPECTED -> TEST PASS]"
            else:
                all_mutations_caught = False
                status_str = "Checker returned PASS [UNEXPECTED -> TEST FAIL]"

            report_lines.append(f"Mutation {desc}")
            report_lines.append(f"  Result : {status_str}")
            report_lines.append(f"  Errors caught ({len(errors)}):")
            for err in errors:
                report_lines.append(f"    * {err}")
            report_lines.append("-" * 76)

    report_lines.append(
        f"SUMMARY: {caught_count}/{len(mutations)} injected mutations failed check_outline.py as required."
    )
    report_lines.append(
        f"OVERALL MUTATION TEST RESULT: {'PASSED (ALL ' + str(len(mutations)) + ' MUTATIONS CAUGHT AS FAIL)' if all_mutations_caught else 'FAILED'}"
    )
    report_lines.append("=" * 76)

    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    report_content = "\n".join(report_lines) + "\n"
    REPORT_OUT.write_text(report_content, encoding="utf-8")
    print(report_content)

    return 0 if all_mutations_caught else 1


if __name__ == "__main__":
    sys.exit(main())
