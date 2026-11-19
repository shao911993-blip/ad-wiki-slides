"""關卡 ④ 瀏覽器渲染檢查：用 headless Chrome 實際打開簡報，逐頁量版面並比對文字。

檢查項目
- 桌面（16:9 畫布等比例縮放）：內文沒有壓到標題或頁尾、沒有元素超出畫布、圖沒有被壓到最小高度、
  縮放後最小字級（報告數值）。
- 手機（寬 ≤ 760，直向捲動）：沒有元素超出畫面寬度（含被 overflow 靜默裁切的情況）。
- 全部視窗：圖片載入、圖解可見且標籤至少 14 px、表格英文不拆行、KaTeX、換頁與講者備註。
- 內容一致：草稿的學習目標、投影片內容、延伸閱讀每一行（含表格每格），在畫面文字中都找得到。
  比對前先拿掉 class="lbl" 的版面標籤，並忽略空白與「，。；：、」（版型會把句子拆到不同格子）。
  公式 $…$ 不比對文字，改比對投影片內文的 KaTeX 數量。檢查前會先按下所有「顯示解答」。

用法：python scripts/check_render.py slides/evolution-of-anomaly-detection [--katex-dir DIR] [--chrome PATH] [--screenshots]
需要：pip install playwright（並 playwright install chromium，或用 --chrome 指定本機 Chrome）。
"""
import argparse
import http.server
import json
import os
import re
import sys
import threading
import unicodedata
from pathlib import Path

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("deck")
ap.add_argument("--katex-dir", help="本機 KaTeX 0.16.11 的 dist 資料夾；不給就直接連 CDN")
ap.add_argument("--chrome", default=os.environ.get("CHROME_PATH"))
ap.add_argument("--screenshots", action="store_true", help="另存 1366×768 每頁截圖到 reports/screenshots/")
args = ap.parse_args()
DECK_DIR = Path(args.deck).resolve()
ROOT = DECK_DIR.parent.parent
DECK = f"{DECK_DIR.relative_to(ROOT).as_posix()}/index.html"
OUT = DECK_DIR / "reports"
SHOTS = OUT / "screenshots"
KATEX = Path(args.katex_dir) if args.katex_dir else None
if args.screenshots:
    SHOTS.mkdir(parents=True, exist_ok=True)
PUNCT = "，。；：、,.;:"
VIEWPORTS = {"desktop-1366x768": (1366, 768), "desktop-1366x657": (1366, 657), "desktop-1920x1080": (1920, 1080),
             "mobile-390x844": (390, 844), "mobile-360x640": (360, 640)}


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def log_message(self, *a):
        pass


httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{httpd.server_address[1]}/{DECK}"


def route_cdn(route):
    m = re.search(r"katex@0\.16\.11/dist/(.+)$", route.request.url)
    if not m:
        return route.abort()
    f = KATEX / m.group(1)
    ctype = "text/css" if f.suffix == ".css" else ("application/javascript" if f.suffix == ".js" else "font/woff2")
    route.fulfill(status=200, body=f.read_bytes(), content_type=ctype)


