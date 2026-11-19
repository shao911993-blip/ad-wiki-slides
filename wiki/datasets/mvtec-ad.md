---
title: "MVTec AD 資料集與評估指標（ROC AUC & PRO）"
type: "dataset"
tags: ["MVTec AD", "Dataset", "Evaluation Metric", "AUROC", "PRO", "Industrial AD"]
sources: ["bergmann2019-mvtec-ad.pdf", "zavrtanik2021-riad.pdf", "roth2022-patchcore.pdf", "zhang2023-diffusionad.pdf", "lee2026-lambda.pdf", "hecklerkram2025-mvtec-ad-2.pdf"]
updated: "2026-11-14"
---

# MVTec AD 資料集與評估指標（ROC AUC & PRO）

## 1. 概述與定位

**MVTec AD（MVTec Anomaly Detection）** 由 Bergmann 等人於 CVPR 2019 提出（見單篇論文頁 [Bergmann et al. (2019) — MVTec AD](../papers/bergmann2019-mvtec-ad.md)），是視覺異常檢測領域最具代表性的工業光學檢測基準資料集。其核心特色在於：
1. **純正常樣本訓練（One-Class / Unsupervised Setting）**：訓練集僅含無缺陷影像（共 **3,629** 張），測試集同時包含正常影像（**467** 張）與真實工業缺陷影像（**1,258** 張），總計 **5,354** 張高解析度影像（出自 `bergmann2019-mvtec-ad.pdf` p. 4 Table 1 & Sec. 3）。
2. **多樣化紋理與物件類別**：涵蓋 **5** 種材質紋理（`Carpet`、`Grid`、`Leather`、`Tile`、`Wood`）與 **10** 種工業／日常物件（`Bottle`、`Cable`、`Capsule`、`Hazelnut`、`Metal Nut`、`Pill`、`Screw`、`Toothbrush`、`Transistor`、`Zipper`），共 **15** 個類別、**73** 種缺陷類型（出自 `bergmann2019-mvtec-ad.pdf` p. 4 Table 1 & Sec. 3）。
3. **像素級精確標註**：提供 **1,888** 個缺陷區域的像素級 Ground Truth Mask，同時支援**影像級異常分類（Image-level Classification）**與**像素級異常定位／分割（Pixel-level Segmentation）**雙重評估（出自 `bergmann2019-mvtec-ad.pdf` p. 2 Sec. 1、p. 4 Table 1）。

---

## 2. 初學者版（AI 整理）

> **（AI 整理）**
> - **為什麼異常檢測需要同時看「整張圖（Image-level）」跟「每個像素（Pixel-level）」？**
>   想像工廠品管有兩道問題：
>   1. **第一問（分類）**：「這顆藥丸有沒有瑕疵，該不該淘汰？」——這看的是整張圖的異常分數。
>   2. **第二問（定位／分割）**：「瑕疵在藥丸的哪裡？是刮痕還是缺角？」——如果模型說這顆藥丸有問題，結果標出來的位置卻是背景陰影，那代表模型根本沒看對地方！因此必須檢查模型預測的異常區域跟真實瑕疵標註（Ground Truth）重疊得準不準。
> - **為什麼除了 Pixel-AUROC，還需要 PRO（Per-Region Overlap）指標？**
>   假設一張圖裡有一道占 **1,000** 個像素的大刮痕，和一個只占 **10** 個像素的微小針孔。
>   - **Pixel-AUROC** 把整張圖所有像素混在一起算：就算模型完全漏掉那個 **10** 像素的小針孔，只要抓對大刮痕，分數還是很高（大瑕疵主導了分數）。
>   - **PRO（相對單區域重疊率）** 則是「不管大瑕疵還小瑕疵，每一個獨立瑕疵區域都算一票（先算每個區域內的重疊比例再平均）」。這樣一來，漏掉小針孔就會明顯拉低分數，更能反映工業品管不能放過微小瑕疵的嚴格要求。

---

## 3. 資料集規格總覽（出自 `bergmann2019-mvtec-ad.pdf` Table 1, p. 4 & Sec. 3, p. 4–5）

