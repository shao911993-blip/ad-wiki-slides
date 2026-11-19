---
title: "非監督式視覺異常檢測（Unsupervised Visual Anomaly Detection）"
type: "concept"
tags: ["Unsupervised Anomaly Detection", "One-Class Classification", "Anomaly Segmentation", "Autoencoder", "Feature Descriptor"]
sources: ["bergmann2019-mvtec-ad.pdf"]
updated: "2026-11-14"
---

# 非監督式視覺異常檢測（Unsupervised Visual Anomaly Detection）

## 1. 概念定義與問題設定

**非監督式視覺異常檢測（Unsupervised Visual Anomaly Detection，亦常稱為 One-Class Anomaly Detection）** 旨在僅使用**無缺陷正常影像（Defect-free / Normal images）**進行訓練的情況下，於測試階段自動判斷輸入影像是否包含未知異常（影像級分類），並精確標示出異常發生的像素區域（像素級分割）（出自 `bergmann2019-mvtec-ad.pdf` p. 1–2 Sec. 1）。

此設定源於真實工業光學檢測的兩大結構性限制（出自 `bergmann2019-mvtec-ad.pdf` p. 2 Sec. 1）：
1. **缺陷類型事前未知**：製造過程中可能出現各種未曾預見的表面刮痕、污染、結構變形或缺件，無法事先窮舉所有異常類別。
2. **異常樣本極度稀缺**：工業產線經過高度優化以降低不良率，可取得的異常樣本極少，但正常良品影像卻非常充足。

---

## 2. 初學者版（AI 整理）

> **（AI 整理）**
> - **什麼是「只看良品學抓瑕疵」？（直覺比喻）**
>   一般的影像分類AI（監督式學習）就像是給學徒看 **1,000** 張貓跟 **1,000** 張狗的照片，教他分辨貓狗；但在工廠品管裡，生產線一天做出一萬顆完美螺絲，可能只出現兩顆瑕疵品，而且下週出現的瑕疵長相還跟這週完全不同！
>   因此，「非監督式異常檢測」採取的策略就像訓練一位**資深驗鈔員**：不給他背假鈔圖鑑，而是讓他把「真鈔的每一處紋理、字樣與結構」摸得滾瓜爛熟。當一張假鈔出現時，只要有任何一個小角落跟記憶中的完美真鈔對不上，驗鈔員就能立刻指出：「這裡不對勁！」
> - **早期學者怎麼讓 AI 當驗鈔員？（兩大直覺思路）**
>   1. **重畫對照法（生成／重建流派，如 Autoencoder、AnoGAN）**：只教 AI 畫完美良品。測試時拿一張瑕疵品給 AI 看並叫它重畫一張；因為 AI 只會畫良品，它畫出來的圖會把瑕疵「修補成正常的樣子」（或者畫壞掉）。把「原圖」跟「AI 重畫的圖」一相減，有差異的地方就是瑕疵！
>   2. **局部特徵比對法（預訓練特徵流派，如 CNN Feature Dictionary）**：借用已經看過百萬張自然影像的預訓練神經網路（如 ResNet-18）當作「視覺觀察員」，把正常影像切成許多小區塊（Patches），記錄正常區塊的特徵分佈（例如聚成 **10** 個群心）；測試時只要某個小區塊的特徵離所有正常群心都很遠，就判定為異常。

---

## 3. 核心任務區分與早期主流流派（出自 `bergmann2019-mvtec-ad.pdf` Sec. 2, p. 2–4 & Sec. 4, p. 5–8）

### 3.1 粗粒度分類 vs. 細粒度局部異常分割
- **傳統 Outlier Detection（跨類別異常）**：早年常將 `MNIST`、`CIFAR10`、`ImageNet` 的少數類別標為 Outlier，其餘類別作為 Inlier 訓練。然而這類異常與正常樣本屬於完全不同的語意類別（整張圖截然不同），無法驗證模型對於「與正常資料流形極為接近、僅在微小局部區域出現偏差」之真實工業異常的偵測能力（出自 `bergmann2019-mvtec-ad.pdf` p. 1–2 Sec. 1 & Sec. 2.1.1）。
- **像素級異常分割（Anomaly Segmentation）**：工業檢測不僅需要二元判定整張影像是否異常，更需要輸出單通道的**空間異常圖（Spatial Anomaly Map）**，並透過在無缺陷驗證集上估計之閾值轉為二值化分割遮罩（出自 `bergmann2019-mvtec-ad.pdf` p. 2 Sec. 1、p. 6 Sec. 4.3）。

