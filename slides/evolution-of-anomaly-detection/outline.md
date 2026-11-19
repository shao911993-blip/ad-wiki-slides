# 簡報大綱：從重建到擴散——工業異常檢測的演進

- **簡報主題**：從重建到擴散：工業異常檢測的演進（Evolution of Industrial Anomaly Detection: From Reconstruction to Diffusion）
- **目標讀者**：視覺異常檢測初學者（具備基礎機器學習概念，欲建立工業異常檢測的方法演進脈絡與評估思維）
- **最終簡報輸出路徑**：`slides/evolution-of-anomaly-detection/index.html`（嚴禁覆寫網站根目錄 `index.html`）
- **所依據的 Wiki Commit**：`df11944`（完整 Hash：`df11944472bf30fe7e23a34dccba2e15e376f78a`；知識內容基準 Commit：`df11944`，關卡 ③ 修正 wiki 後更新；原基準為 `e626497`）
- **總頁數**：共 16 頁（頁碼 1–16）
- **封面核心聲明**：這是選定 7 篇論文的發展脈絡，不代表後面的方法全面取代前面的。
- **投影片密度規範**：每頁於 `1366×768` 單一畫面內看完（不需垂直捲動）；可見正文 130 字以內（白話呈現）；最多 3 個關鍵數字；最多 1 張圖或 1 個 4 列以內的小表；最多 1 條公式；其餘細節收錄於「查證資料與講稿備註」並以「延伸閱讀」連向 `wiki/` 段落。

---

## 第 1 頁：封面＋學習目標

### 學習目標
了解本簡報涵蓋之 7 篇視覺異常檢測代表論文的演進主軸、四大核心學習目標，以及不同流派各具適用場景而非單向取代的前提。

### 用到的 Wiki 頁與段落
- `wiki/index.md` `## 1. 單篇論文解析（papers/）`
- `wiki/comparisons/embedding-vs-reconstruction.md` `## 1. 比較維度與脈絡概述`
- `wiki/comparisons/embedding-vs-reconstruction.md` `## 5. 演進趨勢與取捨分析（AI 整理）`

### 預計使用的圖檔
- 無

### 投影片可見內容
- **主標題**：從重建到擴散：工業異常檢測的演進
- **封面聲明**：這是選定 **7** 篇論文的發展脈絡，不代表後面的方法全面取代前面的。
- **可見正文（92 字）**：
  1. **任務與基準**：認識只用正常品訓練的設定，以及影像級分類與像素級分割評估。
  2. **方法演進**：對比「重建正常外觀」與「比對正常特徵」如何走向潛在擴散融合。
  3. **嚴格評測與選型**：看懂 `PRO` 與 `AU-PRO0.05` 指標意義，建立實務測試思維。
