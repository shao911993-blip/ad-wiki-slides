#!/usr/bin/env python3
"""把已核准的草稿 drafts/NN.md 組成單一靜態 HTML 簡報（關卡 ④）。

- 文字只從草稿的「學習目標」「投影片內容」「延伸閱讀」「講者備註」取出，不改寫。
- 每頁怎麼排由 <deck>/layout.json 決定；layout.json 不放知識內容，只放版型與版面標籤。
- 版面標籤（站名、「這頁要學會」等）一律包在 class="lbl" 裡，檢查程式比對文字時會先拿掉。
- 大數字版面要把一句話拆到不同格子：程式會把拆開的片段拼回去，和草稿原句比對，
  只容許拿掉拆開處的標點，不一致就停止產生。
- 講者備註放在預設隱藏的面板（N 鍵或按鈕開關）；主張記錄表不輸出。

用法：python scripts/build_deck.py slides/evolution-of-anomaly-detection
"""
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

PUNCT = "，。；：、,.;:"


# ---------- 草稿解析 ----------
def section(text, name):
    m = re.search(r"^## " + re.escape(name) + r"[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else ""


def fix_path(p):
    return p[3:] if p.startswith("../") else p


def reading_link(path):
    path, sep, fragment = fix_path(path).partition("#")
    if path.startswith("../../wiki/") and path.endswith(".md"):
        path = path.replace("../../wiki/", "../../wiki-html/", 1).removesuffix(".md") + ".html"
    return path + sep + fragment


SUBS = [
    (re.compile(r"AU-PRO(0\.\d\d)"), r"AU-PRO<sub>\1</sub>"),
    (re.compile(r"TESTpriv,mix"), r"TEST<sub>priv,mix</sub>"),
    (re.compile(r"TESTpriv(?!,)"), r"TEST<sub>priv</sub>"),
]


def subs(s):
    for pat, rep in SUBS:
        s = pat.sub(rep, s)
    return s


def inline(md):
    """行內 Markdown → HTML：保留 $…$ 給 KaTeX，處理 `code`、**粗體**、*斜體*、[連結](路徑)。"""
    out, pos = [], 0
    for m in re.finditer(r"\$[^$]+\$", md):
        out.append(_inline_text(md[pos:m.start()]))
        out.append(html.escape(m.group(0), quote=False))
        pos = m.end()
    out.append(_inline_text(md[pos:]))
    return "".join(out)


def _inline_text(s):
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", keep, s)
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               lambda m: f'<a href="{html.escape(reading_link(m.group(2)))}">{m.group(1)}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", s)
    s = subs(s)
    return re.sub(r"\x00(\d+)\x00",
                  lambda m: f'<span class="term">{subs(html.escape(codes[int(m.group(1))], quote=False))}</span>', s)


def plain(md):
    s = unicodedata.normalize("NFKC", md)
    s = s.replace("**", "").replace("`", "")
    s = re.sub(r"\s+", "", s)
    return "".join(ch for ch in s if ch not in PUNCT)


def parse_body(body):
    blocks, lines, i = [], body.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", ln.strip())
        if m:
            cap = lines[i + 1].strip() if i + 1 < len(lines) else ""
            blocks.append({"k": "figure", "alt": m.group(1), "src": fix_path(m.group(2)), "cap": cap})
            i += 2
            continue
        if ln.strip().startswith("$$"):
            blocks.append({"k": "math", "tex": ln.strip()})
            i += 1
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            blocks.append({"k": "table", "head": rows[0], "rows": rows[2:]})
            continue
        if ln.startswith("- "):
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("  - ")):
                if lines[i].startswith("  - "):
                    items[-1]["sub"].append(lines[i][4:])
                else:
                    items.append({"text": lines[i][2:], "sub": []})
                i += 1
            blocks.append({"k": "bullets", "items": items})
            continue
        blocks.append({"k": "para", "text": ln.strip()})
        i += 1
    return blocks


def split_label(md):
    """「**標籤**：內文」→（標籤, 內文）；標籤後沒有冒號也可以。"""
    m = re.match(r"^\*\*(.+?)\*\*\s*[：:]?\s*(.*)$", md)
    return (m.group(1), m.group(2)) if m else (None, md)


# ---------- 共用元件 ----------
def L(text):
    return f'<span class="lbl">{html.escape(text)}</span>'


