---
title: "規範引導一步去噪與合成異常分割（Norm-Guided One-Step Denoising & Anomaly Synthesis）"
type: "concept"
tags: ["One-step Denoising", "Norm-guided Denoising", "Noise-to-Norm", "Anomaly Synthesis", "Diffusion Model", "Industrial AD"]
sources: ["ho2020-ddpm.pdf", "zhang2023-diffusionad.pdf", "lee2026-lambda.pdf"]
updated: "2026-11-14"
---

# 規範引導一步去噪與合成異常分割（Norm-Guided One-Step Denoising & Anomaly Synthesis）

## 1. 概念定義與解決的問題

**規範引導一步去噪（Norm-Guided One-Step Denoising, `NOD`）**與**合成異常判別分割（Synthetic Anomaly Discriminative Segmentation）**是由 [DiffusionAD（Zhang et al., 2023/2025）](../papers/zhang2023-diffusionad.md) 提出的擴散式異常檢測核心技術框架，旨在同時解決重建式異常檢測長期面臨的三大核心矛盾（出自 `zhang2023-diffusionad` Sec. I & IV, p. 1–6）：

1. **Autoencoder 的「異常捷徑複製」與「正常細節模糊」矛盾**：
   - 傳統基於自編碼器（Autoencoder, `AE`）的重建模型（包含結合判別分割網路的 `DRAEM`）缺乏強大的生成先驗，一方面容易透過瓶頸層或跳躍連接將異常特徵直接傳遞至輸出（異常不變重建，導致 False Negatives），另一方面對複雜正常結構與高頻紋理的重建能力不足（粗糙重建，導致 False Positives）（出自 `zhang2023-diffusionad` Sec. I, p. 1–2, Fig. 1–2）。
2. **多步擴散模型（Iterative DDPM / DDIM）的「推論延遲」與「訓練—推論不一致」瓶頸**：
   - 將 [DDPM](../papers/ho2020-ddpm.md) 引入異常檢測的方法（如 `AnoDDPM`、`DiffAD` 需 50 步、`KLAD` 需 20 步）雖具備優異的「由雜訊恢復正常（`Noise-to-Norm`）」能力，但推論時需重複執行數十至數百步神經網路去噪（速度僅約 `1.2 FPS`），不僅無法部署於即時工業產線，更導致訓練階段難以直接產出重建圖來端到端訓練後段分割網路（出自 `zhang2023-diffusionad` Sec. I & IV-A, p. 2, 4, Table VI–VIII）。
3. **單一加噪尺度無法兼顧「大面積語意異常清除」與「小尺度正常邊緣保留」**：
   - 在擴散加噪—去噪過程中，小加噪步數 $t_s$ 能保留正常背景細膩度並修復微小缺陷，卻無法抹除大面積或結構性異常；大加噪步數 $t_b$ 能徹底摧毀大面積異常並恢復正確正常語意，卻會洗掉正常區域的高頻紋理細節（出自 `zhang2023-diffusionad` Sec. I & IV-B, p. 2, 5, Fig. 5）。

---

## 初學者版（AI 整理）

> **本節為初學者導讀（AI 整理）**：以下生活化比喻與直覺說明由 AI 依據論文內容整理，旨在幫助初學者理解擴散模型如何做到「又快又準地修圖找碴」，與下方第 3、4 節之原始數學公式嚴格區分。

### 三個核心觀念：為什麼擴散修圖可以「一步到位」還能「大小通吃」？（AI 整理）

1. **從「遮住重畫（Mask-to-Norm）」進化到「撒沙子濾鏡（Noise-to-Norm）」**（AI 整理）
   - 先前的 [RIAD](../papers/zavrtanik2021-riad.md) 是把圖片挖洞遮住（Masking），叫 AI 看旁邊猜洞裡是什麼；而 `Noise-to-Norm` 則是往整張圖片均勻撒上一層高斯雜訊沙子（AI 整理）。
   - 當沙子撒下去後，原本突兀的刮痕或髒污跟沙子混在一起，失去了「異常特徵」；接著請只學過正常產品的擴散模型把沙子掃掉，模型就會順手把瑕疵也當成沙子一起掃掉，還原出乾淨的正常品（AI 整理）！
