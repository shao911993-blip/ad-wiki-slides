# 生成式 AI 第十週作業｜視覺異常檢測 LLM Wiki

## 1. LLM Wiki 主題與簡介

工業檢查常遇到一個問題：正常品多，已知瑕疵的範例少。這個 Wiki 從「只有正常品可以拿來學習，怎麼找出可疑區域？」出發，整理正常特徵比對、影像重建、擴散去噪與評估基準。讀者是具備基礎機器學習概念、初次接觸視覺異常檢測的人。

資料來源共七篇。MVTec AD 與 MVTec AD 2 提供資料與評估脈絡，DDPM 提供擴散基礎，RIAD、PatchCore、DiffusionAD、LAMBDA 分別支援四種方法的教學。各篇的實際用途列在簡報第 16 頁。[七篇論文與 Wiki 索引](https://shao911993-blip.github.io/ad-wiki-slides/wiki-html/index.html)

沿用 Karpathy LLM Wiki 的原始資料、Markdown Wiki、協作規範三層架構。因為下游要教初學者，每篇知識頁另設「初學者版（AI 整理）」，技術層保留論文位置、指標與實驗條件，投影片以主張 ID 回溯到對應 Wiki 段落。原始 PDF 依專案規範留在本機。

## 2. LLM Wiki 成果

- [可直接閱讀的 Wiki](https://shao911993-blip.github.io/ad-wiki-slides/wiki-html/index.html)
- [GitHub repo 與專案結構](https://github.com/shao911993-blip/ad-wiki-slides)
- [AGENTS.md 協作規範](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/AGENTS.md)和 [Wiki 操作紀錄](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/wiki/log.md)

目前共有七篇論文頁、六篇概念頁、兩篇資料集與指標頁及一篇跨方法比較頁。各頁以相對連結串起方法、基準與指標。閱讀網頁由原有 Markdown 產生，講者的引用與查證留在逐頁草稿。

## 3. 教學 HTML 簡報

[從重建到擴散：工業異常檢測的演進](https://shao911993-blip.github.io/ad-wiki-slides/slides/evolution-of-anomaly-detection/)

| 學習順序 | 初學者做到什麼 |
| :--- | :--- |
| 第 1–6 頁：任務與基本方法 | 說出「這張有沒有問題」和「問題在哪裡」的差異，並用 RIAD、PatchCore 解釋重建與特徵比對。 |
| 第 7–10 頁：擴散方法 | 用加噪與去噪的流程解釋擴散怎麼用於異常檢測，再讀懂同一評測中的效果與成本取捨。 |
| 第 11–16 頁：評估與選型 | 用大、小缺陷的例子讀懂 PRO，解釋評估規則和光照改變如何影響結論，最後完成少量正常樣本與 GPU 資源受限的選型題。 |

例如第 8 頁把「強雜訊分支先去噪得到正常範本，再引導弱雜訊分支」連到 DiffusionAD 的方法段落。第 14 頁則把比較表的模型版本、引用來源和平均分母帶到同一畫面。第 15 頁讓讀者先作答再看解答，練習區分「值得先試」和「已證明能部署」。[第 8 頁](https://shao911993-blip.github.io/ad-wiki-slides/slides/evolution-of-anomaly-detection/#8) · [第 14 頁](https://shao911993-blip.github.io/ad-wiki-slides/slides/evolution-of-anomaly-detection/#14) · [第 15 頁](https://shao911993-blip.github.io/ad-wiki-slides/slides/evolution-of-anomaly-detection/#15)

## 4. Graph 設計

```text
固定 Wiki 版本 → 大綱與七篇來源覆蓋檢查 → 人確認大綱
       ↑                  │
       │                  └── 設計或順序有問題 → 改大綱
       │
       └── 證據有缺口 → 暫停下游 → 修 Wiki 並重查受影響的主張

核准大綱 →［寫一頁 → 查來源、數值、條件、密度與連結］× 16
                                  ↑             │
                                  └── 單頁失敗 ───┘
         → 獨立 AI 審查 → 依錯誤種類退回 Wiki／大綱／草稿
                │ 通過
                ↓
         從草稿產生 HTML → 瀏覽器逐頁檢查 → 人驗收
                ↑                  │
                └── 版型有問題：修範本後重建 ───┘
```

大綱先確認教學順序和來源覆蓋，讓後續的重寫限於出問題的頁。逐頁查表時，要把數字與列、欄、表題、實驗條件一起核對。程式無法判定的語意交給獨立審查，例如模型變體的適用範圍。同一主張 ID 如跨頁使用，修正時一併重查。每頁同一問題重寫達三次仍未通過，就記錄問題交給人處理。瀏覽器驗收處理螢幕、換頁與公式等草稿階段無法量測的問題。[大綱與主張記錄](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/slides/evolution-of-anomaly-detection/outline.md)

## 5. 實際執行與檢查紀錄

| 執行階段 | 發現、退回與重驗 |
| :--- | :--- |
| 第一次獨立審查 | 發現第 7 頁混合 DDPM 原始用途與後續異常檢測用法，第 14 頁也把模型變體等必要條件留在隱藏區域。分別退回來源與逐頁草稿，補足事實的來源和適用條件。[第一次審查](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/slides/evolution-of-anomaly-detection/reports/gate3-review-gpt.md) |
| 第二次審查與再次驗收 | 仍有三項阻擋，包括第 8 頁漏掉產生正常範本的去噪步驟，第 11 頁混合原文與換算，第 14 頁的比較條件仍需呈現在可見表格。回到對應的 Wiki 或草稿修正，第三次逐項驗收通過。[第二次審查](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/slides/evolution-of-anomaly-detection/reports/gate3-review-gpt-round2.md) · [修正紀錄](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/slides/evolution-of-anomaly-detection/reports/gate3-response.md) · [第三次驗收](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/slides/evolution-of-anomaly-detection/reports/gate3-review-gpt-round3.md) |
| 瀏覽器複驗 | 舊報告中手機圖高為 0 仍被放行。修正手機版範本，加入「教學圖實際可見」判定，再用暫存副本植入零高度圖，確認會被攔截。[逐頁渲染報告](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/slides/evolution-of-anomaly-detection/reports/render-check.txt) · [植入錯誤測試](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/slides/evolution-of-anomaly-detection/reports/render-check-mutations.txt) · [手機第 8 頁截圖](https://shao911993-blip.github.io/ad-wiki-slides/slides/evolution-of-anomaly-detection/reports/screenshots/mobile-390x844-08.png) |
| 人驗收 | 上線後我看簡報，論文重繪的技術圖放進投影片太小、看不清楚，退回版型。Codex 把第 5–9、12 頁改成簡報專用流程圖，之後重跑草稿、渲染和站內連結檢查，都通過。[桌面第 5 頁截圖](https://shao911993-blip.github.io/ad-wiki-slides/slides/evolution-of-anomaly-detection/reports/screenshots/desktop-1366x768-05.png) · [桌面第 8 頁截圖](https://shao911993-blip.github.io/ad-wiki-slides/slides/evolution-of-anomaly-detection/reports/screenshots/desktop-1366x768-08.png) |

本次重跑大綱、草稿與大綱變異測試。草稿程式逐格核對 23 筆表格主張，另 34 筆語意判斷須查獨立審查紀錄。成品以三種桌面和兩種手機視窗檢查 16 頁，另比對 342 段畫面文字，並查驗網站內的連結與 Wiki 段落錨點。[大綱檢查](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/slides/evolution-of-anomaly-detection/reports/outline-check.txt) · [草稿檢查](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/slides/evolution-of-anomaly-detection/reports/drafts-check.txt) · [站內連結檢查](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/slides/evolution-of-anomaly-detection/reports/site-check.txt)

GitHub Pages 上線後，我用未登入的 Chrome 工作階段複驗桌面與手機版。兩種尺寸均開啟全部 16 頁簡報與 18 頁 Wiki，圖解、KaTeX 和延伸閱讀錨點皆正常。

## 6. 反思

**最常出錯的節點**是把 Wiki 的方法與實驗濃縮成一頁草稿。最常看見的是正文超出字數，最影響理解的是省略限定條件。例如模型變體或平均分母一旦只留在備註，讀者就可能把數字理解成同一模型在各欄的直接比較。

**把查證往前移到大綱與每頁初稿。** 第 10、14 頁在大綱就列出數據主張和 Wiki 段落。逐頁稿一完成便核對儲存格與上下文，並確認讀者在畫面上看得見足以解讀數字的資訊。

**因此增加兩種回路。** 先檢查草稿的內容與證據，再由獨立審查複核「簡化後會不會改變意思」。瀏覽器檢查則加上圖片實際尺寸與故障植入。前者攔下錯誤解讀，後者攔下檔案載入成功、畫面卻沒有教學圖的情況。

## AI 使用說明

Gemini（Antigravity）依 AGENTS.md 建立 Wiki 並撰寫第 1–11 頁草稿；Claude 接手第 12–16 頁草稿、數字核對與檢查腳本、A 風格版型，並在專案資料夾遺失後從副本重建檔案；Codex（GPT）負責三輪獨立審查，以及重建後的 git、Wiki 閱讀網頁、版面與示意圖重繪和部署。我看過第一版後退回外觀，從保留下來的版型二與 A／B 風格樣張中選定 A 風格三站版型。另一項有紀錄的決定是草稿原先每頁正文上限 120 字，第 15 頁三次改寫仍超限，由我改為 130 字，讓問題情境能以完整白話呈現。圖表所需的數字和比較條件仍由同一套檢查核對。[原選版型](https://shao911993-blip.github.io/ad-wiki-slides/slides/_templates/template-2-top-figure.html) · [風格樣張](https://shao911993-blip.github.io/ad-wiki-slides/slides/evolution-of-anomaly-detection/reports/style-samples.html) · [逐頁重寫紀錄](https://github.com/shao911993-blip/ad-wiki-slides/blob/main/slides/evolution-of-anomaly-detection/reports/drafts-rewrites.json)
