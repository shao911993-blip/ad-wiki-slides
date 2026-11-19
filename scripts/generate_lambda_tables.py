import re
import pypdf

pdf_path = r"c:\Users\User\Downloads\ad-wiki-slides\raw\papers\lee2026-lambda.pdf"
md_path = r"c:\Users\User\Downloads\ad-wiki-slides\wiki\papers\lee2026-lambda.md"

reader = pypdf.PdfReader(pdf_path)

def extract_page_with_bold(page_idx):
    chunks = []
    def visitor(text, cm, tm, fontDict, fontSize):
        if text and fontDict:
            bf = str(fontDict.get("/BaseFont", ""))
            is_bold = ("Bold" in bf or "Medi" in bf)
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

def tokenize_numbers_with_bold(line_rest):
    bold_state = False
    tokens = []
    i = 0
    cur_tok = ""
    cur_bold = False
    while i < len(line_rest):
        if line_rest[i:i+2] == "**":
            bold_state = not bold_state
            i += 2
            continue
        ch = line_rest[i]
        if ch.isdigit() or ch == ".":
            if not cur_tok:
                cur_bold = bold_state
            cur_tok += ch
        elif ch == " " and cur_tok and cur_tok.endswith("."):
            # Handle occasional PDF kerning space around decimal point like "98 .2"
            pass
        else:
            # Check if next char is "." after space like "98 .2"
            if ch == " " and cur_tok and i + 1 < len(line_rest) and line_rest[i+1] == ".":
                i += 1
                continue
            if cur_tok:
                tokens.append((cur_tok, cur_bold))
                cur_tok = ""
        i += 1
    if cur_tok:
        tokens.append((cur_tok, cur_bold))
    return tokens

def fmt_tok(tok_tuple):
    val, is_b = tok_tuple
    return f"**{val}**" if is_b else val

def parse_table1(page_text):
    models = ["DiffusionAD", "DRAEM", "DDAD", "D3AD", "LAMBDA", "LAMBDA w/o  VAE"]
    lines = page_text.split("\n")
    start_idx = next(i for i, l in enumerate(lines) if "Table" in l and "1" in l)
    rows = []
    idx = start_idx + 1
    for m in models:
        while idx < len(lines):
            line = lines[idx].strip()
            idx += 1
            if line.startswith(m):
                rest = line[len(m):].strip()
                toks = tokenize_numbers_with_bold(rest)
                # Expected 13 numeric tokens:
                # 0..5: I-AUROC, I-AP, P-AUROC, P-AP, P-AUPRO, mAD
                # 6, 7: GPU Train, GPU Eval
                # 8, 9: FPS Train, FPS Eval
                # 10: Latency
                # 11, 12: Train hours, Train mins
                assert len(toks) == 13, f"Table 1 {m}: expected 13 tokens, got {len(toks)}: {toks}"
                m_disp = m.replace("  ", " ")
                c_det = [fmt_tok(toks[k]) for k in range(6)]
                gpu_tr = f"{fmt_tok(toks[6])} GB"
                gpu_ev = f"{fmt_tok(toks[7])} GB"
                fps_tr = fmt_tok(toks[8])
                fps_ev = fmt_tok(toks[9])
                lat = f"{fmt_tok(toks[10])} ms"
                if toks[11][1] and toks[12][1]:
                    tr_time = f"**{toks[11][0]}h {toks[12][0]}m**"
                else:
                    tr_time = f"{toks[11][0]}h {toks[12][0]}m"
                rows.append((m_disp, c_det + [gpu_tr, gpu_ev, fps_tr, fps_ev, lat, tr_time]))
                break
    assert len(rows) == len(models)
    return rows

def parse_simple_metric_table(page_text, header_marker, row_keys, num_cols):
    lines = page_text.split("\n")
    start_idx = next(i for i, l in enumerate(lines) if header_marker in l)
    rows = []
    idx = start_idx + 1
    for rk in row_keys:
        while idx < len(lines):
            line = lines[idx].strip()
            idx += 1
            clean_line = line.replace("**", "")
            if clean_line.startswith(rk + " "):
                # Find where rk ends in original line by consuming len(rk) non-* chars
                pos = 0
                matched = 0
                while pos < len(line) and matched < len(rk):
                    if line[pos:pos+2] == "**":
                        pos += 2
                    else:
                        pos += 1
                        matched += 1
                while pos < len(line) and line[pos:pos+2] == "**":
                    pos += 2
                rest = line[pos:].strip()
                toks = tokenize_numbers_with_bold(rest)
                assert len(toks) == num_cols, f"{header_marker} {rk}: expected {num_cols}, got {len(toks)}: {toks}"
                cells = [fmt_tok(t) for t in toks]
                rows.append((rk, cells))
                break
    assert len(rows) == len(row_keys)
    return rows

