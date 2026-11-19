---
title: "潛在空間記憶庫引導去噪與引導尺度圖（Latent Diffusion with Memory Bank-Guided Denoising & Guidance Scale Map）"
type: "concept"
tags: ["Latent Diffusion", "VAE", "Memory Bank-Guided Denoising", "Guidance Scale Map", "One-step Denoising", "Lightweight AD"]
sources: ["lee2026-lambda.pdf", "zhang2023-diffusionad.pdf", "roth2022-patchcore.pdf", "ho2020-ddpm.pdf"]
updated: "2026-11-14"
---

# 潛在空間記憶庫引導去噪與引導尺度圖（Latent Diffusion with Memory Bank-Guided Denoising & Guidance Scale Map）

## 1. 概念定義與解決的問題

**潛在空間記憶庫引導去噪（Memory Bank-Guided Denoising, `MBG`）**與**空間自適應引導尺度圖（Guidance Scale Map, `GSM`）**是由 [LAMBDA（Lee & Kang, 2026）](../papers/lee2026-lambda.md) 提出的輕量化擴散異常檢測核心機制。其核心設計理念為：**利用預訓練變分自編碼器（`VAE`）將高解析度影像壓縮至低維潛在空間（Latent Space），並預先儲存正常訓練樣本之潛在表徵記憶庫 $\mathcal{M}_b$；在執行單次一步去噪（One-step Denoising）時，由 $\mathcal{M}_b$ 檢索最相似正常潛在表徵 $L^g$ 作為參考範本，並依據記憶庫像素距離統計量動態計算空間自適應引導尺度圖 $G$（`GSM`），精準調節各空間位置的語意引導強度**（出自 `lee2026-lambda.pdf` Sec. 3 & Sec. 4, p. 3–6, Fig. 1–3）。

此框架同時解決了擴散式異常檢測與現有條件引導技術的三大結構性瓶頸（出自 `lee2026-lambda.pdf` Sec. 1, Sec. 3.5 & Sec. 5.8, p. 1–2, 4, 9–11）：

1. **像素空間擴散與雙尺度規範引導（`NOD`）的高記憶體與延遲瓶頸**：
   - 先前的 [DiffusionAD](../papers/zhang2023-diffusionad.md) 雖以一步去噪取代多步馬可夫鏈採樣，但仍在原始像素空間運作，且其規範引導機制（[Norm-Guided One-Step Denoising, `NOD`](norm-guided-one-step-denoising.md)）需將時間步切分為大小兩尺度（$t_s=200, t_b=400$）執行兩次去噪預測，導致訓練階段需耗費高達 **`48.4 GB`** GPU 記憶體，推論速度受限於 `10.9 FPS`（`91.7 ms/image`）（出自 `lee2026-lambda.pdf` Sec. 5.4 & 5.8.2, p. 7–8, 10–11, Table 1）。
2. **無分類器引導（Classifier-Free Guidance, `CFG`）於異常重建的雙倍開銷與條件模糊性**：
   - `CFG` 僅能提供抽象的「正常」類別條件，無法指明待測影像應朝哪一種具體正常空間結構重建；更重要的是，`CFG` 在訓練時必須同時學習條件與無條件分佈（訓練複雜度加倍），推論時每步亦須計算條件與無條件兩次雜訊預測（推論運算量加倍）（出自 `lee2026-lambda.pdf` Sec. 3.5, p. 4）。
3. **傳統語意擴散引導（Semantic Diffusion Guidance, `SDG`）的空間均一性（Spatial Uniformity）限制**：
   - `SDG` 雖改用具體參考樣本引導去噪，但對整個潛在空間套用單一標量引導強度 $G$，忽略了待測影像中「正常區域已與參考樣本高度吻合（僅需極小引導）」與「異常區域嚴重偏離正常參考（急需強力引導修復）」的空間異質性，容易導致正常變異被過度修正（產生假陽性）或異常區域修正不足（產生假陰性）（出自 `lee2026-lambda.pdf` Sec. 3.5 & 4.5, p. 4–6）。

---

## 2. 初學者版（AI 整理）

> **本節為初學者導讀（AI 整理）**：以下生活化比喻與直覺說明由 AI 依據論文內容整理，旨在幫助初學者理解潛在空間壓縮、`MBG` 與 `GSM` 的運作直覺，與下方第 3、4 節之原始數學公式嚴格區分。

### 三個核心直覺：如何讓擴散修圖既省顯卡、又快、又不修壞背景？（AI 整理）