### 3.2 早期四大基礎流派與代表方法
根據 [Bergmann et al. (2019)](../papers/bergmann2019-mvtec-ad.md) 在 [MVTec AD](../datasets/mvtec-ad.md) 上的基準評估，早期非監督式視覺異常檢測主要分為四大技術路線（出自 `bergmann2019-mvtec-ad.pdf` p. 3–6 Sec. 2.2 & Sec. 4.1）：

| 技術流派 | 代表方法 | 核心運作機制 | 關鍵限制（出自論文 Sec. 4.4, p. 7–8） |
| :--- | :--- | :--- | :--- |
| **1. 深度自編碼器重建**<br>*(Deep Convolutional Autoencoders)* | `AE (L2)`<br>`AE (SSIM)` | 透過 Bottleneck 潛在空間（維度 **100**）壓縮並重建正常影像；以像素級 $\ell^2$ 距離或結構相似度（`SSIM`，視窗 **11 × 11**）計算重建誤差作為異常圖。 | 物件類別表現相對最佳，但 Bottleneck 會抹除高頻細節導致重建模糊，在 `Tile`、`Zipper` 等高頻紋理產生大量假陽性。 |
| **2. 生成對抗網路重建**<br>*(Generative Adversarial Networks)* | `AnoGAN` | 在正常影像上訓練 GAN（潛在維度 **64**）；測試時透過 **300** 次梯度迭代在潛在空間搜尋最接近輸入影像的生成樣本，比較像素級 $\ell^2$ 差異。 | 訓練易發生 Mode Collapse；面對姿態多變物件或複雜紋理（如 `Carpet`）無法收斂出良好重建，且測試期迭代搜尋極慢。 |
| **3. 預訓練 CNN 特徵描述符**<br>*(Pre-trained CNN Features)* | `CNN Feature Dictionary` | 擷取 ImageNet 預訓練 `ResNet-18` 的 **512** 維特徵，經 PCA（保留 **95%** 變異量，約 **100** 維）與 K-means（**10** 個群心）建立正常特徵字典，於 **16 × 16** 區塊滑動比對。 | 在多數紋理類別上 ROC AUC 穩定，但未保留特徵的空間位置資訊（Spatial location），在結構化物件類別上表現退化，且滑動視窗異常圖粗糙。 |
| **4. 傳統機器視覺統計模型**<br>*(Traditional Statistical Models)* | `GMM Texture Inspection`<br>`Variation Model` | `GMM` 在 **4** 層影像金字塔上對 **7 × 7** 區塊建模負對數概似值；`Variation Model` 則對齊物件輪廓後計算每像素灰階平均值與標準差（**30** 張訓練影像）。 | `GMM` 僅限規則紋理且轉灰階無法抓色彩缺陷；`Variation Model` 強制要求精確剛性對齊，無法處理表面有隨機字樣（如 `Capsule`）或可變形物件。 |

---

## 4. 相關 Wiki 頁面連結

- **基準資料集**：[MVTec AD 資料集與評估指標](../datasets/mvtec-ad.md)、[MVTec AD 2 資料集與進階評估協定（AU-PRO0.05、F1 與光照分佈偏移）](../datasets/mvtec-ad-2.md)
- **跨論文流派比較**：[預訓練特徵嵌入 vs. 重建式異常檢測流派對比](../comparisons/embedding-vs-reconstruction.md)
- **單篇論文解析**：
  - [Bergmann et al. (2019) — MVTec AD](../papers/bergmann2019-mvtec-ad.md)
  - [Ho et al. (2020) — DDPM](../papers/ho2020-ddpm.md)
  - [Zavrtanik et al. (2021) — RIAD](../papers/zavrtanik2021-riad.md)
  - [Roth et al. (2022) — PatchCore](../papers/roth2022-patchcore.md)
  - [Zhang et al. (2023/2025) — DiffusionAD](../papers/zhang2023-diffusionad.md)
  - [Lee & Kang (2026) — LAMBDA](../papers/lee2026-lambda.md)
  - [Heckler-Kram et al. (2025) — MVTec AD 2](../papers/hecklerkram2025-mvtec-ad-2.md)
- **相關核心概念**：
  - [去噪擴散機率模型（Denoising Diffusion Probabilistic Models, DDPM）](denoising-diffusion-probabilistic-models.md)
  - [遮罩修復重建與多尺度梯度相似度（Reconstruction by Inpainting & MSGMS）](reconstruction-by-inpainting.md)
  - [局部特徵記憶庫與核心集下採樣（Patch-Level Memory Bank & Coreset Subsampling）](memory-bank.md)
  - [規範引導一步去噪與合成異常分割（Norm-Guided One-Step Denoising & Anomaly Synthesis）](norm-guided-one-step-denoising.md)
  - [潛在空間記憶庫引導去噪與引導尺度圖（Latent Diffusion with MBG & GSM）](memory-bank-guided-latent-diffusion.md)
