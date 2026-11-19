# LLM Wiki 操作紀錄（Log）

本檔案為 Append-only 時間軸紀錄，記載每次 `ingest`、`query` 與 `lint` 操作。

---

## [2026-11-13] init | 專案與 Wiki 架構初始化

- **動作**：建立 [AGENTS.md](../AGENTS.md)、`wiki/` 四大分類子資料夾（`papers/`、`concepts/`、`datasets/`、`comparisons/`）、總目錄 [index.md](index.md)、操作日誌 `log.md` 以及 `slides/` 目錄。
- **待 Ingest 佇列（共 7 篇）**：
  1. `bergmann2019-mvtec-ad.pdf`
  2. `ho2020-ddpm.pdf`
  3. `zavrtanik2021-riad.pdf`
  4. `roth2022-patchcore.pdf`
  5. `zhang2023-diffusionad.pdf`
  6. `lee2026-lambda.pdf`
  7. `hecklerkram2025-mvtec-ad-2.pdf`

---

## [2026-11-13] ingest | bergmann2019-mvtec-ad

- **讀取原始來源**：`raw/papers/bergmann2019-mvtec-ad.pdf`（Bergmann et al., *MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection*, CVPR 2019）
- **新增 Wiki 頁面**：
  - 單篇論文頁：[papers/bergmann2019-mvtec-ad.md](papers/bergmann2019-mvtec-ad.md)
  - 資料集與指標頁：[datasets/mvtec-ad.md](datasets/mvtec-ad.md)
  - 核心概念頁：[concepts/unsupervised-anomaly-detection.md](concepts/unsupervised-anomaly-detection.md)
- **更新索引與入口頁**：
  - 更新 [wiki/index.md](index.md)（累計：論文 1 篇、概念 1 篇、資料集 1 篇）
  - 建立根目錄入口頁 [../index.html](../index.html)

---

## [2026-11-13] ingest | ho2020-ddpm

- **讀取原始來源**：`raw/papers/ho2020-ddpm.pdf`（Ho et al., *Denoising Diffusion Probabilistic Models*, NeurIPS 2020）
- **新增與重繪素材**：
  - 新增單篇論文頁：[papers/ho2020-ddpm.md](papers/ho2020-ddpm.md)
  - 新增核心概念頁：[concepts/denoising-diffusion-probabilistic-models.md](concepts/denoising-diffusion-probabilistic-models.md)
  - 新增重繪 SVG 示意圖：[../assets/diagrams/ho2020-ddpm-fig2.svg](../assets/diagrams/ho2020-ddpm-fig2.svg)（依論文 Fig. 2 重繪）
- **更新既有頁面與索引**：
  - 更新雙向連結：[concepts/unsupervised-anomaly-detection.md](concepts/unsupervised-anomaly-detection.md)
  - 更新 [wiki/index.md](index.md) 與根目錄入口頁 [../index.html](../index.html)（目前累計：論文 2 篇、概念 2 篇、資料集 1 篇）

---

## [2026-11-13] fix | 修正 bergmann2019 與 ho2020-ddpm 審查項目

- **修正內容**：
  1. [papers/bergmann2019-mvtec-ad.md](papers/bergmann2019-mvtec-ad.md) §5.2 `Zipper` 列：`AE (L2)` 之 `0.97 / 0.63` 補上粗體（與 `AE (SSIM)` 平均同為 `0.80`）。
  2. [datasets/mvtec-ad.md](datasets/mvtec-ad.md) §5.1 `CNN Feature Dictionary` 列：物件類別最高值修正為 `0.87 (Screw)`。
  3. [../assets/diagrams/ho2020-ddpm-fig2.svg](../assets/diagrams/ho2020-ddpm-fig2.svg)：移除 `_{ }` 寫法，改用 Unicode 下標（`x₀`、`xₜ`、`xₜ₋₁`）與 `<tspan baseline-shift="sub">`（`x_T`、`p_θ`）。
  4. [papers/ho2020-ddpm.md](papers/ho2020-ddpm.md) §2 核心貢獻第 3 點：將後續異常檢測應用之推論與論文原始出處括號分開，並明確標註「（AI 整理）」。

