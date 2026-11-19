---
title: "預訓練特徵嵌入 vs. 重建式異常檢測流派對比（Feature Embedding vs. Reconstruction-Based AD）"
type: "comparison"
tags: ["Comparison", "Feature Embedding", "Memory Bank", "Reconstruction", "Inpainting", "Diffusion Model", "Latent Diffusion", "Autoencoder", "PatchCore", "RIAD", "DiffusionAD", "LAMBDA"]
sources: ["bergmann2019-mvtec-ad.pdf", "ho2020-ddpm.pdf", "zavrtanik2021-riad.pdf", "roth2022-patchcore.pdf", "zhang2023-diffusionad.pdf", "lee2026-lambda.pdf", "hecklerkram2025-mvtec-ad-2.pdf"]
updated: "2026-11-14"
---

# 預訓練特徵嵌入 vs. 重建式異常檢測流派對比（Feature Embedding vs. Reconstruction-Based AD）

## 1. 比較維度與脈絡概述

在非監督式視覺異常檢測（[Unsupervised Visual Anomaly Detection](../concepts/unsupervised-anomaly-detection.md)）的發展歷程中，面對「訓練期僅有無缺陷正常樣本（Nominal-only / Cold-start）」的核心限制，學界演化出兩大截然不同的主流技術典範，並在後續進一步融合出「擴散重建 + 判別分割」與「潛在擴散 + 記憶庫引導」的新世代架構（出自 `bergmann2019-mvtec-ad.pdf` p. 3–4 Sec. 2.2、`zavrtanik2021-riad.pdf` p. 1–2 Sec. 1–2、`roth2022-patchcore.pdf` p. 1–3 Sec. 1–2、`zhang2023-diffusionad.pdf` p. 1–3 Sec. I–II、`lee2026-lambda.pdf` p. 1–4 Sec. 1–3）：

1. **重建式異常檢測流派（Reconstruction-Based Methods）**：
   - **核心假設**：在正常樣本上訓練生成模型或自編碼器（如 `AE (SSIM/L2)`、`AnoGAN`、遮罩修補 [RIAD](../papers/zavrtanik2021-riad.md)、自編碼器結合分割 `DRAEM`，以及基於 [DDPM](../papers/ho2020-ddpm.md) 的一步去噪擴散模型 [DiffusionAD](../papers/zhang2023-diffusionad.md) 與潛在空間記憶庫引導擴散模型 [LAMBDA](../papers/lee2026-lambda.md)），使網路僅學會將受損或加噪影像恢復為正常視覺結構；測試時比對輸入影像與無異常重建影像（透過規則式梯度指標或端到端分割網路），定位重建差異區域。
2. **預訓練特徵嵌入與記憶庫流派（Pretrained Feature Embedding & Memory Bank Methods）**：
   - **核心假設**：不訓練像素重建網路，直接借用大型外部自然影像資料集（如 `ImageNet`）預訓練之深層網路（如 `ResNet` / `WideResNet`），將正常樣本的深層／中階特徵分布記錄下來（如早期的 `CNN Feature Dictionary`、師生知識蒸餾 `Uninformed Students` / `RD4AD` / `RD++`、高斯分佈 `PaDiM`、全量記憶庫 `SPADE` 與核心集記憶庫 [PatchCore](../papers/roth2022-patchcore.md)）；測試時透過特徵空間的距離度量直接定位偏離正常特徵流形的異常區域。
3. **跨流派融合典範（Hybrid Memory Bank-Guided Latent Diffusion，[LAMBDA](../papers/lee2026-lambda.md)）**：
   - **核心假設**：結合預訓練 `VAE` 潛在空間壓縮、正常潛在記憶庫（`Memory Bank` $\mathcal{M}_b$）與一步去噪擴散重建（`MBG` + `GSM`），利用記憶庫中檢索出的最相似正常原型與距離統計標準化圖來引導單步擴散去噪，一舉消除像素空間雙尺度擴散的高昂記憶體成本與推論延遲。

---

## 2. 初學者版（AI 整理）