MEASURE = r"""() => {
  const s = document.querySelector('.slide.active');
  const r = s.getBoundingClientRect();
  const scale = parseFloat(s.dataset.scale || '1');
  const narrow = window.innerWidth <= 760;
  const vis = el => !el.closest('.speaker-notes') && !el.closest('.katex-mathml') && el.getClientRects().length > 0;
  const all = [...s.querySelectorAll('*')].filter(vis);
  const outside = [];
  all.forEach(el => {
    if (el.closest('.katex') && !el.classList.contains('katex')) return;
    const b = el.getBoundingClientRect(); if (b.width === 0 && b.height === 0) return;
    if (narrow) { if (b.right > window.innerWidth + 0.5 || b.left < -0.5) outside.push(el.className || el.tagName); }
    else if (b.bottom > r.bottom + 0.5 || b.right > r.right + 0.5 || b.left < r.left - 0.5 || b.top < r.top - 0.5) outside.push(el.className || el.tagName);
  });
  let overlap = false, slack = null;
  const content = s.querySelector('.content'), foot = s.querySelector('.foot'), title = s.querySelector('.title');
  if (content && !narrow) {
    const inner = [...content.querySelectorAll('*')].filter(vis).filter(e => !(e.closest('.katex') && !e.classList.contains('katex')));
    const lastB = Math.max(...inner.map(e => e.getBoundingClientRect().bottom));
    const firstT = Math.min(...inner.map(e => e.getBoundingClientRect().top));
    const footTop = foot.getBoundingClientRect().top;
    const head = s.querySelector('.goal') || title;
    overlap = lastB > footTop + 0.5 || firstT < head.getBoundingClientRect().bottom - 0.5;
    slack = Math.round((footTop - lastB) / scale);
  }
  // 最小字級（縮放後，排除頁尾、圖說、版面標籤）
  let minFont = 99, minFontEl = '';
  s.querySelectorAll('.content p, .content li, .content td, .content th, .content h3, .content .unit, .content .chip, .title, .goal, .cover-goal, .claim, .stop span').forEach(el => {
    if (!vis(el)) return;
    const f = parseFloat(getComputedStyle(el).fontSize) * (narrow ? 1 : scale);
    if (f < minFont) { minFont = f; minFontEl = el.tagName + '.' + el.className; }
  });
  const imgs = [...s.querySelectorAll('img')].filter(i => i.closest('.fig') || vis(i)).map(i => {
    const rect = i.getBoundingClientRect();
    return {ok: i.complete && i.naturalWidth > 0, visible: vis(i) && rect.width > 0 && rect.height > 0,
      h: Math.round(rect.height / (narrow ? 1 : scale)), fig: !!i.closest('.fig')};
  });
  const diagrams = [...s.querySelectorAll('.teaching-diagram')].map(diagram => {
    const labels = [...diagram.querySelectorAll('strong, small, .noise-tile, .defect-legend span')];
    const visible = el => {
      const {width, height} = el.getBoundingClientRect();
      const {visibility, opacity} = getComputedStyle(el);
      return vis(el) && width > 0 && height > 0 && visibility === 'visible' && Number(opacity) > 0;
    };
    const font = el => parseFloat(getComputedStyle(el).fontSize) * (narrow ? 1 : scale);
    return {visible: visible(diagram) && labels.length > 0 && labels.every(visible),
      minFont: Math.floor(Math.min(...labels.map(font)) * 10) / 10};
  });
  const broken = [];
  s.querySelectorAll('table td, table th').forEach(cell => {
    const w = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT); let t;
    while ((t = w.nextNode())) { const re = /[A-Za-z][A-Za-z0-9+.%-]*/g; let m;
      while ((m = re.exec(t.data))) { const rg = document.createRange(); rg.setStart(t, m.index); rg.setEnd(t, m.index + m[0].length);
        if (new Set([...rg.getClientRects()].map(c => Math.round(c.top))).size > 1) broken.push(m[0]); } }
  });
  const clone = s.cloneNode(true);
  clone.querySelectorAll('.speaker-notes, .lbl, .katex, .teaching-diagram').forEach(n => n.remove());
  document.body.appendChild(clone); clone.style.cssText = 'position:absolute;left:-99999px;display:flex;transform:none';
  const text = clone.innerText; clone.remove();
  return { n: +s.dataset.n, scale, slack, overlap, outside: [...new Set(outside)].slice(0, 5), minFont: Math.round(minFont * 10) / 10, minFontEl,
    imgs, diagrams, brokenWords: broken, katex: s.querySelectorAll('.content .katex, .cover-left .katex').length,
    katexInBody: [...s.querySelectorAll('.content .katex')].length,
    katexErr: s.querySelectorAll('.katex-error').length, rawDollar: /\$/.test(text), text,
    docW: document.documentElement.scrollWidth, winW: window.innerWidth };
}"""

