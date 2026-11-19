import re
import pypdf

pdf_path = r"c:\Users\User\Downloads\ad-wiki-slides\raw\papers\zhang2023-diffusionad.pdf"
md_path = r"c:\Users\User\Downloads\ad-wiki-slides\wiki\papers\zhang2023-diffusionad.md"

reader = pypdf.PdfReader(pdf_path)

def extract_page_with_bold(page_idx):
    chunks = []
    def visitor(text, cm, tm, fontDict, fontSize):
        if text and fontDict:
            bf = str(fontDict.get("/BaseFont", ""))
            is_bold = ("Medi" in bf or "Bold" in bf)
            chunks.append((is_bold, text))
        elif text:
            chunks.append((False, text))
    reader.pages[page_idx].extract_text(visitor_text=visitor)
    out = ""
    for is_b, t in chunks:
        if is_b and any(c.isdigit() for c in t):
            lead = len(t) - len(t.lstrip())
            trail = len(t) - len(t.rstrip())
            core = t.strip()
            out += t[:lead] + f"**{core}**" + (t[len(t)-trail:] if trail > 0 else "")
        else:
            out += t
    return out

def parse_pair_table(raw_text, table_header, categories):
    lines = raw_text.split("\n")
    start_idx = None
    for i, line in enumerate(lines):
        if table_header in line:
            start_idx = i
            break
    assert start_idx is not None, f"Could not find {table_header}"
    rows = []
    line_idx = start_idx + 1
    for cat in categories:
        while line_idx < len(lines):
            line = lines[line_idx].strip()
            line_idx += 1
            if line.startswith(cat):
                rest = line[len(cat):].strip()
                bold_state = False
                tokens = []
                i = 0
                cur_tok = ""
                cur_bold = False
                while i < len(rest):
                    if rest[i:i+2] == "**":
                        bold_state = not bold_state
                        i += 2
                        continue
                    ch = rest[i]
                    if ch.isdigit() or ch == ".":
                        if not cur_tok:
                            cur_bold = bold_state
                        cur_tok += ch
                    else:
                        if cur_tok:
                            tokens.append((cur_tok, cur_bold))
                            cur_tok = ""
                    i += 1
                if cur_tok:
                    tokens.append((cur_tok, cur_bold))
                assert len(tokens) == 16, f"Expected 16 numbers for {cat}, got {len(tokens)}: {tokens}"
                cells = []
                for m in range(8):
                    v1, b1 = tokens[2*m]
                    v2, b2 = tokens[2*m+1]
                    s1 = f"**{v1}**" if b1 else v1
                    s2 = f"**{v2}**" if b2 else v2
                    cells.append(f"{s1} / {s2}")
                rows.append((cat, cells, tokens))
                break
    assert len(rows) == len(categories), f"Missing rows in {table_header}"
    return rows

visa_cats = [
    "candle", "capsules", "cashew", "chewinggum", "fryum",
    "macaroni1", "macaroni2", "pcb1", "pcb2", "pcb3", "pcb4", "pipe fryum", "Average"
]
mvtec_cats = [
    "Carpet", "Grid", "Leather", "Tile", "Wood",
    "Bottle", "Cable", "Capsule", "Hazelnut", "Metal nut",
    "Pill", "Screw", "Toothbrush", "Transistor", "Zipper", "Average"
]

p7_text = extract_page_with_bold(6)
p8_text = extract_page_with_bold(7)
p9_text = extract_page_with_bold(8)

t1_rows = parse_pair_table(p7_text, "TABLE I:", visa_cats)
t2_rows = parse_pair_table(p8_text, "TABLE II:", visa_cats)
t3_rows = parse_pair_table(p8_text, "TABLE III:", mvtec_cats)
t4_rows = parse_pair_table(p9_text, "TABLE IV:", mvtec_cats)

def build_md_table(rows):
    header = "| Category | PatchCore [2] | RD4AD [7] | RD++ [8] | SimpleNet [4] | DMAD [12] | DRAEM [3] | FastFlow [26] | DiffusionAD (Ours) |"
    align = "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    lines = [header, align]
    for cat, cells, _ in rows:
        lines.append(f"| **{cat}** | " + " | ".join(cells) + " |")
    return "\n".join(lines)