- **總類別數**：**15** 類（**5** 類 Textures ＋ **10** 類 Objects）
  - **規則紋理（Regular Textures，2 類）**：`Carpet`、`Grid`
  - **隨機紋理（Random Textures，3 類）**：`Leather`、`Tile`、`Wood`
  - **剛性／變形／自然變異物件（Objects，10 類）**：`Bottle`、`Cable`、`Capsule`、`Hazelnut`、`Metal Nut`、`Pill`、`Screw`、`Toothbrush`、`Transistor`、`Zipper`
  - **灰階單通道類別（3 類）**：`Grid`、`Screw`、`Zipper`（其餘 **12** 類為 RGB 彩色影像）
- **影像張數統計**：
  - 總張數：**5,354** 張
  - 訓練與驗證集（全數無缺陷）：**3,629** 張（單類最少為 `Toothbrush` **60** 張，最多為 `Hazelnut` **391** 張）
  - 測試集總數：**1,725** 張（正常 **467** 張 ＋ 異常 **1,258** 張）
- **缺陷與影像尺寸**：
  - 缺陷種類數（Defect groups）：**73** 種（平均每類約 **5** 種）
  - 像素標註缺陷區域總數（Defect regions）：**1,888** 個
  - 原始感測器解析度：**2048 × 2048** 像素（搭配 **1:5** 與 **1:1** 雙側遠心鏡頭）；裁切後影像邊長介於 **700 × 700** 至 **1024 × 1024** 像素。

*(各類別詳細張數拆解請參閱 [Bergmann et al. (2019) — MVTec AD §4.2](../papers/bergmann2019-mvtec-ad.md)。)*

---

## 4. 官方評估指標定義（出自 `bergmann2019-mvtec-ad.pdf` Sec. 4.3, p. 6–7）

1. **影像級分類正確率（Classification Accuracy）**：
   - 以無缺陷驗證集估計出分割閾值與最小缺陷面積後，分別計算測試集中無缺陷影像與異常影像的正確分類比例，並取兩者平均。
2. **像素級 ROC AUC（Area Under the ROC Curve）**：
   - 不依賴單一二值化閾值，掃描所有可能閾值，計算整個類別測試集中：
     - **True Positive Rate (TPR)**：被正確判定為異常的異常像素百分比。
     - **False Positive Rate (FPR)**：被誤判為異常的正常像素百分比。
   - 取 TPR 對 FPR 曲線下之面積作為整體像素異常圖品質指標。
3. **相對單區域重疊率（Relative Per-Region Overlap, PRO）**：
   - 針對測試集中每一個真實缺陷連通區域（Ground Truth connected component），計算預測二值化分割區域與該真實區域的重疊比例並進行平均，使不同面積大小的缺陷區域具有相同權重。

---

## 5. 收錄方法於 MVTec AD 的基準表現匯總

### 5.1 MVTec AD 原論文 Baseline 像素級分割表現（出自 `bergmann2019-mvtec-ad.pdf` Table 3, p. 7）
*註：以下列出原論文 4 種主要跨類別方法於 5 類紋理、10 類物件上之各類表現範圍（格式：`PRO / Pixel-AUROC`；完整 15 類逐類數據見 [Bergmann et al. (2019) §5.3](../papers/bergmann2019-mvtec-ad.md)）。*

