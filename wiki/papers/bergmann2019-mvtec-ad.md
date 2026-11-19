---
title: "MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection"
type: "paper"
tags: ["Dataset", "Industrial AD", "Benchmark", "Autoencoder", "GAN", "Feature Descriptor"]
sources: ["bergmann2019-mvtec-ad.pdf"]
updated: "2026-11-14"
---

# MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection

## 1. 基本資訊

- **簡稱**：`MVTec AD`（論文內亦簡稱 `MAD`，出自論文 p. 2 Sec. 1）
- **發表年份與出處**：`CVPR 2019`（pp. 9592–9600，出自論文 p. 1 頁首與頁尾）
- **作者**：Paul Bergmann, Michael Fauser, David Sattlegger, Carsten Steger（MVTec Software GmbH，出自論文 p. 1）
- **主分類**：`資料集`
- **技術標籤**：`Dataset`、`Industrial AD`、`Pixel-Precise Ground Truth`、`Unsupervised Anomaly Detection`、`Benchmark`
- **官方外部連結**：
  - 資料集官網：`https://www.mvtec.com/company/research/datasets`（出自論文 p. 2 Footnote 1）
  - 機構網站：`https://www.mvtec.com`（出自論文 p. 1）
  - arXiv / DOI / 官方 GitHub：待確認（PDF 內未載明；註：p. 5 Footnote 3 之 `www.github.com/LeeDoYup/AnoGAN` 為第三方 AnoGAN 實作，p. 6 Footnote 4 之 `www.mvtec.com/products/halcon` 為 HALCON 函式庫網站）
- **關聯 Wiki 頁面**：
  - 資料集與指標頁：[MVTec AD 資料集與評估指標](../datasets/mvtec-ad.md)
  - 核心概念頁：[非監督式視覺異常檢測（Unsupervised Anomaly Detection）](../concepts/unsupervised-anomaly-detection.md)

---

## 2. 一句話總結（TL;DR）與核心貢獻

- **TL;DR**：提出首個模擬真實工業光學檢測場景、涵蓋 **15** 個類別（**5** 種材質紋理與 **10** 種物件）、共 **5,354** 張高解析度影像與 **1,888** 個像素級別缺陷標註區域的非監督式異常檢測基準資料集 **MVTec AD**，並系統性評估深度學習與傳統機器視覺方法在影像分類與像素分割上的表現（出自論文 p. 1 Abstract、p. 2 Sec. 1、p. 4 Table 1）。
- **解決的核心痛點**：
  1. **既有分類資料集轉換不符真實情境**：過去常將 `MNIST`、`CIFAR10`、`ImageNet` 的部分類別直接當作 Outlier，這類跨類別異常與訓練分佈差異極大，無法反映真實場景中「僅在微小局部區域出現細微偏差」的異常檢測需求（出自論文 p. 1–2 Sec. 1 & Sec. 2.1.1）。
  2. **既有分割資料集規模與多樣性不足**：如 `NanoTWICE` 僅有 **45** 張單一奈米纖維灰階影像（**5** 張正常訓練、**40** 張異常測試），而 `DAGM 2007`（**10** 類，每類 **1,000** 張正常訓練、**150** 張異常測試）則為人工合成灰階紋理加上粗糙橢圓標註，缺乏真實世界多類別物件與精確像素標註（出自論文 p. 3 Sec. 2.1.2）。
- **核心貢獻**（出自論文 p. 2 Sec. 1）：
  1. **建立多類別、多缺陷真實工業資料集**：包含 **5** 種獨特紋理與 **10** 種物件共 **15** 個類別、**5,354** 張高解析度影像（**3,629** 張無缺陷訓練／驗證影像、**1,725** 張測試影像）、**73** 種缺陷類型與 **1,888** 個像素級別 Ground Truth 標註區域（出自論文 p. 2 Sec. 1、p. 4 Table 1 & Sec. 3）。
  2. **建立嚴謹的無異常驗證集閾值估計與基準評測**：在不接觸任何異常影像的前提下，僅用無缺陷驗證集估計分割閾值，全面評估 `AE (SSIM)`、`AE (L2)`、`AnoGAN`、`CNN Feature Dictionary`、`GMM Texture Inspection` 與 `Variation Model` 在異常分類與像素級分割上的優劣（出自論文 p. 2 Sec. 1、p. 5–7 Sec. 4）。