---

## [2026-11-13] ingest | zavrtanik2021-riad

- **讀取原始來源**：`raw/papers/zavrtanik2021-riad.pdf`（Zavrtanik et al., *Reconstruction by inpainting for visual anomaly detection*, Pattern Recognition 112 (2021) 107706）
- **新增與重繪素材**：
  - 新增單篇論文頁：[papers/zavrtanik2021-riad.md](papers/zavrtanik2021-riad.md)
  - 新增核心概念頁：[concepts/reconstruction-by-inpainting.md](concepts/reconstruction-by-inpainting.md)
  - 新增重繪 SVG 示意圖：[../assets/diagrams/zavrtanik2021-riad-fig1.svg](../assets/diagrams/zavrtanik2021-riad-fig1.svg)（依論文 Fig. 1 重繪）
- **更新既有頁面與索引**：
  - 擴充 MVTec AD 基準表現匯總表與連結：[datasets/mvtec-ad.md](datasets/mvtec-ad.md)
  - 更新雙向連結：[papers/bergmann2019-mvtec-ad.md](papers/bergmann2019-mvtec-ad.md)、[concepts/unsupervised-anomaly-detection.md](concepts/unsupervised-anomaly-detection.md)、[concepts/denoising-diffusion-probabilistic-models.md](concepts/denoising-diffusion-probabilistic-models.md)
  - 更新 [wiki/index.md](index.md) 與根目錄入口頁 [../index.html](../index.html)（目前累計：論文 3 篇、概念 3 篇、資料集 1 篇）

---

## [2026-11-13] fix | 修正 zavrtanik2021-riad 審查項目

- **修正內容**：
  1. [papers/zavrtanik2021-riad.md](papers/zavrtanik2021-riad.md)（§5.2 Table 1、§5.3 Table 2）與 [datasets/mvtec-ad.md](datasets/mvtec-ad.md)（§5.2 `US` 列）：加註「US 數據為 RIAD 作者重新實作之多尺度版本；US 原論文未提供影像級結果（出自論文 Sec. 4.2, p. 5）」。
  2. [papers/zavrtanik2021-riad.md](papers/zavrtanik2021-riad.md)（§5.5 消融表第 3 列）：補上論文原意「Skip Connections 的效果依類別而異（Sec. 6, p. 7–8）」，並將總平均提升 `3.1` 個百分點標註為「（AI 整理，依 Table 6 計算）」。


---

## [2026-11-13] ingest | roth2022-patchcore

- **讀取原始來源**：`raw/papers/roth2022-patchcore.pdf`（Roth et al., *Towards Total Recall in Industrial Anomaly Detection*, `arXiv:2106.08265v2 [cs.CV] 5 May 2022`）
- **新增與重繪素材**：
  - 新增單篇論文頁：[papers/roth2022-patchcore.md](papers/roth2022-patchcore.md)
  - 新增核心概念頁：[concepts/memory-bank.md](concepts/memory-bank.md)
  - 新增跨論文比較頁：[comparisons/embedding-vs-reconstruction.md](comparisons/embedding-vs-reconstruction.md)
  - 新增重繪 SVG 示意圖：[../assets/diagrams/roth2022-patchcore-fig2.svg](../assets/diagrams/roth2022-patchcore-fig2.svg)（依論文 Fig. 2 重繪）