| 方法名稱 | 方法類型 | 紋理類別（5 類）Pixel-AUROC 範圍 | 物件類別（10 類）Pixel-AUROC 範圍 | 主要優勢與瓶頸（出自論文 Sec. 4.4, p. 7–8） |
| :--- | :--- | :---: | :---: | :--- |
| **AE (SSIM)** | 重建法（結構相似度 Autoencoder） | 0.59 (`Tile`) – 0.94 (`Grid`) | 0.82 (`Cable`) – 0.97 (`Hazelnut`) | 物件類別 Pixel-AUROC 表現突出，但高頻紋理重建模糊且僅支援灰階影像 |
| **AE (L2)** | 重建法（像素 $\ell^2$ Autoencoder） | 0.51 (`Tile`) – 0.90 (`Grid`) | 0.77 (`Zipper`) – 0.96 (`Screw`) | 物件類別之 PRO 整體高於 AE (SSIM)，表示無異常驗證集閾值估計較穩健 |
| **AnoGAN** | 生成對抗網路（GAN 潛在空間搜尋） | 0.50 (`Tile`) – 0.64 (`Leather`) | 0.76 (`Metal Nut`) – 0.90 (`Toothbrush`) | 易受 Mode Collapse 影響，難以重建複雜紋理與多變姿態物件，推論耗時長 |
| **CNN Feature Dictionary** | 預訓練特徵聚類（ResNet-18 + PCA + K-means） | 0.59 (`Grid`) – 0.93 (`Tile`) | 0.66 (`Transistor`) – 0.87 (`Screw`) | 紋理類別 ROC AUC 最穩定，但缺乏空間位置資訊導致物件類別表現退化 |

### 5.2 後續收錄方法於 MVTec AD 的演進表現匯總