2. **為什麼不用走 1000 步？因為「半路起跑」一步就能看清終點（One-Step Denoising）**（AI 整理）
   - [DDPM](../papers/ho2020-ddpm.md) 之所以要走 1000 步，是因為它從第 1000 步（全黑全白雪花點）出發，完全不知道畫面裡有什麼，只能一小步一小步摸索（AI 整理）。
   - 但在異常檢測裡，我們最多只把圖片加噪到第 200～400 步（圖片裡還看得出零件的大致模樣）。在這個「半路起跑」的狀態下，只要讓擴散網路預測一次「現在圖上有多少沙子」，直接用減法公式一步把沙子扣掉，得到的正常圖跟慢慢走 400 步幾乎一模一樣，速度卻直接暴增數百倍（AI 整理）！
3. **雙尺度規範引導（`NOD`）：用「遠看抓大局」引導「近看修細節」**（AI 整理）
   - 想像你在修復一幅古畫：如果你離畫很近（小尺度加噪 $t_s = 200$），你能把細微裂痕修得很精緻，但畫上一大塊墨水污漬你會以為原本就是畫的一部分而留著；如果你退後十步瞇著眼看（大尺度加噪 $t_b = 400$），大塊墨水污漬會被忽略並還原出正確的構圖，但筆觸細節會變模糊（AI 整理）。
   - `NOD` 的作法就是：**先退後十步（$t_b = 400$）一步畫出「構圖完全正確的草稿（Norm $n = \hat{x}_{0_b}$）」，再湊近畫布（$t_s = 200$）看著這張草稿當參考範本，一步完成既沒有大污漬、筆觸又極度清晰的最終修復圖 $\hat{x}_{0_g}$**（AI 整理）！

---

## 3. 核心原理與數學公式

### 3.1 一步去噪（One-Step Denoising）閉式推導

在 [DDPM](../papers/ho2020-ddpm.md) 的前向擴散過程（Forward Process）中，任意時間步 $t \in \{0, 1, \dots, T\}$ 的加噪影像 $x_t$ 可由原始影像 $x_0$ 與標準高斯雜訊 $\epsilon_t \sim \mathcal{N}(\mathbf{0}, \mathbf{I})$ 直接合成（出自 `ho2020-ddpm` Eq. 4；`zhang2023-diffusionad` Sec. III-A, p. 3, Eq. 1）：

$$
x_t = \sqrt{\bar{\alpha}_t}\, x_0 + \sqrt{1 - \bar{\alpha}_t}\, \epsilon_t
$$

其中 $\bar{\alpha}_t = \prod_{i=0}^t (1 - \beta_i)$。當去噪網路 $\epsilon_\theta(x_t, t)$ 預測出雜訊估計值後，無需透過馬可夫鏈逐步採樣 $x_{t-1}, x_{t-2}, \dots, x_0$，而是直接將上式對 $x_0$ 求解，一步推算出無異常重建影像 $\hat{x}_0$（出自 `zhang2023-diffusionad` Sec. IV-A, p. 4, Eq. 6）：

$$
\hat{x}_0 = \frac{1}{\sqrt{\bar{\alpha}_t}}\left(x_t - \sqrt{1 - \bar{\alpha}_t}\,\epsilon_\theta(x_t, t)\right)
$$

- **適用條件與物理意義**：當 $t < 500$（如 $t \le 400$，$T = 1000$）時，訊噪比仍足以支撐單步線性逆推，一步重建之均方誤差（MSE）與 $t$ 步逐步去噪幾乎完全一致（出自 `zhang2023-diffusionad` Fig. 4, p. 4），使推論複雜度由 $\mathcal{O}(t)$ 降至 $\mathcal{O}(1)$。

### 3.2 規範引導雙尺度一步去噪（Norm-Guided One-Step Denoising, `NOD`）

為同時處理不同尺寸與語意層級的異常，`NOD` 將時間步區間 $\{0, 1, \dots, T\}$ 以閾值 $\tau = 300$ 切分為**小尺度區間 $S = \{0, \dots, \tau\}$** 與**大尺度區間 $B = \{\tau + 1, \dots, T\}$**（出自 `zhang2023-diffusionad` Sec. IV-B, p. 5, Eq. 7–8）：

1. **雙尺度前向加噪與雜訊預測**：
   - 對輸入影像 $x_0$ 分別取 $t_s \in S$（推論時 $t_s = 200$）與 $t_b \in B$（推論時 $t_b = 400$）加噪得 $x_{t_s}, x_{t_b}$，並以共享權重的擴散網路預測雜訊 $\epsilon_\theta(x_{t_s})$ 與 $\epsilon_\theta(x_{t_b})$。
2. **建立大尺度無異常參考規範（Norm $n$）**：
   - 利用大尺度預測雜訊一步重建出徹底清除大面積異常的參考影像（Norm）：
     $$n = \hat{x}_{0_b} = \frac{1}{\sqrt{\bar{\alpha}_{t_b}}}\left(x_{t_b} - \sqrt{1 - \bar{\alpha}_{t_b}}\,\epsilon_\theta(x_{t_b})\right)$$