- **更新既有頁面與索引**：
  - 擴充 MVTec AD 基準表現匯總表與連結：[datasets/mvtec-ad.md](datasets/mvtec-ad.md)
  - 更新雙向連結：[papers/bergmann2019-mvtec-ad.md](papers/bergmann2019-mvtec-ad.md)、[papers/ho2020-ddpm.md](papers/ho2020-ddpm.md)、[papers/zavrtanik2021-riad.md](papers/zavrtanik2021-riad.md)、[concepts/unsupervised-anomaly-detection.md](concepts/unsupervised-anomaly-detection.md)、[concepts/denoising-diffusion-probabilistic-models.md](concepts/denoising-diffusion-probabilistic-models.md)、[concepts/reconstruction-by-inpainting.md](concepts/reconstruction-by-inpainting.md)
  - 更新 [wiki/index.md](index.md) 與根目錄入口頁 [../index.html](../index.html)（目前累計：論文 4 篇、概念 4 篇、資料集 1 篇、比較頁 1 篇，共 10 篇 Wiki 知識頁）


---

## [2026-11-13] fix | 修正 roth2022-patchcore 審查項目

- **修正內容**：
  1. [comparisons/embedding-vs-reconstruction.md](comparisons/embedding-vs-reconstruction.md) §4 `Uninformed Students (US)` 列：加註「Image/Pixel AUROC 為 RIAD 作者重新實作之版本（`zavrtanik2021-riad.pdf` Sec. 4.2）；PRO 85.7 為 PatchCore 引用之原始 US 結果（`roth2022-patchcore.pdf` Table 3）；兩者實作不同，不宜直接比較。」
  2. [papers/roth2022-patchcore.md](papers/roth2022-patchcore.md) §5.2(B) Ensemble 列：於 PRO `94.9 / 5.6` 後加註「（原文如此，100 − 94.9 應為 5.1）」。


---

## [2026-11-13] ingest | zhang2023-diffusionad

- **讀取原始來源**：`raw/papers/zhang2023-diffusionad.pdf`（Zhang et al., *DiffusionAD: Norm-guided One-step Denoising Diffusion for Anomaly Detection*, `arXiv:2303.08730v4 [cs.CV] 17 May 2025`）
- **新增與重繪素材**：
  - 新增單篇論文頁：[papers/zhang2023-diffusionad.md](papers/zhang2023-diffusionad.md)
  - 新增核心概念頁：[concepts/norm-guided-one-step-denoising.md](concepts/norm-guided-one-step-denoising.md)
  - 新增重繪 SVG 示意圖：[../assets/diagrams/zhang2023-diffusionad-fig3.svg](../assets/diagrams/zhang2023-diffusionad-fig3.svg)（依論文 Fig. 3 重繪）
- **更新既有頁面與索引**：
  - 擴充 MVTec AD 基準表現匯總表與連結：[datasets/mvtec-ad.md](datasets/mvtec-ad.md)
  - 擴充跨流派比較頁（納入一步擴散重建 + 分割範式）：[comparisons/embedding-vs-reconstruction.md](comparisons/embedding-vs-reconstruction.md)
  - 更新雙向連結與演進說明：[papers/bergmann2019-mvtec-ad.md](papers/bergmann2019-mvtec-ad.md)、[papers/ho2020-ddpm.md](papers/ho2020-ddpm.md)、[papers/zavrtanik2021-riad.md](papers/zavrtanik2021-riad.md)、[papers/roth2022-patchcore.md](papers/roth2022-patchcore.md)、[concepts/unsupervised-anomaly-detection.md](concepts/unsupervised-anomaly-detection.md)、[concepts/denoising-diffusion-probabilistic-models.md](concepts/denoising-diffusion-probabilistic-models.md)、[concepts/reconstruction-by-inpainting.md](concepts/reconstruction-by-inpainting.md)、[concepts/memory-bank.md](concepts/memory-bank.md)
  - 更新 [wiki/index.md](index.md) 與根目錄入口頁 [../index.html](../index.html)（目前累計：論文 5 篇、概念 5 篇、資料集 1 篇、比較頁 1 篇，共 12 篇 Wiki 知識頁）


---

## [2026-11-13] fix | 修正 zhang2023-diffusionad 數據表與消融段落並新增表格抽取規範