def parse_table3_wilcoxon(page_text):
    lines = page_text.split("\n")
    start_idx = next(i for i, l in enumerate(lines) if "Table **3**" in l or "Table 3" in l)
    end_idx = next(i for i in range(start_idx, len(lines)) if "Statistically significant" in lines[i])
    block = " ".join(l.strip() for l in lines[start_idx:end_idx])
    comparisons = [
        "LAMBDA vs.  DiffusionAD",
        "LAMBDA vs.  DRAEM",
        "LAMBDA vs.  DDAD",
        "LAMBDA vs.  D3AD",
    ]
    rows = []
    for idx_c, comp in enumerate(comparisons):
        pos = block.index(comp) + len(comp)
        next_pos = block.index(comparisons[idx_c + 1]) if idx_c + 1 < len(comparisons) else len(block)
        seg = block[pos:next_pos].strip()
        pairs = re.findall(r"(\d+\.\d+)\s*(\*)?", seg)
        assert len(pairs) == 2, f"Table 3 {comp}: got {pairs} in {seg}"
        c1 = pairs[0][0] + pairs[0][1]
        c2 = pairs[1][0] + pairs[1][1]
        rows.append((comp.replace("  ", " "), [c1, c2]))
    assert len(rows) == 4
    return rows

def parse_appendix_5tuple_table(page_text, header_marker, categories, num_groups):
    lines = page_text.split("\n")
    start_idx = next(i for i, l in enumerate(lines) if header_marker in l)
    rows = []
    idx = start_idx + 1
    for cat in categories:
        while idx < len(lines):
            line = lines[idx].strip()
            idx += 1
            if line.startswith(cat + " "):
                rest = line[len(cat):].strip()
                toks = tokenize_numbers_with_bold(rest)
                expected = num_groups * 5
                assert len(toks) == expected, f"{header_marker} {cat}: expected {expected}, got {len(toks)}: {toks}"
                cells = []
                for g in range(num_groups):
                    base = g * 5
                    s_img = f"{fmt_tok(toks[base])}/{fmt_tok(toks[base+1])}"
                    s_pix = f"{fmt_tok(toks[base+2])}/{fmt_tok(toks[base+3])}/{fmt_tok(toks[base+4])}"
                    cells.append(f"{s_img} {s_pix}")
                rows.append((cat, cells, toks))
                break
    assert len(rows) == len(categories), f"Missing categories in {header_marker}"
    return rows

p8_text = extract_page_with_bold(7)
p9_text = extract_page_with_bold(8)
p10_text = extract_page_with_bold(9)
p13_text = extract_page_with_bold(12)
p14_text = extract_page_with_bold(13)

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

t1_rows = parse_table1(p8_text)
t2_rows = parse_simple_metric_table(p9_text, "Table **2**", ["DiffusionAD", "DRAEM", "DDAD", "D3AD", "LAMBDA"], 6)
t3_rows = parse_table3_wilcoxon(p9_text)
t5_rows = parse_simple_metric_table(p10_text, "Table **5**", ["50", "100", "150", "200", "250"], 6)
t6_rows = parse_simple_metric_table(p10_text, "Table **6**", ["0.1", "0.2", "0.5", "1 (Ours)", "2", "5", "10"], 6)

ta1_rows = parse_appendix_5tuple_table(p13_text, "Table **A.1**", visa_cats, 5)
ta2_rows = parse_appendix_5tuple_table(p13_text, "Table **A.2**", mvtec_cats, 5)
ta3_rows = parse_appendix_5tuple_table(p13_text, "Table **A.3**", bmad_cats, 5)
ta4_rows = parse_appendix_5tuple_table(p13_text, "Table **A.4**", visa_cats, 4)
ta5_rows = parse_appendix_5tuple_table(p14_text, "Table **A.5**", mvtec_cats, 5)
ta6_rows = parse_appendix_5tuple_table(p14_text, "Table **A.6**", mvtec_cats, 7)