3. **確定性加噪對齊與條件梯度引導**：
   - 為在時間步 $t_s$ 比較 $x_{t_s}$ 與參考規範 $n$，使用已預測出的小尺度雜訊 $\epsilon_\theta(x_{t_s})$（而非隨機高斯雜訊，以避免引入隨機誤差）將 $n$ 轉換至 $t_s$ 時刻：
     $$n_{t_s} = \sqrt{\bar{\alpha}_{t_s}}\, n + \sqrt{1 - \bar{\alpha}_{t_s}}\, \epsilon_\theta(x_{t_s})$$
   - 定義特徵空間負平方歐氏距離相似度 $\text{sim}(x_{t_s}, n_{t_s}) = -\frac{1}{2}\|n_{t_s} - x_{t_s}\|^2$，其對 $x_{t_s}$ 之梯度為 $\nabla_{x_{t_s}} \text{sim}(x_{t_s}, n_{t_s}) = n_{t_s} - x_{t_s}$。代入參考影像條件擴散引導公式（Eq. 5），得到修正後的小尺度雜訊與最終一步重建影像 $\hat{x}_{0_g}$（出自 `zhang2023-diffusionad` Sec. IV-B, p. 5, Eq. 7–8）：

$$
\begin{gathered}
\epsilon_\theta(x_{t_s}, n_{t_s}) = \epsilon_\theta(x_{t_s}) - \sqrt{1 - \bar{\alpha}_{t_s}}\, w (n_{t_s} - x_{t_s}) \\
\hat{x}_{0_g} = \frac{1}{\sqrt{\bar{\alpha}_{t_s}}}\left(x_{t_s} - \sqrt{1 - \bar{\alpha}_{t_s}}\,\epsilon_\theta(x_{t_s}, n_{t_s})\right)
\end{gathered}
$$

   - 其中 $w$ 為引導權重（預設 $w = 1$）。將兩式展開可看出，修正式實質上是在小尺度重建的基礎上，依照 $x_{t_s}$ 與無異常規範 $n_{t_s}$ 的殘差 $(n_{t_s} - x_{t_s})$ 進行加權補償（AI 整理）。

### 3.3 前景限制異常合成與端到端判別分割（Anomaly Synthesis & Discriminative Segmentation）

單純依賴像素級重建殘差（如 $|x_0 - \hat{x}_0|$）容易受邊緣微小對齊誤差干擾。`DiffusionAD` 結合**前景限制之線上異常合成**與**判別式分割 U-Net**（出自 `zhang2023-diffusionad` Sec. IV-C, p. 5–6, Eq. 9–12）：

- **前景限制異常合成（Foreground Constrained Synthesis）**：
  - 以二值化 Perlin 雜訊 $P$ 乘上物件前景遮罩 $F$ 產生異常區域遮罩 $M = P \odot F$（正常區域遮罩 $\bar{M} = 1 - M$），並將正常影像 $N$ 與外部紋理（`DTD` 或自身增強）$A$ 按不透明度 $\beta$ 混合生成合成異常影像 $S$（出自 `zhang2023-diffusionad` Eq. 12）：
    $$S = \beta (M \odot N) + (1 - \beta)(M \odot A) + \bar{M} \odot N$$
- **雙子網路聯合訓練目標**：
  - 擴散模型僅在正常樣本（$y = 0$）上計算雙尺度去噪損失 $\mathcal{L}_{noise}$，避免模型學到合成異常；分割 U-Net 接收 $\text{Concat}(x_0, \hat{x}_{0_g})$，以 Smooth $L_1$ 與 Focal Loss 監督預測遮罩 $\hat{M}$（出自 `zhang2023-diffusionad` Eq. 9–11）：

$$
\begin{gathered}
\mathcal{L}_{noise} = \frac{(1 - y)\left(\|\epsilon_{t_s} - \epsilon_\theta(x_{t_s})\|^2 + \|\epsilon_{t_b} - \epsilon_\theta(x_{t_b})\|^2\right)}{2} \\
\mathcal{L}_{mask} = \text{Smooth}_{\mathcal{L}_1}(M, \hat{M}) + \gamma \mathcal{L}_{focal}(M, \hat{M}), \quad \mathcal{L}_{total} = \mathcal{L}_{noise} + \mathcal{L}_{mask}
\end{gathered}
$$

---

## 4. 在異常檢測中的應用與演進脈絡

