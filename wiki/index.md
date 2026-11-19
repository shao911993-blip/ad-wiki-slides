# 視覺異常檢測 LLM Wiki 總目錄（Index）

> **統計資訊**：目前已收錄論文 **7** 篇 ｜ 概念頁 **6** 篇 ｜ 資料集與指標頁 **2** 篇 ｜ 比較頁 **1** 篇
> **最後更新日期**：2026-11-14

本目錄為視覺異常檢測（Visual Anomaly Detection）LLM Wiki 的總索引（Single Source of Truth）。所有頁面皆包含論文技術細節與獨立的「初學者版（AI 整理）」小節，作為教學簡報（`../slides/`）的唯一知識來源。

---

## 1. 單篇論文解析（`papers/`）

- **[Bergmann et al. (2019) — MVTec AD](papers/bergmann2019-mvtec-ad.md)**（`CVPR 2019`｜`資料集`）：提出首個涵蓋 15 類工業紋理與物件、共 5,354 張高解析度影像與 1,888 個像素級缺陷標註區域的非監督式異常檢測基準資料集，並評測 6 種早期深度學習與傳統機器視覺方法。
- **[Ho et al. (2020) — DDPM](papers/ho2020-ddpm.md)**（`NeurIPS 2020`｜`基礎方法`）：建立擴散模型與多尺度去噪分數匹配及朗之萬動力學之等價性，提出預測高斯雜訊 $\boldsymbol{\epsilon}$ 的參數化與簡化損失 $L_{\text{simple}}$，奠定後續擴散式異常檢測重建方法的理論與架構基礎。
- **[Zavrtanik et al. (2021) — RIAD](papers/zavrtanik2021-riad.md)**（`Pattern Recognition 2021`｜`異常檢測方法`）：將異常檢測轉化為自監督遮罩修補（Reconstruction-by-Inpainting）問題，透過隨機遮蔽多尺度網格迫使 U-Net 僅依賴鄰域像素重建，搭配多尺度梯度幅值相似度（MSGMS）於 MVTec AD 達 91.7% Image 與 94.2% Pixel ROC AUC。
- **[Roth et al. (2022) — PatchCore](papers/roth2022-patchcore.md)**（`2022 / arXiv:2106.08265v2`｜`異常檢測方法`）：擷取 ImageNet 預訓練網路的中階局部鄰域聚合 Patch 特徵建立最大化正常資訊記憶庫，並以貪婪核心集下採樣（Greedy Coreset Subsampling）大幅降低冗餘與推論延遲，於 MVTec AD 創下單模型 99.1%（整合模型 99.6%）Image AUROC 與 98.1% Pixel AUROC。
- **[Zhang et al. (2023/2025) — DiffusionAD](papers/zhang2023-diffusionad.md)**（`arXiv:2303.08730v4`｜`異常檢測方法`）：提出「由雜訊恢復正常（Noise-to-Norm）」之擴散重建子網路與 U-Net 分割子網路，透過一步去噪（One-step Denoising）達 23.5 FPS 高速推論，並以規範引導雙尺度去噪（NOD）融合大尺度無異常語意與小尺度正常細節，於 MVTec AD（99.7% Image AUROC / 76.1% Pixel AP）與 VisA 等四大基準全面刷新紀錄。
- **[Lee & Kang (2026) — LAMBDA](papers/lee2026-lambda.md)**（`Applied Soft Computing 2026`｜`異常檢測方法`）：將一步去噪擴散模型移至預訓練 `VAE` 潛在空間（$64\times$ 空間降維），提出記憶庫引導去噪（`MBG`）與引導尺度圖（`GSM`）取代雙尺度加噪分支，使訓練峰值 GPU 記憶體大幅降低 80.8%（48.4 GB → 9.3 GB）、推論達 42.3 FPS（23.6 ms，出自 Table 1），並於醫療基準 BMAD 拿下 87.1% Image AUROC 與 75.5% mAD 最高表現（出自 Table 2）。
- **[Heckler-Kram et al. (2025) — MVTec AD 2](papers/hecklerkram2025-mvtec-ad-2.md)**（`2025 / arXiv:2503.21622v1`｜`資料集`）：針對既有基準飽和問題，提出涵蓋 8 大工業檢測場景（散裝重疊、透明折射、高反光、高正常變異與影像邊界缺陷）、共 8,004 張高解析度影像（出自 Table 4 & Sec. 3.1）之新世代基準，首次引入真實光照分佈偏移測試（`TESTpriv` vs. `TESTpriv,mix`）、嚴格指標 $\text{AU-PRO}_{0.05}$ 與私密 Ground Truth 評估伺服器；在輸入 $256 \times 256$ 下，7 種受測 SOTA 模型於 `TESTpriv` 最高僅達 58.7% $\text{AU-PRO}_{0.30}$（出自 Table 1 & Table 9）與 30.8% $\text{AU-PRO}_{0.05}$（出自 Table 7）。