def build_md_table(headers, rows):
    h_line = "| " + " | ".join(headers) + " |"
    a_line = "| :--- | " + " | ".join([":---:"] * (len(headers) - 1)) + " |"
    out = [h_line, a_line]
    for r_tuple in rows:
        rk, cells = r_tuple[0], r_tuple[1]
        out.append(f"| **{rk}** | " + " | ".join(cells) + " |")
    return "\n".join(out)

t1_md = build_md_table(
    ["Model", "Image AUROC", "Image AP", "Pixel AUROC", "Pixel AP", "Pixel AUPRO", "mAD", "GPU Mem (Train)", "GPU Mem (Eval)", "FPS (Train)", "FPS (Eval)", "Detection Latency", "Training Time"],
    t1_rows
)

t2_md = build_md_table(
    ["Model", "Image AUROC", "Image AP", "Pixel AUROC", "Pixel AP", "Pixel AUPRO", "mAD"],
    t2_rows
)

t3_md = build_md_table(
    ["Method Comparison", "Pixel AUROC p-value", "Pixel AP p-value"],
    t3_rows
)

# Table 4 on page 10 is embedded as a vector figure (/Fo0) in the PDF, while its 5 detection metrics match Table A.4 Average row.
t4_rows = [
    ("Ours", ["98.1", "98.1", "98.6", "50.2", "94.2", "87.8", "**9.3 GB**", "**5.8 GB**", "25.3", "42.3"]),
    ("w/o GSM", ["95.5 (-2.6)", "96.3 (-1.8)", "96.4 (-2.2)", "44.5 (-5.7)", "90.2 (-4.0)", "84.6 (-3.2)", "**9.3 GB** (+0.0%)", "**5.8 GB** (+0.0%)", "**25.5** (+0.7%)", "**42.4** (+0.2%)"]),
    ("w/o MBG", ["95.0 (-3.1)", "95.3 (-2.8)", "97.4 (-1.2)", "47.0 (-3.2)", "92.5 (-1.7)", "85.4 (-2.4)", "11.2 GB (+20.4%)", "**5.8 GB** (+0.0%)", "18.8 (-25.7%)", "32.7 (-22.7%)"]),
    ("w/o VAE", ["**99.0** (+0.8)", "**98.9** (+0.8)", "**99.2** (+0.5)", "**54.4** (+4.2)", "**95.4** (+1.2)", "**89.4** (+1.6)", "33.8 GB (+263.4%)", "9.2 GB (+58.6%)", "14.4 (-43.1%)", "28.4 (-32.9%)"]),
]
t4_md = build_md_table(
    ["Model", "Image AUROC", "Image AP", "Pixel AUROC", "Pixel AP", "Pixel AUPRO", "mAD", "GPU Mem (Train)", "GPU Mem (Eval)", "FPS (Train)", "FPS (Eval)"],
    t4_rows
)

t5_md = build_md_table(
    ["n_m", "Image AUROC", "Image AP", "Pixel AUROC", "Pixel AP", "Pixel AUPRO", "mAD"],
    t5_rows
)

t6_md = build_md_table(
    ["λ", "Image AUROC", "Image AP", "Pixel AUROC", "Pixel AP", "Pixel AUPRO", "mAD"],
    t6_rows
)

ta1_md = build_md_table(
    ["Category", "DiffusionAD", "DRAEM", "DDAD", "D3AD", "Ours (LAMBDA)"],
    ta1_rows
)

ta2_md = build_md_table(
    ["Category", "DiffusionAD", "DRAEM*", "DDAD", "D3AD", "Ours (LAMBDA)"],
    ta2_rows
)

ta3_md = build_md_table(
    ["Category", "DiffusionAD", "DRAEM", "DDAD", "D3AD", "Ours (LAMBDA)"],
    ta3_rows
)

ta4_md = build_md_table(
    ["Category", "Ours", "w/o GSM", "w/o MBG", "w/o VAE"],
    ta4_rows
)

ta5_md = build_md_table(
    ["Category", "n_m=50", "n_m=100", "n_m=150", "n_m=200", "n_m=250"],
    ta5_rows
)

ta6_md = build_md_table(
    ["Category", "λ=0.1", "λ=0.2", "λ=0.5", "λ=1 (Ours)", "λ=2", "λ=5", "λ=10"],
    ta6_rows
)