| 技術演進階段 | 代表方法 | 異常抹除機制 | 重建步數／速度 | 異常評分方式 | 核心優勢與瓶頸（出自 `zhang2023-diffusionad` Sec. I–II & Table V–VII） |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **自監督遮罩修補** | [RIAD](../papers/zavrtanik2021-riad.md) (2021) | 多尺度隨機網格遮罩（`Mask-to-Norm`） | 3 尺度 × $k$ 次前向 | 規則式 `MSGMS` 梯度比較 | 不需外部資料；但多次遮罩推論慢且對大面積語意異常修補有限 |
| **自編碼器 + 合成異常分割** | `DRAEM` (2021) | 瓶頸層壓縮（Autoencoder） | 1 步（`32.4 FPS`） | 判別式 U-Net 分割 | 推論極快、邊界銳利；但 AE 易原樣重建異常且正常背景重建粗糙（VisA Image AUROC 僅 `88.7%`） |
| **多步擴散重建** | `DiffAD` / `KLAD` | 部分前向加噪（`Noise-to-Norm`） | 20～50 步（`1.2 FPS`） | 特徵／像素差異或分割 | 擴散先驗大幅改善重建品質；但多步去噪極慢，且訓練與推論難一致 |
| **規範引導一步去噪擴散 + 分割** | **[DiffusionAD](../papers/zhang2023-diffusionad.md)** | 雙尺度前向加噪 + `NOD`（$t_s=200, t_b=400$） | **1 步（`23.5 FPS`）** | 端到端 U-Net 分割 $\hat{M}$ | 兼顧大異常清除與小細節保留，訓練推論完全一致，於 MVTec AD（`99.7%` I-AUROC / `76.1%` AP）與 VisA（`98.8%` I-AUROC）刷新紀錄 |
| **潛在空間記憶庫引導一步去噪 + 分割** | **[LAMBDA](../papers/lee2026-lambda.md)** (2026) | `VAE` 潛在壓縮 + 記憶庫檢索 `MBG` + 引導尺度圖 `GSM`（$t_s=200$） | **1 步（`42.3 FPS`）** | 端到端 U-Net 分割 $\hat{M}$ | 以記憶庫參考樣本 $L^g$ 與 `GSM` 取代 `NOD` 第二趟大尺度去噪，訓練記憶體減少 **80.8%**（`48.4 → 9.3 GB`）、推論加速 **3.9×**（出自 `lee2026-lambda` Table 1 & 4） |

---

## 5. 相關 Wiki 頁面連結

- **原始論文頁**：
  - [Zhang et al. (2023/2025) — DiffusionAD](../papers/zhang2023-diffusionad.md)
  - [Lee & Kang (2026) — LAMBDA](../papers/lee2026-lambda.md)
  - [Ho et al. (2020) — DDPM](../papers/ho2020-ddpm.md)
  - [Zavrtanik et al. (2021) — RIAD](../papers/zavrtanik2021-riad.md)
  - [Roth et al. (2022) — PatchCore](../papers/roth2022-patchcore.md)
  - [Bergmann et al. (2019) — MVTec AD](../papers/bergmann2019-mvtec-ad.md)
  - [Heckler-Kram et al. (2025) — MVTec AD 2](../papers/hecklerkram2025-mvtec-ad-2.md)
- **其他概念、資料集與比較頁**：
  - [潛在空間記憶庫引導去噪與引導尺度圖（Latent Diffusion with MBG & GSM）](memory-bank-guided-latent-diffusion.md)
  - [去噪擴散機率模型（Denoising Diffusion Probabilistic Models, DDPM）](denoising-diffusion-probabilistic-models.md)
  - [遮罩修復重建與多尺度梯度相似度（Reconstruction by Inpainting & MSGMS）](reconstruction-by-inpainting.md)
  - [局部特徵記憶庫與核心集下採樣（Patch-Level Memory Bank & Coreset Subsampling）](memory-bank.md)
  - [非監督式視覺異常檢測（Unsupervised Visual Anomaly Detection）](unsupervised-anomaly-detection.md)
  - [MVTec AD 資料集與評估指標（ROC AUC & PRO）](../datasets/mvtec-ad.md)
  - [MVTec AD 2 資料集與進階評估協定（AU-PRO0.05、F1 與光照分佈偏移）](../datasets/mvtec-ad-2.md)
  - [預訓練特徵嵌入 vs. 重建式異常檢測流派對比（Feature Embedding vs. Reconstruction-Based AD）](../comparisons/embedding-vs-reconstruction.md)