- **修正內容**：
  1. **[papers/zhang2023-diffusionad.md](papers/zhang2023-diffusionad.md) §5.3、§5.4**：以 Python（`pypdf`）由 `raw/papers/zhang2023-diffusionad.pdf` 直接抽取 Table I–IV 完整 8 個方法欄位之文字與粗體標記並自動生成 Markdown 表格；填表後再以獨立程式逐格比對 PDF：
     - **Table I（VisA `Image AUROC / Pixel PRO`）**：檢查 **104** 格（208 個數值），錯誤 **0** 格。
     - **Table II（VisA `Pixel AUROC / Pixel AP`）**：檢查 **104** 格（208 個數值），錯誤 **0** 格。
     - **Table III（MVTec AD `Image AUROC / Pixel AUROC`）**：檢查 **128** 格（256 個數值），錯誤 **0** 格。
     - **Table IV（MVTec AD `Pixel PRO / Pixel AP`）**：檢查 **128** 格（256 個數值），錯誤 **0** 格。
     - **總計比對結果**：共檢查 **464** 格（**928** 個數值），錯誤 **0** 格。
  2. **[papers/zhang2023-diffusionad.md](papers/zhang2023-diffusionad.md) §5.6(C)**：移除原誤植段落，改寫為論文實際記載之單尺度加噪強度影響（Fig. 8 & Fig. 9，$t \ge 500$ 時 `Image AUROC` 下降，Sec. V-C）、引導權重 $w$ 消融（Fig. 10，$w$ 經驗設為 `1`）與推論固定 $t_s = 200, t_b = 400$（Sec. IV），並說明 Fig. 11–13 為定性視覺化範例。
  3. **[datasets/mvtec-ad.md](datasets/mvtec-ad.md) §5.2 與 [comparisons/embedding-vs-reconstruction.md](comparisons/embedding-vs-reconstruction.md) §4**：依 Table III 以程式重算並更正「（AI 整理）」紋理／物件平均（`Image / Pixel AUROC`）：`FastFlow` `85.1 / 95.3 ｜ 93.1 / 95.7`、`RD4AD` `99.5 / 98.5 ｜ 98.3 / 97.5`、`SimpleNet` `99.1 / 97.0 ｜ 99.8 / 97.9`、`DMAD` `100.0 / 97.9 ｜ 99.4 / 98.4`。
  4. **[../AGENTS.md](../AGENTS.md) §4.1 步驟 2**：新增規則「超過 5 列的數據表必須用程式從 PDF 抽取文字填寫，填完用程式逐格比對 PDF；AI 自行計算的數字也要用程式計算。」


---

## [2026-11-14] fix | 儲存 DiffusionAD 驗證腳本與報告、移除 AI 整理平均值粗體並修正 §5.6(C) 出處

- **修正內容**：
  1. 新增腳本與檢查報告：[../scripts/generate_diffusionad_tables.py](../scripts/generate_diffusionad_tables.py)、[../scripts/verify_diffusionad_tables.py](../scripts/verify_diffusionad_tables.py) 與 [../scripts/reports/diffusionad-table-check.txt](../scripts/reports/diffusionad-table-check.txt)。
  2. [datasets/mvtec-ad.md](datasets/mvtec-ad.md) §5.2 與 [comparisons/embedding-vs-reconstruction.md](comparisons/embedding-vs-reconstruction.md) §4：移除所有「（AI 整理）」紋理／物件平均欄位中之粗體標記。
  3. [papers/zhang2023-diffusionad.md](papers/zhang2023-diffusionad.md) §5.6(C)：將 $T = 1000$ 與 $\tau = 300$ 之出處標註為 `Sec. V-A, p. 7`，$S$、$B$ 區間定義與 $t_s = 200, t_b = 400$ 維持 `Sec. IV-B & IV-C, p. 5–6`。


---

## [2026-11-14] ingest | lee2026-lambda