> **（AI 整理）**
> - **抓瑕疵的兩大門派與最新進化：「臨摹畫家派（重建法）」vs.「顯微鏡相簿派（特徵嵌入法）」**
>   1. **早期臨摹畫家派（Reconstruction，如 Autoencoder、RIAD、DRAEM）**：
>      請一位畫家看著數百張良品零件苦練畫功。測試時把零件遮住一部分（[RIAD](../papers/zavrtanik2021-riad.md) 挖洞 `Mask-to-Norm`），叫畫家把零件重畫出來，再拿原圖跟畫作比對。
>      - **早期痛點**：如果用自編碼器（如 `DRAEM`），畫家容易把瑕疵照抄畫出來（異常不變重建）或把正常複雜紋路畫糊（正常粗糙重建）；如果用挖洞修補（`RIAD`），遇到隨機方向的螺絲或電線很容易畫歪誤報（AI 整理）。
>   2. **顯微鏡相簿派（Pretrained Feature Embedding，如 PaDiM、PatchCore）**：
>      完全不訓練畫家！直接拿一台已經調校好的「超級顯微鏡（ImageNet 預訓練網路）」，把良品零件的每個 $3 \times 3$ 小區塊特徵拍下來，挑出最具代表性的 **1%～25%** 存進「記憶相簿（[Memory Bank](../concepts/memory-bank.md)）」。測試時只要翻相簿找「有沒有看過類似的正常區塊」就完成了！
>      - **優點與邊界**：**免訓練（Training-free）**、推論極快（`PatchCore-1%` 僅 **0.17** 秒／張），在 [MVTec AD](../datasets/mvtec-ad.md) 上達 **99.1%～99.6%** Image AUROC；但若待測影像與 `ImageNet` 差異過大，或需要極高精度的像素邊界（如 Pixel AP），固定解析度的預訓練特徵仍有極限（AI 整理）。
>   3. **新世代擴散畫家 + 找碴裁判派（[DiffusionAD](../papers/zhang2023-diffusionad.md)）**：
>      改請「擴散模型（[DDPM](../papers/ho2020-ddpm.md)）」當畫家，往圖片撒上薄厚兩種高斯雜訊沙子（`Noise-to-Norm`），利用**規範引導一步去噪（[NOD](../concepts/norm-guided-one-step-denoising.md)）**在 **1 步之內（`23.5 FPS`）**同時抹除大塊異常並保留銳利背景細節，最後交給專屬的「找碴裁判（Segmentation U-Net）」直接畫出瑕疵邊界——在 MVTec AD（`99.7%` I-AUROC / `76.1%` AP）與 VisA（`98.8%` I-AUROC）上一舉超越兩大舊門派（AI 整理）！
>   4. **兩大門派終極合體：帶著記憶相簿的輕量擴散畫家（[LAMBDA](../papers/lee2026-lambda.md)）**：
>      `DiffusionAD` 雖然準，但要在高清原圖上撒兩次沙子，訓練時得吃掉 **48.4 GB** 顯卡記憶體！`LAMBDA` 把「相簿派」跟「擴散畫家派」合而為一：先用預訓練 `VAE` 把圖片縮小 64 倍變成「潛在明信片」，並把 **200 張正常良品明信片**收進相簿（`MBG`），搭配「分區施力地圖（`GSM`）」只跑**單次一步去噪**——結果訓練顯卡記憶體狂降 **80.8%**（只剩 **9.3 GB**），推論速度飆上 **42.3 FPS**，還能在醫療影像（`BMAD`）拿下第一名（AI 整理）！

---

## 3. 各流派核心機制與優劣對照表