results = {}
with sync_playwright() as p:
    br = p.chromium.launch(**({"executable_path": args.chrome} if args.chrome else {}), args=["--no-sandbox"])
    for name, (w, h) in VIEWPORTS.items():
        ctx = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
        page = ctx.new_page()
        if KATEX:
            page.route(re.compile(r"https://cdn\.jsdelivr\.net/.*"), route_cdn)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(BASE + "#1")
        page.wait_for_function("document.querySelectorAll('.katex').length > 0", timeout=15000)
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(300)
        res = []
        for n in range(1, 17):
            page.evaluate(f"location.hash = '#{n}'")
            page.wait_for_timeout(150)
            page.evaluate("document.querySelectorAll('.slide.active [data-reveal]').forEach(e => e.classList.add('open'))")
            page.evaluate("window.dispatchEvent(new Event('resize'))")
            page.evaluate("""Promise.allSettled([...document.querySelectorAll('.slide.active img')]
                .map(img => img.decode()))""")
            page.wait_for_timeout(120)
            res.append(page.evaluate(MEASURE))
            if args.screenshots and name == "desktop-1366x768":
                page.evaluate("document.querySelectorAll('[data-reveal]').forEach(e => e.classList.remove('open'))")
                page.screenshot(path=str(SHOTS / f"{name}-{n:02d}.png"))
            if args.screenshots and name == "mobile-390x844" and n in (3, 5, 8, 12):
                page.screenshot(path=str(SHOTS / f"{name}-{n:02d}.png"), full_page=True)
        nav = {}
        page.goto(BASE + "#1"); page.wait_for_timeout(200)
        page.keyboard.press("ArrowRight"); nav["ArrowRight_from_1"] = page.inner_text("#page-indicator")
        page.keyboard.press("ArrowLeft"); nav["ArrowLeft_back"] = page.inner_text("#page-indicator")
        page.keyboard.press("ArrowLeft"); nav["ArrowLeft_at_1_stays"] = page.inner_text("#page-indicator")
        page.keyboard.press("End"); nav["End"] = page.inner_text("#page-indicator")
        page.keyboard.press("ArrowRight"); nav["ArrowRight_at_16_stays"] = page.inner_text("#page-indicator")
        page.keyboard.press("Home"); nav["Home"] = page.inner_text("#page-indicator")
        page.click("#next-btn"); page.click("#next-btn"); nav["next_btn_x2"] = page.inner_text("#page-indicator")
        page.click("#prev-btn"); nav["prev_btn"] = page.inner_text("#page-indicator")
        nav["hash_after"] = page.evaluate("location.hash")
        cur = "document.querySelector('.slide.active .speaker-notes')"
        nav["notes_hidden_default"] = page.evaluate(f"getComputedStyle({cur}).display")
        page.keyboard.press("n"); nav["notes_after_N"] = page.evaluate(f"getComputedStyle({cur}).display")
        page.keyboard.press("n")
        page.goto(BASE + "#15"); page.wait_for_timeout(200)
        page.evaluate("document.querySelectorAll('[data-reveal]').forEach(e => e.classList.remove('open'))")
        nav["answer_hidden_default"] = page.evaluate("getComputedStyle(document.querySelector('.slide.active .answer-body')).display")
        page.click(".slide.active .reveal-btn")
        nav["answer_after_click"] = page.evaluate("getComputedStyle(document.querySelector('.slide.active .answer-body')).display")
        page.goto(BASE + "#9"); page.wait_for_timeout(200); nav["deep_link_#9"] = page.inner_text("#page-indicator")
        results[name] = {"slides": res, "nav": nav, "pageErrors": errors}
        ctx.close()
    br.close()
httpd.shutdown()

# ---------- 報告 ----------
lines = []
P = lines.append
P("關卡 ④ 瀏覽器渲染檢查報告（scripts/check_render.py 產生）")
P(f"受檢檔案：{DECK}；KaTeX 來源：{'本機 0.16.11' if KATEX else 'CDN'}")
P("桌面：1280×720 畫布等比例縮放，檢查內文不壓到標題／頁尾、元素不超出畫布、圖不被壓到最小高度（150 px）；「餘裕」為內文底端到頁尾的距離（畫布座標）。")
P("手機：寬 ≤ 760 改為直向捲動，檢查元素不超出畫面寬度。全部視窗：教學圖標籤至少 14 px，並檢查圖片、表格拆字、KaTeX、換頁與備註。")
errors = 0
EXPECT = {"ArrowRight_from_1": "2 / 16", "ArrowLeft_back": "1 / 16", "ArrowLeft_at_1_stays": "1 / 16", "End": "16 / 16",
          "ArrowRight_at_16_stays": "16 / 16", "Home": "1 / 16", "next_btn_x2": "3 / 16", "prev_btn": "2 / 16",
          "hash_after": "#2", "notes_hidden_default": "none", "notes_after_N": "block",
          "answer_hidden_default": "none", "answer_after_click": "block", "deep_link_#9": "9 / 16"}