- **讀取原始來源**：`raw/papers/lee2026-lambda.pdf`（Lee & Kang, *Memory bank-guided diffusion model for lightweight anomaly detection*, *Applied Soft Computing* 186 (2026) 114215, DOI: `https://doi.org/10.1016/j.asoc.2025.114215`）
- **新增與重繪素材**：
  - 新增單篇論文頁：[papers/lee2026-lambda.md](papers/lee2026-lambda.md)
  - 新增核心概念頁：[concepts/memory-bank-guided-latent-diffusion.md](concepts/memory-bank-guided-latent-diffusion.md)
  - 新增重繪 SVG 示意圖：[../assets/diagrams/lee2026-lambda-fig1.svg](../assets/diagrams/lee2026-lambda-fig1.svg)（依論文 Fig. 1、Fig. 2、Fig. 3 重繪）
  - 新增表格自動抽取與逐格比對腳本及報告：[../scripts/generate_lambda_tables.py](../scripts/generate_lambda_tables.py)、[../scripts/verify_lambda_tables.py](../scripts/verify_lambda_tables.py)、[../scripts/reports/lambda-table-check.txt](../scripts/reports/lambda-table-check.txt)（涵蓋論文全部 12 張數據表 `Table 1`–`6` 與 `Table A.1`–`A.6`，共檢查 **665** 格、**2,473** 個數值，錯誤 **0** 格）
- **更新既有頁面與索引**：
  - 擴充 MVTec AD 基準表現匯總表與連結：[datasets/mvtec-ad.md](datasets/mvtec-ad.md)
  - 擴充跨流派比較頁（納入預訓練 `VAE` 潛在擴散 + 記憶庫引導 `MBG` + `GSM` 混合流派）：[comparisons/embedding-vs-reconstruction.md](comparisons/embedding-vs-reconstruction.md)
  - 更新雙向連結與演進說明：[papers/bergmann2019-mvtec-ad.md](papers/bergmann2019-mvtec-ad.md)、[papers/ho2020-ddpm.md](papers/ho2020-ddpm.md)、[papers/zavrtanik2021-riad.md](papers/zavrtanik2021-riad.md)、[papers/roth2022-patchcore.md](papers/roth2022-patchcore.md)、[papers/zhang2023-diffusionad.md](papers/zhang2023-diffusionad.md)、[concepts/unsupervised-anomaly-detection.md](concepts/unsupervised-anomaly-detection.md)、[concepts/denoising-diffusion-probabilistic-models.md](concepts/denoising-diffusion-probabilistic-models.md)、[concepts/reconstruction-by-inpainting.md](concepts/reconstruction-by-inpainting.md)、[concepts/memory-bank.md](concepts/memory-bank.md)、[concepts/norm-guided-one-step-denoising.md](concepts/norm-guided-one-step-denoising.md)
  - 更新 [wiki/index.md](index.md) 與根目錄入口頁 [../index.html](../index.html)（目前累計：論文 6 篇、概念 6 篇、資料集 1 篇、比較頁 1 篇，共 14 篇 Wiki 知識頁）


---

## [2026-11-14] fix | 修正 lee2026-lambda 審查項目並強化跨頁數據與控制字元驗證

- **修正內容**：
  1. [comparisons/embedding-vs-reconstruction.md](comparisons/embedding-vs-reconstruction.md) §4 註 2、§5（以及 [index.md](index.md)、[../index.html](../index.html)）：依 `lee2026-lambda.pdf` Table 2 更正 `BMAD` 數據為 `LAMBDA` `87.1 / 88.1 / 90.3 / 41.8 / 70.2`（mAD `75.5`）、`DiffusionAD` `83.4 / 85.9 / 86.9 / 39.9 / 68.2`（mAD `72.9`），並標明欄位順序 `Image AUROC / Image AP / Pixel AUROC / Pixel AP / AUPRO` 與 Table 編號。
  2. [../scripts/generate_lambda_tables.py](../scripts/generate_lambda_tables.py) 與 [papers/lee2026-lambda.md](papers/lee2026-lambda.md) L222：將含反斜線字串改為 raw string（`rf"""..."""`），修正 L222 因 `\a` 轉義產生之 `\x07` 控制字元為 `$\alpha = 0.05$`，並於 [../scripts/verify_lambda_tables.py](../scripts/verify_lambda_tables.py) 新增全 `wiki/` 控制字元掃描（16 個檔案 0 錯誤）。
  3. [../assets/diagrams/lee2026-lambda-fig1.svg](../assets/diagrams/lee2026-lambda-fig1.svg) L66、L99：將 `ℝ^{n_m × d}` 與 `∇_{L_t}` 中的字面底線改為 `<tspan>` 巢狀上下標。
  4. [../AGENTS.md](../AGENTS.md) §4.1 步驟 3：新增規範「寫進論文頁以外（比較頁、概念頁、資料集頁、`wiki/index.md`、`index.html`）的數字，只能從已驗證的論文頁表格複製並註明 Table 編號；寫完必須用程式把這些數字和 PDF 比對一次」，並更新 [../scripts/verify_lambda_tables.py](../scripts/verify_lambda_tables.py) 與 [../scripts/reports/lambda-table-check.txt](../scripts/reports/lambda-table-check.txt) 納入跨頁數據與 PDF 自動比對。