1. **為什麼要先過 `VAE`？（把海報縮成明信片再修圖）**（AI 整理）
   - 直接在高清大圖上讓擴散模型預測雜訊，就像拿小畫筆在整面牆壁大小的巨幅海報上作畫，極度耗費顯卡記憶體（`48.4 GB`）（AI 整理）。
   - `LAMBDA` 先借用 `Stable Diffusion` 已經訓練好的 `VAE` 壓縮機，把長寬各縮小 8 倍（面積縮小 64 倍），變成一張濃縮了所有結構精華的「潛在特徵明信片 $L$」。在明信片上掃完沙子修好圖，最後再放大回海報——訓練顯卡記憶體立刻省下 **80.8%**（只剩 `9.3 GB`）（AI 整理）！
2. **什麼是「記憶庫引導去噪（`MBG`）」？（翻相簿找雙胞胎，省去自己畫草稿）**（AI 整理）
   - [DiffusionAD](../papers/zhang2023-diffusionad.md) 為了消除大塊瑕疵，每次都要先撒一把厚沙子（$t_b=400$）自己畫一張「無瑕疵草稿」，再拿草稿引導薄沙子（$t_s=200$）修圖，等於每張圖要算兩遍（AI 整理）。
   - `LAMBDA` 結合了 [PatchCore](../papers/roth2022-patchcore.md) 的點子：既然訓練集裡本來就有正常良品，不如先挑 **200 張正常良品**壓成明信片收進**「記憶相簿 $\mathcal{M}_b$」**！測試時直接從相簿裡挑出跟待測圖長得最像的「雙胞胎良品 $L^g$」當現成參考草稿，只要在 $t_s=200$ 算**一遍**一步去噪就大功告成，推論速度直接翻了將近 4 倍（`42.3 FPS`）（AI 整理）！
3. **什麼是「引導尺度圖（`GSM`）」？（看相簿標準差決定哪裡要用力擦）**（AI 整理）
   - 就算找到長得最像的雙胞胎良品 $L^g$，兩張圖的正常零件邊緣或紋理還是有一點點自然誤差。如果整張圖都硬逼它改成跟 $L^g$ 一模一樣，正常的地方反而會被改壞（AI 整理）。
   - `GSM` 就像一張**「分區施力地圖」**：它先算待測圖 $L$ 跟參考圖 $L^g$ 每一格的距離，再除以「相簿裡 200 張良品彼此之間的正常標準差」：
     - **差距在正常標準差以內（暗區）** $\rightarrow$ 這是正常的自然誤差，引導力道調到最小，保留原圖細節（AI 整理）！
     - **差距遠超出正常標準差（亮區）** $\rightarrow$ 這裡肯定是異常瑕疵，引導力道開到最大，強制把瑕疵拉回正常參考圖 $L^g$ 的模樣（AI 整理）！

---

## 3. 核心原理與數學公式（出自 `lee2026-lambda.pdf` Sec. 3 & Sec. 4, p. 3–6）

### 3.1 預訓練 VAE 潛在空間一步去噪（Latent Space One-Step Denoising）

1. **潛在空間編碼**：輸入 RGB 影像 $I \in \mathbb{R}^{3 \times H \times W}$ 經預訓練 `VAE` 編碼器 $E(\cdot)$ 投影至潛在表徵 $L_0 = L = E(I) \in \mathbb{R}^{4 \times H/8 \times W/8}$（出自 `lee2026-lambda.pdf` Sec. 3.1, p. 3）。
2. **前向高斯加噪與一步去噪閉式解**：在時間步 $t \in [1, T]$（訓練時隨機取樣 $t \sim \text{Uniform}(1, 1000)$，推論時固定 $t = t_s = 200$）加入高斯雜訊 $\epsilon_t \sim \mathcal{N}(\mathbf{0}, \mathbf{I})$ 得 $L_t$，並以去噪網路 $\epsilon_\theta(L_t, t)$ 執行一步去噪重建 $\hat{L}_0$（出自 `lee2026-lambda.pdf` Sec. 3.2–3.3, p. 3–4, Eq. 1, 3, 4）：

$$
\begin{gathered}
L_t = \sqrt{\bar{\alpha}_t}\, L_0 + \sqrt{1 - \bar{\alpha}_t}\, \epsilon_t, \quad \mathcal{L}_{\text{simple}} = \mathbb{E}_{t, L_0, \epsilon_t}\left[\left\|\epsilon_t - \epsilon_\theta(L_t, t)\right\|^2\right] \\
\hat{L}_0 = \frac{1}{\sqrt{\bar{\alpha}_t}}\left(L_t - \sqrt{1 - \bar{\alpha}_t}\,\epsilon_\theta(L_t, t)\right)
\end{gathered}
$$