tables_section = rf"""### 5.2 工業異常檢測與計算效率綜合分析：VisA 基準與統計顯著性檢定（出自論文 Table 1、Table 3 & Fig. 4）

#### (A) VisA 資料集檢測精度與計算效率綜合比較（出自論文 Table 1, p. 8）

*註：粗體表示最佳結果（論文原表亦以底線標示次佳結果）；異常檢測指標單位為 `%`（註：論文 Sec. 5.3 p. 7 內文誤將 `Table 1` 寫為 `Table 3`，且內文將 `LAMBDA` 之 Pixel AUROC 與 AUPRO 寫為 `98.5%` 與 `93.9%`，而 `Table 1`、`Table 4`、`Table A.1`、`Table A.4` 與 `Sec. 6` 皆為 `98.6%` 與 `94.2%`）。*

{t1_md}

- **關鍵計算效率與精度發現（出自論文 Sec. 5.3–5.5, p. 7–9, Fig. 4）**：
  1. **GPU 記憶體大幅節省**：訓練階段 `LAMBDA` 僅需 **`9.3 GB`**，較同為兩階段架構的 [DiffusionAD](zhang2023-diffusionad.md)（`48.4 GB`）減少 **`80.8%`**，較單階段擴散模型 `DDAD`（`12.8 GB`）減少 **`27.3%`**；推論階段僅需 **`5.8 GB`**，較 `DiffusionAD`（`12.4 GB`）與 `DDAD`（`9.4 GB`）分別減少 **`53.2%`** 與 **`38.3%`**（出自論文 Sec. 5.4, p. 7）。
  2. **訓練與推論速度全面領先兩階段擴散模型**：相較於 `DiffusionAD`（訓練 `11.2 FPS`、推論 `10.9 FPS`、延遲 `91.7 ms`），`LAMBDA` 達成 **`2.3×` 訓練加速（`25.3 FPS`）** 與 **`3.9×` 推論加速（`42.3 FPS`、延遲僅 `23.6 ms/image`）**；對比單階段擴散模型 `DDAD`（推論 `12.2 FPS`）與 `D3AD`（推論 `9.7 FPS`），推論速度分別快上 **`3.5×`** 與 **`4.4×`**（出自論文 Sec. 5.4, p. 7–8）。
  3. **免除單階段模型額外特徵擷取器微調（Feature Extractor Tuning）成本**：雖然單階段模型 `D3AD`（`13h 19m`）與 `DDAD`（`15h 34m`）表面報告的去噪網路訓練時間較短，但它們在評估前**必須額外執行數小時的特徵擷取器微調**（未計入報告時間內）；而 `LAMBDA`（`27h 57m`，較 `DiffusionAD` 的 `58h 10m` 節省逾一半時間）訓練完成後即可直接部署推論（出自論文 Sec. 5.4, p. 7–8）。
  4. **像素級 ROC 與 PR 曲線分析（Fig. 4, p. 8）**：在正常像素佔比超過 `95%` 的極端類別不平衡下，所有方法之像素級 `AP` 皆落在 `50%～54%` 區間，而 `LAMBDA` 在工業界最關鍵的低假陽性率區間（`0–0.2 FPR`）與 `DiffusionAD` 緊密重疊（皆逼近 `99%` Pixel AUROC）（出自論文 Sec. 5.5, p. 8–9）。

#### (B) 跨 30 個獨立類別之成對 Wilcoxon 符號等級統計檢定（出自論文 Sec. 5.7 & Table 3, p. 9）

為驗證性能差異具統計顯著性，論文將 `MVTec AD`（15 類）、`VisA`（12 類）與 `BMAD`（3 類）共 **30 個獨立類別**視為成對觀測值，進行成對 Wilcoxon 符號等級檢定（Paired Wilcoxon signed-rank test，顯著水準 $\alpha = 0.05$）：

{t3_md}

- **統計檢定結論**：`LAMBDA` 與最強基準 [DiffusionAD](zhang2023-diffusionad.md) 在像素級 `AUROC`（$p = 0.812$）與 `AP`（$p = 0.436$）上**無統計顯著差異**（$p > 0.05$），證實其在大幅降低 `80.8%` 訓練記憶體並加速 `3.9×` 推論的同時，完整保留了 SOTA 等級的檢測精度；相對地，`LAMBDA` 對 `DRAEM`、`DDAD` 與 `D3AD` 的所有 $p$ 值皆小於 `0.05`（帶 `*` 號），具備統計顯著的精度提升（出自論文 Sec. 5.7, p. 9）。

---

### 5.3 醫療影像異常檢測結果：BMAD 基準（出自論文 Sec. 5.6、Table 2 & Table A.3）

#### (A) BMAD 醫療資料集整體表現對比（出自論文 Table 2, p. 9，單位：%）

{t2_md}

#### (B) BMAD 3 大醫學解剖類別（Brain、Liver、Retinal）詳細數據（出自論文 Table A.3, p. 13，單位：%）

*註：每個類別單元格格式為 `Image AUROC/Image AP Pixel AUROC/Pixel AP/Pixel AUPRO`，粗體代表最佳結果。*

{ta3_md}

- **跨領域泛化分析（出自論文 Sec. 5.6, p. 9）**：`LAMBDA` 在 `BMAD` 醫療基準的所有綜合指標上全面奪冠（影像級 `87.1%` AUROC / `88.1%` AP，像素級 `90.3%` AUROC / `41.8%` AP / `70.2%` AUPRO，綜合 `mAD` 達 **`75.5%`**），在 `Image AUROC` 上領先 `DiffusionAD`（`83.4%`）達 `+3.7%`、領先 `DDAD`（`84.9%`）達 `+2.2%`，證明記憶庫引導與局部統計校準機制能穩健泛化至非工業之醫療異常檢測領域。

---

### 5.4 VisA 與 MVTec AD 逐類別完整數據（出自論文 Appendix A Table A.1 & Table A.2）

#### (A) VisA 12 類別逐類表現：`Image AUROC/AP Pixel AUROC/AP/AUPRO`（出自論文 Table A.1, p. 13，單位：%）

{ta1_md}

#### (B) MVTec AD 15 類別逐類表現：`Image AUROC/AP Pixel AUROC/AP/AUPRO`（出自論文 Table A.2, p. 13，單位：%）

{ta2_md}

---

### 5.5 消融實驗與超參數敏感度分析（Ablation Studies，出自論文 Sec. 5.8、Tables 4–6 & Tables A.4–A.6）

#### (A) 核心組件消融（VAE 潛在壓縮、MBG 記憶庫引導、GSM 引導尺度圖）（出自論文 Sec. 5.8.1–5.8.4、Table 4、Fig. 5–6 & Table A.4）

1. **VisA 整體檢測表現與計算效率消融（出自論文 Table 4, p. 10）**：
   *註：`w/o MBG` 變體改採用 [DiffusionAD](zhang2023-diffusionad.md) 的雙尺度 `Norm Guide`；括號內數值代表相對於完整模型 `Ours` 的變化量。*

{t4_md}

2. **VisA 12 類別逐類消融詳細數據：`Image AUROC/AP Pixel AUROC/AP/AUPRO`（出自論文 Table A.4, p. 13，單位：%）**：

{ta4_md}

3. **各組件貢獻與收斂效率關鍵結論（出自論文 Sec. 5.8.1–5.8.4, p. 9–11, Fig. 5–6）**：
   - **VAE 潛在壓縮之效應（`Ours` vs. `w/o VAE`，Sec. 5.8.1）**：移除 `VAE` 直接在原始像素空間運作雖可微幅提升檢測指標（`Pixel AUROC` `98.6% → 99.2%`、`AUPRO` `94.2% → 95.4%`），但訓練記憶體從 `9.3 GB` 暴增 **`+263.4%`** 至 `33.8 GB`，訓練速度從 `25.3 FPS` 下降 **`43.1%`** 至 `14.4 FPS`，且收斂所需訓練時間增加約 **`3×`**（Fig. 6），證實 `VAE` 壓縮是兼顧精度與部署可行性的關鍵。
   - **記憶庫引導去噪之效應（`Ours` vs. `w/o MBG`，Sec. 5.8.2）**：以單次前向之 `MBG` 取代 `DiffusionAD` 雙尺度 `Norm Guide`，不僅使 `VisA` 之 `Image AUROC` 提升 `+3.1%`（`95.0% → 98.1%`）、`mAD` 提升 `+2.4%`（`85.4% → 87.8%`），同時將訓練記憶體由 `11.2 GB`（若對比完整像素空間 `Norm Guide` 則為 `48.4 GB`）降至 `9.3 GB`（推論 `5.8 GB`），並減少正常區域的假陽性誤報（Fig. 5）。
   - **空間自適應引導尺度圖之效應（`Ours` vs. `w/o GSM`，Sec. 5.8.3）**：移除 `GSM` 改用全圖均一引導強度會導致正常區域產生大量假陽性雜訊（Fig. 5），加入 `GSM` 後在幾乎不增加額外運算開銷（訓練 `25.5 → 25.3 FPS`、推論 `42.4 → 42.3 FPS`）的前提下，將 `VisA` 之 `Pixel AUROC` 從 `96.4%` 提升至 `98.6%`（`+2.2%`）、`Pixel AP` 從 `44.5%` 提升至 `50.2%`（`+5.7%`）、`AUPRO` 從 `90.2%` 提升至 `94.2%`（`+4.0%`）。
   - **訓練收斂速度（Fig. 6, Sec. 5.8.4）**：完整 `LAMBDA` 模型於 **`100,000` 秒**內即可收斂至目標精度，而移除 `GSM` 或 `MBG` 的變體則出現收斂受限或震盪，移除 `VAE` 則需約 `3` 倍運行時間。

#### (B) 記憶庫大小 $n_m$ 消融實驗（出自論文 Sec. 5.8.5、Table 5 & Table A.5）

1. **MVTec AD 不同記憶庫容量 $n_m \in \{{50, 100, 150, 200, 250\}}$ 平均表現（出自論文 Table 5, p. 10，單位：%）**：

{t5_md}

2. **MVTec AD 15 類別於不同記憶庫容量 $n_m$ 之逐類表現：`Image AUROC/AP Pixel AUROC/AP/AUPRO`（出自論文 Table A.5, p. 14，單位：%）**：

{ta5_md}

- **關鍵發現（出自論文 Sec. 5.8.5, p. 11）**：隨著 $n_m$ 由 `50` 增加至 `200`，`AUPRO` 由 `93.5%` 穩步上升至 **`94.9%`**、`mAD` 由 `90.8%` 提升至 **`91.8%`**，且由於記憶庫檢索僅佔整體推論管線極小比例，$n_m$ 由 `50` 增至 `250` 對總推論時間影響極微；然而當進一步擴大至 $n_m = 250$ 時，因引入冗餘近似圖樣與極端邊緣正常樣本，像素級表現反而出現飽和微降（`Pixel AP` `69.1% → 68.7%`、`AUPRO` `94.9% → 94.4%`），故選定 **$n_m = 200$** 為最佳配置。

#### (C) 分割損失權重因子 $\lambda$ 消融實驗（出自論文 Sec. 5.8.6、Table 6 & Table A.6）

1. **MVTec AD 不同 Focal Loss 權重 $\lambda \in \{{0.1, 0.2, 0.5, 1, 2, 5, 10\}}$ 平均表現（出自論文 Table 6, p. 10，單位：%）**：

{t6_md}

2. **MVTec AD 15 類別於不同權重 $\lambda$ 之逐類表現：`Image AUROC/AP Pixel AUROC/AP/AUPRO`（出自論文 Table A.6, p. 14，單位：%）**：

{ta6_md}

- **關鍵發現（出自論文 Sec. 5.8.6, p. 11–12）**：當 $\lambda \in [0.1, 0.5]$ 過小時，Focal Loss 權重不足以克服異常像素佔比低於 `5%` 的極端前景／背景不平衡，導致邊界定位能力低落（`AUPRO` 僅 `87.9%～91.5%`）；在 **$\lambda = 1$（預設配置）** 時達到 Smooth $L_1$ 穩定梯度與 Focal Loss 困難樣本聚焦的最佳平衡（最高 `mAD` **`91.8%`**，`AUPRO` **`94.9%`**），且於 $\lambda = 2$ 時保持穩定（`91.7%` mAD）；當 $\lambda \ge 5$ 過大時，過度強調困難負樣本會破壞 $L_1$ 損失的平滑梯度，使 `AUPRO` 回落至 `93.9%`（$\lambda=5$）與 `93.5%`（$\lambda=10$）。"""

with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

if "{{TABLES_PLACEHOLDER}}" in md_content:
    md_content = md_content.replace("{{TABLES_PLACEHOLDER}}", tables_section)
else:
    pattern = re.compile(
        r"### 5\.2 工業異常檢測與計算效率綜合分析.*?---\n\n## 6\. 論文限制",
        re.DOTALL
    )
    assert pattern.search(md_content), "Could not find tables section in lee2026-lambda.md"
    md_content = pattern.sub(lambda m: tables_section + "\n\n---\n\n## 6. 論文限制", md_content)

with open(md_path, "w", encoding="utf-8") as f:
    f.write(md_content)

print("Successfully generated and inserted all tables into wiki/papers/lee2026-lambda.md!")