---

## [2026-11-14] ingest | hecklerkram2025-mvtec-ad-2

- **讀取原始來源**：`raw/papers/hecklerkram2025-mvtec-ad-2.pdf`（Heckler-Kram et al., *The MVTec AD 2 Dataset: Advanced Scenarios for Unsupervised Anomaly Detection*, `arXiv:2503.21622v1 [cs.CV] 27 Mar 2025`）
- **新增與重繪素材**：
  - 新增單篇論文頁：[papers/hecklerkram2025-mvtec-ad-2.md](papers/hecklerkram2025-mvtec-ad-2.md)
  - 新增資料集與指標頁：[datasets/mvtec-ad-2.md](datasets/mvtec-ad-2.md)
  - 新增重繪 SVG 示意圖：[../assets/diagrams/hecklerkram2025-mvtec-ad-2-fig4.svg](../assets/diagrams/hecklerkram2025-mvtec-ad-2-fig4.svg)（依論文 Fig. 4 重繪）
  - 新增表格自動抽取與逐格比對腳本及報告：[../scripts/generate_mvtec_ad_2_tables.py](../scripts/generate_mvtec_ad_2_tables.py)、[../scripts/verify_mvtec_ad_2_tables.py](../scripts/verify_mvtec_ad_2_tables.py)、[../scripts/reports/mvtec-ad-2-table-check.txt](../scripts/reports/mvtec-ad-2-table-check.txt)（涵蓋論文全部 12 張表 `Table 1`–`12`，共檢查 **607** 格、**907** 個數值，跨頁數據比對 **38** 項，全 `wiki/` 控制字元與相對連結檢查 **0** 錯誤）
- **更新既有頁面與索引**：
  - 擴充 MVTec AD 資料集頁（新增 §5.3 獨立子表收錄 MVTec AD 2 作者重評測之 `AU-PRO0.30` 跨資料集表現，與既有 PRO 欄位嚴格區隔，並註明 `RD` 即 `RD4AD`）：[datasets/mvtec-ad.md](datasets/mvtec-ad.md)
  - 擴充跨流派比較頁（新增 §4.2 MVTec AD 2 跨流派重評測與光照偏移強健性對比表及 §5 第 5 點演進分析）：[comparisons/embedding-vs-reconstruction.md](comparisons/embedding-vs-reconstruction.md)
  - 更新雙向連結：[papers/bergmann2019-mvtec-ad.md](papers/bergmann2019-mvtec-ad.md)、[papers/ho2020-ddpm.md](papers/ho2020-ddpm.md)、[papers/zavrtanik2021-riad.md](papers/zavrtanik2021-riad.md)、[papers/roth2022-patchcore.md](papers/roth2022-patchcore.md)、[papers/zhang2023-diffusionad.md](papers/zhang2023-diffusionad.md)、[papers/lee2026-lambda.md](papers/lee2026-lambda.md)、[concepts/unsupervised-anomaly-detection.md](concepts/unsupervised-anomaly-detection.md)、[concepts/memory-bank.md](concepts/memory-bank.md)、[concepts/norm-guided-one-step-denoising.md](concepts/norm-guided-one-step-denoising.md)、[concepts/memory-bank-guided-latent-diffusion.md](concepts/memory-bank-guided-latent-diffusion.md)
  - 更新 [wiki/index.md](index.md) 與根目錄入口頁 [../index.html](../index.html)（目前累計：論文 7 篇、概念 6 篇、資料集 2 篇、比較頁 1 篇，共 16 篇 Wiki 知識頁；指定之 7 篇論文已全數完成 Ingest）