### 3.2 記憶庫引導去噪（Memory Bank-Guided Denoising, `MBG`）

1. **記憶庫建構與餘弦相似度檢索**：
   - 自正常訓練集隨機抽樣 $n_m = 200$ 張正常影像編碼為潛在表徵，構成記憶庫 $\mathcal{M}_b \in \mathbb{R}^{n_m \times d}$（出自 `lee2026-lambda.pdf` Sec. 4.4 & Algorithm 1, p. 5–6）。
   - 對輸入潛在表徵計算與 $\mathcal{M}_b$ 中 $n_m$ 個正常樣本的**餘弦相似度（Cosine Similarity）**，檢索出最相似的參考潛在表徵 $L^g \in \mathcal{M}_b$（出自 `lee2026-lambda.pdf` Sec. 4.4, p. 5）。
2. **參考樣本加噪對齊與空間引導雜訊修正**：
   - 將 $L^g$ 以相同雜訊排程與預測雜訊 $\epsilon_\theta(L_t, t)$ 擾動至時間步 $t$ 得到 $L_t^g$，再結合空間引導尺度圖 $G$（取代傳統標量引導尺度）與相似度度量 $\text{sim}(L_t, L_t^g) = \|L_t - L_t^g\|_2^2$ 修正預測雜訊，並一步去噪得到 $\hat{L}_0$（出自 `lee2026-lambda.pdf` Sec. 3.4 & 4.4, p. 4–5, Eq. 4–5 & Fig. 2）：

$$
\begin{gathered}
\epsilon_\theta(L_t, t, L_t^g) = \epsilon_\theta(L_t, t) - G\sqrt{1 - \bar{\alpha}_t}\,\nabla_{L_t}\text{sim}(L_t, L_t^g) \\
\hat{L}_0 = \frac{1}{\sqrt{\bar{\alpha}_t}}\left(L_t - \sqrt{1 - \bar{\alpha}_t}\,\epsilon_\theta(L_t, t, L_t^g)\right)
\end{gathered}
$$

### 3.3 空間自適應引導尺度圖（Guidance Scale Map, `GSM`）

為消除參考樣本 $L^g$ 與輸入 $L$ 在正常區域的微幅未對齊影響，`GSM` 利用記憶庫內部統計量校準每個空間位置 $(h, w)$ 的引導強度（出自 `lee2026-lambda.pdf` Sec. 4.5, p. 5–6, Fig. 3, Eq. 6–7）：

1. **像素級距離圖與記憶庫統計標準化（Eq. 6）**：
   - 計算 $L$ 與 $L^g$ 之像素級距離圖 $L^D$，並以記憶庫 $\mathcal{M}_b$ 全體 $n_m$ 個正常樣本計算出之平均像素級距離統計量 $M_b^D$（均值 $\bar{M}_b^D$、標準差 $\text{std}(M_b^D)$）進行標準化：

$$
\tilde{L}_{h,w}^D = \frac{L_{h,w}^D - \bar{M}_b^D}{\text{std}(M_b^D)}, \quad \text{where } h \in [1, H],\; w \in [1, W] \tag{6}
$$

2. **生成空間引導尺度圖 $G$（Eq. 7）**：
   - 計算標準化距離 $\tilde{L}_{h,w}^D$ 與記憶庫距離統計量 $M_{b\, h,w}^D$ 之 $L_2$ 距離度量 $\text{dist}(\cdot, \cdot)$：

$$
G_{h,w} = \left\|\text{dist}\left(\tilde{L}_{h,w}^D, M_{b\, h,w}^D\right)\right\|, \quad \text{where } h \in [1, H],\; w \in [1, W] \tag{7}
$$

---

## 4. 擴散引導策略於異常檢測之演進對比

下表整理 `LAMBDA` 論文（Sec. 3.4–3.5, Sec. 4.4–4.5 & Sec. 5.8, p. 4–6, 9–11）中針對不同擴散引導策略於視覺異常檢測之系統性比較：