| 方法名稱（發表出處） | 方法流派 | 紋理平均 Image / Pixel ROC AUC (%) | 物件平均 Image / Pixel ROC AUC (%) | 全 15 類平均 Image / Pixel ROC AUC / PRO (%) | 數據出處 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **GeoTrans** | 自監督幾何變換預測 | 58.5 / - | 71.6 / - | 67.2 / - / - | `zavrtanik2021-riad.pdf` Table 1 (p. 6) & `roth2022-patchcore.pdf` Table S1 (p. 15) |
| **DSEBM** | 深度結構能量模型 | 63.8 / - *(AI 整理)* | 74.5 / - *(AI 整理)* | 70.9 / - / - | `roth2022-patchcore.pdf` Table S1 (p. 15) |
| **OCSVM** | 單類別支持向量機 | 74.9 / - *(AI 整理)* | 70.4 / - *(AI 整理)* | 71.9 / - / - | `roth2022-patchcore.pdf` Table S1 (p. 15) |
| **GANomaly** | 對抗式自編碼器重建 | 76.5 / - | 75.4 / - | 76.2 / - / - | `zavrtanik2021-riad.pdf` Table 1 (p. 6) & `roth2022-patchcore.pdf` Table S1 (p. 15) |
| **ITAE** | 逆變換自編碼器重建 | 82.2 / - | 84.8 / - | 83.9 / - / - | `zavrtanik2021-riad.pdf` Table 1 (p. 6) & `roth2022-patchcore.pdf` Table S1 (p. 15) |
| **AE-SSIM** | 結構相似度自編碼器重建 | - / 78.2 | - / 90.2 | - / 86.2 *(或 87.0)* / 69.4 | `zavrtanik2021-riad.pdf` Table 2 (p. 6)；括號與 PRO 出自 `roth2022-patchcore.pdf` Tables 2–3 (p. 6–7) |
| **AnoGAN** | 生成對抗網路潛在空間搜尋 | - / 57.7 | - / 82.6 | - / 74.3 / - | `zavrtanik2021-riad.pdf` Table 2 (p. 6) |
| **VEVAE** (`vis. expl. VAE`) | 視覺可解釋變分自編碼器 | - / 80.6 | - / 88.8 | - / 86.1 *(或 86.0)* / - | `zavrtanik2021-riad.pdf` Table 2 (p. 6) & `roth2022-patchcore.pdf` Table S2 (p. 15) |
| **$\gamma$-VAE + grad.** | 能量投影變分自編碼器 | - / 79.9 *(AI 整理)* | - / 93.2 *(AI 整理)* | - / 88.8 / - | `roth2022-patchcore.pdf` Table 2 (p. 6) & Table S2 (p. 15) |
| **$\text{CAVGA-R}_w$** | 注意力引導變分自編碼器 | 87.4 / - *(AI 整理)* | 91.1 / - *(AI 整理)* | 90.0 / 89.0 / - | `roth2022-patchcore.pdf` Table 2 (p. 6) & Tables S1–S2 (p. 15) |
| **Uninformed Students (US)** *(註)* | 師生網路知識蒸餾（9 模型整合） | 91.5 / 93.2 | 85.8 / 94.3 | 87.7 / 93.9 / 85.7 | `zavrtanik2021-riad.pdf` Tables 1–2 (p. 6)；PRO 出自 `roth2022-patchcore.pdf` Table 3 (p. 7) |
| **[RIAD](../papers/zavrtanik2021-riad.md)**（`Pattern Recognition 2021`） | 自監督遮罩修補重建（U-Net + MSGMS） | 95.1 / 93.9 | 89.9 / 94.3 | 91.7 / 94.2 / - | `zavrtanik2021-riad.pdf` Table 1 & Table 2 (p. 6) |
| **SPADE** | 多階層記憶庫最近鄰檢索 | - / 92.9 *(AI 整理)* | - / 97.6 *(AI 整理)* | 85.5 / 96.0 / 91.7 | `roth2022-patchcore.pdf` Tables 1–3 (p. 6–7) & Tables S1–S3 (p. 15) |
| **PatchSVDD** | 自監督 Patch 級 SVDD | 94.5 / 93.7 *(AI 整理)* | 90.8 / 96.7 *(AI 整理)* | 92.1 / 95.7 / - | `roth2022-patchcore.pdf` Tables 1–2 (p. 6) & Tables S1–S2 (p. 15) |
| **DifferNet** | 預訓練特徵 + Normalizing Flows | 94.6 / - *(AI 整理)* | 94.7 / - *(AI 整理)* | 94.9 / - / - | `roth2022-patchcore.pdf` Table 1 (p. 6) & Table S1 (p. 15) |
| **MahalanobisAD** | 全圖預訓練特徵 Mahalanobis 距離 | 97.8 / - *(AI 整理)* | 94.8 / - *(AI 整理)* | 95.8 / - / - | `roth2022-patchcore.pdf` Table 1 (p. 6) & Table S1 (p. 15) |
| **PaDiM** (`PaDiM*`) | 位置綁定高斯分佈 Mahalanobis 距離 | - / 96.9 *(AI 整理)* | - / 97.9 *(AI 整理)* | 95.3 (97.9) / 97.5 / 92.1 | `roth2022-patchcore.pdf` Tables 1–3 (p. 6–7) & Tables S1–S3 (p. 15) |
| **[PatchCore-25%](../papers/roth2022-patchcore.md)**（`2022`） | 中階局部感知記憶庫 + 25% Coreset | 99.0 / 97.5 *(AI 整理)* | 99.2 / 98.4 *(AI 整理)* | **99.1** / **98.1** / 93.4 | `roth2022-patchcore.pdf` Tables 1–3 (p. 6–7) & Tables S1–S3 (p. 15) |
| **[PatchCore-10%](../papers/roth2022-patchcore.md)**（`2022`） | 中階局部感知記憶庫 + 10% Coreset | 98.9 / 97.6 *(AI 整理)* | 98.9 / 98.4 *(AI 整理)* | 99.0 / **98.1** / **93.5** | `roth2022-patchcore.pdf` Tables 1–3 (p. 6–7) & Tables S1–S3 (p. 15) |
| **[PatchCore-1%](../papers/roth2022-patchcore.md)**（`2022`） | 中階局部感知記憶庫 + 1% Coreset | 99.0 / 97.6 *(AI 整理)* | 99.0 / 98.1 *(AI 整理)* | 99.0 / 98.0 / 93.1 | `roth2022-patchcore.pdf` Tables 1–3 (p. 6–7) & Tables S1–S3 (p. 15) |
| **[PatchCore-1% (Ensemble, 320)](../papers/roth2022-patchcore.md)** | 3 骨幹整合 + $320 \times 320$ 解析度 | - | - | **99.6** / **98.2** / **94.9** | `roth2022-patchcore.pdf` Table 4 (p. 7) |
| **FastFlow** | 預訓練特徵 + 2D 正規化流 | 85.1 / 95.3 *(AI 整理)* | 93.1 / 95.7 *(AI 整理)* | 90.5 / 95.5 / 85.6 *(AP: 39.8)* | `zhang2023-diffusionad.pdf` Tables III–V (p. 8–9) |
| **DRAEM** | 自編碼器重建 + 合成異常 U-Net 分割 | 99.1 / 97.9 *(AI 整理)* | 97.4 / 97.0 *(AI 整理)* | 98.0 / 97.3 / 92.1 *(AP: 68.4)* | `zhang2023-diffusionad.pdf` Tables III–V (p. 8–9) |
| **RD4AD** | 反向知識蒸餾（One-Class Embedding） | 99.5 / 98.5 *(AI 整理)* | 98.3 / 97.5 *(AI 整理)* | 98.5 / 97.8 / 93.9 *(AP: 58.0)* | `zhang2023-diffusionad.pdf` Tables III–V (p. 8–9) |
| **RD++** | 改良反向知識蒸餾 | 99.8 / 98.1 *(AI 整理)* | 99.3 / 98.4 *(AI 整理)* | 99.4 / 98.3 / 95.0 *(AP: 60.8)* | `zhang2023-diffusionad.pdf` Tables III–V (p. 8–9) |
| **SimpleNet** | 預訓練特徵空間高斯雜訊合成判別 | 99.1 / 97.0 *(AI 整理)* | 99.8 / 97.9 *(AI 整理)* | 99.6 / 97.6 / 90.0 *(AP: 54.8)* | `zhang2023-diffusionad.pdf` Tables III–V (p. 8–9) |
| **DMAD** | 變形重建異常檢測 | 100.0 / 97.9 *(AI 整理)* | 99.4 / 98.4 *(AI 整理)* | 99.6 / 98.2 / 90.6 *(AP: 53.5)* | `zhang2023-diffusionad.pdf` Tables III–V (p. 8–9) |
| **KLAD** | 潛在空間擴散模型重建（20 步） | - | - | - / 96.7 / 94.1 | `zhang2023-diffusionad.pdf` Table VI (p. 9) |
| **DiffAD** | 擴散重建 + 分割網路（50 步，1.2 FPS） | - | - | 98.7 / 98.3 / - *(AP: 74.6)* | `zhang2023-diffusionad.pdf` Table VI (p. 9) |
| **[DiffusionAD](../papers/zhang2023-diffusionad.md)**（`2023/2025`） | 雙尺度規範引導一步去噪擴散 + 分割（1 步，23.5 FPS） | 99.8 / 99.0 *(AI 整理)* | 99.6 / 98.4 *(AI 整理)* | **99.7** / **98.7** / **95.7** *(AP: **76.1**)* | `zhang2023-diffusionad.pdf` Tables III–VI (p. 8–9) |
| **DDAD** | 條件去噪擴散異常檢測（單階段） | 94.1 / 93.4 | 99.4 / 97.8 | 97.7 / 96.3 / 86.3 *(P-AP: 55.4)* | `lee2026-lambda.pdf` Table A.2 (p. 13) |
| **D3AD** | 動態加噪擴散異常檢測（單階段） | 89.0 / 94.9 | 95.3 / 97.3 | 93.1 / 96.5 / 90.7 *(P-AP: 54.2)* | `lee2026-lambda.pdf` Table A.2 (p. 13) |
| **[LAMBDA](../papers/lee2026-lambda.md)**（`Applied Soft Computing 2026`） | 潛在空間一步擴散 + 記憶庫引導 `MBG` + `GSM` + 分割（1 步，42.3 FPS） | 99.6 / 99.3 | 97.6 / 96.6 | 98.2 / 97.5 / 94.9 *(P-AP: 69.1, mAD: 91.8)* | `lee2026-lambda.pdf` Tables 5–6 (p. 10) & Table A.2 (p. 13) |