- **延伸閱讀**：[Wiki 總目錄](../../wiki/index.md#1-單篇論文解析papers)、[預訓練特徵嵌入 vs. 重建式異常檢測流派對比](../../wiki/comparisons/embedding-vs-reconstruction.md#1-比較維度與脈絡概述)

### 查證資料與講稿備註
- **副標題與定位**：給初學者的 7 篇經典論文導讀——從 `MVTec AD (2019)` 基準、`RIAD (2021)` 遮罩修補、`PatchCore (2022)` 特徵記憶庫、`DDPM (2020)` 與 `DiffusionAD (2023/2025)` 一步擴散、`LAMBDA (2026)` 潛在記憶庫引導，到 `MVTec AD 2 (2025)` 新世代評測。
- **四大核心學習目標展開說明（講者口頭補充）**：
  1. 理解為何工業檢測通常只能收集正常品訓練（第 2–3 頁）。
  2. 用同一組四個問題（輸入什麼、保存或學到什麼、怎麼產生異常分數、主要限制）拆解 `RIAD`、`PatchCore`、`DiffusionAD`、`LAMBDA`（第 4–10 頁）。
  3. 區分 `TPR` 與 `PRO`，並理解高解析度場景為何將假陽性率積分上限收緊至 `0.05`（第 11–14 頁）。
  4. 學會從現有實驗證據規劃候選方法與目標環境實測（第 15–16 頁）。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C01-01` | 本簡報呈現選定 7 篇論文（MVTec AD、DDPM、RIAD、PatchCore、DiffusionAD、LAMBDA、MVTec AD 2）的技術發展脈絡，各流派有其工程取捨與適用條件，不代表後期方法全面取代前期方法（AI 整理） | 跨方法導覽 | 跨資料集 | 無 | 7 篇代表論文之教學脈絡聲明 | `wiki/comparisons/embedding-vs-reconstruction.md` `## 5. 演進趨勢與取捨分析（AI 整理）` | 無（課程導覽定位聲明） | AI 推論 |

---

## 第 2 頁：任務設定：只用正常品訓練、影像級與像素級輸出

### 學習目標
理解工業異常檢測為何採用只用正常品訓練的問題設定（以及部分方法會合成異常樣本），並區分影像級與像素級兩種輸出。

### 用到的 Wiki 頁與段落
- `wiki/concepts/unsupervised-anomaly-detection.md` `## 1. 概念定義與問題設定`
- `wiki/concepts/unsupervised-anomaly-detection.md` `## 2. 初學者版（AI 整理）`
- `wiki/concepts/unsupervised-anomaly-detection.md` `## 3. 核心任務區分與早期主流流派（出自 bergmann2019-mvtec-ad.pdf Sec. 2, p. 2–4 & Sec. 4, p. 5–8）`
- `wiki/papers/bergmann2019-mvtec-ad.md` `## 2. 一句話總結（TL;DR）與核心貢獻`
- `wiki/concepts/norm-guided-one-step-denoising.md` `## 1. 概念定義與解決的問題`

### 預計使用的圖檔
- 無

### 投影片可見內容
- **可見正文（112 字）**：
  - **問題設定**：本簡報採用「**只用正常品訓練**」的問題設定，因產線缺陷事前未知且不良品極少；部分進階方法（如 `DiffusionAD`、`LAMBDA`）會在正常品上**人工合成異常樣本**輔助訓練分割網路。
  - **兩種輸出任務**：
    1. **影像級輸出**：給整張圖 **1** 個異常分數，判斷產品是否不良。
    2. **像素級輸出**：輸出 **1** 張空間異常圖，標出瑕疵像素位置。
- **延伸閱讀**：[非監督式視覺異常檢測 §1–§3](../../wiki/concepts/unsupervised-anomaly-detection.md#1-概念定義與問題設定)、[規範引導一步去噪與合成異常分割 §1](../../wiki/concepts/norm-guided-one-step-denoising.md#1-概念定義與解決的問題)

### 查證資料與講稿備註
- **為什麼只能用正常品訓練？**
  1. 缺陷類型事前未知：製造過程可能出現未曾預見的刮痕、污染、結構變形或缺件，無法事先窮舉。
  2. 異常樣本極度稀缺：產線優化後不良品極少，但正常良品影像充足。
  3. 初學者比喻（AI 整理）：就像訓練驗鈔員熟記真鈔的每一處細節，任何偏離正常樣態的區域即為異常。
  4. 合成異常補充：雖然訓練集只收集真實正常品，但 `DiffusionAD` 與 `LAMBDA` 會在訓練階段利用 Perlin 雜訊與 `DTD` 紋理在正常影像上合成人工異常，以監督訓練分割子網路。
- **為什麼不能直接拿 CIFAR-10 / ImageNet 抽換類別當異常檢測？**
  - 跨類別 Outlier（整張圖是不同物種）與真實工業異常（與正常品極度相似、僅在局部微小區域出現細微偏差）本質不同。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C02-01` | 真實工業光學檢測面臨「事先未知會出現何種缺陷」與「異常樣本極度稀缺、正常樣本充足」兩大限制，因此非監督式異常檢測僅使用無缺陷正常影像進行訓練 | 非監督式異常檢測任務定義 | MVTec AD | 無 | 訓練集僅含無缺陷正常影像 | `wiki/concepts/unsupervised-anomaly-detection.md` `## 1. 概念定義與問題設定` | `bergmann2019-mvtec-ad.pdf` Sec. 1, p. 1–2 | 原文事實 |
| `C02-02` | 將 MNIST、CIFAR10、ImageNet 的部分類別當作 Outlier 屬於跨類別語意差異，無法反映真實工業場景中「僅在微小局部區域出現細微偏差」的檢測需求 | 非監督式異常檢測任務定義 | MVTec AD / CIFAR10 / ImageNet | 無 | 局部細微異常 vs. 跨類別異常 | `wiki/papers/bergmann2019-mvtec-ad.md` `## 2. 一句話總結（TL;DR）與核心貢獻` | `bergmann2019-mvtec-ad.pdf` Sec. 1 & Sec. 2.1.1, p. 1–2 | 原文事實 |
| `C02-03` | 視覺異常檢測在測試階段需同時支援「影像級異常分類（判斷整張影像是否包含異常）」與「像素級異常分割（輸出空間異常圖標示異常像素區域）」 | 非監督式異常檢測任務定義 | MVTec AD | 無 | Image-level 與 Pixel-level 雙層輸出 | `wiki/concepts/unsupervised-anomaly-detection.md` `## 1. 概念定義與問題設定` | `bergmann2019-mvtec-ad.pdf` Sec. 1, p. 1–2 & Sec. 4.3, p. 6 | 原文事實 |
| `C02-04` | 部分重建與分割方法（如 DiffusionAD 與 LAMBDA）在僅有真實正常訓練樣本的前提下，會透過 Perlin 雜訊與外部紋理在正常影像上合成異常樣本，以聯合訓練像素級分割子網路 | DiffusionAD / LAMBDA 異常合成設定 | MVTec AD / VisA | 無 | 僅用真實正常品 + 人工合成異常訓練分割網路 | `wiki/papers/zhang2023-diffusionad.md` `### 4.5 線上異常合成策略（Online Anomaly Synthesis Strategy）`；`wiki/papers/lee2026-lambda.md` `### 4.2 異常合成策略（Anomaly Synthesis Strategy，出自論文 Sec. 4.2, p. 4–5, Fig. 1a）` | `zhang2023-diffusionad.pdf` Sec. IV-C, p. 6, Fig. 6, Eq. 12；`lee2026-lambda.pdf` Sec. 4.2, p. 4–5, Fig. 1a | 原文事實 |

---

## 第 3 頁：MVTec AD 與基本評估

### 學習目標
認識工業異常檢測標準基準 MVTec AD 的資料分工，並理解影像級與像素級（`AUROC` 與 `PRO`）基本評估方式。

### 用到的 Wiki 頁與段落
- `wiki/papers/bergmann2019-mvtec-ad.md` `## 4. 資料集規格與評估指標`
- `wiki/papers/bergmann2019-mvtec-ad.md` `### 5.3 像素級異常分割表現（出自論文 Table 3, p. 7）`
- `wiki/papers/bergmann2019-mvtec-ad.md` `## 6. 各方法失敗案例與限制（Limitations）`
- `wiki/datasets/mvtec-ad.md` `## 4. 官方評估指標定義（出自 bergmann2019-mvtec-ad.pdf Sec. 4.3, p. 6–7）`

### 預計使用的圖檔
- 無

### 投影片可見內容
- **可見正文（105 字）**：
  - **資料分工（MVTec AD，15 類工業紋理與物件）**：
    - **訓練集（3,629 張）**：全部是無缺陷正常品。
    - **測試集（1,725 張）**：同時包含正常品與像素標註瑕疵品。
  - **基本評估方式**：
    - **影像級評估（`Image AUROC`）**：評估整張圖良品／不良品的排序能力。
    - **像素級評估（`Pixel AUROC`、`PRO`）**：評估瑕疵區域定位準確度。
- **延伸閱讀**：[Bergmann et al. (2019) — MVTec AD §4](../../wiki/papers/bergmann2019-mvtec-ad.md#4-資料集規格與評估指標)、[MVTec AD 資料集與評估指標 §3–§4](../../wiki/datasets/mvtec-ad.md#3-資料集規格總覽出自-bergmann2019-mvtec-adpdf-table-1-p-4--sec-3-p-45)

### 查證資料與講稿備註
- **MVTec AD（CVPR 2019）詳細規格備註**：
  - 涵蓋 **15** 個工業類別（**5** 類材質紋理：`Carpet`、`Grid`、`Leather`、`Tile`、`Wood`；**10** 類剛性或可變形物件：`Bottle`、`Cable`、`Capsule`、`Hazelnut`、`Metal Nut`、`Pill`、`Screw`、`Toothbrush`、`Transistor`、`Zipper`）。
  - 總計 **5,354** 張高解析度影像（邊長 $700 \times 700$ 至 $1024 \times 1024$）：訓練集 **3,629** 張正常品；測試集 **1,725** 張（**467** 張正常 + **1,258** 張異常），涵蓋 **73** 種缺陷類型與 **1,888** 個像素級標註區域。
- **指標與早期挑戰備註**：
  - `ROC AUC`（`AUROC`）掃描所有可能閾值計算 TPR 對 FPR 之曲線下面積；`PRO` 則對每個獨立連通缺陷區域分別計算重疊率再取平均。
  - 在 MVTec AD 原論文評測的 6 種早期方法中，無單一方法能通吃全部 15 類；例如 `AE (SSIM)` 在 `Hazelnut` 雖有 `0.97` ROC AUC，但在無缺陷驗證集估計之單一閾值下 `PRO` 僅 `0.00`（Table 3, p. 7）。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C03-01` | MVTec AD 包含 15 個類別（5 種紋理與 10 種物件）、共 5,354 張高解析度影像（邊長 700×700 至 1024×1024），其中訓練集為 3,629 張無缺陷影像，測試集為 1,725 張影像（467 張正常、1,258 張異常），涵蓋 73 種缺陷類型與 1,888 個像素級標註區域 | 資料集設計（Bergmann et al., 2019） | MVTec AD | 資料集規模統計 | 15 類、總計 5,354 張（訓練 3,629 正常／測試 467 正常 + 1,258 異常）、73 種缺陷、1,888 個標註區域 | `wiki/papers/bergmann2019-mvtec-ad.md` `## 4. 資料集規格與評估指標` | `bergmann2019-mvtec-ad.pdf` Sec. 1, p. 2, Table 1 & Sec. 3, p. 4–5 | 原文事實 |
| `C03-02` | Pixel-level ROC AUC 計算全測試集正確分類異常像素比例（TPR）對誤判正常像素比例（FPR）的曲線下面積；PRO（Relative Per-Region Overlap）則計算各獨立連通缺陷區域的重疊比例並取平均 | 評估指標定義（Bergmann et al., 2019） | MVTec AD | Pixel ROC AUC / PRO | 無閾值曲線下面積 vs. 連通缺陷區域平均重疊率 | `wiki/datasets/mvtec-ad.md` `## 4. 官方評估指標定義（出自 bergmann2019-mvtec-ad.pdf Sec. 4.3, p. 6–7）` | `bergmann2019-mvtec-ad.pdf` Sec. 4.3, p. 6–7 & Table 3, p. 7 | 原文事實 |
| `C03-03` | 在 MVTec AD 原論文評測的 6 種早期基準方法中，無單一方法能通吃全部 15 個類別；且僅靠無缺陷驗證集估計二值化分割閾值極為困難（如 `AE (SSIM)` 在 `Hazelnut` 雖有高 ROC AUC，但驗證集閾值下 PRO 極低） | AE (SSIM) 等 6 種早期 Baseline | MVTec AD | 定性失敗與閾值估計挑戰 | 無單一方法通吃 15 類；無異常驗證集閾值估計困難 | `wiki/papers/bergmann2019-mvtec-ad.md` `## 6. 各方法失敗案例與限制（Limitations）` | `bergmann2019-mvtec-ad.pdf` Sec. 4.4, p. 7–8 | 原文事實 |

---

## 第 4 頁：兩條基本路線：重建正常外觀／比對正常特徵

### 學習目標
掌握視覺異常檢測的兩條基本技術路線——「重建正常外觀」與「比對正常特徵」的核心直覺與各自難題。

### 用到的 Wiki 頁與段落
- `wiki/comparisons/embedding-vs-reconstruction.md` `## 1. 比較維度與脈絡概述`
- `wiki/comparisons/embedding-vs-reconstruction.md` `## 2. 初學者版（AI 整理）`
- `wiki/papers/bergmann2019-mvtec-ad.md` `## 6. 各方法失敗案例與限制（Limitations）`

### 預計使用的圖檔
- 無

### 投影片可見內容
- **可見正文（110 字）**：
  - **路線一：重建正常外觀（臨摹畫家派，AI 整理）**
    - **直覺**：只教模型重畫正常品；測試時把異常處修成正常，相減即得瑕疵。
    - **難題**：壓太扁會連正常紋理也畫糊；記太細又會連瑕疵一起照抄。
  - **路線二：比對正常特徵（顯微鏡相簿派，AI 整理）**
    - **直覺**：借用預訓練網路提取正常區塊特徵存檔，測試時比對距離。
    - **難題**：早期作法沒記住位置資訊，且預訓練特徵未必懂工業零件。
- **延伸閱讀**：[預訓練特徵嵌入 vs. 重建式異常檢測流派對比 §1–§2](../../wiki/comparisons/embedding-vs-reconstruction.md#1-比較維度與脈絡概述)、[MVTec AD 各方法失敗案例與限制 §6](../../wiki/papers/bergmann2019-mvtec-ad.md#6-各方法失敗案例與限制limitations)

### 查證資料與講稿備註
- **早期方法具體瓶頸（留於講稿補充，不放入投影片可見畫面）**：
  1. `Autoencoder`（`AE (L2)`、`AE (SSIM)`）：透過維度 `100` 的 Bottleneck 壓縮重建會丟失高頻細節，在 `Tile`、`Zipper` 等高頻紋理產生大量假陽性；若直接加 Skip Connections 又會發生恆等映射（照抄異常）。
  2. `AnoGAN`：容易發生 Mode Collapse，且測試時需 `300` 次潛在空間迭代搜尋，耗時極長。
  3. `CNN Feature Dictionary`：擷取預訓練 `ResNet-18` 的 `512` 維特徵，經 PCA（保留 `95%` 變異）與 K-means（`10` 個群心）建立字典，因未納入空間位置資訊且為滑動視窗，在結構化物件類別表現退化、異常圖粗糙。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C04-01` | 傳統深度自編碼器（`AE (L2)`、`AE (SSIM)`）透過 Bottleneck 重建影像會丟失高頻細節導致重建模糊，在 `Tile` 與 `Zipper` 等高頻紋理上產生大量假陽性 | AE (L2) / AE (SSIM) | MVTec AD | 定性失敗分析 | 高頻紋理重建模糊導致 False Positives | `wiki/papers/bergmann2019-mvtec-ad.md` `## 6. 各方法失敗案例與限制（Limitations）` | `bergmann2019-mvtec-ad.pdf` Sec. 4.1.2, p. 5 & Sec. 4.4.2, p. 8 | 原文事實 |
| `C04-02` | `AnoGAN` 容易發生 Mode Collapse，難以處理形狀或朝向變化大的物件及 `Carpet` 細緻紋理，且測試階段潛在空間迭代搜尋耗時極長 | AnoGAN | MVTec AD | 定性失敗分析 | Mode Collapse 與潛在空間迭代搜尋耗時 | `wiki/papers/bergmann2019-mvtec-ad.md` `## 6. 各方法失敗案例與限制（Limitations）` | `bergmann2019-mvtec-ad.pdf` Sec. 4.1.1, p. 5 & Sec. 4.4.1, p. 8 | 原文事實 |
| `C04-03` | 早期 `CNN Feature Dictionary` 因未納入特徵的空間位置資訊且採滑動視窗比對，在物件類別上表現明顯退化且異常圖粗糙 | CNN Feature Dictionary | MVTec AD | 定性失敗分析 | 缺乏空間位置資訊導致物件類別退化 | `wiki/papers/bergmann2019-mvtec-ad.md` `## 6. 各方法失敗案例與限制（Limitations）` | `bergmann2019-mvtec-ad.pdf` Sec. 2.2.3, p. 4, Sec. 4.1.3, p. 5 & Sec. 4.4.3, p. 8 | 原文事實 |
| `C04-04` | 重建路線如同「臨摹畫家派（只練畫良品，比對原圖與重畫差異）」，預訓練特徵路線則如同「顯微鏡相簿派（用預訓練網路拍下正常局部特徵存檔比對）」（AI 整理） | 重建式 vs. 特徵嵌入流派 | 無 | 無 | 兩大路線直覺對比 | `wiki/comparisons/embedding-vs-reconstruction.md` `## 2. 初學者版（AI 整理）` | 無（基於跨論文流派特性之教學比喻） | AI 推論 |
| `C04-05` | 傳統 Autoencoder 若加入 `U-Net` 的 Skip Connections，低階特徵會直接傳到輸出層，形成連異常也照抄的平凡解（Trivial solution），這是 RIAD 改用遮罩修補的動機之一 | Autoencoder + Skip Connections（RIAD 所述背景） | MVTec AD | 無 | 無 | `wiki/papers/zavrtanik2021-riad.md` `## 2. 一句話總結（TL;DR）與核心貢獻` | `zavrtanik2021-riad.pdf` Abstract & Sec. 1, p. 1、Sec. 3.2, p. 3 | 原文事實 |

---

## 第 5 頁：RIAD

### 學習目標
理解 RIAD 如何透過「隨機網格挖空修補（Reconstruction by Inpainting）」阻斷異常像素照抄，並利用多尺度梯度幅值相似度（MSGMS）定位異常。

### 用到的 Wiki 頁與段落
- `wiki/papers/zavrtanik2021-riad.md` `## 4. 方法架構與核心設計`
- `wiki/papers/zavrtanik2021-riad.md` `### 5.1 實驗設定（出自論文 Sec. 4.1–4.3, p. 5–6）`
- `wiki/papers/zavrtanik2021-riad.md` `### 5.2 MVTec AD 影像級異常檢測結果（出自論文 Table 1, p. 6，指標：Image ROC AUC %）`
- `wiki/papers/zavrtanik2021-riad.md` `### 5.3 MVTec AD 像素級異常定位結果（出自論文 Table 2, p. 6，指標：Pixel ROC AUC %）`
- `wiki/papers/zavrtanik2021-riad.md` `### 5.5 消融實驗重點（Ablation Studies，出自論文 Sec. 6 & Tables 4–6, p. 7–8）`
- `wiki/papers/zavrtanik2021-riad.md` `## 6. 論文限制（Limitations）與延伸筆記`
- `wiki/datasets/mvtec-ad.md` `### 5.2 後續收錄方法於 MVTec AD 的演進表現匯總`

### 預計使用的圖檔
- `assets/diagrams/zavrtanik2021-riad-fig1.svg`（簡報相對路徑：`../../assets/diagrams/zavrtanik2021-riad-fig1.svg`）

### 投影片可見內容
- **上方架構圖**：`../../assets/diagrams/zavrtanik2021-riad-fig1.svg`（標註：示意圖，依論文 Fig. 1 重繪）
- **下方四問卡片（統一四問結構，共 108 字，含 3 個關鍵數字：3、12、94.2%）**：
  1. **輸入什麼？** 將影像切成多尺度網格，隨機分成 **3** 組互斥遮罩輪流挖空後的殘缺影像。
  2. **保存或學到什麼？** 訓練 U-Net 僅靠周圍未遮蔽的正常鄰域修補挖空處，防止直接照抄瑕疵。
  3. **怎麼產生異常分數？** 拼回修補區塊，以多尺度梯度幅值相似度（`MSGMS`）比對原圖與重建圖（MVTec AD 像素級 AUROC 達 **94.2%**）。
  4. **主要限制？** 單張圖需跑 **12** 次前向推論；隨機結構難以由鄰域猜出，純色差瑕疵反應較弱。
- **延伸閱讀**：[Zavrtanik et al. (2021) — RIAD §4–§6](../../wiki/papers/zavrtanik2021-riad.md#4-方法架構與核心設計)、[遮罩修復重建與多尺度梯度相似度](../../wiki/concepts/reconstruction-by-inpainting.md#1-概念定義與解決的問題)

### 查證資料與講稿備註
- **四問詳細查證參數與公式備註**：
  1. 輸入：將 $256 \times 256$ 影像切分為 $k \times k$（MVTec AD 預設 $K = \{2, 4, 8, 16\}$）網格，隨機均分為 $n = 3$ 個互斥子集輪流置零：$\mathbf{I}_i = M_{S_i} \odot \mathbf{I}$。
  2. 學習目標：訓練含 Skip Connections 的 U-Net（300 Epochs，結合 `MSGMS` + `SSIM` + $L_2$ 損失），僅取每次被遮蔽區塊的修補結果拼回完整重建圖 $\mathbf{I}_r = \sum_{i=1}^n \overline{M_{S_i}} \odot \mathbf{I}_{ri}$。
  3. 評分與表現：計算 4 層金字塔 Prewitt 梯度幅值相似度（`MSGMS`），經 $21 \times 21$ 均值平滑並跨 4 個尺度平均得異常圖 $G_A$，取最大值為影像級分數。於 MVTec AD 全類別平均（$\text{avg}$）達 **91.7%** Image ROC AUC（Table 1）與 **94.2%** Pixel ROC AUC（Table 2）；消融實驗顯示 `MSGMS`（91.7%）比改用 `SSIM` 評分的 `RIAD_SSIM`（85.2%）高出 6.5 個百分點（Table 6）。
  4. 限制：單張影像需 $N_K \times n = 4 \times 3 = 12$ 次 U-Net 推論；`cable`、`hazelnut` 等隨機結構與 `pill`、`screw` 等純顏色異常表現受限。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C05-01` | RIAD 將輸入影像（$256 \times 256$）切分為 $k \times k$ 網格（MVTec AD 預設 $K=\{2,4,8,16\}$）並隨機均分為 $n=3$ 個互斥子集輪流遮蔽，使含 Skip Connections 的 U-Net 在修補目標區塊時看不見該處原始像素，最後僅取被遮蔽區塊拼回完整重建影像 $\mathbf{I}_r$ | RIAD | MVTec AD | 架構與超參數設定 | 輸入 256×256，$n=3$，$K=\{2,4,8,16\}$，300 Epochs | `wiki/papers/zavrtanik2021-riad.md` `## 4. 方法架構與核心設計`；`wiki/papers/zavrtanik2021-riad.md` `### 5.1 實驗設定（出自論文 Sec. 4.1–4.3, p. 5–6）` | `zavrtanik2021-riad.pdf` Sec. 3.1–3.3, p. 2–4, Fig. 1, Fig. 4 & Sec. 4.3, p. 6 | 原文事實 |
| `C05-02` | RIAD 於 MVTec AD 全 15 類平均取得 91.7% Image ROC AUC（Table 1）與 94.2% Pixel ROC AUC（Table 2），紋理平均為 95.1% / 93.9%、物件平均為 89.9% / 94.3% | RIAD（Pattern Recognition 2021） | MVTec AD | 紋理平均 Image / Pixel ROC AUC (%) / 物件平均 Image / Pixel ROC AUC (%) / 全 15 類平均 Image / Pixel ROC AUC / PRO (%) | 95.1 / 93.9｜89.9 / 94.3｜91.7 / 94.2 / - | `wiki/datasets/mvtec-ad.md` `### 5.2 後續收錄方法於 MVTec AD 的演進表現匯總`；`wiki/papers/zavrtanik2021-riad.md` `### 5.2 MVTec AD 影像級異常檢測結果（出自論文 Table 1, p. 6，指標：Image ROC AUC %）` | `zavrtanik2021-riad.pdf` Table 1 & Table 2, p. 6 | 原文事實 |
| `C05-03` | 在 MVTec AD 消融實驗（Table 6）中，無 Skip Connections `RIAD_ns`（88.6%）vs. 改用 SSIM 評分 `RIAD_SSIM`（85.2%）vs. 完整 `RIAD`（91.7%），顯示加入 Skip Connections 與採用 `MSGMS` 評分皆能提升表現 | 3. U-Net Skip Connections 與異常評分函數 | MVTec AD | 關鍵比較設定與平均 Image ROC AUC (%) | 無 Skip Connections RIAD_ns (88.6%) vs. 改用 SSIM 評分 RIAD_SSIM (85.2%) vs. 完整 RIAD (91.7%) | `wiki/papers/zavrtanik2021-riad.md` `### 5.5 消融實驗重點（Ablation Studies，出自論文 Sec. 6 & Tables 4–6, p. 7–8）`；`wiki/papers/zavrtanik2021-riad.md` `### 5.2 MVTec AD 影像級異常檢測結果（出自論文 Table 1, p. 6，指標：Image ROC AUC %）` | `zavrtanik2021-riad.pdf` Sec. 6 & Table 6, p. 8 | 原文事實 |
| `C05-04` | RIAD 的主要限制包含：(1) 單張測試影像需執行 $N_K \times n = 4 \times 3 = 12$ 次 U-Net 前向修補；(2) 包含大量隨機結構或與鄰域缺乏強相關性的區域（如 `cable`、`hazelnut`）難以由鄰域準確重建；(3) 純顏色異常在 `MSGMS` 下不如 `SSIM` 敏感（如 `pill`、`screw`） | RIAD | MVTec AD | 推論次數與方法限制 | 單張影像需 12 次網路前向推論 | `wiki/papers/zavrtanik2021-riad.md` `## 6. 論文限制（Limitations）與延伸筆記` | `zavrtanik2021-riad.pdf` Sec. 3.1, 3.3–3.4, p. 2–4 & Sec. 5–6, p. 6–8, Table 6 | 原文事實 |

---

## 第 6 頁：PatchCore

### 學習目標
理解 PatchCore 如何在不訓練目標網路權重的前提下，利用預訓練中階局部特徵與貪婪核心集下採樣（Greedy Coreset）達成高精準度與快速推論。

### 用到的 Wiki 頁與段落
- `wiki/papers/roth2022-patchcore.md` `## 4. 方法架構與核心設計`
- `wiki/papers/roth2022-patchcore.md` `#### (A) 影像級異常檢測（Table 1, p. 6）與像素級異常分割（Table 2, p. 6 & Table 3, p. 7）匯總`
- `wiki/papers/roth2022-patchcore.md` `#### (C) 單張影像平均推論時間與近似最近鄰比較（出自論文 Table 5, p. 7）`
- `wiki/papers/roth2022-patchcore.md` `## 6. 論文限制（Limitations）與延伸筆記`
- `wiki/concepts/memory-bank.md` `## 3. 核心原理與數學公式（出自 roth2022-patchcore.pdf Sec. 3, p. 3–5）`

### 預計使用的圖檔
- `assets/diagrams/roth2022-patchcore-fig2.svg`（簡報相對路徑：`../../assets/diagrams/roth2022-patchcore-fig2.svg`）

### 投影片可見內容
- **上方架構圖**：`../../assets/diagrams/roth2022-patchcore-fig2.svg`（標註：示意圖，依論文 Fig. 2 重繪）
- **下方四問卡片（統一四問結構，共 115 字，含 3 個關鍵數字：1%、99.0%、0.17 s）**：
  1. **輸入什麼？** 無資料擴增之單張影像（縮放並中心裁切），送入固定的 ImageNet 預訓練骨幹網路。
  2. **保存或學到什麼？** 不需訓練網路權重；擷取中階局部鄰域聚合特徵建立記憶庫 \(\mathcal{M}\)，再以貪婪核心集（Greedy Coreset）壓縮至 **1%** 代表性特徵 \(\mathcal{M}_C\)。
  3. **怎麼產生異常分數？** 計算測試 Patch 到 \(\mathcal{M}_C\) 的最近鄰距離並以鄰域密度重加權（`PatchCore-1%` 於 MVTec AD 達 **99.0%** 影像 AUROC、單張推論 **0.17 s**）。
  4. **主要限制？** 受限於 ImageNet 預訓練特徵對目標領域的可遷移性，高正常變異易誤報，且中心裁切會漏檢邊界瑕疵。
- **延伸閱讀**：[Roth et al. (2022) — PatchCore §4–§6](../../wiki/papers/roth2022-patchcore.md#4-方法架構與核心設計)、[局部特徵記憶庫與核心集下採樣 §3](../../wiki/concepts/memory-bank.md#3-核心原理與數學公式出自-roth2022-patchcorepdf-sec-3-p-35)

### 查證資料與講稿備註
- **四問詳細查證參數與公式備註**：
  1. 輸入：MVTec AD 預設將影像縮放至 $256 \times 256$ 後中心裁切為 $224 \times 224$，不使用資料擴增，送入預訓練 `WideResNet50`（Sec. 4.1, p. 5）。
  2. 記憶庫與核心集公式：擷取第 2 與第 3 區塊中階特徵，以 $p=3$ 鄰域平均池化聚合建立 $\mathcal{M}$，再求解極小化極大設施選址目標（Eq. 5）：
     $$\mathcal{M}_C^* = \arg\min_{\mathcal{M}_C \subset \mathcal{M}} \max_{m \in \mathcal{M}} \min_{n \in \mathcal{M}_C} \|m - n\|_2$$
  3. 評分公式與 Table 1–3 vs. Table 5 嚴格區分：
     - Table 1–3（§5.2 A）：`PatchCore-25%` 達 **99.1%** Image AUROC、**98.1%** Pixel AUROC、**93.4%** PRO（誤分類 **42** 張）；`PatchCore-10%` 為 **99.0%** / **98.1%** / **93.5%**；`PatchCore-1%` 為 **99.0%** / **98.0%** / **93.1%**（註：Table 1–3 不含推論時間；Table 5 未測 `PatchCore-25%` 之推論時間，不得補值）。
     - Table 5（§5.2 C，同一 `WideResNet50` 與 Tesla V4 GPU 重實作評測）：`PatchCore-100%` 為 `99.1% / 98.0% / 93.3% / 0.60 s`；`PatchCore-10%` 為 `99.0% / 98.1% / 93.5% / 0.22 s`；`PatchCore-1%` 為 `99.0% / 98.0% / 93.1% / 0.17 s`；`PaDiM（重實作，WideResNet50）` 為 `95.4% / 97.3% / 91.8% / 0.19 s`；`SPADE（重實作，WideResNet50）` 為 `85.3% / 96.6% / 91.5% / 0.66 s`。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C06-01` | PatchCore 不需在目標資料集上訓練微調網路權重，預設使用 ImageNet 預訓練 `WideResNet50` 擷取第 2 與第 3 區塊中階特徵，並以 $p=3$ 局部鄰域自適應平均池化聚合建立全圖共享之 Patch 特徵記憶庫 $\mathcal{M}$，再以極小化極大設施選址目標執行貪婪核心集下採樣（Greedy Coreset）與最近鄰密度重加權評分 | PatchCore | MVTec AD | 架構與核心集公式 | 預訓練 WideResNet50 層級 2+3，鄰域 $p=3$，Eq. 5 Coreset 目標、Eq. 6–7 最近鄰距離與重加權 | `wiki/papers/roth2022-patchcore.md` `## 4. 方法架構與核心設計` | `roth2022-patchcore.pdf` Sec. 3.1–3.3, p. 3–5, Eq. 1–7 & Algorithm 1 | 原文事實 |
| `C06-02` | 在 MVTec AD（Table 1–3）上，`PatchCore-25%` 達到 99.1% Image AUROC、98.1% Pixel AUROC、93.4% PRO，且在 1,725 張測試影像中誤分類張數為 42 張（以 F1 最佳閾值計算的假陽性加假陰性總數，且只對 PatchCore 計算） | PatchCore-25% | MVTec AD | Image AUROC ↑ (%) / Pixel AUROC ↑ (%) / PRO ↑ (%) / 誤分類張數 ↓ (共 1,725 張) | 99.1 / 98.1 / 93.4 / 42 | `wiki/papers/roth2022-patchcore.md` `#### (A) 影像級異常檢測（Table 1, p. 6）與像素級異常分割（Table 2, p. 6 & Table 3, p. 7）匯總` | `roth2022-patchcore.pdf` Tables 1–3, p. 6–7 | 原文事實 |
| `C06-03` | 在 MVTec AD 推論時間評測（Table 5）中，`PatchCore-1%` 達到 99.0% Image AUROC、98.0% Pixel AUROC、93.1% PRO，單張影像平均推論時間為 0.17 s；同表 `PatchCore-10%` 為 99.0% / 98.1% / 93.5% / 0.22 s | PatchCore-1% / PatchCore-10% | MVTec AD | Image AUROC (%) / Pixel AUROC (%) / PRO (%) / 單張影像平均推論時間 (秒) | 99.0 / 98.0 / 93.1 / 0.17 s｜99.0 / 98.1 / 93.5 / 0.22 s | `wiki/papers/roth2022-patchcore.md` `#### (C) 單張影像平均推論時間與近似最近鄰比較（出自論文 Table 5, p. 7）` | `roth2022-patchcore.pdf` Table 5, p. 7 & Supp. A, p. 12 | 原文事實 |
| `C06-04` | PatchCore 的主要限制在於其表現受限於預訓練特徵對目標領域的可遷移性（未進行特徵調適），面對高正常變異易產生假陽性，且前處理中心裁切曾導致邊緣瑕疵被裁掉而漏檢 | PatchCore | MVTec AD | 方法限制與錯誤分析 | 預訓練特徵遷移限制；19 張 FP 與 23 張 FN 錯誤剖析 | `wiki/papers/roth2022-patchcore.md` `## 6. 論文限制（Limitations）與延伸筆記` | `roth2022-patchcore.pdf` Sec. 5, p. 8 & Supp. Sec. C.4, p. 12–14 | 原文事實 |

---

## 第 7 頁：DDPM 入門

### 學習目標
理解去噪擴散機率模型（DDPM）的前向加噪、逆向預測雜訊與單步重建估計 $\hat{\mathbf{x}}_0$，以及如何應用於異常檢測。

### 用到的 Wiki 頁與段落
- `wiki/papers/ho2020-ddpm.md` `## 4. 方法架構與核心設計`
- `wiki/papers/ho2020-ddpm.md` `## 5. 在異常檢測中怎麼被使用（與關鍵實驗特性）`
- `wiki/papers/ho2020-ddpm.md` `## 6. 論文限制（Limitations）與延伸筆記`
- `wiki/concepts/denoising-diffusion-probabilistic-models.md` `## 3. 核心數學原理與公式（出自 ho2020-ddpm.pdf Sec. 2 & Sec. 3, p. 2–5）`

### 預計使用的圖檔
- `assets/diagrams/ho2020-ddpm-fig2.svg`（簡報相對路徑：`../../assets/diagrams/ho2020-ddpm-fig2.svg`）

### 投影片可見內容
- **上方架構圖**：`../../assets/diagrams/ho2020-ddpm-fig2.svg`（標註：示意圖，依論文 Fig. 2 重繪）
- **可見正文（106 字，不放 CIFAR10 的 FID／IS，集中在加噪、預測雜訊、重建）**：
  - **前向加噪**：利用閉式解直接跳到第 \(t\) 步混入高斯雜訊，把局部瑕疵淹沒。
  - **逆向預測雜訊**：訓練 U-Net 網路 \(\boldsymbol{\epsilon}_\theta(\mathbf{x}_t, t)\) 預測混入的雜訊 \(\boldsymbol{\epsilon}\)。
  - **單步重建正常外觀**：不需慢速走完 **1000** 步，可直接由含噪圖與預測雜訊一步推算無雜訊重建圖 \(\hat{\mathbf{x}}_0\)：
- **可見公式（1 條）**：
  $$\hat{\mathbf{x}}_0 = \frac{\mathbf{x}_t - \sqrt{1 - \bar{\alpha}_t}\boldsymbol{\epsilon}_\theta(\mathbf{x}_t, t)}{\sqrt{\bar{\alpha}_t}}$$
- **延伸閱讀**：[Ho et al. (2020) — DDPM §4–§5](../../wiki/papers/ho2020-ddpm.md#4-方法架構與核心設計)、[去噪擴散機率模型（DDPM） §3](../../wiki/concepts/denoising-diffusion-probabilistic-models.md#3-核心數學原理與公式出自-ho2020-ddpmpdf-sec-2--sec-3-p-25)

### 查證資料與講稿備註
- **前向閉式解與簡化損失備註**：
  - 前向過程閉式解：$\mathbf{x}_t = \sqrt{\bar{\alpha}_t}\mathbf{x}_0 + \sqrt{1 - \bar{\alpha}_t}\boldsymbol{\epsilon}$（Eq. 4，預設總步數 $T=1000$）。
  - 訓練目標：$L_{\text{simple}}(\theta) = \mathbb{E}_{t, \mathbf{x}_0, \boldsymbol{\epsilon}}[\|\boldsymbol{\epsilon} - \boldsymbol{\epsilon}_\theta(\mathbf{x}_t, t)\|^2]$（Eq. 14）。
- **在異常檢測中的關鍵角色備註**：
  - 部分擴散（Partial Diffusion）：加噪至 $t = 1000$ 會完全抹除原圖結構；若只加噪至中間步數 $t < T$（如 $t = 250$ 或 $500$），能保留物件全域姿態與正常大結構，同時用高斯雜訊淹沒局部細微異常（AI 整理）。
  - 克服取樣耗時：完整 $T = 1000$ 步逐步取樣極慢（128 張 $256 \times 256$ 影像在 TPU v3-8 需 300 秒，Appendix B, p. 14），而 Eq. 15 單步重建估計成為後續 `DiffusionAD` 與 `LAMBDA` 一步去噪重建的數學基礎。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C07-01` | DDPM 前向過程具閉式解 $\mathbf{x}_t = \sqrt{\bar{\alpha}_t}\mathbf{x}_0 + \sqrt{1-\bar{\alpha}_t}\boldsymbol{\epsilon}$，逆向過程將高斯平均數參數化為預測雜訊 $\boldsymbol{\epsilon}_\theta(\mathbf{x}_t, t)$ 並以無權重簡化損失 $L_{\text{simple}}$ 訓練（預設總步數 $T=1000$） | DDPM | 無（理論與架構設計） | 前向閉式解與逆向雜訊預測目標 | $T=1000$，Eq. 4 前向閉式解、Eq. 14 簡化損失 $L_{\text{simple}}$ | `wiki/papers/ho2020-ddpm.md` `## 4. 方法架構與核心設計` | `ho2020-ddpm.pdf` Sec. 2–3, p. 2–5, Eq. 4 & Eq. 14 | 原文事實 |
| `C07-02` | DDPM 在任意時間步 $t$ 可由含噪影像 $\mathbf{x}_t$ 與預測雜訊直接計算單步重建估計 $\hat{\mathbf{x}}_0 = (\mathbf{x}_t - \sqrt{1-\bar{\alpha}_t}\boldsymbol{\epsilon}_\theta(\mathbf{x}_t, t))/\sqrt{\bar{\alpha}_t}$，且固定中間時間步 $t$ 去噪時具有「大 $t$ 決定粗粒度全域結構、小 $t$ 保留細部特徵」之漸進式解碼特性 | DDPM | CIFAR10 / CelebA-HQ / LSUN | 重建估計公式與漸進生成特性 | Eq. 15 單步重建估計；$t \in \{1000, 750, 500, 250\}$ 插值與重建實驗 | `wiki/papers/ho2020-ddpm.md` `## 4. 方法架構與核心設計`；`wiki/papers/ho2020-ddpm.md` `## 5. 在異常檢測中怎麼被使用（與關鍵實驗特性）` | `ho2020-ddpm.pdf` Sec. 4.3, p. 6–7, Eq. 15, Fig. 7 & Appendix D, p. 15–16 | 原文事實 |
| `C07-03` | DDPM 完整執行 $T=1000$ 步逆向序列取樣速度較慢（在 TPU v3-8 上取樣一批 128 張 $256 \times 256$ 影像需 300 秒） | DDPM | LSUN / 256×256 影像 | 取樣耗時 | 128 張 256×256 影像需 300 秒（T=1000，TPU v3-8） | `wiki/papers/ho2020-ddpm.md` `## 5. 在異常檢測中怎麼被使用（與關鍵實驗特性）`；`wiki/papers/ho2020-ddpm.md` `## 6. 論文限制（Limitations）與延伸筆記` | `ho2020-ddpm.pdf` Sec. 4, p. 5 & Appendix B, p. 14 | 原文事實 |
| `C07-04` | 後續異常檢測方法（如 DiffusionAD 與 LAMBDA）利用 DDPM 的部分步數加噪（$t < T$）淹沒局部異常並保留正常全域結構，再藉由 Eq. 15 一步去噪重建正常外觀（AI 整理） | DDPM 應用於異常檢測 | 無 | 無 | 部分擴散 + 一步去噪於異常檢測之連結 | `wiki/papers/ho2020-ddpm.md` `## 5. 在異常檢測中怎麼被使用（與關鍵實驗特性）` | 無（跨論文方法連結分析） | AI 推論 |

---

## 第 8 頁：DiffusionAD

### 學習目標
理解 DiffusionAD 如何透過「一步去噪（One-step Denoising）」與「雙尺度規範引導（NOD）」兼顧大面積異常抹除、正常細節保留與高速推論。

### 用到的 Wiki 頁與段落
- `wiki/papers/zhang2023-diffusionad.md` `## 4. 方法架構與核心設計`
- `wiki/papers/zhang2023-diffusionad.md` `### 5.1 實驗設定、資料集與評估指標`
- `wiki/papers/zhang2023-diffusionad.md` `### 5.2 四大資料集綜合基準對比（出自論文 Table V）`
- `wiki/papers/zhang2023-diffusionad.md` `## 6. 論文限制（Limitations）與延伸筆記`
- `wiki/concepts/norm-guided-one-step-denoising.md` `## 3. 核心原理與數學公式`

### 預計使用的圖檔
- `assets/diagrams/zhang2023-diffusionad-fig3.svg`（簡報相對路徑：`../../assets/diagrams/zhang2023-diffusionad-fig3.svg`）

### 投影片可見內容
- **上方架構圖**：`../../assets/diagrams/zhang2023-diffusionad-fig3.svg`（標註：示意圖，依論文 Fig. 3 重繪）
- **下方四問卡片（統一四問結構，共 114 字，含 3 個關鍵數字：200、400、99.7%）**：
  1. **輸入什麼？** 對輸入影像同時施加小尺度（\(t_s=\) **200**）與大尺度（\(t_b=\) **400**）雙尺度高斯雜訊（訓練時搭配合成異常）。
  2. **保存或學到什麼？** 聯合訓練「擴散去噪網路」（將異常視為雜訊濾除）與「分割 U-Net」（比對原圖與重建圖差異）。
  3. **怎麼產生異常分數？** 以大尺度一步重建結果引導小尺度一步去噪（`NOD`），再由分割網路輸出異常圖（MVTec AD 影像 AUROC 達 **99.7%**）。
  4. **主要限制？** 固定雙加噪尺度缺乏動態適應力，仰賴合成異常訓練，且像素空間雙尺度訓練耗費較多 GPU 記憶體。
- **延伸閱讀**：[Zhang et al. (2023/2025) — DiffusionAD §4–§6](../../wiki/papers/zhang2023-diffusionad.md#4-方法架構與核心設計)、[規範引導一步去噪與合成異常分割 §3](../../wiki/concepts/norm-guided-one-step-denoising.md#3-核心原理與數學公式)

### 查證資料與講稿備註
- **四問詳細查證參數與數據備註**：
  1. 輸入：影像縮放至 $256 \times 256$；訓練時 Batch size = 16（8 張正常 + 8 張由前景限制 Perlin 雜訊與 `DTD`／自身增強混合的合成異常）；雙尺度分界點 $\tau = 300$，推論時固定小尺度 $t_s = 200$、大尺度 $t_b = 400$。
  2. 學習目標：端到端聯合訓練 3000 Epochs——擴散重建子網路 $\epsilon_\theta$ 僅在正常樣本上學習雙尺度雜訊預測（`Noise-to-Norm`），分割 U-Net 以 Smooth $L_1$ + Focal Loss 學習預測異常遮罩。
  3. 評分與表現：先由 $x_{t_b}$ 一步重建參考規範 $n = \hat{x}_{0_b}$，再引導 $x_{t_s}$ 一步重建 $\hat{x}_{0_g}$（引導權重 $w=1$）；將 $x_0$ 與 $\hat{x}_{0_g}$ 拼接送入分割網路輸出異常圖 $\hat{M}$，取前 $K=50$ 最高像素平均為影像級分數。於 MVTec AD（Table V）達 `99.7 / 98.7 / 95.7 / 76.1`（`I / P / O / A` %），於 VisA（Table V）達 `98.8 / 98.9 / 96.0 / 45.8`（`I / P / O / A` %），一步去噪推論速度達 `23.5 FPS`（Table VI–VII）。
  4. 限制：固定雙加噪尺度（$t_s=200, t_b=400$）缺乏動態自適應性；合成異常未必涵蓋所有複雜或邏輯異常（Sec. VI, p. 11）。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C08-01` | DiffusionAD 發現當加噪步數 $t < 500$（$t \le 400$）時一步去噪與逐步去噪重建品質相當；其雙尺度規範引導（`NOD`）以分界點 $\tau=300$ 劃分區間，推論時固定以大尺度 $t_b=400$ 一步重建參考規範 $n=\hat{x}_{0_b}$ 引導小尺度 $t_s=200$ 一步重建 $\hat{x}_{0_g}$（引導權重 $w=1$，前 $K=50$ 最高像素平均為影像級分數） | DiffusionAD | MVTec AD / VisA / DAGM / MPDD | 架構與超參數設定 | 輸入 256×256，$T=1000, \tau=300$，推論 $t_s=200, t_b=400, w=1, K=50$，Batch size 16（8 正常 + 8 合成異常），3000 Epochs | `wiki/papers/zhang2023-diffusionad.md` `## 4. 方法架構與核心設計`；`wiki/papers/zhang2023-diffusionad.md` `### 5.1 實驗設定、資料集與評估指標` | `zhang2023-diffusionad.pdf` Sec. IV-A–IV-C, p. 4–6, Eq. 6–12, Fig. 3–5 & Sec. V-A, p. 6–7 | 原文事實 |
| `C08-02` | 在 Table V 四大資料集綜合基準對比中，`DiffusionAD（本篇）` 於 MVTec AD 的 `I / P / O / A`（Image AUROC / Pixel AUROC / Pixel PRO / Pixel AP）為 `99.7 / 98.7 / 95.7 / 76.1`，於 VisA 的 `I / P / O / A` 為 `98.8 / 98.9 / 96.0 / 45.8` | DiffusionAD（本篇） | MVTec AD / VisA | MVTec AD (`I / P / O / A`) / VisA (`I / P / O / A`) | 99.7 / 98.7 / 95.7 / 76.1｜98.8 / 98.9 / 96.0 / 45.8 | `wiki/papers/zhang2023-diffusionad.md` `### 5.2 四大資料集綜合基準對比（出自論文 Table V）` | `zhang2023-diffusionad.pdf` Table V, p. 9 | 原文事實 |
| `C08-03` | DiffusionAD 作者指出的主要限制為：(1) 依賴預先固定的雙加噪尺度（$t_s=200, t_b=400$），缺乏自適應加噪尺度與動態引導；(2) 依賴基於 Perlin 雜訊與紋理替換的合成異常，未必能完全涵蓋所有複雜或邏輯異常 | DiffusionAD | 跨資料集 | 方法限制 | 固定加噪尺度限制與合成異常多樣性限制 | `wiki/papers/zhang2023-diffusionad.md` `## 6. 論文限制（Limitations）與延伸筆記` | `zhang2023-diffusionad.pdf` Sec. VI, p. 11 | 原文事實 |

---

## 第 9 頁：LAMBDA

### 學習目標
理解 LAMBDA 如何結合預訓練 `VAE` 潛在壓縮、記憶庫引導去噪（MBG）與引導尺度圖（GSM），實現輕量化單次一步去噪重建。

### 用到的 Wiki 頁與段落
- `wiki/papers/lee2026-lambda.md` `## 4. 方法架構與核心設計`
- `wiki/papers/lee2026-lambda.md` `#### (A) VisA 資料集檢測精度與計算效率綜合比較（出自論文 Table 1, p. 8）`
- `wiki/papers/lee2026-lambda.md` `#### (B) 記憶庫大小 $n_m$ 消融實驗（出自論文 Sec. 5.8.5、Table 5 & Table A.5）`
- `wiki/papers/lee2026-lambda.md` `## 6. 論文限制（Limitations）與延伸筆記`
- `wiki/concepts/memory-bank-guided-latent-diffusion.md` `## 3. 核心原理與數學公式（出自 lee2026-lambda.pdf Sec. 3 & Sec. 4, p. 3–6）`

### 預計使用的圖檔
- `assets/diagrams/lee2026-lambda-fig1.svg`（簡報相對路徑：`../../assets/diagrams/lee2026-lambda-fig1.svg`）

### 投影片可見內容
- **上方架構圖**：`../../assets/diagrams/lee2026-lambda-fig1.svg`（標註：示意圖，依論文 Fig. 1 重繪）
- **下方四問卡片（統一四問結構，共 116 字，不放 BMAD 成績與 p-value，聚焦 VAE、記憶庫、引導各自的角色；含 3 個關鍵數字：64、200、94.2%）**：
  1. **輸入什麼？** 影像經預訓練 `VAE` 壓縮至面積縮小 **64** 倍的潛在空間，並於單一時間步加入高斯雜訊。
  2. **保存或學到什麼？** 記憶庫保存 **200** 張正常潛在表徵與距離統計；同時訓練潛在去噪網路與像素分割網路。
  3. **怎麼產生異常分數？** 檢索最相似正常潛在表徵，用引導尺度圖（`GSM`）在異常處強引導、正常處弱引導，一步去噪解碼後分割（`VisA` 像素 AUPRO 達 **94.2%**）。
  4. **主要限制？** `VAE` 有損壓縮會損失微細細節，記憶庫容量需調優，極度複雜異常引導效果可能受限。
- **延伸閱讀**：[Lee & Kang (2026) — LAMBDA §4–§6](../../wiki/papers/lee2026-lambda.md#4-方法架構與核心設計)、[潛在空間記憶庫引導去噪與引導尺度圖 §3](../../wiki/concepts/memory-bank-guided-latent-diffusion.md#3-核心原理與數學公式出自-lee2026-lambdapdf-sec-3--sec-4-p-36)

### 查證資料與講稿備註
- **VAE、記憶庫（MBG）與引導尺度圖（GSM）角色分工備註**：
  1. **預訓練 `VAE`（`Stable Diffusion v1.4` 凍結權重）**：將 RGB 影像 $I \in \mathbb{R}^{3 \times H \times W}$ 壓縮為潛在表徵 $L = E(I) \in \mathbb{R}^{4 \times H/8 \times W/8}$（空間面積降維 $64\times$），大幅降低擴散去噪的記憶體與運算量。
  2. **潛在記憶庫與 `MBG`（Memory Bank-Guided Denoising）**：預先隨機抽樣 $n_m = 200$ 張正常訓練影像編碼存入 $\mathcal{M}_b$；推論時在固定步數 $t_s = 200$ 以餘弦相似度從 $\mathcal{M}_b$ 檢索最相似正常潛在表徵 $L^g$ 作為無異常參考規範，免除 `DiffusionAD` 昂貴的大尺度去噪分支。
  3. **空間自適應引導尺度圖 `GSM`（Guidance Scale Map）**：利用記憶庫內正常樣本平均距離圖 $M_b^D$（均值與標準差）標準化輸入 $L$ 與 $L^g$ 的距離圖生成 $G$——偏離正常分布的異常區獲得高值強引導以徹底抹除異常，正常區獲得低值弱引導以保留原圖細節。
  4. **分割評分與限制**：`VAE` 解碼重建影像 $\hat{I}$ 與原圖拼接送入分割網路輸出 $\hat{M}$，取前 $K=50$ 最高像素平均為影像分數。限制包括 `VAE` 有損壓縮、記憶庫容量 $n_m$ 需調優（MVTec AD Table 5 當 $n_m$ 從 200 增至 250 時，Pixel AUPRO 從 94.9% 微降至 94.4%），以及待測異常大範圍劇烈偏離時 `GSM` 引導受限。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C09-01` | LAMBDA 使用預訓練 `Stable Diffusion v1.4` VAE 將影像映射至潛在表徵 $L \in \mathbb{R}^{4 \times H/8 \times W/8}$（$64\times$ 空間面積降維），並隨機抽樣 $n_m=200$ 張正常訓練潛在表徵建立記憶庫 $\mathcal{M}_b$，於推論時在固定步數 $t_s=200$ 檢索餘弦相似度最近鄰 $L^g$ 搭配引導尺度圖 $G$（`GSM`）執行單次一步去噪（`MBG`） | LAMBDA | VisA / MVTec AD / BMAD | 架構與超參數設定 | 預訓練 SD v1.4 VAE，記憶庫 $n_m=200$，$T=1000$，推論固定 $t_s=200$，Top $K=50$，$\lambda=1$，3000 Epochs | `wiki/papers/lee2026-lambda.md` `## 4. 方法架構與核心設計` | `lee2026-lambda.pdf` Sec. 3.1, p. 3, Sec. 4.1–4.7, p. 4–7, Eq. 1–9, Algorithm 1 & Sec. 5.2, p. 7 | 原文事實 |
| `C09-02` | 在 `lee2026-lambda` Table 1 的 VisA 評測中，`LAMBDA` 達到 98.1% Image AUROC、98.6% Pixel AUROC 與 94.2% Pixel AUPRO | LAMBDA | VisA | Image AUROC / Pixel AUROC / Pixel AUPRO | 98.1 / 98.6 / 94.2 | `wiki/papers/lee2026-lambda.md` `#### (A) VisA 資料集檢測精度與計算效率綜合比較（出自論文 Table 1, p. 8）` | `lee2026-lambda.pdf` Table 1, p. 8 | 原文事實 |
| `C09-03` | LAMBDA 的主要限制包括：(1) 預訓練 VAE 有損壓縮造成些微精度取捨；(2) 記憶庫容量 $n_m$ 需調優（在 MVTec AD Table 5 中，$n_m=200$ 之 Pixel AUPRO 為 94.9%、Pixel AP 為 69.1%，當 $n_m=250$ 時微降至 94.4% 與 68.7%）；(3) 待測異常極度複雜且與記憶庫正常圖樣大範圍偏離時，`GSM` 引導效果受限 | 200 / 250 | MVTec AD | Pixel AP / Pixel AUPRO | 69.1 / 94.9 (n_m=200)｜68.7 / 94.4 (n_m=250) | `wiki/papers/lee2026-lambda.md` `#### (B) 記憶庫大小 $n_m$ 消融實驗（出自論文 Sec. 5.8.5、Table 5 & Table A.5）`；`wiki/papers/lee2026-lambda.md` `## 6. 論文限制（Limitations）與延伸筆記` | `lee2026-lambda.pdf` Sec. 5.8.5 & Table 5, p. 10–11, Sec. 6, p. 12 | 原文事實 |

---

## 第 10 頁：效果與成本

### 學習目標
透過 `LAMBDA` 論文 `Table 4` 的核心組件消融數據，分析 `VAE`、`MBG` 與 `GSM` 在 `Pixel AUPRO`、訓練記憶體與推論 `FPS` 上的效果與成本取捨。

### 用到的 Wiki 頁與段落
- `wiki/papers/lee2026-lambda.md` `### 5.1 實驗設定、資料集與評估指標（出自論文 Sec. 5.1–5.2, p. 7）`
- `wiki/papers/lee2026-lambda.md` `#### (A) 核心組件消融（VAE 潛在壓縮、MBG 記憶庫引導、GSM 引導尺度圖）（出自論文 Sec. 5.8.1–5.8.4、Table 4、Fig. 5–6 & Table A.4）`

### 預計使用的圖檔
- 無（本頁使用 1 個 4 列消融小表）

### 投影片可見內容
- **可見正文（96 字，含 3 個關鍵數字：9.3 GB、33.8 GB、8）**：
  - **組件消融取捨（`VisA`）**：
    - **`VAE` 潛在壓縮**：將訓練 GPU 記憶體壓至 **9.3 GB**；移除 `VAE` 後訓練 GPU 記憶體增加至 **33.8 GB**。
    - **`MBG` 單次引導與 `GSM`**：同時提升定位精度並維持低 GPU 記憶體。
  - **測試條件**：`NVIDIA A100`、訓練 Batch **8**；解析度、評估 Batch、計時範圍：**未記載**。
- **可見表格（1 個 4 列 3 數據欄小表，只留 `Pixel AUPRO`、訓練 GPU 記憶體、推論 `FPS` 三欄；括號內差值不放進投影片）**：

| 組態 (`VisA` Table 4) | `Pixel AUPRO` (%) | `GPU Mem (Train)` | `FPS (Eval)` |
| :--- | :---: | :---: | :---: |
| **`Ours`（完整 LAMBDA）** | 94.2 | 9.3 GB | 42.3 |
| **`w/o GSM`（均一引導）** | 90.2 | 9.3 GB | 42.4 |
| **`w/o MBG`（雙尺度引導）** | 92.5 | 11.2 GB | 32.7 |
| **`w/o VAE`（像素空間）** | 95.4 | 33.8 GB | 28.4 |

- **延伸閱讀**：[Lee & Kang (2026) — LAMBDA §5.1 & §5.5 (A) Table 4](../../wiki/papers/lee2026-lambda.md#a-核心組件消融vae-潛在壓縮mbg-記憶庫引導gsm-引導尺度圖出自論文-sec-581584table-4fig-56--table-a4)

### 查證資料與講稿備註
- **嚴格資料來源與邊界規範**：
  - 本頁僅使用 `wiki/papers/lee2026-lambda.md` 中 `Table 4`（p. 10，於 `VisA` 資料集之核心組件消融與效率對比）的數據，主張記錄表中括號內相對 `Ours` 之變化量均為**論文 Table 4 原表所列差值**（投影片可見表格不放括號內差值）。
  - 測試條件透明標示（僅填 `wiki` 明確記載之內容，未記載項目一律標註「`未記載`」）：
    - 評估資料集：`VisA`（12 個工業物件類別平均，出自 `Table 4`）
    - 硬體環境：`NVIDIA A100 GPU`（出自 `§5.1`，`Table 4` 表頭本身未重述）
    - 訓練 Batch Size / Epochs：訓練 Batch Size = `8`、訓練 `3000` Epochs（出自 `§5.1`）
    - 評估（Eval）Batch Size：`未記載`
    - 輸入影像解析度（Resolution）：`未記載`
    - FPS 計時範圍（Timing Scope）：`未記載`
- **Table 4 其餘欄位補充備註（留於講稿備註，不放入投影片可見表格）**：
  - `Ours`：Image AUROC `98.1%`、Image AP `98.1%`、Pixel AUROC `98.6%`、Pixel AP `50.2%`、mAD `87.8%`、GPU Mem (Eval) `5.8 GB`、FPS (Train) `25.3`。
  - `w/o GSM`：Image AUROC `95.5 (-2.6)`、Image AP `96.3 (-1.8)`、Pixel AUROC `96.4 (-2.2)`、Pixel AP `44.5 (-5.7)`、mAD `84.6 (-3.2)`、GPU Mem (Eval) `5.8 GB (+0.0%)`、FPS (Train) `25.5 (+0.7%)`。
  - `w/o MBG`：Image AUROC `95.0 (-3.1)`、Image AP `95.3 (-2.8)`、Pixel AUROC `97.4 (-1.2)`、Pixel AP `47.0 (-3.2)`、mAD `85.4 (-2.4)`、GPU Mem (Eval) `5.8 GB (+0.0%)`、FPS (Train) `18.8 (-25.7%)`。
  - `w/o VAE`：Image AUROC `99.0 (+0.8)`、Image AP `98.9 (+0.8)`、Pixel AUROC `99.2 (+0.5)`、Pixel AP `54.4 (+4.2)`、mAD `89.4 (+1.6)`、GPU Mem (Eval) `9.2 GB (+58.6%)`、FPS (Train) `14.4 (-43.1%)`。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C10-01` | LAMBDA 完整模型（`Ours`）在 VisA（Table 4）之 Pixel AUPRO 為 94.2%、訓練 GPU 記憶體為 9.3 GB、評估推論速度為 42.3 FPS | Ours | VisA | Pixel AUPRO / GPU Mem (Train) / FPS (Eval) | 94.2 / 9.3 GB / 42.3（硬體：NVIDIA A100 GPU；訓練 Batch Size：8；評估 Batch Size：未記載；影像解析度：未記載；計時範圍：未記載） | `wiki/papers/lee2026-lambda.md` `#### (A) 核心組件消融（VAE 潛在壓縮、MBG 記憶庫引導、GSM 引導尺度圖）（出自論文 Sec. 5.8.1–5.8.4、Table 4、Fig. 5–6 & Table A.4）` | `lee2026-lambda.pdf` Sec. 5.2, p. 7 & Table 4, p. 10 | 原文事實 |
| `C10-02` | 移除引導尺度圖之變體（`w/o GSM`）在 VisA（Table 4）之 Pixel AUPRO 為 90.2 (-4.0)、訓練 GPU 記憶體為 9.3 GB (+0.0%)、評估推論速度為 42.4 (+0.2%) FPS（括號內為論文所列差值） | w/o GSM | VisA | Pixel AUPRO / GPU Mem (Train) / FPS (Eval) | 90.2 (-4.0) / 9.3 GB (+0.0%) / 42.4 (+0.2%)（論文所列差值；硬體：NVIDIA A100 GPU；訓練 Batch Size：8；評估 Batch Size：未記載；影像解析度：未記載；計時範圍：未記載） | `wiki/papers/lee2026-lambda.md` `#### (A) 核心組件消融（VAE 潛在壓縮、MBG 記憶庫引導、GSM 引導尺度圖）（出自論文 Sec. 5.8.1–5.8.4、Table 4、Fig. 5–6 & Table A.4）` | `lee2026-lambda.pdf` Sec. 5.8.3, p. 10–11 & Table 4, p. 10 | 原文事實 |
| `C10-03` | 移除記憶庫引導去噪之變體（`w/o MBG`）在 VisA（Table 4）之 Pixel AUPRO 為 92.5 (-1.7)、訓練 GPU 記憶體為 11.2 GB (+20.4%)、評估推論速度為 32.7 (-22.7%) FPS（括號內為論文所列差值） | w/o MBG | VisA | Pixel AUPRO / GPU Mem (Train) / FPS (Eval) | 92.5 (-1.7) / 11.2 GB (+20.4%) / 32.7 (-22.7%)（論文所列差值；硬體：NVIDIA A100 GPU；訓練 Batch Size：8；評估 Batch Size：未記載；影像解析度：未記載；計時範圍：未記載） | `wiki/papers/lee2026-lambda.md` `#### (A) 核心組件消融（VAE 潛在壓縮、MBG 記憶庫引導、GSM 引導尺度圖）（出自論文 Sec. 5.8.1–5.8.4、Table 4、Fig. 5–6 & Table A.4）` | `lee2026-lambda.pdf` Sec. 5.8.2, p. 10–11 & Table 4, p. 10 | 原文事實 |
| `C10-04` | 移除預訓練 VAE 之變體（`w/o VAE`）在 VisA（Table 4）之 Pixel AUPRO 雖為 95.4 (+1.2)，但訓練 GPU 記憶體增加至 33.8 GB (+263.4%)、評估推論速度降至 28.4 (-32.9%) FPS（括號內為論文所列差值） | w/o VAE | VisA | Pixel AUPRO / GPU Mem (Train) / FPS (Eval) | 95.4 (+1.2) / 33.8 GB (+263.4%) / 28.4 (-32.9%)（論文所列差值；硬體：NVIDIA A100 GPU；訓練 Batch Size：8；評估 Batch Size：未記載；影像解析度：未記載；計時範圍：未記載） | `wiki/papers/lee2026-lambda.md` `#### (A) 核心組件消融（VAE 潛在壓縮、MBG 記憶庫引導、GSM 引導尺度圖）（出自論文 Sec. 5.8.1–5.8.4、Table 4、Fig. 5–6 & Table A.4）` | `lee2026-lambda.pdf` Sec. 5.8.1, p. 9–10 & Table 4, p. 10 | 原文事實 |
| `C10-05` | LAMBDA 論文在實驗設定記載硬體為 NVIDIA A100 GPU、訓練 Batch Size 為 8、訓練 3000 Epochs；以 PDF 全文檢索核對，全文未記載輸入影像解析度、評估階段（Eval）Batch Size 以及 FPS 與延遲的計時範圍（檢索紀錄見 wiki LAMBDA 頁 §5.1），故於簡報中如實標示為「未記載」 | LAMBDA 實驗設定記載狀態 | VisA | 測試條件記載完整性 | 硬體：NVIDIA A100 GPU；訓練 Batch Size：8；影像解析度：未記載；評估 Batch Size：未記載；計時範圍：未記載 | `wiki/papers/lee2026-lambda.md` `### 5.1 實驗設定、資料集與評估指標（出自論文 Sec. 5.1–5.2, p. 7）` | `lee2026-lambda.pdf` Sec. 5.1–5.2, p. 7 & Table 4, p. 10 | 原文事實 |

---

## 第 11 頁：MVTec AD 2：舊基準沒涵蓋的難題

### 學習目標
認識 MVTec AD 2 針對舊基準飽和問題所引入的八大高難度工業場景、真實光照分佈偏移測試（`TESTpriv,mix`）與私密評估伺服器協定。

### 用到的 Wiki 頁與段落
- `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 2. 一句話總結（TL;DR）與核心貢獻`
- `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 4. 資料集規格、取像設定與評估指標`
- `wiki/datasets/mvtec-ad-2.md` `## 3. 資料集規格與三大測試子集總覽（出自 hecklerkram2025-mvtec-ad-2.pdf Table 3, p. 5 & Table 4, p. 6）`

### 預計使用的圖檔
- 無

### 投影片可見內容
- **可見正文（113 字，含 3 個關鍵數字：97.8%、8、8,004）**：
  - **舊基準飽和**：在舊版 `MVTec AD` 上頂尖模型平均已達 **97.8%** `AU-PRO`，難分高下。
  - **MVTec AD 2（8 大場景、共 8,004 張高解析度影像）四大新難題**：
    1. **散裝重疊物件**：數量與位置隨機、互相接觸重疊。
    2. **透明與高反光材質**：搭配背光與暗場特殊照明。
    3. **影像邊界缺陷**：瑕疵緊貼邊框，中心裁切直接漏檢。
    4. **未知光照偏移與私密伺服器**：測試混合未知光照（`TESTpriv,mix`），真值不公開。
- **延伸閱讀**：[Heckler-Kram et al. (2025) — MVTec AD 2 §2 & §4](../../wiki/papers/hecklerkram2025-mvtec-ad-2.md#4-資料集規格取像設定與評估指標)、[MVTec AD 2 資料集與進階評估協定 §3](../../wiki/datasets/mvtec-ad-2.md#3-資料集規格與三大測試子集總覽出自-hecklerkram2025-mvtec-ad-2pdf-table-3-p-5--table-4-p-6)

### 查證資料與講稿備註
- **8 大場景與子集統計備註**：
  - 8 個場景：`Can`、`Fabric`、`Fruit Jelly`、`Rice`、`Sheet Metal`、`Vial`、`Wall Plugs`、`Walnuts`（解析度 2.6–5 MP，邊長 $1400 \times 1900$ 至 $4224 \times 1056$）。
  - 影像張數：訓練集 `2,528` 張、驗證集 `302` 張、測試集共 `5,174` 張（公開 `TESTpub` `1,084` 張、同光照私密 `TESTpriv` `2,045` 張、混合已知與未知光照私密 `TESTpriv,mix` `2,045` 張），總計 `8,004` 張（依原文 Table 4 跨 8 類加總計算）。
  - 評估伺服器：`TESTpriv` 與 `TESTpriv,mix` 的 Ground Truth 保留於 `https://benchmark.mvtec.com/`，防止針對測試集微調超參數。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C11-01` | （MVTec AD 2 論文發表時的背景報告）既有基準（如 MVTec AD 最佳模型達 97.8% mean AU-PRO、Real-IAD 在 1/20 解析度下達 94.4% $\text{AU-PRO}_{0.30}$）已趨近飽和，各頂尖模型差距常小於 1 個百分點，且存在依測試集微調超參數的問題 | 資料集背景分析（Heckler-Kram et al., 2025） | MVTec AD / VisA / Real-IAD | mean AU-PRO / AU-PRO0.30 | MVTec AD 最高 97.8% mean AU-PRO；Real-IAD (1/20 尺寸) 94.4% AU-PRO0.30；模型差距 < 1 個百分點 | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 2. 一句話總結（TL;DR）與核心貢獻` | `hecklerkram2025-mvtec-ad-2.pdf` Sec. 1, p. 1 & Sec. 2.1, p. 3 | 原文事實 |
| `C11-02` | MVTec AD 2 收錄 8 個工業場景（`Can`、`Fabric`、`Fruit Jelly`、`Rice`、`Sheet Metal`、`Vial`、`Wall Plugs`、`Walnuts`）、共 8,004 張高解析度影像（正文寫 2.6 至 5 MP；Table 4 的 Can 為 2232×1024，與正文範圍不一致，原文如此；面積換算見同頁 Can 影像面積換算主張），涵蓋散裝重疊物件、透明／反光材質、高正常變異、背光／暗場照明以及位於影像邊界的缺陷 | 資料集設計（Heckler-Kram et al., 2025） | MVTec AD 2 | 資料集規模與場景特性 | 8 個場景、8,004 張影像；正文寫 2.6–5 MP，Table 4 的 Can 為 2232×1024（與正文範圍不一致，原文如此） | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 4. 資料集規格、取像設定與評估指標` | `hecklerkram2025-mvtec-ad-2.pdf` Table 2, p. 3, Sec. 3.1, p. 4, Fig. 2 & Tables 3–4, p. 5–6 | 原文事實 |
| `C11-03` | MVTec AD 2 跨 8 類加總之訓練集為 2,528 張、驗證集為 302 張、公開測試集 `TESTpub` 為 1,084 張、同光照私密測試集 `TESTpriv` 為 2,045 張、混合未知光照私密測試集 `TESTpriv,mix` 為 2,045 張（測試集共 5,174 張，總計 8,004 張） | Total (AI 整理) | MVTec AD 2 | 訓練集 (# Train) / 驗證集 (# Val) / TESTpub (無異常/有異常) / TESTpriv (無異常/有異常) / TESTpriv,mix (無異常/有異常) / 測試集總計 total (無異常/有異常) | 2528 / 302 / 1084 (379/705) / 2045 (748/1297) / 2045 (748/1297) / 5174 (1875/3299)（依原文 Table 4 跨 8 類加總計算） | `wiki/datasets/mvtec-ad-2.md` `## 3. 資料集規格與三大測試子集總覽（出自 hecklerkram2025-mvtec-ad-2.pdf Table 3, p. 5 & Table 4, p. 6）` | `hecklerkram2025-mvtec-ad-2.pdf` Sec. 3.2–3.3, p. 4, Table 4 & Table 6, p. 6（總計列為依原文 Table 4 數據加總計算） | 依原文數據計算 |
| `C11-04` | 依原文數據計算：Table 4 的 `Can` 影像為 2232×1024 像素，2232 × 1024 = 2,285,568 像素，以十進位 MP（百萬像素）換算並四捨五入至小數第 2 位約為 2.29 MP，低於正文所寫的 2.6 MP 下限；2.29 為換算值，不是作者報告值，無平均 | 資料集設計（Heckler-Kram et al., 2025） | MVTec AD 2 | 影像面積（MP） | 輸入 2232 × 1024 像素；結果 2,285,568 像素 ≈ 2.29 MP（四捨五入至小數第 2 位） | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 4. 資料集規格、取像設定與評估指標` | `hecklerkram2025-mvtec-ad-2.pdf` Sec. 3.1, p. 4、Table 4, p. 6 | 依原文數據計算 |

---

## 第 12 頁：PRO vs. TPR

### 學習目標
透過 MVTec AD 2 論文 `Fig. 4` 的概念示例，理解為何單區域重疊率（PRO）比像素級真陽性率（TPR）更能防止「抓大放小」的評估盲點。

### 用到的 Wiki 頁與段落
- `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 4. 資料集規格、取像設定與評估指標`
- `wiki/datasets/mvtec-ad-2.md` `## 4. 評估指標定義：$\text{AU-PRO}_{0.05}$ vs. $\text{AU-PRO}_{0.30}$ 與二值化 $F_1$（出自 hecklerkram2025-mvtec-ad-2.pdf Sec. 4.2, p. 8–9 & Supplemental Material B, p. 14）`

### 預計使用的圖檔
- `assets/diagrams/hecklerkram2025-mvtec-ad-2-fig4.svg`（簡報相對路徑：`../../assets/diagrams/hecklerkram2025-mvtec-ad-2-fig4.svg`）

### 投影片可見內容
- **上方示意圖**：`../../assets/diagrams/hecklerkram2025-mvtec-ad-2-fig4.svg`（標註：示意圖，依論文 Fig. 4 重繪——此為論文概念示例數字，非模型實驗結果）
- **可見正文（95 字，含 3 個關鍵數字：3、0.77、0.33）**：
  - **像素級 `TPR` 的盲點**：把整張圖所有瑕疵像素混在一起算，面積大的瑕疵會完全主導分數。
  - **`PRO` 的公平性**：讓圖中 **3** 個不同大小的獨立瑕疵區域享有相等權重。當模型只抓到大瑕疵卻漏掉兩個小瑕疵（情境 `iv`），`TPR` 高達 **0.77**，`PRO` 則誠實給出 **0.33**。
- **可見公式（1 條）**：
  $$\text{PRO} = \frac{1}{k} \sum_{i=1}^{|D_{\text{test}}|} \sum_{j=1}^{k_i} \frac{|P_{\text{ano}} \cap C_{i,j}|}{|C_{i,j}|}$$
- **延伸閱讀**：[Heckler-Kram et al. (2025) — MVTec AD 2 §4.5 (A)](../../wiki/papers/hecklerkram2025-mvtec-ad-2.md#a-無閾值指標threshold-independent-metric與-au-pro005-的物理意義)、[MVTec AD 2 資料集與進階評估協定 §4](../../wiki/datasets/mvtec-ad-2.md#4-評估指標定義textau-pro_005-vs-textau-pro_030-與二值化-f_1出自-hecklerkram2025-mvtec-ad-2pdf-sec-42-p-89--supplemental-material-b-p-14)

### 查證資料與講稿備註
- **論文 `Fig. 4` 完整四種情境拆解備註（教學示例數字，非模型實驗結果）**：
  - Ground Truth 含 **3** 個異常連通區域，面積分別為 **4、2、20 像素**（總計 **26** 個異常像素）：
  - 情境 `i)` 全部檢出：$\text{PRO} = 1.00$，$\text{TPR} = 1.00$。
  - 情境 `ii)` 各檢出一半（2、1、10 像素）：$\text{PRO} = 0.50$，$\text{TPR} = 0.50$。
  - 情境 `iii)` 檢出 2 個小缺陷（4、2 像素），漏檢大缺陷（0 像素）：3 區檢出 2 區 $\rightarrow \text{PRO} = 0.67$；檢出像素 $6/26 \rightarrow \text{TPR} = 0.23$。
  - 情境 `iv)` 只檢出 1 個大缺陷（20 像素），漏檢 2 個小缺陷：檢出像素 $20/26 \rightarrow \text{TPR} = 0.77$；而 $\text{PRO} = 0.33$。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C12-01` | 像素級 AU-ROC 衡量整體真陽性率（TPR）對假陽性率（FPR），當圖中同時存在大面積與小面積缺陷時，TPR 會被大面積缺陷主導；而 PRO（Eq. 1）對每個獨立連通缺陷區域 $C_{i,j}$ 先計算區域內重疊率再取平均，賦予大小缺陷相等權重 | PRO vs. TPR 指標定義 | MVTec AD 2 | PRO / TPR | $\text{PRO} = \frac{1}{k}\sum_{i=1}^{\lvert D_{\text{test}}\rvert}\sum_{j=1}^{k_i}\frac{\lvert P_{\text{ano}}\cap C_{i,j}\rvert}{\lvert C_{i,j}\rvert}$ | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 4. 資料集規格、取像設定與評估指標` | `hecklerkram2025-mvtec-ad-2.pdf` Sec. 4.2.1 & Eq. 1, p. 8 | 原文事實 |
| `C12-02` | 【論文 Fig. 4 教學示例】給定面積為 4、2、20 像素（共 26 像素）的 3 個真實異常區域：情境 iii) 檢出 2 個小缺陷但漏檢大缺陷時，PRO = 0.67、TPR = 0.23；情境 iv) 僅檢出 20 像素大缺陷卻漏檢 2 個小缺陷時，TPR 高達 0.77，而 PRO 則為 0.33（註：此為論文 Fig. 4 概念示例數字，非模型實驗結果） | PRO vs. TPR 概念示例 | 無（論文 Fig. 4 教學示例） | PRO / TPR | 3 個缺陷區域（4, 2, 20 px，共 26 px）：iii) PRO=0.67, TPR=0.23；iv) PRO=0.33, TPR=0.77（教學示例數字） | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 4. 資料集規格、取像設定與評估指標` | `hecklerkram2025-mvtec-ad-2.pdf` Fig. 4 & Sec. 4.2.1, p. 8 | 原文事實 |

---

## 第 13 頁：AU-PRO0.05：0.05 是 FPR 積分上限

### 學習目標
理解 $\text{AU-PRO}$ 指標中下標 `0.30` 與 `0.05` 代表假陽性率（FPR）積分上限，以及為何高解析度微小缺陷場景必須將積分上限收緊至 `0.05`。

### 用到的 Wiki 頁與段落
- `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 1. 基本資訊`
- `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 4. 資料集規格、取像設定與評估指標`
- `wiki/datasets/mvtec-ad-2.md` `## 4. 評估指標定義：$\text{AU-PRO}_{0.05}$ vs. $\text{AU-PRO}_{0.30}$ 與二值化 $F_1$（出自 hecklerkram2025-mvtec-ad-2.pdf Sec. 4.2, p. 8–9 & Supplemental Material B, p. 14）`
- `wiki/datasets/mvtec-ad-2.md` `## 5. 七大 SOTA 方法於 MVTec AD 2 之基準表現總覽`

### 預計使用的圖檔
- 無

### 投影片可見內容
- **可見正文（112 字，聚焦 FPR 積分上限，含 3 個關鍵數字：0.30、0.05、25,000）**：
  - **下標是假陽性率（FPR）積分上限**：
    - **`AU-PRO0.30`**：把 `PRO–FPR` 曲線積分到背景誤報率 **0.30**（容許三成正常背景被誤判）。
    - **`AU-PRO0.05`**：將積分上限收緊至 **0.05**；兩者範圍不同，**不可混用或直接互比**。
  - **為何必須收緊？（論文數量級示例）**：在 500 萬像素大圖找 10 像素小瑕疵，即使 FPR = `0.05`，誤報面積仍超過瑕疵的 **25,000** 倍！
- **延伸閱讀**：[Heckler-Kram et al. (2025) — MVTec AD 2 §4.5 (A)–(B)](../../wiki/papers/hecklerkram2025-mvtec-ad-2.md#a-無閾值指標threshold-independent-metric與-au-pro005-的物理意義)、[MVTec AD 2 資料集與進階評估協定 §4](../../wiki/datasets/mvtec-ad-2.md#4-評估指標定義textau-pro_005-vs-textau-pro_030-與二值化-f_1出自-hecklerkram2025-mvtec-ad-2pdf-sec-42-p-89--supplemental-material-b-p-14)

### 查證資料與講稿備註
- **二值化 $F_1$ 與 `PatchCore` 測試集正規化案例（留於講稿備註，不放入投影片可見畫面）**：
  - 實務產線需以無缺陷驗證集像素異常值之 $\mu_{\text{val}} + 3\sigma_{\text{val}}$ 決定單一二值化閾值，計算像素分割 $F_1$（Table 8）與影像分類 $F_1$（Table 12）。
  - 案例：在 $256 \times 256$ 下，`PatchCore` 於 `TESTpriv / TESTpriv,mix` 雖取得 `28.8 / 26.0` 之 $\text{AU-PRO}_{0.05}$（Table 7 `Mean` 列），但因其官方實作預設跨整個輸入資料集將異常分數正規化至 $[0,1]$，使純正常驗證集推導出過高閾值，導致像素分割 `F1` 跌至 `3.7 / 3.4`（Table 8 `Mean` 列）。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C13-01` | $\text{AU-PRO}_{0.30}$ 與 $\text{AU-PRO}_{0.05}$ 分別代表將 PRO 對 FPR 曲線積分至假陽性率上限 $\text{FPR} = 0.30$（用於 Table 1、Table 9）與 $\text{FPR} = 0.05$（MVTec AD 2 主力指標，用於 Table 7、10、11）並正規化至 $[0,1]$；兩者積分上限不同，不可混用或直接互相比較 | AU-PRO0.30 與 AU-PRO0.05 指標定義 | MVTec AD 2 | AU-PRO0.30 / AU-PRO0.05 | FPR 積分上限 0.30 vs. 0.05 | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 1. 基本資訊`；`wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 4. 資料集規格、取像設定與評估指標` | `hecklerkram2025-mvtec-ad-2.pdf` Sec. 4.2.1, p. 8 & Supplemental Material B.1, p. 14 | 原文事實 |
| `C13-02` | 【論文 Sec. 4.2.1 數量級示例】在一張 500 萬像素（5 MP）影像中僅占 10 個像素的微小缺陷場景下，即使將積分上限設為 $\text{FPR} = 5\%$（0.05），誤報的錯誤分割面積約為該缺陷本身面積的 25,000 倍（論文原文寫 more than 25,000 times，屬數量級敘述；此為說明指標動機之示例數字，非模型實驗結果） | AU-PRO0.05 動機示例 | MVTec AD 2（5 MP 影像示例） | FPR 誤報面積比例 | 5 MP 影像、10 像素缺陷、FPR = 5% (0.05) 時誤報面積約為缺陷面積之 25,000 倍（數量級示例） | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 4. 資料集規格、取像設定與評估指標` | `hecklerkram2025-mvtec-ad-2.pdf` Sec. 4.2.1 & Fig. 5, p. 8 | 原文事實 |
| `C13-03` | 在 MVTec AD 2（輸入 $256 \times 256$）中，`PatchCore` 於 `AU-PRO0.05` (`TESTpriv / TESTpriv,mix`) 為 `28.8 / 26.0`（Table 7），而像素分割 `F1` (`TESTpriv / TESTpriv,mix`) 為 `3.7 / 3.4`（Table 8） | PatchCore | MVTec AD 2 | $256 \times 256$<br>`AU-PRO0.05` (%)<br>(`TESTpriv / TESTpriv,mix`)<br>[Table 7] / $256 \times 256$<br>像素分割 `F1` (%)<br>(`TESTpriv / TESTpriv,mix`)<br>[Table 8] | 28.8 / 26.0｜3.7 / 3.4 | `wiki/datasets/mvtec-ad-2.md` `## 5. 七大 SOTA 方法於 MVTec AD 2 之基準表現總覽`；`wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 4. 資料集規格、取像設定與評估指標` | `hecklerkram2025-mvtec-ad-2.pdf` Sec. 4.2.2 & 4.3.2, p. 9, Table 7 & Table 8, p. 10 | 原文事實 |

---

## 第 14 頁：新基準結果

### 學習目標
透過 MVTec AD 2 論文 `Table 1` 在相同 $\text{AU-PRO}_{0.30}$ 指標下的跨基準數據，理解表中 7 個代表性方法在三個資料集上的平均表現差異與解讀邊界。

### 用到的 Wiki 頁與段落
- `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `### 5.1 受測之 7 種 SOTA 方法與實作參數（出自論文 Sec. 4.1, p. 7–8）`
- `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `### 5.2 跨資料集分割表現對比：Table 1（指標：$\text{AU-PRO}_{0.30}$，出自論文 Table 1, p. 2）`

### 預計使用的圖檔
- 無（本頁使用 1 個 4 列精選小表，完整 7 方法 + Mean 收錄於主張記錄表與備註）

### 投影片可見內容
- **可見正文（114 字，含 3 個關鍵數字：7、92.4%、52.6%）**：
  - **跨基準同指標對比（`Table 1`，指標：`AU-PRO0.30` %，輸入 `256×256`）**：表列 **7** 個方法的平均（`Mean`）在 `MVTec AD` 為 **92.4%**，在 `MVTec AD 2`（`TESTpriv`）為 **52.6%**。
  - **解讀邊界**：此為表列 7 個方法在各資料集**分別訓練與評估**的平均表現，**不得解讀為同一已訓練模型直接跨資料集測試的退化幅度**；結論僅涵蓋表中 7 個方法。
- **可見表格（1 個 4 列小表，呈現 Table 1 代表性列與全 7 方法平均 `Mean`；其餘列見延伸閱讀與講稿備註）**：

| 方法 (`Table 1` 選列) | `MVTec AD` `AU-PRO0.30` (%) | `VisA` `AU-PRO0.30` (%) | `MVTec AD 2` (`TESTpriv`) `AU-PRO0.30` (%) |
| :--- | :---: | :---: | :---: |
| **`PatchCore`** | 92.7 | 79.7 | 53.8 |
| **`RD`（即 `RD4AD`）** | 93.9 | 89.0 | 53.0 |
| **`EfficientAD`** | 93.5 | 94.0 | 58.7 |
| **`Mean`（表列 7 方法平均）** | **92.4** | **82.4** | **52.6** |

- **延伸閱讀**：[Heckler-Kram et al. (2025) — MVTec AD 2 §5.1–§5.2 Table 1 完整 7 方法數據](../../wiki/papers/hecklerkram2025-mvtec-ad-2.md#52-跨資料集分割表現對比table-1指標textau-pro_030出自論文-table-1-p-2)

### 查證資料與講稿備註
- **Table 1 完整 7 個方法 + Mean 查證數據（指標皆為 $\text{AU-PRO}_{0.30}$ %，輸入 $256 \times 256$）**：
  - `PatchCore`（3 骨幹整合、0.01% Coreset、關閉中心裁切）：MVTec AD `92.7%`｜VisA `79.7%`｜MVTec AD 2 (`TESTpriv`) `53.8%`
  - `RD`（即本 Wiki 之 `RD4AD`）：MVTec AD `93.9%`（引自原論文 [17]）｜VisA `89.0%`｜MVTec AD 2 (`TESTpriv`) `53.0%`
  - `RD++`：MVTec AD `95.0%`（引自原論文 [31]）｜VisA `89.3%`｜MVTec AD 2 (`TESTpriv`) `54.3%`
  - `EfficientAD`（MVTec AD / VisA 採 `EfficientAD-M`，MVTec AD 2 採 `EfficientAD-S`）：MVTec AD `93.5%`｜VisA `94.0%`｜MVTec AD 2 (`TESTpriv`) `58.7%`
  - `MSFlow`（統一採 $256 \times 256$）：MVTec AD `91.2%`｜VisA `88.4%`｜MVTec AD 2 (`TESTpriv`) `52.7%`
  - `SimpleNet`（固定訓練 160 Epochs）：MVTec AD `89.6%`｜VisA `68.9%`｜MVTec AD 2 (`TESTpriv`) `46.4%`
  - `DSR`：MVTec AD `90.8%`｜VisA `68.1%`｜MVTec AD 2 (`TESTpriv`) `49.0%`
  - `Mean`（7 方法平均）：MVTec AD `92.4%`｜VisA `82.4%`｜MVTec AD 2 (`TESTpriv`) `52.6%`
- **嚴格解讀邊界**：
  - 表中數據係表列 7 個方法在各資料集上分別依統一無場景調參協定訓練與評估後的平均表現，非單一已訓練模型直接跨資料集測試的退化幅度；本頁結論僅涵蓋表中 7 個方法（不含未列入該表的 `RIAD`、`DiffusionAD`、`LAMBDA`）。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C14-01` | 在 `hecklerkram2025-mvtec-ad-2` Table 1 的統一無場景調參協定下，`PatchCore` 在 MVTec AD、VisA 與 MVTec AD 2 (`TESTpriv`, 256×256) 的 `AU-PRO0.30` (%) 分別為 92.7、79.7 與 53.8 | PatchCore | MVTec AD / VisA / MVTec AD 2 (`TESTpriv`) | MVTec AD `AU-PRO0.30` (%) / VisA `AU-PRO0.30` (%) / MVTec AD 2 (ours, `TESTpriv`) `AU-PRO0.30` (%) | 92.7 / 79.7 / 53.8 | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `### 5.2 跨資料集分割表現對比：Table 1（指標：$\text{AU-PRO}_{0.30}$，出自論文 Table 1, p. 2）` | `hecklerkram2025-mvtec-ad-2.pdf` Table 1, p. 2, Sec. 4.1, p. 7 & Table 9, p. 15 | 原文事實 |
| `C14-02` | 在 Table 1 中，`RD` *(即 RD4AD)* 在 MVTec AD、VisA 與 MVTec AD 2 (`TESTpriv`, 256×256) 的 `AU-PRO0.30` (%) 分別為 93.9、89.0 與 53.0；其中 MVTec AD 欄數值為 MVTec AD 2 論文引自 RD4AD 原論文，不是本篇重新實驗（見同頁「受測之 7 種 SOTA 方法與實作參數」一節） | RD *(即 RD4AD)* | MVTec AD / VisA / MVTec AD 2 (`TESTpriv`) | MVTec AD `AU-PRO0.30` (%) / VisA `AU-PRO0.30` (%) / MVTec AD 2 (ours, `TESTpriv`) `AU-PRO0.30` (%) | 93.9 / 89.0 / 53.0 | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `### 5.2 跨資料集分割表現對比：Table 1（指標：$\text{AU-PRO}_{0.30}$，出自論文 Table 1, p. 2）` | `hecklerkram2025-mvtec-ad-2.pdf` Table 1, p. 2, Sec. 4.1, p. 7 & Table 9, p. 15 | 原文事實 |
| `C14-03` | 在 Table 1 中，`RD++` 在 MVTec AD、VisA 與 MVTec AD 2 (`TESTpriv`, 256×256) 的 `AU-PRO0.30` (%) 分別為 95.0、89.3 與 54.3；其中 MVTec AD 欄數值為 MVTec AD 2 論文引自 RD++ 原論文，不是本篇重新實驗（見同頁「受測之 7 種 SOTA 方法與實作參數」一節） | RD++ | MVTec AD / VisA / MVTec AD 2 (`TESTpriv`) | MVTec AD `AU-PRO0.30` (%) / VisA `AU-PRO0.30` (%) / MVTec AD 2 (ours, `TESTpriv`) `AU-PRO0.30` (%) | 95.0 / 89.3 / 54.3 | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `### 5.2 跨資料集分割表現對比：Table 1（指標：$\text{AU-PRO}_{0.30}$，出自論文 Table 1, p. 2）` | `hecklerkram2025-mvtec-ad-2.pdf` Table 1, p. 2, Sec. 4.1, p. 7 & Table 9, p. 15 | 原文事實 |
| `C14-04` | 在 Table 1 中，`EfficientAD` 在 MVTec AD、VisA 與 MVTec AD 2 (`TESTpriv`, 256×256) 的 `AU-PRO0.30` (%) 分別為 93.5、94.0 與 58.7；MVTec AD 與 VisA 欄使用 EfficientAD-M，MVTec AD 2 欄使用 EfficientAD-S，模型大小不同（見同頁「受測之 7 種 SOTA 方法與實作參數」一節） | EfficientAD | MVTec AD / VisA / MVTec AD 2 (`TESTpriv`) | MVTec AD `AU-PRO0.30` (%) / VisA `AU-PRO0.30` (%) / MVTec AD 2 (ours, `TESTpriv`) `AU-PRO0.30` (%) | 93.5 / 94.0 / 58.7 | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `### 5.2 跨資料集分割表現對比：Table 1（指標：$\text{AU-PRO}_{0.30}$，出自論文 Table 1, p. 2）` | `hecklerkram2025-mvtec-ad-2.pdf` Table 1, p. 2, Sec. 4.1, p. 7 & Table 9, p. 15 | 原文事實 |
| `C14-05` | 在 Table 1 中，`MSFlow` 在 MVTec AD、VisA 與 MVTec AD 2 (`TESTpriv`, 256×256) 的 `AU-PRO0.30` (%) 分別為 91.2、88.4 與 52.7 | MSFlow | MVTec AD / VisA / MVTec AD 2 (`TESTpriv`) | MVTec AD `AU-PRO0.30` (%) / VisA `AU-PRO0.30` (%) / MVTec AD 2 (ours, `TESTpriv`) `AU-PRO0.30` (%) | 91.2 / 88.4 / 52.7 | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `### 5.2 跨資料集分割表現對比：Table 1（指標：$\text{AU-PRO}_{0.30}$，出自論文 Table 1, p. 2）` | `hecklerkram2025-mvtec-ad-2.pdf` Table 1, p. 2, Sec. 4.1, p. 7–8 & Table 9, p. 15 | 原文事實 |
| `C14-06` | 在 Table 1 中，`SimpleNet` 在 MVTec AD、VisA 與 MVTec AD 2 (`TESTpriv`, 256×256) 的 `AU-PRO0.30` (%) 分別為 89.6、68.9 與 46.4 | SimpleNet | MVTec AD / VisA / MVTec AD 2 (`TESTpriv`) | MVTec AD `AU-PRO0.30` (%) / VisA `AU-PRO0.30` (%) / MVTec AD 2 (ours, `TESTpriv`) `AU-PRO0.30` (%) | 89.6 / 68.9 / 46.4 | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `### 5.2 跨資料集分割表現對比：Table 1（指標：$\text{AU-PRO}_{0.30}$，出自論文 Table 1, p. 2）` | `hecklerkram2025-mvtec-ad-2.pdf` Table 1, p. 2, Sec. 4.1, p. 8 & Table 9, p. 15 | 原文事實 |
| `C14-07` | 在 Table 1 中，`DSR` 在 MVTec AD、VisA 與 MVTec AD 2 (`TESTpriv`, 256×256) 的 `AU-PRO0.30` (%) 分別為 90.8、68.1 與 49.0 | DSR | MVTec AD / VisA / MVTec AD 2 (`TESTpriv`) | MVTec AD `AU-PRO0.30` (%) / VisA `AU-PRO0.30` (%) / MVTec AD 2 (ours, `TESTpriv`) `AU-PRO0.30` (%) | 90.8 / 68.1 / 49.0 | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `### 5.2 跨資料集分割表現對比：Table 1（指標：$\text{AU-PRO}_{0.30}$，出自論文 Table 1, p. 2）` | `hecklerkram2025-mvtec-ad-2.pdf` Table 1, p. 2, Sec. 4.1, p. 8 & Table 9, p. 15 | 原文事實 |
| `C14-08` | 表列 7 個方法（`PatchCore`、`RD`、`RD++`、`EfficientAD`、`MSFlow`、`SimpleNet`、`DSR`）在各資料集分別訓練與評估之平均（`Mean`）`AU-PRO0.30` (%) 於 MVTec AD 為 92.4、於 VisA 為 82.4、於 MVTec AD 2 (`TESTpriv`, 256×256) 為 52.6；Mean 是原表 7 個方法的平均（非投影片所列 3 列的平均）；此為該 7 個方法在三個基準上的各自平均表現，非單一已訓練模型直接跨資料集測試的退化幅度，且結論僅涵蓋表中 7 個方法 | Mean | MVTec AD / VisA / MVTec AD 2 (`TESTpriv`) | MVTec AD `AU-PRO0.30` (%) / VisA `AU-PRO0.30` (%) / MVTec AD 2 (ours, `TESTpriv`) `AU-PRO0.30` (%) | 92.4 / 82.4 / 52.6 | `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `### 5.2 跨資料集分割表現對比：Table 1（指標：$\text{AU-PRO}_{0.30}$，出自論文 Table 1, p. 2）` | `hecklerkram2025-mvtec-ad-2.pdf` Sec. 1 & Table 1, p. 2, Sec. 4.1, p. 7–8 | 原文事實 |

---

## 第 15 頁：方法脈絡＋一題情境判斷題

### 學習目標
綜合串聯 7 篇論文的方法演進脈絡，並透過情境判斷題辨識候選方法與部署前尚須在目標資料與硬體上補齊的實測條件。

### 用到的 Wiki 頁與段落
- `wiki/comparisons/embedding-vs-reconstruction.md` `## 3. 各流派核心機制與優劣對照表`
- `wiki/comparisons/embedding-vs-reconstruction.md` `## 5. 演進趨勢與取捨分析（AI 整理）`
- `wiki/papers/roth2022-patchcore.md` `#### (A) MVTec AD 少樣本（Low-Shot）異常檢測表現（出自論文 Sec. 4.5, p. 7–8 Fig. 6 & Supp. Table S5, p. 16）`
- `wiki/papers/lee2026-lambda.md` `#### (A) VisA 資料集檢測精度與計算效率綜合比較（出自論文 Table 1, p. 8）`

### 預計使用的圖檔
- 無

### 投影片可見內容
- **可見正文（118 字，含 2 個關鍵數字：16、9.3 GB）**：
  - **演進脈絡（AI 整理）**：`MVTec AD` 建立基準 $\rightarrow$ `RIAD` 挖洞修補／`PatchCore` 特徵核心集 $\rightarrow$ `DDPM` 奠基 $\rightarrow$ `DiffusionAD` 雙尺度一步擴散 $\rightarrow$ `LAMBDA` 潛在記憶庫引導 $\rightarrow$ `MVTec AD 2` 嚴格評測。
  - **情境判斷題（AI 整理）**：針對「僅 **16** 張正常圖、無訓練預算」與「單卡 GPU 記憶體受限、需端到端擴散分割（`LAMBDA` 於 A100 訓練為 **9.3 GB**）」，**哪個方法值得優先測試？現有證據還缺哪些條件才能確認部署需求？**
  - **解答**：`PatchCore`（不需訓練網路權重，但仍需擷取正常特徵、建立記憶庫並選取核心集）與 `LAMBDA` 可作為候選，但**必須在目標資料與目標硬體上實測**；**不得從 `A100` 上的記憶體與 `FPS` 直接推論其他顯卡能達到的速度**。
- **延伸閱讀**：[預訓練特徵嵌入 vs. 重建式異常檢測流派對比 §3 & §5](../../wiki/comparisons/embedding-vs-reconstruction.md#5-演進趨勢與取捨分析ai-整理)、[PatchCore 少樣本實驗 §5.4 (A)](../../wiki/papers/roth2022-patchcore.md#a-mvtec-ad-少樣本low-shot異常檢測表現出自論文-sec-45-p-78-fig-6--supp-table-s5-p-16)、[LAMBDA 效率比較 §5.2 (A)](../../wiki/papers/lee2026-lambda.md#a-visa-資料集檢測精度與計算效率綜合比較出自論文-table-1-p-8)

### 查證資料與講稿備註
- **情境判斷題完整分析與證據邊界備註（AI 整理）**：
  1. **候選方法一：`PatchCore`（少樣本／免訓練權重場景候選）**
     - 現有論文證據：`PatchCore` 不需在目標資料集上訓練微調網路權重（但仍需通過預訓練骨幹網路擷取正常樣本特徵、建立記憶庫 $\mathcal{M}$ 並執行貪婪核心集下採樣選取 $\mathcal{M}_C$，並非零準備時間）；在 MVTec AD 每類別 **16 Shots (6.6%)** 下，`PatchCore-25%` 達 `95.5 ± 0.6%` Image AUROC、`96.8 ± 0.3%` Pixel AUROC、`91.7 ± 0.1%` PRO（Table S5, p. 16）。
     - 尚缺的部署驗證條件：目標產線零件與 ImageNet 預訓練特徵的領域差距、目標解析度下的核心集建構時間與推論延遲，以及無缺陷驗證集二值化閾值設定（避免如 MVTec AD 2 中因跨測試集正規化導致分割 $F_1$ 低落）。
  2. **候選方法二：`LAMBDA`（GPU 記憶體受限之擴散分割場景候選）**
     - 現有論文證據：在 `lee2026-lambda` Table 1（於 `VisA` 資料集、**NVIDIA A100 GPU**、訓練 Batch Size = `8`）中，`DiffusionAD` 訓練需 `48.4 GB` GPU 記憶體、推論為 `10.9 FPS`，而 `LAMBDA` 訓練 GPU 記憶體為 `9.3 GB`、評估 GPU 記憶體為 `5.8 GB`、評估推論為 `42.3 FPS`（延遲 `23.6 ms`）。
     - 尚缺的部署驗證條件：論文未記載輸入解析度、評估 Batch Size 與 FPS 計時範圍，且所有數據皆在伺服器級 **NVIDIA A100 GPU** 上測得；不同顯卡架構、記憶體頻寬、解析度與前後處理會顯著影響實際延遲與 GPU 記憶體佔用，因此**絕對不得從 A100 上的 9.3 GB 與 42.3 FPS 直接外推其他顯卡能達到的速度**，必須在目標資料與目標硬體上實測。

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C15-01` | PatchCore 在 MVTec AD 少樣本（Table S5）設定下，當每類別正常訓練樣本為 `16 Shots (6.6%)` 時，`Image AUROC — PatchCore-25%` 為 `95.5 ± 0.6`、`Pixel AUROC — PatchCore-25%` 為 `96.8 ± 0.3` | Image AUROC — PatchCore-25% / Pixel AUROC — PatchCore-25% | MVTec AD (Low-Shot) | 16 Shots (6.6%) | 95.5 ± 0.6 / 96.8 ± 0.3 | `wiki/papers/roth2022-patchcore.md` `#### (A) MVTec AD 少樣本（Low-Shot）異常檢測表現（出自論文 Sec. 4.5, p. 7–8 Fig. 6 & Supp. Table S5, p. 16）` | `roth2022-patchcore.pdf` Sec. 4.5, p. 7–8, Fig. 6 & Supp. Table S5, p. 16 | 原文事實 |
| `C15-02` | 在 `lee2026-lambda` Table 1 的 VisA 效率評測（NVIDIA A100 GPU）中，`DiffusionAD` 之 `GPU Mem (Train)` 為 48.4 GB、`GPU Mem (Eval)` 為 12.4 GB、`FPS (Eval)` 為 10.9；`LAMBDA` 之 `GPU Mem (Train)` 為 9.3 GB、`GPU Mem (Eval)` 為 5.8 GB、`FPS (Eval)` 為 42.3 | DiffusionAD / LAMBDA | VisA | GPU Mem (Train) / GPU Mem (Eval) / FPS (Eval) | 48.4 GB / 12.4 GB / 10.9 (DiffusionAD)｜9.3 GB / 5.8 GB / 42.3 (LAMBDA) | `wiki/papers/lee2026-lambda.md` `#### (A) VisA 資料集檢測精度與計算效率綜合比較（出自論文 Table 1, p. 8）` | `lee2026-lambda.pdf` Sec. 5.4, p. 7–8 & Table 1, p. 8 | 原文事實 |
| `C15-03` | 實務選型上，`PatchCore`（不需訓練網路權重，但仍需擷取正常特徵、建立記憶庫並選取核心集）與 `LAMBDA`（潛在空間記憶庫引導一步去噪）可分別作為少樣本與低 GPU 記憶體擴散分割之優先測試候選，但現有數據缺解析度、評估 Batch Size、計時範圍與目標領域表現，必須在目標資料與目標硬體上實測，不得從 A100 上的記憶體與 FPS 推論其他顯卡能達到的速度（AI 整理） | PatchCore / LAMBDA | 跨資料集 | 候選方法與部署實測判斷準則 | 候選評估與硬體外推限制（AI 整理） | `wiki/comparisons/embedding-vs-reconstruction.md` `## 5. 演進趨勢與取捨分析（AI 整理）`；`wiki/papers/lee2026-lambda.md` `### 5.1 實驗設定、資料集與評估指標（出自論文 Sec. 5.1–5.2, p. 7）` | 無（基於各論文實驗條件邊界之工程選型推論） | AI 推論 |

---

## 第 16 頁：參考資料：7 篇各支援哪幾頁

### 學習目標
查閱本簡報所依據之 7 篇核心論文完整書目資訊、對應 Wiki 頁面連結，以及每篇論文實際支援教學主張的簡報頁碼索引。

### 用到的 Wiki 頁與段落
- `wiki/index.md` `## 1. 單篇論文解析（papers/）`
- `wiki/papers/bergmann2019-mvtec-ad.md` `## 1. 基本資訊`
- `wiki/papers/ho2020-ddpm.md` `## 1. 基本資訊`
- `wiki/papers/zavrtanik2021-riad.md` `## 1. 基本資訊`
- `wiki/papers/roth2022-patchcore.md` `## 1. 基本資訊`
- `wiki/papers/zhang2023-diffusionad.md` `## 1. 基本資訊`
- `wiki/papers/lee2026-lambda.md` `## 1. 基本資訊`
- `wiki/papers/hecklerkram2025-mvtec-ad-2.md` `## 1. 基本資訊`

### 預計使用的圖檔
- 無

### 投影片可見內容
- **可見正文（108 字，含 1 個關鍵數字：7）**：
  - **本簡報收錄之 7 篇核心論文與支援頁碼索引**：
    1. `MVTec AD` (CVPR 2019) $\rightarrow$ 第 2、3、4 頁
    2. `RIAD` (PR 2021) $\rightarrow$ 第 5 頁
    3. `PatchCore` (2022) $\rightarrow$ 第 6、15 頁
    4. `DDPM` (NeurIPS 2020) $\rightarrow$ 第 7 頁
    5. `DiffusionAD` (2023/2025) $\rightarrow$ 第 8 頁
    6. `LAMBDA` (ASOC 2026) $\rightarrow$ 第 9、10、15 頁
    7. `MVTec AD 2` (2025) $\rightarrow$ 第 11、12、13、14 頁
- **延伸閱讀**：[Wiki 總目錄：7 篇單篇論文深度解析頁](../../wiki/index.md#1-單篇論文解析papers)

### 查證資料與講稿備註
- **7 篇收錄論文完整書目與支援主張 ID 對照清單**：
  1. **`bergmann2019-mvtec-ad`** — Bergmann et al., *"MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection"*, CVPR 2019 ([wiki/papers/bergmann2019-mvtec-ad.md](../../wiki/papers/bergmann2019-mvtec-ad.md))
     - 實際支援教學主張頁碼：**第 2、3、4 頁**（`C02-01`、`C02-02`、`C02-03`、`C03-01`、`C03-02`、`C03-03`、`C04-01`、`C04-02`、`C04-03`）
  2. **`ho2020-ddpm`** — Ho et al., *"Denoising Diffusion Probabilistic Models"*, NeurIPS 2020 ([wiki/papers/ho2020-ddpm.md](../../wiki/papers/ho2020-ddpm.md))
     - 實際支援教學主張頁碼：**第 7 頁**（`C07-01`、`C07-02`、`C07-03`）
  3. **`zavrtanik2021-riad`** — Zavrtanik et al., *"Reconstruction by Inpainting for Visual Anomaly Detection"*, Pattern Recognition 2021 ([wiki/papers/zavrtanik2021-riad.md](../../wiki/papers/zavrtanik2021-riad.md))
     - 實際支援教學主張頁碼：**第 5 頁**（`C05-01`、`C05-02`、`C05-03`、`C05-04`）
  4. **`roth2022-patchcore`** — Roth et al., *"Towards Total Recall in Industrial Anomaly Detection"*, 2022 / `arXiv:2106.08265v2` ([wiki/papers/roth2022-patchcore.md](../../wiki/papers/roth2022-patchcore.md))
     - 實際支援教學主張頁碼：**第 6、15 頁**（`C06-01`、`C06-02`、`C06-03`、`C06-04`、`C15-01`）
  5. **`zhang2023-diffusionad`** — Zhang et al., *"DiffusionAD: Norm-guided One-step Denoising Diffusion for Anomaly Detection"*, 2023 / 2025 `arXiv:2303.08730v4` ([wiki/papers/zhang2023-diffusionad.md](../../wiki/papers/zhang2023-diffusionad.md))
     - 實際支援教學主張頁碼：**第 8 頁**（`C08-01`、`C08-02`、`C08-03`）
  6. **`lee2026-lambda`** — Lee & Kang, *"Memory bank-guided diffusion model for lightweight anomaly detection"*, Applied Soft Computing 2026 ([wiki/papers/lee2026-lambda.md](../../wiki/papers/lee2026-lambda.md))
     - 實際支援教學主張頁碼：**第 9、10、15 頁**（`C09-01`、`C09-02`、`C09-03`、`C10-01`～`C10-05`、`C15-02`）
  7. **`hecklerkram2025-mvtec-ad-2`** — Heckler-Kram et al., *"The MVTec AD 2 Dataset: Advanced Scenarios for Unsupervised Anomaly Detection"*, 2025 / `arXiv:2503.21622v1` ([wiki/papers/hecklerkram2025-mvtec-ad-2.md](../../wiki/papers/hecklerkram2025-mvtec-ad-2.md))
     - 實際支援教學主張頁碼：**第 11、12、13、14 頁**（`C11-01`～`C11-03`、`C12-01`～`C12-02`、`C13-01`～`C13-03`、`C14-01`～`C14-08`）

### 預計的主張記錄表
| 主張 ID | 內容 | 方法 | 資料集 | 指標 | 數值與條件 | wiki 頁與段落 | 原文位置 | 原文事實／依原文數據計算／AI 推論 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C16-01` | 本簡報收錄之 7 篇論文各自皆在第二至十五頁支援具體教學主張：MVTec AD 支援第二至四頁、RIAD 支援第四至五頁、PatchCore 支援第六與十五頁、DDPM 支援第七頁、DiffusionAD 支援第八頁、LAMBDA 支援第九至十與十五頁、MVTec AD 2 支援第十一至十四頁（AI 整理） | 7 篇論文與簡報頁碼映射 | 跨資料集 | 無 | 7 篇論文各支援至少一筆第二至十五頁之實際教學主張 | `wiki/index.md` `## 1. 單篇論文解析（papers/）` | 各論文 p. 1 書目資訊與對應章節 | AI 推論 |