sec_53_54 = f"""### 5.3 MVTec AD 15 類別詳細數據（出自論文 Table III & Table IV）

#### (A) MVTec AD 逐類異常檢測與定位：`Image AUROC / Pixel AUROC`（出自論文 Table III, p. 8，單位：%）

{build_md_table(t3_rows)}

#### (B) MVTec AD 逐類異常定位：`Pixel PRO / Pixel AP`（出自論文 Table IV, p. 9，單位：%）

{build_md_table(t4_rows)}

*(註：在極具挑戰的像素級精確率 `Pixel AP` 上，`DiffusionAD` 平均達 `76.1%`，領先特徵嵌入流派最佳方法 `RD++`（`60.8%`）達 `+15.3%`、領先生成模型流派最佳方法 `DRAEM`（`68.4%`）達 `+7.7%`；在 `Pixel PRO` 上亦領先 `DRAEM`（`92.1%`）達 `+3.6%`，出自論文 Sec. V-B, p. 7–9。)*

### 5.4 VisA 12 類別詳細數據（出自論文 Table I & Table II）

#### (A) VisA 逐類異常檢測與定位：`Image AUROC / Pixel PRO`（出自論文 Table I, p. 7，單位：%）

{build_md_table(t1_rows)}

#### (B) VisA 逐類異常定位：`Pixel AUROC / Pixel AP`（出自論文 Table II, p. 8，單位：%）

{build_md_table(t2_rows)}"""

with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

pattern_53_54 = re.compile(
    r"### 5\.3 MVTec AD 15 類別詳細數據（出自論文 Table III & Table IV）.*?### 5\.5 與其他擴散異常檢測方法之速度與精度對比（出自論文 Table VI）",
    re.DOTALL
)
assert pattern_53_54.search(content), "Could not find §5.3–§5.4 block in markdown"
content = pattern_53_54.sub(lambda m: sec_53_54 + "\n\n### 5.5 與其他擴散異常檢測方法之速度與精度對比（出自論文 Table VI）", content)

sec_56c = r"""#### (C) 加噪尺度（Noise Scale）與規範引導權重 $w$ 消融分析（出自論文 Sec. IV、Sec. V-A & Sec. V-C, Fig. 8–10）

- **推論雙加噪尺度設定（出自論文 Sec. IV-B & IV-C, p. 5–6；Sec. V-A, p. 7）**：
  - 總擴散步數 $T = 1000$ 與雙尺度分界點 $\tau = 300$（出自論文 Sec. V-A, p. 7）將時間步劃分為小尺度區間 $S = \{0, 1, \dots, \tau\}$ 與大尺度區間 $B = \{\tau + 1, \dots, T\}$，並於推論階段固定採樣小尺度 **$t_s = 200$** 與大尺度 **$t_b = 400$**（出自論文 Sec. IV-B & IV-C, p. 5–6）。
- **單尺度加噪強度對重建與檢測之影響（出自論文 Sec. V-C, p. 9–10, Fig. 8 & Fig. 9）**：
  - **對無異常重建品質之影響（Fig. 8）**：一步去噪隨加噪步數 $t$ 增大，直接預測難度提高、像素細節品質下降；然而修復較顯著的大面積異常需要較大的加噪尺度才能徹底擾動異常結構以獲得較佳語意品質。`NOD` 結合兩尺度優勢，使一步重建同時具備像素細節與語意正確性，逼近 $t = 400$ 逐步去噪的重建上限。
- **對異常檢測性能與速度之影響（Fig. 9）**：採用一步去噪時，不同加噪尺度 $t$ 的推論時間維持恆定；但當加噪步數過大（**$t \ge 500$**）時，由於單步重建品質下降，`Image AUROC` 隨之明顯下滑。相對地，逐步去噪（Iterative）與 `DDIM` 雖在不同加噪尺度 $t$ 下 `Image AUROC` 變化不大，但其推論耗時隨加噪步數 $t$ 增加而上升。
- **規範引導權重 $w$ 消融（出自論文 Sec. V-C, p. 10–11, Fig. 10）**：
  - Fig. 10 展示大尺度重建規範 $\hat{x}_{0_b}$ 如何透過引導尺度 $w \in \{1, 2, 3\}$ 調節最終無異常重建：隨著 $w$ 增大，引導重建結果越來越趨近於大尺度參考規範 $\hat{x}_{0_b}$。論文經驗上將 **$w$ 設為 `1`**（Empirically set to 1），以取得雙尺度重建的最佳融合效果（註：論文 Fig. 11–13 則為 `MVTec AD`、`VisA`、`DAGM` 與 `MPDD` 上的額外定性視覺化範例，出自論文 p. 8, 11）。"""

pattern_56c = re.compile(
    r"#### \(C\) .*?---\n\n## 6\. 論文限制",
    re.DOTALL
)
assert pattern_56c.search(content), "Could not find §5.6(C) block in markdown"
content = pattern_56c.sub(lambda m: sec_56c + "\n\n---\n\n## 6. 論文限制", content)

with open(md_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated wiki/papers/zhang2023-diffusionad.md!")