---

## [2026-11-15] lint | 新增投影片密度規則、更新簡報大綱與範本二、強化大綱儲存格核對腳本與突變測試

- **規範與範本更新**：
  1. [../AGENTS.md](../AGENTS.md) §5：新增「投影片密度規則」（每頁於 `1366×768` 單一畫面內看完不需垂直捲動、正文 120 字以內白話、最多 3 個關鍵數字、最多 1 張圖或 1 個 4 列以內小表、最多 1 條公式、其餘細節以「延伸閱讀」連向 `wiki` 段落；關卡 ④ 瀏覽器檢查量測每頁高度是否超出畫面）。經程式實測整份 `AGENTS.md` 為 **10,123** 字元（符合 $\le 12,000$ 字元上限）。
  2. 版面範本（`slides/_templates/`）：刪除 `template-1-split.html` 與 `template-3-lecture-note.html`，保留並重寫 [../slides/_templates/template-2-top-figure.html](../slides/_templates/template-2-top-figure.html)（上方架構圖、下方四問卡片依 `1 → 2 → 3 → 4` 順序排列、單一畫面無 `overflow: hidden`，效率與精度數據僅引用 `roth2022-patchcore` Table 5 原列原值）。
- **簡報大綱與自動核對腳本強化**：
  1. [../slides/evolution-of-anomaly-detection/outline.md](../slides/evolution-of-anomaly-detection/outline.md)：全 16 頁新增「`### 投影片可見內容`」並將原規劃小節改名為「`### 查證資料與講稿備註`」，套用投影片密度規則與各頁內容取捨（含第 10 頁註明「論文所列差值」、第 15 頁更新情境判斷題與 `C15-03` 及 `PatchCore` 準備流程描述）。
  2. [../scripts/check_outline.py](../scripts/check_outline.py) 與 [../slides/evolution-of-anomaly-detection/reports/outline-check.txt](../slides/evolution-of-anomaly-detection/reports/outline-check.txt)：改為逐筆檢查每條主張自身的「`wiki 頁與段落`」檔案與標題是否存在，對表格數據主張動態解析所引 `wiki` 段落的 Markdown 表格（以「`方法`」找列、「`指標`」找欄並驗證資料集脈絡與儲存格數值），並將全 55 筆主張分為三類統計（**已由程式核對儲存格 23 筆｜待 AI 審查 32 筆｜尚未檢查 0 筆**）。
  3. 新增突變測試腳本 [../scripts/tests/test_check_outline.py](../scripts/tests/test_check_outline.py) 與報告 [../slides/evolution-of-anomaly-detection/reports/outline-check-mutation-tests.txt](../slides/evolution-of-anomaly-detection/reports/outline-check-mutation-tests.txt)：針對 (a)–(f) 共 6 項植入錯誤進行測試，6 項全數被 `check_outline.py` 判定為 `FAIL`。

---

## [2026-11-15] slides | 關卡 ② 逐頁草稿完成（01–16）、正文字數上限由 120 改為 130