def figure_html(b, cls="fig"):
    src, alt = b["src"], html.escape(b["alt"])
    if src.endswith(".html"):
        diagrams = Path(__file__).resolve().parents[1] / "assets" / "diagrams" / "slides"
        path = diagrams / Path(src).name
        if src != f"../../assets/diagrams/slides/{path.name}":
            sys.exit(f"教學圖解路徑無效：{src}")
        diagram = path.read_text(encoding="utf-8").strip()
        cls += " diagram"
        visual = f'<div class="teaching-diagram" role="img" aria-label="{alt}">{diagram}</div>'
    else:
        visual = f'<img src="{html.escape(src)}" alt="{alt}" />'
    return f'<figure class="{cls}">{visual}<figcaption>{inline(b["cap"])}</figcaption></figure>'


def card(label_md, body_md, cls="card", sub=None, num=None):
    head = ""
    if num is not None:
        head += f'<span class="lbl num">{num}</span>'
    if label_md is not None:
        head += f'<h3>{inline(label_md)}</h3>'
    subhtml = ""
    if sub:
        subhtml = '<ul class="sub">' + "".join(f"<li>{inline(s)}</li>" for s in sub) + "</ul>"
    return f'<div class="{cls}">{head}<p>{inline(body_md)}</p>{subhtml}</div>'


def table_html(b):
    th = "".join(f"<th>{inline(c)}</th>" for c in b["head"])
    trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in b["rows"])
    return f'<div class="table-wrap"><table class="data-table"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def math_html(b):
    return f'<div class="formula">{html.escape(b["tex"], quote=False)}</div>'


# ---------- 各版型 ----------
def blocks_of(blocks, kind):
    return [b for b in blocks if b["k"] == kind]


def all_items(blocks):
    return [it for b in blocks_of(blocks, "bullets") for it in b["items"]]


def lay_cover(pg, cfg, spec):
    items = all_items(pg["blocks"])
    claim = items[0]
    stops = []
    for n, it in enumerate(items[1:], 1):
        lab, body = split_label(it["text"])
        stops.append(f'<div class="stop"><span class="lbl num st{n}">{n}</span>'
                     f'<span><strong>{inline(lab)}</strong>：{inline(body)}</span></div>')
    return f'''
  <div class="cover-left">
    <div class="kicker">{L(cfg["cover_kicker"])}</div>
    <h1 class="title">{html.escape(cfg["deck_title"]).replace("：", "：<br>", 1)}</h1>
    <p class="cover-goal">{inline(pg["goal"])}</p>
    <div class="claim">{inline(claim["text"])}</div>
    <div class="route">{"".join(stops)}</div>
    {pg["foot"]}
  </div>
  <div class="cover-right"><img src="{cfg["mascot"]}" alt="拿放大鏡的吉祥物" /></div>'''


def lay_cards(pg, cfg, spec):
    items = all_items(pg["blocks"])
    out, k = [], 0
    for n in spec.get("rows", [len(items)]):
        row = items[k:k + n]
        k += n
        out.append(f'<div class="row-cards cols{n}">' +
                   "".join(card(*split_label(it["text"]), sub=it["sub"]) for it in row) + "</div>")
    return '<div class="stack">' + "".join(out) + "</div>"


def lay_bignums(pg, cfg, spec):
    items = all_items(pg["blocks"])
    src = items[spec["bullet"]]["text"]
    pieces = spec["label"] + "".join(t["pre"] + t["n"] + t["unit"] for t in spec["tiles"])
    if plain(pieces) != plain(src):
        sys.exit(f"[p{pg['n']}] 大數字拆段拼回後與草稿不同：\n  草稿：{plain(src)}\n  拼回：{plain(pieces)}")
    tiles = "".join(
        f'<div class="bignum"><div class="pre">{inline(t["pre"] or spec["label"])}</div>'
        f'<div class="n">{html.escape(t["n"])}</div><div class="unit">{html.escape(t["unit"])}</div></div>'
        for t in spec["tiles"])
    rest = [it for i, it in enumerate(items) if i != spec["bullet"]]
    defs = "".join(card(*split_label(it["text"]), cls="card def") for it in rest)
    return (f'<div class="stack"><div class="bignums">{tiles}</div>'
            f'<div class="row-cards cols{len(rest)}">{defs}</div></div>')


def lay_versus(pg, cfg, spec):
    items = all_items(pg["blocks"])
    sides = []
    for idx, it in enumerate(items):
        lab, body = split_label(it["text"])
        m = re.match(r"^(.*?)(（.*）)$", lab)
        main, paren = (m.group(1), m.group(2)) if m else (lab, "")
        parts = [p for p in body.split(spec["split"]) if p.strip()]
        rows = "".join(
            f'<div class="vrow{" warn" if j else ""}">{L(spec["row_labels"][j]) if j < len(spec["row_labels"]) else ""}'
            f'<p>{inline(p)}</p></div>' for j, p in enumerate(parts))
        icon = f'<span class="lbl icon" aria-hidden="true">{spec["icons"][idx]}</span>' if spec.get("icons") else ""
        sides.append(f'<div class="side side{idx}"><h3>{icon}{inline(main)}<small>{inline(paren)}</small></h3>{rows}</div>')
    return f'<div class="versus">{sides[0]}<div class="vs">{L("vs")}</div>{sides[1]}</div>'