---

## 3. 初學者版（AI 整理）

> **（AI 整理）**
> - **為什麼需要 MVTec AD？（核心痛點比喻）**：
>   在工廠產線上，良品（正常樣本）成千上萬，但瑕疵品（異常樣本）極少，且事前根本無法預知未來會出現刮痕、凹陷還是缺件。因此模型只能看「良品」學習（非監督式學習）。然而在 MVTec AD 問世前，學界常拿「叫只看過貓的模型去認出狗（如 CIFAR-10 抽換類別）」來當異常檢測實驗——這就像考品管員「在螺絲產線上認出一顆蘋果」一樣不切實際，因為真實品管考驗的是「在螺絲上找出一道 **1** 毫米的細微刮痕」。
> - **MVTec AD 做了什麼？（生活化理解）**：
>   研究團隊用工業級高解析度相機與遠心鏡頭，在嚴格控光下拍攝了 **15** 種日常與工業物品（包含地毯、皮革、磁磚等 **5** 種表面紋理，以及藥丸、螺絲、金屬螺母、電晶體等 **10** 種零件），並親手製造了 **73** 種逼真的表面刮傷、結構變形與缺件瑕疵，還把每個瑕疵的輪廓一格一格像素精確描繪出來。這份資料集讓所有異常檢測演算法終於有了一場貼近真實工廠品管的標準考題。

---

## 4. 資料集規格與評估指標

### 4.1 資料集規模與拍攝規格
- **總影像數**：**5,354** 張高解析度影像（出自論文 p. 1 Abstract、p. 2 Sec. 1、p. 4 Table 1）。
  - **訓練與驗證集（全數為正常無缺陷影像）**：**3,629** 張（每類別介於 **60** 至 **391** 張，出自論文 p. 4 Table 1 & Sec. 3）。
  - **測試集（含正常與異常影像）**：共 **1,725** 張（出自論文 p. 4 Sec. 3），其中正常測試影像 **467** 張、異常測試影像 **1,258** 張（出自論文 p. 4 Table 1）。
- **類別組成（共 15 類）**（出自論文 p. 4 Table 1 & Sec. 3）：
  - **紋理類別（Textures，共 5 類）**：規則紋理（`Carpet`、`Grid`）與隨機紋理（`Leather`、`Tile`、`Wood`）。
  - **物件類別（Objects，共 10 類）**：包含剛性固定外觀物件（如 `Bottle`、`Metal Nut`）、可變形物件（`Cable`）與具自然變異物件（`Hazelnut`）；擺放姿態分為大致對齊（如 `Toothbrush`、`Capsule`、`Pill`）與隨機旋轉（如 `Metal Nut`、`Screw`、`Hazelnut`）。
  - **色彩通道**：多數為 RGB 彩色影像；其中 **3** 個類別（`Grid`、`Screw`、`Zipper`）為單通道灰階影像（出自論文 p. 5 Sec. 3）。
- **取像硬體與解析度**（出自論文 p. 4 Table 1、p. 5 Sec. 3）：
  - 使用 **2048 × 2048** 像素工業 RGB 感測器，搭配放大倍率分別為 **1:5** 與 **1:1** 的 **2** 顆雙側遠心鏡頭（Bilateral Telecentric Lenses）在受控光源下拍攝。
  - 裁切後輸出影像邊長介於 **700 × 700** 至 **1024 × 1024** 像素之間。
- **缺陷與標註規格**（出自論文 p. 2 Sec. 1、p. 4 Table 1 & Sec. 3）：
  - 共 **73** 種不同缺陷類型（平均每類別約 **5** 種），涵蓋表面缺陷（刮痕、凹陷）、結構缺陷（零件扭曲變形）與缺件缺陷。
  - 提供像素級精確 Ground Truth Mask（Pixel-precise ground truth regions），總計 **1,888** 個標註缺陷區域（正文 p. 5 Sec. 3 亦敘述為「將近 **1,900** 個」）。

### 4.2 各類別統計明細（出自論文 Table 1, p. 4）