*註 1：上表 `US` 之 Image/Pixel ROC AUC 為 RIAD 作者重新實作之多尺度版本（US 原論文未提供影像級結果，出自 `zavrtanik2021-riad.pdf` Sec. 4.2, p. 5）；PRO `85.7%` 則引自 `roth2022-patchcore.pdf` Table 3 (p. 7)。*
*註 2：標註 `*(AI 整理)*` 之紋理／物件分類平均係由 AI 依據 `roth2022-patchcore.pdf` Tables S1–S2 及 `zhang2023-diffusionad.pdf` Table III 之 5 類紋理（`Carpet`, `Grid`, `Leather`, `Tile`, `Wood`）與 10 類物件逐類數值算術平均計算（AI 整理）；`lee2026-lambda.pdf` Table A.2 則於原表直接提供 `Texture Avg.` 與 `Object Avg.`。*
*註 3：`zhang2023-diffusionad.pdf` Table V 亦引用 `PatchCore` 於 MVTec AD 之表現為 `99.1 / 98.1 / 93.5`（Pixel AP 為 `56.1%`）；`lee2026-lambda.pdf` Table A.2 亦報告其重評測之 `DiffusionAD` 為 `99.5 / 98.4 / 96.0`（P-AP: `77.9%`，紋理平均 `99.9 / 99.5`、物件平均 `99.3 / 97.9`）與 `DRAEM*` 為 `98.5 / 97.4 / 93.7`（P-AP: `69.0%`，紋理平均 `99.0 / 98.5`、物件平均 `98.3 / 96.8`）。*