- **分工變更**：Antigravity（Gemini 4 Argon）額度用完，停在草稿第 11 頁；第 12–16 頁與後續修訂由 Claude 接手撰寫，並沿用同一套檢查腳本。
- **規範更新**：[../AGENTS.md](../AGENTS.md) §5 投影片密度規則的正文上限由 120 字改為 130 字（使用者決定）。原因：120 字過緊，16 頁中多頁需重寫 1–3 次，句子被壓成電報式；第 15 頁重寫 3 次仍超過 1 字，觸發「同頁同問題最多 3 次」的停止條件並交給人決定。[../scripts/check_drafts.py](../scripts/check_drafts.py) 的上限同步改為 130。
- **草稿**：新增 [../slides/evolution-of-anomaly-detection/drafts/](../slides/evolution-of-anomaly-detection/drafts/) `12.md`–`16.md`；第 03、05、06、08、09、10、11、15 頁的投影片文字改回白話（數字與主張記錄表不變）。
- **程式檢查攔到的問題**（紀錄於 `reports/drafts-rewrites.json`）：`outline.md` 第 12、13 頁的延伸閱讀錨點不存在（已改為 wiki 實際標題的錨點）；第 15 頁正文出現無對應主張的數字；多頁字數超限。
- **結果**：[../slides/evolution-of-anomaly-detection/reports/drafts-check.txt](../slides/evolution-of-anomaly-detection/reports/drafts-check.txt) 16 頁全數通過；主張三類統計為「已由程式核對儲存格 23 筆｜數字存在性已查、語意待 AI 審查 32 筆｜尚未檢查 0 筆」。語意審查留待關卡 ③。

---

## [2026-11-15] lint | 關卡 ③ 審查退回後修正 wiki 證據與簡報草稿

- **審查**：Codex 獨立審查報告 [../slides/evolution-of-anomaly-detection/reports/gate3-review-gpt.md](../slides/evolution-of-anomaly-detection/reports/gate3-review-gpt.md)；逐條以原始 PDF 驗證後的處理見 [../slides/evolution-of-anomaly-detection/reports/gate3-response.md](../slides/evolution-of-anomaly-detection/reports/gate3-response.md)。
- **wiki 修正**：[papers/lee2026-lambda.md](papers/lee2026-lambda.md) §5.1 補全文檢索「未記載項目」紀錄；[comparisons/embedding-vs-reconstruction.md](comparisons/embedding-vs-reconstruction.md) §5 的 256×256 舉例加註、移除對消費級／邊緣 GPU 的外推；[papers/hecklerkram2025-mvtec-ad-2.md](papers/hecklerkram2025-mvtec-ad-2.md) 與 [datasets/mvtec-ad-2.md](datasets/mvtec-ad-2.md) 對「2.6–5 MP」加註原文不一致（Can 約 2.29 MP），並補 25,000 倍的算式說明。
- **圖檔**：修正 `zhang2023-diffusionad-fig3.svg`（(1−y) 是排除異常樣本）與 `hecklerkram2025-mvtec-ad-2-fig4.svg`（TPR 與 AUROC 區分）；新增簡報用精簡圖 `assets/diagrams/slides/lee2026-lambda-simple.svg`、`pro-vs-tpr-simple.svg`。
- **草稿**：修改第 1、3–9、11–16 頁與對應主張；新增主張 C04-05（共 56 筆）。outline.md 與 drafts 的主張記錄同步修改；outline.md 的「投影片可見內容」為舊版，以 drafts 為準。

---

## [2026-11-15] lint | 關卡 ③ 第二輪審查後修正

- 審查報告 [../slides/evolution-of-anomaly-detection/reports/gate3-review-gpt-round2.md](../slides/evolution-of-anomaly-detection/reports/gate3-review-gpt-round2.md) 不通過，3 項（R2-01～03）；處理見 [gate3-response.md](../slides/evolution-of-anomaly-detection/reports/gate3-response.md) 第二輪段落。
- wiki：[papers/hecklerkram2025-mvtec-ad-2.md](papers/hecklerkram2025-mvtec-ad-2.md) 補 Can 面積換算算式；[datasets/mvtec-ad-2.md](datasets/mvtec-ad-2.md) §1、§4 補交叉提示。
- 草稿：第 8、11、14 頁；新增主張 C11-04（共 57 筆）。圖檔：`assets/diagrams/slides/pro-vs-tpr-simple.svg` 加註比例。