*(指定之 7 篇論文已全數完成 Ingest)*

---

## 2. 核心概念與基礎原理（`concepts/`）

- **[非監督式視覺異常檢測（Unsupervised Visual Anomaly Detection）](concepts/unsupervised-anomaly-detection.md)**：定義僅用無缺陷正常影像訓練之 One-Class 問題設定、影像級分類與像素級分割差異，以及早期四大基礎流派（Autoencoder、GAN、預訓練 CNN 特徵字典、傳統統計模型）之原理與瓶頸。
- **[去噪擴散機率模型（Denoising Diffusion Probabilistic Models, DDPM）](concepts/denoising-diffusion-probabilistic-models.md)**：解析前向高斯加噪閉式解、逆向去噪馬可夫鏈、$\boldsymbol{\epsilon}$-Prediction 簡化訓練目標，以及部分擴散（Partial Diffusion）如何解決傳統 Autoencoder 模糊與 GAN 崩潰問題。
- **[遮罩修復重建與多尺度梯度相似度（Reconstruction by Inpainting & MSGMS）](concepts/reconstruction-by-inpainting.md)**：解析隨機互斥子集遮罩如何阻斷 Autoencoder 恆等映射並安全啟用 U-Net Skip Connections，以及 4 尺度 Prewitt 梯度幅值相似度（MSGMS）如何提升結構異常定位強健性。
- **[局部特徵記憶庫與核心集下採樣（Patch-Level Memory Bank & Coreset Subsampling）](concepts/memory-bank.md)**：解析預訓練中階局部鄰域特徵聚合、極小化極大設施選址之貪婪核心集（Greedy Coreset）壓縮與隨機投影，以及從 CNN Feature Dictionary、SPADE、PaDiM 到 PatchCore 與 LAMBDA 的演進脈絡。
- **[規範引導一步去噪與合成異常分割（Norm-Guided One-Step Denoising & Anomaly Synthesis）](concepts/norm-guided-one-step-denoising.md)**：解析擴散模型於中低加噪尺度下的一步去噪（One-step Denoising）閉式解、融合大小加噪尺度的規範引導機制（NOD），以及前景限制 Perlin/DTD 異常合成與端到端分割 U-Net 之聯合訓練。
- **[潛在空間記憶庫引導去噪與引導尺度圖（Latent Diffusion with MBG & GSM）](concepts/memory-bank-guided-latent-diffusion.md)**：解析預訓練 `VAE` 潛在擴散（$64\times$ 空間降維）、記憶庫餘弦相似度最近鄰檢索之無異常引導去噪（`MBG`），以及利用記憶庫平均距離 $M_b^D$ 進行空間動態標準化的引導尺度圖（`GSM`）。

---

## 3. 資料集與評估指標（`datasets/`）

- **[MVTec AD 資料集與評估指標（ROC AUC & PRO）](datasets/mvtec-ad.md)**：整理 MVTec AD 之 15 類別（5 類紋理、10 類物件）影像與缺陷統計、無異常驗證集閾值估計協定、Pixel-level ROC AUC 與 Relative Per-Region Overlap (PRO) 指標定義及跨方法基準表現表。
- **[MVTec AD 2 資料集與進階評估協定（AU-PRO0.05、F1 與光照分佈偏移）](datasets/mvtec-ad-2.md)**：整理 MVTec AD 2 之 8 大工業場景與 8,004 張影像統計（出自 Table 4）、三子集（`TESTpub`、`TESTpriv`、`TESTpriv,mix`）光照偏移設計、嚴格指標 $\text{AU-PRO}_{0.05}$ vs. $\text{AU-PRO}_{0.30}$ 與無異常驗證集二值化 $F_1$ 協定及 7 大方法多解析度基準表現表（出自 Tables 1, 7–12）。

---

## 4. 跨論文流派對比與演進（`comparisons/`）

- **[預訓練特徵嵌入 vs. 重建式異常檢測流派對比（Feature Embedding vs. Reconstruction-Based AD）](comparisons/embedding-vs-reconstruction.md)**：系統對比重建式流派（AE、AnoGAN、RIAD）、預訓練特徵嵌入／記憶庫流派（US、SPADE、PaDiM、PatchCore）、雙尺度一步擴散（DiffusionAD）與潛在記憶庫引導混合流派（LAMBDA）在訓練成本、推論速度、跨領域泛化以及 MVTec AD 與 MVTec AD 2 表現上的取捨與演進趨勢。