### 5.3 MVTec AD 2 論文（Heckler-Kram et al., 2025）重新評測之跨資料集對照（出自 `hecklerkram2025-mvtec-ad-2.pdf` Table 1, p. 2、Table 7, p. 10 & Table 9, p. 15）

> **重要指標與出處區分說明**：
> 1. 下表之 `MVTec AD` 與 `VisA` 數據係 [Heckler-Kram et al. (2025) — MVTec AD 2](../papers/hecklerkram2025-mvtec-ad-2.md) 作者於統一無場景調參協定（輸入 $256 \times 256$；其中 `PatchCore` 關閉中心裁切並採 `0.01%` Coreset、`SimpleNet` 固定訓練 `160` Epochs、`EfficientAD` 於 MVTec AD / VisA 採 `EfficientAD-M` 而於 MVTec AD 2 採 `EfficientAD-S`、`RD` 與 `RD++` 之 MVTec AD 數據引自其原論文 [17], [31]，見該論文 p. 7–8 Sec. 4.1）下彙整／重新評測之結果，評估指標為 **$\text{AU-PRO}_{0.30}$（%，FPR 積分上限 `0.30`）**，因此獨立列表呈現，不可與 §5.2 其他論文之 PRO 欄位直接混排比較。
> 2. 論文同時定義兩種不同積分上限之指標：**$\text{AU-PRO}_{0.30}$**（`Table 1`、`Table 9`）與更嚴格的 **$\text{AU-PRO}_{0.05}$**（`Table 7`、`Table 10`、`Table 11`），兩者分列於不同欄位，不可混用或直接互相比較。
> 3. `MVTec AD 2` 欄位每格包含兩個數值，順序為 **`TESTpriv / TESTpriv,mix`**（同訓練集標準光照測試集／隨機混合已知與未知光照測試集）。
> 4. 論文中的 **`RD`（Reverse Distillation [17]）即本 Wiki 既有的 `RD4AD`**。