| 類別分組 | 類別名稱 (Category) | 訓練集張數 (# Train) | 測試正常張數 (# Test good) | 測試異常張數 (# Test defective) | 缺陷種類數 (# Defect groups) | 缺陷標註區域數 (# Defect regions) | 影像邊長 (Image side length) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Textures** | Carpet | 280 | 28 | 89 | 5 | 97 | 1024 |
| **Textures** | Grid | 264 | 21 | 57 | 5 | 170 | 1024 |
| **Textures** | Leather | 245 | 32 | 92 | 5 | 99 | 1024 |
| **Textures** | Tile | 230 | 33 | 84 | 5 | 86 | 840 |
| **Textures** | Wood | 247 | 19 | 60 | 5 | 168 | 1024 |
| **Objects** | Bottle | 209 | 20 | 63 | 3 | 68 | 900 |
| **Objects** | Cable | 224 | 58 | 92 | 8 | 151 | 1024 |
| **Objects** | Capsule | 219 | 23 | 109 | 5 | 114 | 1000 |
| **Objects** | Hazelnut | 391 | 40 | 70 | 4 | 136 | 1024 |
| **Objects** | Metal Nut | 220 | 22 | 93 | 4 | 132 | 700 |
| **Objects** | Pill | 267 | 26 | 141 | 7 | 245 | 800 |
| **Objects** | Screw | 320 | 41 | 119 | 5 | 135 | 1024 |
| **Objects** | Toothbrush | 60 | 12 | 30 | 1 | 66 | 1024 |
| **Objects** | Transistor | 213 | 60 | 40 | 4 | 44 | 1024 |
| **Objects** | Zipper | 240 | 32 | 119 | 7 | 177 | 1024 |
| **Total** | **15 Categories** | **3629** | **467** | **1258** | **73** | **1888** | **-** |

### 4.3 官方評估協定與指標（出自論文 Sec. 4.3, p. 6–7）
1. **無異常驗證集之分割閾值估計（Threshold Estimation）**：
   - 除 `GMM Texture Inspection` 自帶閾值外，其餘方法皆從訓練集中劃分出一組隨機挑選的**無缺陷驗證集（Anomaly-free validation set）**，並為每個類別定義「最小缺陷面積（Minimum defect area）」。
   - 在驗證集異常圖（Anomaly map）上逐步調高二值化閾值，直到驗證集上最大連通異常區域的面積剛好低於該最小缺陷面積為止，將此閾值用於測試集評估。
2. **影像級分類指標（Image-level Classification）**：
   - 在上述估計閾值下，分別計算測試集中「無缺陷影像被正確分類的比例（True Negative Ratio）」與「異常影像被正確分類的比例（True Positive Ratio）」，並以兩者之平均（Balanced Accuracy）作為綜合比較依據（出自論文 p. 6 Table 2 & Sec. 4.3）。
3. **像素級分割指標（Pixel-level Segmentation）**：
   - **Relative Per-Region Overlap（相對單區域重疊率，即後續文獻通稱之 PRO）**：在估計閾值下，計算二值化分割結果與 Ground Truth 各連通缺陷區域的相對重疊比例（出自論文 p. 6 Sec. 4.3、p. 7 Table 3）。
   - **Pixel-level ROC AUC**：不依賴單一閾值，計算整個測試集類別中「正確分類為異常的像素比例（True Positive Rate）」對「誤判為異常的像素比例（False Positive Rate）」之 ROC 曲線下面積（出自論文 p. 6–7 Sec. 4.3、p. 7 Table 3）。

---

## 5. 基準方法設定與實驗表現

### 5.1 評測之 6 種 Baseline 方法與超參數設定（出自論文 Sec. 4.1 & 4.2, p. 5–6）
- **資料擴增（Data Augmentation）**：針對深度學習方法，對紋理影像隨機裁切旋轉固定大小區塊，對物件影像施加隨機平移、旋轉與鏡像翻轉，每個類別皆擴增產生 **10,000** 張訓練區塊（出自論文 p. 6 Sec. 4.2）。
- **AE (SSIM) 與 AE (L2)**（出自論文 p. 5 Sec. 4.1.2）：
  - 紋理類別：重建 **128 × 128** 像素區塊，測試時以步長（Stride）**30** 像素滑動並平均異常圖。
  - 物件類別：多加一層捲積層以處理 **256 × 256** 解析度整張影像。
  - 潛在空間維度（Latent space dimension）設為 **100**；`SSIM` 視窗大小設為 **11 × 11** 像素（訓練與評估 `AE (SSIM)` 時影像轉為灰階）。
- **AnoGAN**（出自論文 p. 5 Sec. 4.1.1）：
  - 潛在空間維度固定為 **64**，生成影像大小 **128 × 128** 像素；訓練 **50** 個 Epochs，初始學習率 **0.0002**。
  - 測試階段執行 **300** 次潛在空間搜尋迭代，初始學習率 **0.02**，以像素級 $\ell^2$ 距離計算異常圖。
  - 物件影像縮放至 **128 × 128**；紋理影像縮放至 **512 × 512** 並切出 **128 × 128** 區塊，測試時水平與垂直步長為 **128** 像素。
- **CNN Feature Dictionary**（出自論文 p. 5 Sec. 4.1.3）：
  - 擷取 ImageNet 預訓練 `ResNet-18` 的 **512** 維 `avgpool` 層特徵（灰階影像複製為 **3** 通道），以 PCA 保留 **95%** 變異量（通常降至約 **100** 個主成分），再以 K-means 分為 **10** 個群心。
  - 區塊大小 **16 × 16** 像素，評估步長 **4** 像素；物件評估於 **256 × 256** 解析度，紋理縮放至 **512 × 512** 解析度。
- **GMM-Based Texture Inspection Model**（出自論文 p. 6 Sec. 4.1.4）：
  - 僅適用於紋理類別（HALCON 實作）：影像縮放至 **400 × 400** 像素，建立 **4** 層影像金字塔，每層檢查區塊大小 **7 × 7** 像素，隨機選取 **10** 張訓練影像訓練 GMM，以負對數概似值（Negative log-likelihood）產生異常圖。
- **Variation Model**（出自論文 p. 6 Sec. 4.1.5）：
  - 僅適用於可透過形狀匹配（Shape-based matching）對齊的 **6** 個物件類別（HALCON 實作）：隨機選取 **30** 張原始尺寸訓練影像（轉為灰階）訓練每個像素位置的平均值與變異數。

### 5.2 影像級異常分類表現（出自論文 Table 2, p. 6）
*註：每格數值格式為「`正常樣本正確率 / 異常樣本正確率`」，粗體表示該類別兩者平均值最高之方法。*

| 類別 (Category) | AE (SSIM) | AE (L2) | AnoGAN | CNN Feature Dictionary | Texture Inspection | Variation Model |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Carpet** | **0.43 / 0.90** | 0.57 / 0.42 | 0.82 / 0.16 | 0.89 / 0.36 | 0.57 / 0.61 | - |
| **Grid** | 0.38 / 1.00 | **0.57 / 0.98** | 0.90 / 0.12 | 0.57 / 0.33 | 1.00 / 0.05 | - |
| **Leather** | 0.00 / 0.92 | 0.06 / 0.82 | 0.91 / 0.12 | **0.63 / 0.71** | 0.00 / 0.99 | - |
| **Tile** | 1.00 / 0.04 | **1.00 / 0.54** | 0.97 / 0.05 | 0.97 / 0.44 | 1.00 / 0.43 | - |
| **Wood** | 0.84 / 0.82 | 1.00 / 0.47 | 0.89 / 0.47 | **0.79 / 0.88** | 0.42 / 1.00 | - |
| **Bottle** | **0.85 / 0.90** | 0.70 / 0.89 | 0.95 / 0.43 | 1.00 / 0.06 | - | 1.00 / 0.13 |
| **Cable** | **0.74 / 0.48** | 0.93 / 0.18 | 0.98 / 0.07 | 0.97 / 0.24 | - | - |
| **Capsule** | 0.78 / 0.43 | **1.00 / 0.24** | 0.96 / 0.20 | 0.78 / 0.03 | - | 1.00 / 0.03 |
| **Hazelnut** | 1.00 / 0.07 | **0.93 / 0.84** | 0.83 / 0.16 | 0.90 / 0.07 | - | - |
| **Metal nut** | 1.00 / 0.08 | **0.68 / 0.77** | 0.86 / 0.13 | 0.55 / 0.74 | - | 0.32 / 0.83 |
| **Pill** | 0.92 / 0.28 | 1.00 / 0.23 | **1.00 / 0.24** | 0.85 / 0.06 | - | 1.00 / 0.13 |
| **Screw** | 0.95 / 0.06 | **0.98 / 0.39** | 0.41 / 0.28 | 0.73 / 0.13 | - | 1.00 / 0.10 |
| **Toothbrush** | 0.75 / 0.73 | **1.00 / 0.97** | 1.00 / 0.13 | 1.00 / 0.03 | - | 1.00 / 0.60 |
| **Transistor** | 1.00 / 0.03 | **0.97 / 0.45** | 0.98 / 0.35 | 1.00 / 0.15 | - | - |
| **Zipper** | **1.00 / 0.60** | **0.97 / 0.63** | 0.78 / 0.40 | 0.78 / 0.29 | - | - |

### 5.3 像素級異常分割表現（出自論文 Table 3, p. 7）
*註：每格數值格式為「`Relative Per-Region Overlap (PRO) / ROC AUC`」，粗體表示該指標於該類別表現最佳之方法。*

| 類別 (Category) | AE (SSIM) | AE (L2) | AnoGAN | CNN Feature Dictionary | Texture Inspection | Variation Model |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Carpet** | **0.69** / 0.87 | 0.38 / 0.59 | 0.34 / 0.54 | 0.20 / 0.72 | 0.29 / **0.88** | - |
| **Grid** | **0.88** / **0.94** | 0.83 / 0.90 | 0.04 / 0.58 | 0.02 / 0.59 | 0.01 / 0.72 | - |
| **Leather** | 0.71 / 0.78 | 0.67 / 0.75 | 0.34 / 0.64 | 0.74 / 0.87 | **0.98** / **0.97** | - |
| **Tile** | 0.04 / 0.59 | **0.23** / 0.51 | 0.08 / 0.50 | 0.14 / **0.93** | 0.11 / 0.41 | - |
| **Wood** | 0.36 / 0.73 | 0.29 / 0.73 | 0.14 / 0.62 | 0.47 / **0.91** | **0.51** / 0.78 | - |
| **Bottle** | 0.15 / **0.93** | **0.22** / 0.86 | 0.05 / 0.86 | 0.07 / 0.78 | - | 0.03 / 0.82 |
| **Cable** | 0.01 / 0.82 | 0.05 / **0.86** | 0.01 / 0.78 | **0.13** / 0.79 | - | - |
| **Capsule** | 0.09 / **0.94** | **0.11** / 0.88 | 0.04 / 0.84 | 0.00 / 0.84 | - | 0.01 / 0.76 |
| **Hazelnut** | 0.00 / **0.97** | **0.41** / 0.95 | 0.02 / 0.87 | 0.00 / 0.72 | - | - |
| **Metal Nut** | 0.01 / **0.89** | **0.26** / 0.86 | 0.00 / 0.76 | 0.13 / 0.82 | - | 0.19 / 0.60 |
| **Pill** | 0.07 / **0.91** | **0.25** / 0.85 | 0.17 / 0.87 | 0.00 / 0.68 | - | 0.13 / 0.83 |
| **Screw** | 0.03 / **0.96** | **0.34** / **0.96** | 0.01 / 0.80 | 0.00 / 0.87 | - | 0.12 / 0.94 |
| **Toothbrush** | 0.08 / 0.92 | **0.51** / **0.93** | 0.07 / 0.90 | 0.00 / 0.77 | - | 0.24 / 0.68 |
| **Transistor** | 0.01 / **0.90** | **0.22** / 0.86 | 0.08 / 0.80 | 0.03 / 0.66 | - | - |
| **Zipper** | 0.10 / **0.88** | **0.13** / 0.77 | 0.01 / 0.78 | 0.00 / 0.76 | - | - |

---

## 6. 各方法失敗案例與限制（Limitations）

### 6.1 論文明確指出的限制與失敗分析（出自論文 Sec. 4.4, p. 7–8）
1. **無單一方法能通吃所有類別**：實驗顯示沒有任何一個受測方法能在全部 **15** 個紋理與物件類別上穩定取得最佳表現（出自論文 p. 7 Sec. 4.4）。
2. **無異常影像下之分割閾值估計極度困難**：Table 3 顯示許多方法（如 `AE (SSIM)` 在 `Hazelnut` 拿到 **0.97** ROC AUC，但 PRO 僅 **0.00**）雖然異常圖能有效凸顯異常（高 ROC AUC），卻因僅靠無缺陷驗證集估計出的二值化閾值不佳，導致實際分割重疊率（PRO）極低（出自論文 p. 7 Table 3 & Sec. 4.4）。
3. **各方法固有弱點**（出自論文 p. 8 Sec. 4.4.1–4.4.5）：
   - **AnoGAN**：容易發生 Mode Collapse，難以處理形狀或朝向變化大的物件，也無法重建 `Pill` 上的彩色細微斑點或 `Carpet` 的細緻紋理變化，且潛在空間迭代搜尋耗時極長（亦見 p. 5 Sec. 4.1.1）。
   - **AE (L2) 與 AE (SSIM)**：在物件類別整體表現最佳，但透過 Bottleneck 重建會丟失高頻細節導致影像模糊，因此在 `Tile` 與 `Zipper` 等高頻紋理上會產生大量假陽性（False Positives）。此外 `AE (SSIM)` 僅能處理灰階影像（亦見 p. 5 Sec. 4.1.2）。
   - **CNN Feature Dictionary**：在除 `Grid` 以外的紋理類別上 ROC AUC 表現穩定，但因未納入特徵的空間位置資訊（Spatial location），在物件類別上表現明顯退化，且滑動視窗導致異常圖粗糙（亦見 p. 4 Sec. 2.2.3）。
   - **GMM Texture Inspection**：在 `Grid` 等細小缺陷上靈敏度不足，且因轉為灰階運算而無法偵測色彩缺陷。
   - **Variation Model**：必須依賴嚴格的事前形狀對齊（僅 **6** 個物件類別可用），且無法容忍物件表面的正常隨機變化（例如 `Capsule` 上位置不固定的印刷字樣會被誤判為缺陷）。

### 6.2 延伸洞見（AI 整理）
- **（AI 整理）確立工業異常檢測三大演進方向**：MVTec AD 的初始 Benchmark 清楚揭示了早期三大路線的瓶頸——「Autoencoder 重建高頻模糊」、「GAN 潛在搜尋慢且易崩潰」、「早期的預訓練 CNN 特徵字典缺乏空間位置與多尺度細節」。這直接促成了後續兩大主流技術突破：
  1. **改良重建路線**：透過將問題轉為「遮罩修復（Inpainting，如 RIAD）」或「擴散模型去噪重建（Diffusion，如 DiffusionAD）」來解決 Autoencoder 模糊與恆等映射問題。
  2. **深耕預訓練特徵嵌入路線**：保留預訓練 CNN 不同層級的空間特徵圖並建立局部 Patch 記憶庫（如 PatchCore），克服早期 `CNN Feature Dictionary` 丟失空間資訊與解析度粗糙的缺陷。

---

## 7. 相關 Wiki 頁面連結

- **資料集與評估指標**：
  - [MVTec AD 資料集與評估指標](../datasets/mvtec-ad.md)
  - [MVTec AD 2 資料集與進階評估協定（AU-PRO0.05、F1 與光照分佈偏移）](../datasets/mvtec-ad-2.md)
- **核心概念**：
  - [非監督式視覺異常檢測（Unsupervised Anomaly Detection）](../concepts/unsupervised-anomaly-detection.md)
  - [遮罩修復重建與多尺度梯度相似度（Reconstruction by Inpainting & MSGMS）](../concepts/reconstruction-by-inpainting.md)
  - [局部特徵記憶庫與核心集下採樣（Patch-Level Memory Bank & Coreset Subsampling）](../concepts/memory-bank.md)
  - [規範引導一步去噪與合成異常分割（Norm-Guided One-Step Denoising & Anomaly Synthesis）](../concepts/norm-guided-one-step-denoising.md)
  - [潛在空間記憶庫引導去噪與引導尺度圖（Latent Diffusion with MBG & GSM）](../concepts/memory-bank-guided-latent-diffusion.md)
- **跨論文流派比較**：
  - [預訓練特徵嵌入 vs. 重建式異常檢測流派對比](../comparisons/embedding-vs-reconstruction.md)
- **於本資料集評估之衍生／後續方法與二代基準**：
  - [Zavrtanik et al. (2021) — RIAD](zavrtanik2021-riad.md)
  - [Roth et al. (2022) — PatchCore](roth2022-patchcore.md)
  - [Zhang et al. (2023/2025) — DiffusionAD](zhang2023-diffusionad.md)
  - [Lee & Kang (2026) — LAMBDA](lee2026-lambda.md)
  - [Heckler-Kram et al. (2025) — MVTec AD 2](hecklerkram2025-mvtec-ad-2.md)