def lay_method(pg, cfg, spec):
    fig = blocks_of(pg["blocks"], "figure")[0]
    items = all_items(pg["blocks"])
    cards = "".join(card(*split_label(it["text"]), cls="card q", num=n) for n, it in enumerate(items, 1))
    return f'<div class="method">{figure_html(fig, "fig grow")}<div class="qgrid">{cards}</div></div>'


def lay_figure_side(pg, cfg, spec):
    fig = blocks_of(pg["blocks"], "figure")[0]
    maths = blocks_of(pg["blocks"], "math")
    items = all_items(pg["blocks"])
    steps, notes = [], []
    for it in items:
        lab, body = split_label(it["text"])
        (notes if lab and lab.startswith("（") else steps).append((lab, body))
    step_html = []
    for n, (lab, body) in enumerate(steps, 1):
        extra = math_html(maths[0]) if n == len(steps) and maths else ""
        step_html.append(f'<div class="card step"><span class="lbl num">{n}</span><h3>{inline(lab)}</h3>'
                         f'<p>{inline(body)}</p>{extra}</div>')
    note_html = "".join(f'<div class="callout"><strong>{inline(l)}</strong> {inline(b)}</div>' for l, b in notes)
    return (f'<div class="side-layout"><div class="side-left">{figure_html(fig, "fig")}{note_html}</div>'
            f'<div class="side-right">{"".join(step_html)}</div></div>')


def lay_table_side(pg, cfg, spec):
    items = all_items(pg["blocks"])
    tab = blocks_of(pg["blocks"], "table")[0]
    cards = "".join(card(*split_label(it["text"]), cls="card compact") for it in items)
    return f'<div class="side-layout tbl"><div class="side-left stack">{cards}</div><div class="side-right">{table_html(tab)}</div></div>'


def lay_stat_list(pg, cfg, spec):
    items = all_items(pg["blocks"])
    a = card(*split_label(items[0]["text"]), cls="card stat")
    b = card(*split_label(items[1]["text"]), cls="card stat wide", sub=items[1]["sub"])
    return f'<div class="stat-layout">{a}{b}</div>'


def lay_figure_row(pg, cfg, spec):
    fig = blocks_of(pg["blocks"], "figure")[0]
    items = all_items(pg["blocks"])
    cards = "".join(card(*split_label(it["text"]), cls="card stat") for it in items)
    return f'<div class="method">{figure_html(fig, "fig grow")}<div class="row-cards cols{len(items)}">{cards}</div></div>'


def lay_definition(pg, cfg, spec):
    items = all_items(pg["blocks"])
    top = card(*split_label(items[0]["text"]), cls="card band")
    rest = "".join(card(*split_label(it["text"]), cls="card stat") for it in items[1:])
    return f'<div class="stack">{top}<div class="row-cards cols{len(items) - 1}">{rest}</div></div>'


def lay_table_below(pg, cfg, spec):
    items = all_items(pg["blocks"])
    tab = blocks_of(pg["blocks"], "table")[0]
    paras = "".join(f'<p class="footnote">{inline(b["text"])}</p>' for b in blocks_of(pg["blocks"], "para"))
    cards = "".join(card(*split_label(it["text"]), cls="card compact") for it in items)
    return f'<div class="stack"><div class="row-cards cols{len(items)}">{cards}</div>{table_html(tab)}{paras}</div>'


def lay_timeline(pg, cfg, spec):
    items = all_items(pg["blocks"])
    lab, body = split_label(items[0]["text"])
    parts = [p.strip() for p in body.rstrip("。").split(spec["chain_sep"])]
    chain = f'<span class="arrow">{spec["chain_sep"]}</span>'.join(f'<span class="chip">{inline(p)}</span>' for p in parts)
    q = card(*split_label(items[1]["text"]), cls="card question")
    alab, abody = split_label(items[spec["reveal"]]["text"])
    ans = (f'<div class="card answer" data-reveal><button type="button" class="lbl reveal-btn">顯示解答</button>'
           f'<div class="answer-body"><h3>{inline(alab)}</h3><p>{inline(abody)}</p></div></div>')
    return (f'<div class="stack"><div class="timeline"><h3>{inline(lab)}</h3><div class="chain">{chain}</div></div>'
            f'<div class="qa">{q}{ans}<img class="qa-mascot" src="{cfg["mascot"]}" alt="" aria-hidden="true" /></div></div>')