| 比較維度 | 重建式：傳統 AE / GAN<br>(`AE-SSIM`, `AE-L2`, `AnoGAN`) | 重建式：遮罩修補重建<br>([RIAD](../papers/zavrtanik2021-riad.md)) | 預訓練特徵：核心集記憶庫<br>([PatchCore](../papers/roth2022-patchcore.md)) | 重建 + 分割：一步擴散規範引導<br>([DiffusionAD](../papers/zhang2023-diffusionad.md)) | 混合流派：潛在擴散 + 記憶庫引導<br>([LAMBDA](../papers/lee2026-lambda.md)) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **代表論文與年份** | [Bergmann et al. (CVPR 2019)](../papers/bergmann2019-mvtec-ad.md) | [Zavrtanik et al. (PR 2021)](../papers/zavrtanik2021-riad.md) | [Roth et al. (2022)](../papers/roth2022-patchcore.md) | [Zhang et al. (2023/2025)](../papers/zhang2023-diffusionad.md) | [Lee & Kang (ASOC 2026)](../papers/lee2026-lambda.md) |
| **是否需在目標資料集訓練網路權重** | **需要**（逐類別訓練 AE 或 GAN） | **需要**（逐類別訓練 `U-Net` **300** Epochs） | **完全免訓練（Cold-start）**，僅前向擷取特徵與貪婪核心集挑選 | **需要**（像素空間聯合訓練擴散與分割 U-Net **3000** Epochs） | **需要**（預訓練 `VAE` 凍結，潛在空間聯合訓練去噪與分割網路 **3000** Epochs） |
| **阻斷異常洩漏／捕捉異常的核心機制** | 低維度 Bottleneck（維度 **100** 或 **64**）限制容量 | 隨機將 $k \times k$ 網格分為 $n=3$ 組互斥遮罩置零（`Mask-to-Norm`） | 中階層級（`2+3`）+ $3 \times 3$ 局部鄰域池化 + 貪婪核心集 $\mathcal{M}_C$ 全域最近鄰距離 | 前向高斯加噪（`Noise-to-Norm`）+ 雙尺度規範引導一步去噪（`NOD`, $t_s=200, t_b=400$） | `VAE` $64\times$ 空間降維 + 記憶庫 $\mathcal{M}_b$ ($n_m=200$) 檢索 `MBG` + 空間引導尺度圖 `GSM` ($t_s=200$) |
| **異常評分空間** | 像素空間（$\ell_2$ 或單尺度 `SSIM`） | 像素梯度空間（**4** 尺度 Prewitt 梯度幅值相似度 `MSGMS`） | 預訓練 CNN 中階 Patch 特徵空間（$\ell_2$ 最近鄰距離 + 密度重加權） | 端到端 `Segmentation U-Net` 比對 $\text{Concat}(x_0, \hat{x}_{0_g})$ 輸出 $\hat{M}$ | 端到端 `Segmentation U-Net` 比對 $\text{Concat}(I', \hat{I})$ 輸出 $\hat{M}$（Top $K=50$） |
| **對影像未對齊與跨領域場景的強健性** | `AE` 尚可；`AnoGAN` 對姿態變化極敏感 | 高（捲積修補具平移不變性，但複雜物件邊緣易重建模糊） | **極高**（全域共享記憶庫 $\mathcal{M}_C$；但 `VisA` `macaroni2` 為 `78.1%`） | **極高**（於 `VisA` 達 `98.8%` I-AUROC；`BMAD` 醫療基準 `83.4%` I-AUROC） | **極高**（`GSM` 依記憶庫距離統計動態校準，於 `VisA` 達 `98.1%`、於 `BMAD` 醫療基準達 **`87.1%`** 居冠，出自 `lee2026-lambda.pdf` Tables 1–2） |
| **單張影像推論速度與計算資源消耗** | `AE` 快；`AnoGAN` 需 **300** 次迭代極慢 | 需對 $N_K=4$ 尺度 $\times$ $n=3$ 子集共執行 **12 次 `U-Net` 前向推論** | **極快且省資源**（`PatchCore-1%` 僅 **0.17 s**／張，出自 `roth2022-patchcore.pdf` Table 5） | **快但吃記憶體**（`23.5 FPS`；在 `VisA` 評測中訓練需 **`48.4 GB`**、推論 **`12.4 GB`**，出自 `lee2026-lambda.pdf` Table 1） | **極快且極省記憶體**（推論達 **`42.3 FPS` / `23.6 ms`**，訓練僅需 **`9.3 GB`**［省 `80.8%`］、推論 **`5.8 GB`**［省 `53.2%`］，出自 `lee2026-lambda.pdf` Table 1） |
| **主要限制（出自各論文）** | Bottleneck 抹除高頻細節導致重建模糊；容量過大則連異常一起重建 | 隨機紋理區域難以由鄰域猜出；純色彩異常在 `MSGMS` 反應較弱 | 受限於 `ImageNet` 預訓練特徵可遷移性；特徵圖上採樣使 Pixel AP（`56.1%`）受限 | 依賴預定義固定加噪尺度 $(t_s, t_b)$ 與像素空間高昂訓練記憶體（`48.4 GB`） | 預訓練 `VAE` 有損壓縮帶來微小精度取捨（無 VAE 變體可達 `99.0%` 但耗 `33.8 GB`）；需調優記憶庫大小 $n_m$（出自 `lee2026-lambda.pdf` Table 1, Table 4 & Sec. 6） |

---

## 4. MVTec AD 量化數據綜合比較（標明出處）

以下匯總已收錄論文中於 [MVTec AD](../datasets/mvtec-ad.md)（全 **15** 類別平均）之量化基準表現：

| 方法名稱 | 所屬流派 | 紋理平均 (5 類)<br>Image / Pixel AUROC (%) | 物件平均 (10 類)<br>Image / Pixel AUROC (%) | 全 15 類平均<br>Image AUROC (%) | 全 15 類平均<br>Pixel AUROC (%) | 全 15 類平均<br>PRO (%) | 數據出處 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **AE (SSIM)** | 重建式（自編碼器） | - / 78.2 | - / 90.2 | - | 86.2 *(或 87.0)* | 69.4 | `zavrtanik2021-riad.pdf` Table 2 (p. 6)；括號與 PRO 出自 `roth2022-patchcore.pdf` Tables 2–3 (p. 6–7) |
| **AnoGAN** | 重建式（GAN 搜尋） | - / 57.7 | - / 82.6 | - | 74.3 | - | `zavrtanik2021-riad.pdf` Table 2 (p. 6) |
| **GANomaly** | 重建式（對抗自編碼器） | 76.5 / - | 75.4 / - | 76.2 | - | - | `zavrtanik2021-riad.pdf` Table 1 (p. 6) & `roth2022-patchcore.pdf` Table S1 (p. 15) |
| **ITAE** | 重建式（逆變換自編碼器） | 82.2 / - | 84.8 / - | 83.9 | - | - | `zavrtanik2021-riad.pdf` Table 1 (p. 6) & `roth2022-patchcore.pdf` Table S1 (p. 15) |
| **[RIAD](../papers/zavrtanik2021-riad.md)** | 重建式（多尺度遮罩修補 + MSGMS） | 95.1 / 93.9 | 89.9 / 94.3 | 91.7 | 94.2 | - | `zavrtanik2021-riad.pdf` Tables 1–2 (p. 6) |
| **Uninformed Students (US)** *(註)* | 預訓練特徵（師生知識蒸餾） | 91.5 / 93.2 | 85.8 / 94.3 | 87.7 | 93.9 | 85.7 | Image/Pixel 出自 `zavrtanik2021-riad.pdf` Tables 1–2 (p. 6)；PRO 出自 `roth2022-patchcore.pdf` Table 3 (p. 7) |
| **SPADE** | 預訓練特徵（多階層記憶庫 kNN） | - / 92.9 *(AI 整理)* | - / 97.6 *(AI 整理)* | 85.5 | 96.0 | 91.7 | `roth2022-patchcore.pdf` Tables 1–3 (p. 6–7) & Table S2 (p. 15) |
| **PatchSVDD** | 自監督局部特徵 SVDD | 94.5 / 93.7 *(AI 整理)* | 90.8 / 96.7 *(AI 整理)* | 92.1 | 95.7 | - | `roth2022-patchcore.pdf` Tables 1–2 (p. 6) & Tables S1–S2 (p. 15) |
| **DifferNet** | 預訓練特徵 + Normalizing Flows | 94.6 / - *(AI 整理)* | 94.7 / - *(AI 整理)* | 94.9 | - | - | `roth2022-patchcore.pdf` Table 1 (p. 6) & Table S1 (p. 15) |
| **PaDiM** (`PaDiM*`) | 預訓練特徵（位置高斯 Mahalanobis） | - / 96.9 *(AI 整理)* | - / 97.9 *(AI 整理)* | 95.3 (**97.9**) | 97.5 | 92.1 | `roth2022-patchcore.pdf` Tables 1–3 (p. 6–7) & Table S2 (p. 15) |
| **[PatchCore-25%](../papers/roth2022-patchcore.md)** | 預訓練特徵（中階局部記憶庫 + Coreset） | 99.0 / 97.5 *(AI 整理)* | 99.2 / 98.4 *(AI 整理)* | **99.1** | **98.1** | 93.4 | `roth2022-patchcore.pdf` Tables 1–3 (p. 6–7) & Tables S1–S3 (p. 15) |
| **[PatchCore-10%](../papers/roth2022-patchcore.md)** | 預訓練特徵（中階局部記憶庫 + Coreset） | 98.9 / 97.6 *(AI 整理)* | 98.9 / 98.4 *(AI 整理)* | 99.0 | **98.1** | **93.5** | `roth2022-patchcore.pdf` Tables 1–3 (p. 6–7) & Tables S1–S3 (p. 15) |
| **[PatchCore-1%](../papers/roth2022-patchcore.md)** | 預訓練特徵（100 倍壓縮 Coreset） | 99.0 / 97.6 *(AI 整理)* | 99.0 / 98.1 *(AI 整理)* | 99.0 | 98.0 | 93.1 | `roth2022-patchcore.pdf` Tables 1–3 (p. 6–7) & Tables S1–S3 (p. 15) |
| **[PatchCore-1% (Ensemble, 320)](../papers/roth2022-patchcore.md)** | 預訓練特徵（3 骨幹整合 + 高解析度） | - | - | **99.6** | **98.2** *(WRN101 1+2+3 達 **98.4**)* | **94.9** *(WRN101 1+2+3 達 **95.0**)* | `roth2022-patchcore.pdf` Table 4 (p. 7) & Table S4 (p. 15) |
| **DRAEM** | 重建 + 分割（AE 重建 + 合成異常 U-Net） | 99.1 / 97.9 *(AI 整理)* | 97.4 / 97.0 *(AI 整理)* | 98.0 | 97.3 | 92.1 *(AP: 68.4)* | `zhang2023-diffusionad.pdf` Tables III–V (p. 8–9) |
| **RD4AD** | 預訓練特徵（反向知識蒸餾） | 99.5 / 98.5 *(AI 整理)* | 98.3 / 97.5 *(AI 整理)* | 98.5 | 97.8 | 93.9 *(AP: 58.0)* | `zhang2023-diffusionad.pdf` Tables III–V (p. 8–9) |
| **RD++** | 預訓練特徵（改良反向知識蒸餾） | 99.8 / 98.1 *(AI 整理)* | 99.3 / 98.4 *(AI 整理)* | 99.4 | 98.3 | 95.0 *(AP: 60.8)* | `zhang2023-diffusionad.pdf` Tables III–V (p. 8–9) |
| **SimpleNet** | 預訓練特徵 + 特徵空間異常合成判別 | 99.1 / 97.0 *(AI 整理)* | 99.8 / 97.9 *(AI 整理)* | 99.6 | 97.6 | 90.0 *(AP: 54.8)* | `zhang2023-diffusionad.pdf` Tables III–V (p. 8–9) |
| **[DiffusionAD](../papers/zhang2023-diffusionad.md)** | 重建 + 分割（雙尺度一步擴散 `NOD` + U-Net） | 99.8 / 99.0 *(AI 整理)* | 99.6 / 98.4 *(AI 整理)* | **99.7** | **98.7** | **95.7** *(AP: **76.1**)* | `zhang2023-diffusionad.pdf` Tables III–VI (p. 8–9) |
| **DDAD** | 重建式（單階段條件去噪擴散） | 94.1 / 93.4 | 99.4 / 97.8 | 97.7 | 96.3 | 86.3 *(P-AP: 55.4)* | `lee2026-lambda.pdf` Table A.2 (p. 13) |
| **D3AD** | 重建式（單階段動態加噪擴散） | 89.0 / 94.9 | 95.3 / 97.3 | 93.1 | 96.5 | 90.7 *(P-AP: 54.2)* | `lee2026-lambda.pdf` Table A.2 (p. 13) |
| **[LAMBDA](../papers/lee2026-lambda.md)** | 混合流派（預訓練 VAE 潛在擴散 + `MBG` + `GSM` + 分割） | 99.6 / 99.3 | 97.6 / 96.6 | 98.2 | 97.5 | 94.9 *(P-AP: 69.1, mAD: 91.8)* | `lee2026-lambda.pdf` Tables 5–6 (p. 10) & Table A.2 (p. 13) |

*註 1：`Uninformed Students (US)` 列之 Image/Pixel AUROC 為 RIAD 作者重新實作之版本（`zavrtanik2021-riad.pdf` Sec. 4.2）；PRO `85.7` 為 PatchCore 引用之原始 US 結果（`roth2022-patchcore.pdf` Table 3）；兩者實作不同，不宜直接比較。*
*註 2：`lee2026-lambda.pdf` Table A.2 (p. 13) 亦報告其重評測之 `DiffusionAD` 為 `99.5 / 98.4 / 96.0`（P-AP: `77.9%`，紋理平均 `99.9 / 99.5`、物件平均 `99.3 / 97.9`）與 `DRAEM*` 為 `98.5 / 97.4 / 93.7`（P-AP: `69.0%`）；且於 `VisA` 與醫療基準 `BMAD` 上，`LAMBDA` 展示跨領域泛化與輕量化優勢（於 `BMAD` 按 `Image AUROC / Image AP / Pixel AUROC / Pixel AP / AUPRO` 欄位順序，`LAMBDA` 平均達 `87.1 / 88.1 / 90.3 / 41.8 / 70.2`［mAD `75.5`］，超越 `DiffusionAD` 的 `83.4 / 85.9 / 86.9 / 39.9 / 68.2`［mAD `72.9`］，出自 `lee2026-lambda.pdf` Table 2, p. 9）。*

### 4.2 新世代高難度基準 MVTec AD 2 跨流派重評測與光照偏移強健性對比（出自 `hecklerkram2025-mvtec-ad-2.pdf` Table 1, p. 2 & Tables 7–12, p. 10, 15）

> **重要指標、欄位順序與出處說明**：
> 1. 下表數據全部出自 [Heckler-Kram et al. (2025) — MVTec AD 2](../papers/hecklerkram2025-mvtec-ad-2.md)。該論文同時使用兩種不同假陽性率積分上限之指標：**$\text{AU-PRO}_{0.30}$**（FPR 積分上限 `0.30`，用於 `Table 1` 與 `Table 9`）與 **$\text{AU-PRO}_{0.05}$**（FPR 積分上限 `0.05`，用於 `Table 7`、`Table 10` 與 `Table 11`），兩者嚴格分列於不同欄位，不可混在同一欄或直接比較。
> 2. `Table 1` 中之 `MVTec AD` 與 `VisA` 數據為該篇作者於統一無場景調參協定下彙整／重新評測之 **$\text{AU-PRO}_{0.30}$**（%），與上方 §4 主表各原論文報告之 PRO 設定不同，故另立專屬欄位並標明出處。
> 3. `MVTec AD 2`（Tables 7–12）每格包含兩個數值，順序固定為 **`TESTpriv / TESTpriv,mix`**（同訓練集標準光照測試集／隨機混合已知與未知光照測試集）。
> 4. 論文中的 **`RD`（Reverse Distillation [17]）即本 Wiki 既有的 `RD4AD`**。

| 方法名稱 (Method) | 所屬流派 | MVTec AD<br>`AU-PRO0.30` (%)<br>[Table 1] | VisA<br>`AU-PRO0.30` (%)<br>[Table 1] | MVTec AD 2 ($256 \times 256$)<br>`AU-PRO0.30` (%)<br>(`TESTpriv / TESTpriv,mix`)<br>[Table 1 & Table 9] | MVTec AD 2 ($256 \times 256$)<br>`AU-PRO0.05` (%)<br>(`TESTpriv / TESTpriv,mix`)<br>[Table 7] | MVTec AD 2 ($1/2$ 原始寬高)<br>`AU-PRO0.05` (%)<br>(`TESTpriv / TESTpriv,mix`)<br>[Table 11] | MVTec AD 2 ($256 \times 256$)<br>像素分割 `F1` (%)<br>(`TESTpriv / TESTpriv,mix`)<br>[Table 8] | MVTec AD 2 ($256 \times 256$)<br>影像分類 `F1` (%)<br>(`TESTpriv / TESTpriv,mix`)<br>[Table 12] |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **[PatchCore](../papers/roth2022-patchcore.md)** | 預訓練特徵記憶庫（3 骨幹整合，無中心裁切） | 92.7 | 79.7 | 53.8 / 50.8 | 28.8 / 26.0 | 62.3 / 52.6 | 3.7 / 3.4 | 8.0 / 9.9 |
| **RD** *(即 RD4AD)* | 預訓練特徵（反向知識蒸餾） | 93.9 | 89.0 | 53.0 / 50.3 | 26.4 / 25.0 | 53.7 / 49.5 | 18.1 / 16.7 | 70.8 / 72.9 |
| **RD++** | 預訓練特徵（改良反向知識蒸餾） | 95.0 | 89.3 | 54.3 / 50.4 | 27.1 / 25.2 | 55.3 / 46.8 | 19.2 / 16.7 | 70.5 / 73.0 |
| **EfficientAD** | 輕量師生網路 + 自編碼器 | 93.5 | 94.0 | 58.7 / 44.1 | 30.8 / 19.2 | 50.8 / 33.5 | 15.4 / 8.0 | 76.8 / 77.8 |
| **MSFlow** | 預訓練特徵 + 多尺度正規化流 | 91.2 | 88.4 | 52.7 / 37.1 | 24.3 / 11.9 | 58.2 / 29.0 | 21.8 / 9.0 | 51.1 / 72.0 |
| **SimpleNet** | 預訓練特徵 + 特徵空間異常合成 | 89.6 | 68.9 | 46.4 / 37.6 | 21.1 / 13.7 | 45.7 / 34.1 | 17.7 / 8.7 | 73.3 / 77.1 |
| **DSR** | 雙子空間重投影 + 異常合成 | 90.8 | 68.1 | 49.0 / 45.2 | 20.3 / 17.4 | - *(僅 Rice: 16.0 / 13.5)* | 10.9 / 9.5 | 78.0 / 78.0 |
| **Mean (7 方法平均)** | **跨方法平均** | 92.4 | 82.4 | 52.6 / - *(Table 1 僅報 TESTpriv)* | - | - | - | - |

---

## 5. 演進趨勢與取捨分析（AI 整理）

> **（AI 整理）**
> 1. **第一波典範轉移（2019–2022）：為什麼在物件類別（Objects）上，PatchCore 能比早期重建法 RIAD 高出超過 9 個百分點（`99.2%` vs. `89.9%` Image AUROC）？**
>    - 在 [RIAD](../papers/zavrtanik2021-riad.md) 中，紋理類別平均達 **95.1%**，但物件類別平均僅 **89.9%**（例如 `cable` **81.9%**、`hazelnut` **83.3%**、`pill` **83.8%**、`screw` **84.5%**，出自 `zavrtanik2021-riad.pdf` p. 6 Table 1）。這是因為像素級遮罩修補必須從「同張影像的空間鄰域」推論被挖空的區域，當物件朝向隨機（如 `screw`、`hazelnut`）或結構複雜（如 `cable`）時，單靠周圍像素很難精確畫出高梯度邊緣或隨機結構，產生假陽性重建誤差。
>    - 反觀 [PatchCore](../papers/roth2022-patchcore.md)，它直接在中階語意特徵空間（`WideResNet50` Blocks `2+3`）將測試 Patch 與**「跨整個正常訓練集所有影像、所有位置」**的核心集記憶庫 $\mathcal{M}_C$ 比對。因此只要訓練集中任何一張正常影像、任何一個位置出現過類似角度的螺紋或電線結構，測試 Patch 就能找到距離極近的最近鄰 $m^*$，將物件類別平均一舉推升至 **99.2%**（其中 `bottle`、`hazelnut`、`metal nut`、`toothbrush`、`transistor` 皆達 **100%**，出自 `roth2022-patchcore.pdf` p. 15 Table S1）。
> 2. **第二波典範轉移（2023+）：DiffusionAD 如何讓「重建式流派」逆襲超越 PatchCore？**
>    - 儘管 `PatchCore` 在標準 MVTec AD 上表現驚人，但預訓練特徵記憶庫在後續更複雜的基準（如 `VisA` 多實例類別 `capsules` `81.6%`、`macaroni2` `78.1%`）與高精密像素邊界指標（MVTec AD `Pixel AP` 僅 `56.1%`，出自 `zhang2023-diffusionad.pdf` Table I, IV, V）上顯露瓶頸——因為 `PatchCore` 輸出的異常圖是由較低解析度的中階特徵圖（$28 \times 28$）雙線性插值放大並以 $\sigma = 4$ 高斯平滑而成，難以描繪極細微或形狀複雜的缺陷邊界。
>    - [DiffusionAD](../papers/zhang2023-diffusionad.md) 結合了三大創新實現逆襲：
>      1. **以擴散 `Noise-to-Norm` 取代 Autoencoder 壓縮與遮罩挖洞**：解決了 `DRAEM` 異常原樣重建與正常背景模糊的痛點（在 `VisA` 上 `DiffusionAD` 達 `98.8%` I-AUROC，大幅超越 `DRAEM` 的 `88.7%` 與 `PatchCore` 的 `95.1%`，出自 `zhang2023-diffusionad.pdf` Table V）。
>      2. **雙尺度規範引導一步去噪（[NOD](../concepts/norm-guided-one-step-denoising.md)）**：同時利用大尺度 $t_b=400$ 清除大面積語意異常、小尺度 $t_s=200$ 保留正常高頻細節，並以 **1 步去噪（`23.5 FPS`）**打破擴散模型推論緩慢的宿命。
>      3. **端到端分割 U-Net + 前景限制異常合成**：取代手工設計的像素／梯度距離，在像素級別直接輸出銳利的異常分割遮罩 $\hat{M}$，使 MVTec AD 的 `Pixel AP` 從 `PatchCore` 的 `56.1%` 躍升至 **`76.1%`**（`+20.0%`），`Image AUROC` 達 **`99.7%`**（出自 `zhang2023-diffusionad.pdf` Table III–V）。
> 3. **第三波跨流派融合（2026）：LAMBDA 如何把「記憶庫」與「擴散去噪」合而為一，破解記憶體與跨領域雙重瓶頸？**
>    - `DiffusionAD` 雖然讓擴散模型邁入實用速度，但其在原始像素空間同時運行兩條不同加噪尺度的去噪路徑，使訓練峰值 GPU 記憶體高達 **`48.4 GB`**（推論 **`12.4 GB`**），且固定尺度的引導權重在醫療影像基準 `BMAD` 上容易對正常解剖變異產生過強修正（`I-AUROC` 降至 `83.4%`，出自 `lee2026-lambda.pdf` Tables 1–2）。
>    - [LAMBDA](../papers/lee2026-lambda.md) 將兩大流派的長處深度結合：
>      1. **預訓練 `VAE` 潛在空間壓縮（$64\times$ 空間降維）**：借鑒 `Latent Diffusion` 精神，將影像壓縮為 $4 \times H/8 \times W/8$ 的潛在表徵（空間面積縮小 64 倍；舉例而言，若輸入為 $256 \times 256 \times 3$ 則為 $32 \times 32 \times 4$，但論文未記載實際輸入解析度），大幅減少擴散運算量。
>      2. **記憶庫引導去噪（`MBG`）取代雙尺度加噪（`NOD`）**：吸收 `Memory Bank` 流派的「跨全體正常樣本檢索」思維，以 $n_m=200$ 個正常潛在原型中最相似的 $L^g$ 作為單步去噪（$t_s=200$）的正常方向導引，省去大尺度 $t_b$ 去噪分支（出自 `lee2026-lambda.pdf` Sec. 3.2）。
>      3. **引導尺度圖（`GSM`）動態空間加權**：以記憶庫正常樣本的逐位置平均距離 $M_b^D$ 標準化測試距離 $L^D$，使高變異正常背景獲得小權重、異常區域獲得大權重——不僅讓訓練記憶體暴降 **80.8%**（僅 **`9.3 GB`**）、推論飆升至 **`42.3 FPS`**，更在醫療基準 `BMAD` 拿下 **`87.1%` I-AUROC** 與 **`75.5%` mAD** 全場最高分（出自 `lee2026-lambda.pdf` Tables 1–2）。
> 4. **工程實務選型建議（AI 整理）**：
>    - 若產線面臨**冷啟動、零訓練時間預算、或僅有極少數（1～5 張）正常樣本**，免訓練且極速建模的 [PatchCore](../papers/roth2022-patchcore.md) 依然是首選。
>    - 若產線具備充足的高階 GPU 訓練資源（`> 48 GB` VRAM），且追求工業標準基準（MVTec AD / VisA）上**極致的無損像素級缺陷邊緣分割精度**，像素空間雙尺度一步擴散的 [DiffusionAD](../papers/zhang2023-diffusionad.md) 具有最高精度上限（或採用 `LAMBDA` 的無 VAE 變體，在 `VisA` 達 **`99.0%` I-AUROC** 且耗用 `33.8 GB` 記憶體，出自 `lee2026-lambda.pdf` Table 1 & Table 4）。
>    - 若訓練 GPU 記憶體有限、需要較高吞吐量，或應用於個體差異較大的醫療影像（如 `BMAD`），可把結合預訓練 `VAE`、`MBG` 與 `GSM` 的 [LAMBDA](../papers/lee2026-lambda.md) 列為**優先實測的候選**。注意：論文的 `9.3 GB` 訓練記憶體與 `42.3 FPS` 是在 NVIDIA A100、VisA 上量得，論文未記載輸入解析度、評估 Batch Size 與計時範圍（見 [LAMBDA §5.1](../papers/lee2026-lambda.md)），不能據此推論消費級或邊緣 GPU 能否達到相同記憶體與速度，必須在目標硬體上實測。
> 5. **第四波真實工業壓力測試（2025 MVTec AD 2）：光照偏移、高解析度微小缺陷與無異常閾值估計如何重塑流派排名？**
>    - [Heckler-Kram et al. (2025) — MVTec AD 2](../papers/hecklerkram2025-mvtec-ad-2.md) 的實驗（見上方 §4.2）揭示了三大關鍵轉折：
>      1. **固定光照 vs. 光照分佈偏移（`TESTpriv` vs. `TESTpriv,mix`）**：在 $256 \times 256$ 標準光照（`TESTpriv`）下，輕量師生網路 `EfficientAD` 以 **`30.8%` $\text{AU-PRO}_{0.05}$**（**`58.7%` $\text{AU-PRO}_{0.30}$**）領先 `PatchCore`（`28.8%` $\text{AU-PRO}_{0.05}$ / `53.8%` $\text{AU-PRO}_{0.30}$）；然而一旦進入隨機混合未知光照的 `TESTpriv,mix`，`EfficientAD` 的 $\text{AU-PRO}_{0.05}$ 暴跌至 **`19.2%`**（`MSFlow` 更從 `24.3%` 崩跌至 `11.9%`），反觀反向知識蒸餾 `RD`（即 `RD4AD`）與 `RD++` 分別僅從 `26.4%`、`27.1%` 微降至 **`25.0%`**、**`25.2%`**，展現對光照變化的高度強健性（出自 `hecklerkram2025-mvtec-ad-2.pdf` Table 7 & Table 9）。
>      2. **高解析度輸入下的逆轉（$256 \times 256 \to 1/2$ 原始寬高）**：當輸入放大至原始影像 $1/2$ 寬高（`Table 11`）以保留微小缺陷時，記憶庫流派 `PatchCore` 的 $\text{AU-PRO}_{0.05}$ 躍升超過 2 倍達 **`62.3% / 52.6%`** 奪回第一，多尺度正規化流 `MSFlow` 亦升至 **`58.2% / 29.0%`**，但 `PatchCore` 單張推論延遲高達 **2 秒**，`SimpleNet` 更在最大解析度下記憶體溢位（出自 `hecklerkram2025-mvtec-ad-2.pdf` Sec. 4.3.3, Fig. 6 & Table 11）。
>      3. **無閾值排序（`AU-PRO`）與有閾值決策（$F_1$）的落差**：`PatchCore` 雖在 `AU-PRO` 名列前茅，卻因預設跨整個測試資料集正規化至 $[0, 1]$ 的機制，在僅用無缺陷驗證集估計 $\mu_{\text{val}} + 3\sigma_{\text{val}}$ 閾值時定出過高門檻，導致像素分割 $F_1$ 僅 **`3.7% / 3.4%`**、影像分類 $F_1$ 僅 **`8.0% / 9.9%`**（出自 `hecklerkram2025-mvtec-ad-2.pdf` Table 8, Table 12 & Supplemental Material B.2）。

---

## 6. 相關 Wiki 頁面連結

- **單篇論文解析**：
  - [Bergmann et al. (2019) — MVTec AD](../papers/bergmann2019-mvtec-ad.md)
  - [Ho et al. (2020) — DDPM](../papers/ho2020-ddpm.md)
  - [Zavrtanik et al. (2021) — RIAD](../papers/zavrtanik2021-riad.md)
  - [Roth et al. (2022) — PatchCore](../papers/roth2022-patchcore.md)
  - [Zhang et al. (2023/2025) — DiffusionAD](../papers/zhang2023-diffusionad.md)
  - [Lee & Kang (2026) — LAMBDA](../papers/lee2026-lambda.md)
  - [Heckler-Kram et al. (2025) — MVTec AD 2](../papers/hecklerkram2025-mvtec-ad-2.md)
- **核心概念**：
  - [非監督式視覺異常檢測（Unsupervised Visual Anomaly Detection）](../concepts/unsupervised-anomaly-detection.md)
  - [局部特徵記憶庫與核心集下採樣（Patch-Level Memory Bank & Coreset Subsampling）](../concepts/memory-bank.md)
  - [遮罩修復重建與多尺度梯度相似度（Reconstruction by Inpainting & MSGMS）](../concepts/reconstruction-by-inpainting.md)
  - [去噪擴散機率模型（Denoising Diffusion Probabilistic Models, DDPM）](../concepts/denoising-diffusion-probabilistic-models.md)
  - [規範引導一步去噪與合成異常分割（Norm-Guided One-Step Denoising & Anomaly Synthesis）](../concepts/norm-guided-one-step-denoising.md)
  - [潛在空間記憶庫引導去噪與引導尺度圖（Latent Diffusion with MBG & GSM）](../concepts/memory-bank-guided-latent-diffusion.md)
- **資料集與評估指標**：
  - [MVTec AD 資料集與評估指標](../datasets/mvtec-ad.md)
  - [MVTec AD 2 資料集與進階評估協定（AU-PRO0.05、F1 與光照分佈偏移）](../datasets/mvtec-ad-2.md)