| 方法名稱 (Method) | MVTec AD<br>`AU-PRO0.30` (%)<br>[Table 1] | VisA<br>`AU-PRO0.30` (%)<br>[Table 1] | MVTec AD 2 ($256 \times 256$)<br>`AU-PRO0.30` (%)<br>(`TESTpriv / TESTpriv,mix`)<br>[Table 1 & Table 9] | MVTec AD 2 ($256 \times 256$)<br>`AU-PRO0.05` (%)<br>(`TESTpriv / TESTpriv,mix`)<br>[Table 7] | 數據出處 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **[PatchCore](../papers/roth2022-patchcore.md)** | 92.7 | 79.7 | 53.8 / 50.8 | 28.8 / 26.0 | `hecklerkram2025-mvtec-ad-2.pdf` Table 1 (p. 2), Table 7 (p. 10), Table 9 (p. 15) |
| **RD** *(即 RD4AD)* | 93.9 | 89.0 | 53.0 / 50.3 | 26.4 / 25.0 | `hecklerkram2025-mvtec-ad-2.pdf` Table 1 (p. 2), Table 7 (p. 10), Table 9 (p. 15) |
| **RD++** | 95.0 | 89.3 | 54.3 / 50.4 | 27.1 / 25.2 | `hecklerkram2025-mvtec-ad-2.pdf` Table 1 (p. 2), Table 7 (p. 10), Table 9 (p. 15) |
| **EfficientAD** | 93.5 | 94.0 | 58.7 / 44.1 | 30.8 / 19.2 | `hecklerkram2025-mvtec-ad-2.pdf` Table 1 (p. 2), Table 7 (p. 10), Table 9 (p. 15) |
| **MSFlow** | 91.2 | 88.4 | 52.7 / 37.1 | 24.3 / 11.9 | `hecklerkram2025-mvtec-ad-2.pdf` Table 1 (p. 2), Table 7 (p. 10), Table 9 (p. 15) |
| **SimpleNet** | 89.6 | 68.9 | 46.4 / 37.6 | 21.1 / 13.7 | `hecklerkram2025-mvtec-ad-2.pdf` Table 1 (p. 2), Table 7 (p. 10), Table 9 (p. 15) |
| **DSR** | 90.8 | 68.1 | 49.0 / 45.2 | 20.3 / 17.4 | `hecklerkram2025-mvtec-ad-2.pdf` Table 1 (p. 2), Table 7 (p. 10), Table 9 (p. 15) |
| **Mean (7 方法平均)** | 92.4 | 82.4 | 52.6 / - *(Table 1 僅報 TESTpriv)* | - | `hecklerkram2025-mvtec-ad-2.pdf` Table 1 (p. 2) |

*(關於 MVTec AD 2 之 8 大場景規格、$512 \times 512$ 與 $1/2$ 原始寬高之 `AU-PRO0.05` 消融（Table 10–11）及二值化分割／分類 $F_1$（Table 8, 12），請參閱 [MVTec AD 2 資料集與進階評估協定](mvtec-ad-2.md) 與 [Heckler-Kram et al. (2025) — MVTec AD 2](../papers/hecklerkram2025-mvtec-ad-2.md)。)*

---

## 6. 相關 Wiki 頁面連結

- **原始資料集與二代進階資料集論文**：
  - [Bergmann et al. (2019) — MVTec AD](../papers/bergmann2019-mvtec-ad.md)
  - [Heckler-Kram et al. (2025) — MVTec AD 2](../papers/hecklerkram2025-mvtec-ad-2.md)
  - [MVTec AD 2 資料集與進階評估協定（AU-PRO0.05、F1 與光照分佈偏移）](mvtec-ad-2.md)
- **使用本資料集之收錄方法頁**：
  - [Zavrtanik et al. (2021) — RIAD](../papers/zavrtanik2021-riad.md)
  - [Roth et al. (2022) — PatchCore](../papers/roth2022-patchcore.md)
  - [Zhang et al. (2023/2025) — DiffusionAD](../papers/zhang2023-diffusionad.md)
  - [Lee & Kang (2026) — LAMBDA](../papers/lee2026-lambda.md)
- **跨論文流派比較**：
  - [預訓練特徵嵌入 vs. 重建式異常檢測流派對比](../comparisons/embedding-vs-reconstruction.md)
- **核心概念**：
  - [非監督式視覺異常檢測（Unsupervised Anomaly Detection）](../concepts/unsupervised-anomaly-detection.md)
  - [遮罩修復重建與多尺度梯度相似度（Reconstruction by Inpainting & MSGMS）](../concepts/reconstruction-by-inpainting.md)
  - [局部特徵記憶庫與核心集下採樣（Patch-Level Memory Bank & Coreset Subsampling）](../concepts/memory-bank.md)
  - [規範引導一步去噪與合成異常分割（Norm-Guided One-Step Denoising & Anomaly Synthesis）](../concepts/norm-guided-one-step-denoising.md)
  - [潛在空間記憶庫引導去噪與引導尺度圖（Latent Diffusion with MBG & GSM）](../concepts/memory-bank-guided-latent-diffusion.md)