def lay_refs(pg, cfg, spec):
    items = all_items(pg["blocks"])
    cards = "".join(card(*split_label(it["text"]), cls="card ref") for it in items)
    paras = "".join(f'<p class="footnote">{inline(b["text"])}</p>' for b in blocks_of(pg["blocks"], "para"))
    return f'<div class="stack"><div class="refs">{cards}</div>{paras}</div>'


LAYOUTS = {"cover": lay_cover, "cards": lay_cards, "bignums": lay_bignums, "versus": lay_versus,
           "method": lay_method, "figure-side": lay_figure_side, "table-side": lay_table_side,
           "stat-list": lay_stat_list, "figure-row": lay_figure_row, "definition": lay_definition,
           "table-below": lay_table_below, "timeline": lay_timeline, "refs": lay_refs}


# ---------- 組頁 ----------
def station_of(n, cfg):
    for st in cfg["stations"]:
        if n in st["pages"]:
            return st
    return None


def render_slide(n, total, text, cfg):
    spec = cfg["pages"][str(n)]
    reading = section(text, "延伸閱讀")
    links = " ".join(inline(l[2:]) for l in reading.splitlines() if l.startswith("- "))
    foot = (f'<footer class="foot"><span class="reading"><span class="lbl">延伸閱讀</span>{links}</span>'
            f'<span class="lbl pageno">{n} / {total}</span></footer>')
    pg = {"n": n, "goal": section(text, "學習目標"), "blocks": parse_body(section(text, "投影片內容")), "foot": foot,
          "title": re.search(r"^# 第 \d+ 頁：(.+)$", text, re.M).group(1).strip()}
    notes = [l[2:] for l in section(text, "講者備註").splitlines() if l.startswith("- ")]
    notes_html = ('<aside class="speaker-notes" aria-label="講者備註"><h3 class="lbl">講者備註</h3><ul>'
                  + "".join(f"<li>{inline(x)}</li>" for x in notes) + "</ul></aside>")
    body = LAYOUTS[spec["layout"]](pg, cfg, spec)
    if spec["layout"] == "cover":
        return f'<section class="slide cover" id="slide-{n}" data-n="{n}" aria-label="第 {n} 頁">{body}{notes_html}</section>'
    st = station_of(n, cfg)
    if st:
        chip = f'<span class="station">{L("第 " + str(st["no"]) + " 站")}{L(st["name"])}</span>'
        cls, on = f"s{st['no']}", st["no"]
    else:
        chip = f'<span class="station">{L(cfg["appendix_label"])}</span>'
        cls, on = "s0", len(cfg["stations"])
    prog = "".join(f'<i class="{"on" if i < on else ""}"></i>' for i in range(len(cfg["stations"])))
    mascot = (f'  <img class="mascot-peek" src="{cfg["mascot"]}" alt="" aria-hidden="true" />'
              if n in cfg.get("mascot_pages", []) else "")
    return f'''
<section class="slide {cls} lay-{spec["layout"]}" id="slide-{n}" data-n="{n}" aria-label="第 {n} 頁">
  <div class="topbar">{chip}<span class="progress lbl" aria-hidden="true">{prog}</span></div>
  <h2 class="title">{inline(pg["title"])}</h2>
  <p class="goal">{L("這頁要學會")}{inline(pg["goal"])}</p>
  <div class="content">{body}</div>
{mascot}
  {foot}
  {notes_html}
</section>'''


def main():
    deck = Path(sys.argv[1])
    cfg = json.loads((deck / "layout.json").read_text(encoding="utf-8"))
    drafts = sorted((deck / "drafts").glob("[0-9][0-9].md"))
    total = len(drafts)
    missing = [str(i) for i in range(1, total + 1) if str(i) not in cfg["pages"]]
    if missing:
        sys.exit(f"layout.json 缺少頁面設定：{missing}")
    slides = "\n".join(render_slide(i + 1, total, p.read_text(encoding="utf-8"), cfg) for i, p in enumerate(drafts))
    tpl = (Path(__file__).parent / "deck_template.html").read_text(encoding="utf-8")
    out = tpl.replace("{{SLIDES}}", slides).replace("{{TOTAL}}", str(total)).replace("{{DECK_TITLE}}", cfg["deck_title"])
    (deck / "index.html").write_text(out, encoding="utf-8", newline="\n")
    print(f"wrote {deck / 'index.html'} ({total} slides)")


if __name__ == "__main__":
    main()