for name, r in results.items():
    desk = name.startswith("desktop")
    P("")
    P(f"== {name}  頁面錯誤：{r['pageErrors'] or '無'}")
    errors += len(r["pageErrors"])
    for m in r["slides"]:
        flag = []
        if m["overlap"]:
            flag.append("內文壓到標題或頁尾")
        if m["outside"]:
            flag.append("超出" + ("畫布" if desk else "畫面寬度") + ":" + ",".join(m["outside"]))
        if m["docW"] > m["winW"]:
            flag.append("水平捲動")
        if m["brokenWords"]:
            flag.append("英文字被拆:" + ",".join(m["brokenWords"]))
        if m["katexErr"] or m["rawDollar"]:
            flag.append("公式錯誤")
        if not all(i["ok"] for i in m["imgs"]):
            flag.append("圖片未載入")
        if any(i["fig"] and not i["visible"] for i in m["imgs"]) or any(not d["visible"] for d in m["diagrams"]):
            flag.append("教學圖未顯示")
        if any(d["minFont"] < 14 for d in m["diagrams"]):
            flag.append("教學圖標籤低於 14 px")
        if desk and any(i["fig"] and i["h"] <= 151 for i in m["imgs"]):
            flag.append("圖被壓到最小高度")
        errors += bool(flag)
        figs = [i["h"] for i in m["imgs"] if i["fig"]]
        info = (f"餘裕 {m['slack']} px，" if desk and m["slack"] is not None else "") + \
               (f"圖高 {figs[0]} px，" if figs else "") + \
               (f"圖解標籤 {min(d['minFont'] for d in m['diagrams']):g} px，" if m["diagrams"] else "") + \
               f"最小字 {m['minFont']} px"
        P(f"  第 {m['n']:2d} 頁：{info} → {'；'.join(flag) or 'PASS'}")
    bad = {k: r["nav"].get(k) for k, v in EXPECT.items() if r["nav"].get(k) != v}
    errors += len(bad)
    P(f"  換頁、備註、解答按鈕：{'PASS（' + str(len(EXPECT)) + ' 項）' if not bad else 'FAIL ' + json.dumps(bad, ensure_ascii=False)}")


def section(t, name):
    m = re.search(r"^## " + re.escape(name) + r"[^\n]*\n(.*?)(?=^## |\Z)", t, re.S | re.M)
    return m.group(1).strip() if m else ""


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = s.replace("**", "").replace("`", "")
    s = re.sub(r"^\s*-\s+", "", s)
    s = re.sub(r"(?<!\w)\*(.+?)\*", r"\1", s)
    s = re.sub(r"\s+", "", s)
    return "".join(ch for ch in s if ch not in PUNCT)


P("")
P("== 內容與草稿一致性（學習目標、投影片內容、延伸閱讀逐行比對畫面文字；公式比對數量）")
fails = total = 0
for v in ["desktop-1366x768", "mobile-390x844"]:
    for m in results[v]["slides"]:
        n = m["n"]
        t = (DECK_DIR / "drafts" / f"{n:02d}.md").read_text(encoding="utf-8")
        rendered = norm(m["text"])
        segs = []
        for name in ("學習目標", "投影片內容", "延伸閱讀"):
            for ln in section(t, name).splitlines():
                if not ln.strip():
                    continue
                if ln.startswith("|"):
                    if re.match(r"^\|\s*:?-", ln):
                        continue
                    segs += ln.strip().strip("|").split("|")
                else:
                    segs.append(ln)
        if n != 1:
            segs.append(re.search(r"^# 第 \d+ 頁：(.+)$", t, re.M).group(1))
        pieces = [x for sg in segs for x in re.split(r"\$\$?[^$]+\$\$?", sg)]
        for sg in pieces:
            ns = norm(sg)
            if not ns:
                continue
            total += 1
            if ns not in rendered:
                fails += 1
                P(f"  [{v}] 第 {n} 頁找不到：{sg.strip()[:70]}")
        if v == "desktop-1366x768":
            body = section(t, "投影片內容")
            exp = len(re.findall(r"\$\$[^$]+\$\$", body)) + len(re.findall(r"(?<!\$)\$[^$]+\$(?!\$)", body))
            if exp != m["katexInBody"]:
                fails += 1
                P(f"  第 {n} 頁公式數 {m['katexInBody']}，草稿 {exp}")
P(f"  比對 {total} 段文字，不一致 {fails} 處 → {'PASS' if fails == 0 else 'FAIL'}")
errors += fails
P("")
P(f"OVERALL RESULT: {'PASSED' if errors == 0 else 'FAILED'} ({errors} error(s))")
(OUT / "render-check.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
sys.exit(0 if errors == 0 else 1)