| 引導策略（Guidance Strategy） | 代表文獻 | 條件／參考來源 | 空間引導分佈特性 | 訓練與推論計算開銷 | 在異常檢測中的核心優劣（出自 `lee2026-lambda.pdf` Sec. 3.5 & 5.8） |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **Classifier Guidance (`CG`)** | Dhariwal & Nichol (2021) | 預訓練分類器梯度 $\nabla \log p_\phi(y\mid x_t)$ | 全圖由類別梯度控制 | 需額外訓練加噪影像分類器 | 異常檢測缺乏異常類別樣本訓練分類器，且類別標籤無法指引細粒度像素重建 |
| **Classifier-Free Guidance (`CFG`)** | Ho & Salimans (2022) | 抽象「正常」條件與無條件分佈差值 | 全圖均一標量權重 | 訓練需學雙分佈（**2× 複雜度**）；推論每步需算兩次（**2× 開銷**） | 條件過於抽象，無法告知應重建哪種具體正常圖樣；雙倍運算不利即時部署 |
| **Semantic Diffusion Guidance (`SDG`)** | Liu et al. (2023) / `LAMBDA w/o GSM` | 具體參考樣本 $L_t^g$ | **全圖均一標量引導強度 $G$** | 單次去噪（`25.5 / 42.4 FPS`） | 解決抽象條件問題，但均一引導忽略空間異質性，於正常區域產生假陽性（`VisA` AUPRO 降至 `90.2%`，Table 4） |
| **Norm-Guided Denoising (`NOD`)** | [DiffusionAD](../papers/zhang2023-diffusionad.md) (2023/2025) | 大加噪尺度 ($t_b=400$) 一步重建之自身規範 $n = \hat{x}_{0_b}$ | 依 $(n_{t_s} - x_{t_s})$ 殘差與固定權重 $w=1$ 引導 | **需雙尺度兩次去噪預測**（像素空間訓練 `48.4 GB`、推論 `10.9 FPS`） | 精度極高（`VisA` AUPRO `96.2%`），但雙尺度去噪與像素空間運算帶來龐大記憶體與訓練時間開銷（Table 1, Table 4） |
| **Memory Bank + Guidance Scale Map (`MBG + GSM`)** | **[LAMBDA](../papers/lee2026-lambda.md)** (2026) | 潛在記憶庫 $\mathcal{M}_b$ ($n_m=200$) 餘弦相似度最近鄰 $L^g$ | **像素級動態引導尺度圖 $G_{h,w}$（依 $\mathcal{M}_b$ 距離統計標準化）** | **潛在空間單次一步去噪**（訓練 **`9.3 GB`**、推論 **`5.8 GB`**、**`42.3 FPS`**） | 省去第二趟大尺度去噪，訓練記憶體減少 **80.8%**、推論加速 **3.9×**，且像素精度與 `DiffusionAD` 無統計顯著差異（$p=0.812$，Table 1, 3, 4） |

---

## 5. 相關 Wiki 頁面連結

- **原始論文頁**：
  - [Lee & Kang (2026) — LAMBDA](../papers/lee2026-lambda.md)
  - [Zhang et al. (2023/2025) — DiffusionAD](../papers/zhang2023-diffusionad.md)
  - [Roth et al. (2022) — PatchCore](../papers/roth2022-patchcore.md)
  - [Ho et al. (2020) — DDPM](../papers/ho2020-ddpm.md)
  - [Zavrtanik et al. (2021) — RIAD](../papers/zavrtanik2021-riad.md)
  - [Bergmann et al. (2019) — MVTec AD](../papers/bergmann2019-mvtec-ad.md)
  - [Heckler-Kram et al. (2025) — MVTec AD 2](../papers/hecklerkram2025-mvtec-ad-2.md)
- **其他概念、資料集與比較頁**：
  - [規範引導一步去噪與合成異常分割（Norm-Guided One-Step Denoising & Anomaly Synthesis）](norm-guided-one-step-denoising.md)
  - [局部特徵記憶庫與核心集下採樣（Patch-Level Memory Bank & Coreset Subsampling）](memory-bank.md)
  - [去噪擴散機率模型（Denoising Diffusion Probabilistic Models, DDPM）](denoising-diffusion-probabilistic-models.md)
  - [遮罩修復重建與多尺度梯度相似度（Reconstruction by Inpainting & MSGMS）](reconstruction-by-inpainting.md)
  - [非監督式視覺異常檢測（Unsupervised Visual Anomaly Detection）](unsupervised-anomaly-detection.md)
  - [MVTec AD 資料集與評估指標（ROC AUC & PRO）](../datasets/mvtec-ad.md)
  - [MVTec AD 2 資料集與進階評估協定（AU-PRO0.05、F1 與光照分佈偏移）](../datasets/mvtec-ad-2.md)
  - [預訓練特徵嵌入 vs. 重建式異常檢測流派對比（Feature Embedding vs. Reconstruction-Based AD）](../comparisons/embedding-vs-reconstruction.md)
