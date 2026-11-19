"""Build static reading pages from wiki Markdown. Run with python scripts/build_wiki.py."""

import html
import posixpath
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

from check_drafts import github_slug

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
OUTPUT = ROOT / "wiki-html"
TEMPLATE = (ROOT / "scripts" / "wiki_template.html").read_text(encoding="utf-8")


def render_link(tokens, index, options, env):
    token = tokens[index]
    url = urlsplit(token.attrGet("href"))
    if not (url.scheme or url.netloc or not url.path):
        source = env["source"].parent / unquote(url.path)
        target = source.resolve()
        if target.is_dir() and not (target / "index.html").is_file():
            # A GitHub repository can browse folders without an index; Pages cannot.
            token.attrs.pop("href")
        if target.suffix == ".md" and target.is_relative_to(WIKI):
            target = OUTPUT / target.relative_to(WIKI).with_suffix(".html")
            if target in env["pages"]:
                path = posixpath.relpath(target.as_posix(), env["output"].parent.as_posix())
                token.attrSet("href", urlunsplit(url._replace(path=path)))
    return md.renderer.renderToken(tokens, index, options, env)


def render_math(tokens, index, opening, closing):
    return opening + html.escape(tokens[index].content) + closing


md = MarkdownIt("commonmark").enable("table").use(dollarmath_plugin)
md.renderer.rules["link_open"] = render_link
md.renderer.rules["math_inline"] = lambda ts, i, *_: render_math(ts, i, "$", "$")
md.renderer.rules["math_block"] = lambda ts, i, *_: render_math(ts, i, "<div>$$", "$$</div>\n")


def prepare_tokens(text, env):
    tokens = md.parse(text, env)
    anchors = Counter()
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            slug = github_slug(tokens[index + 1].content)
            count = anchors[slug]
            anchors[slug] += 1
            token.attrSet("id", f"{slug}-{count}" if count else slug)
        elif token.type == "table_open":
            labels = []
        elif token.type == "th_open":
            labels.append(tokens[index + 1].content.replace("`", ""))
        elif token.type == "tr_open":
            column = 0
        elif token.type == "td_open":
            token.attrSet("data-label", labels[column])
            column += 1
    return tokens


def main():
    sources = sorted(WIKI.rglob("*.md"))
    pages = {OUTPUT / path.relative_to(WIKI).with_suffix(".html") for path in sources}
    for source in sources:
        output = OUTPUT / source.relative_to(WIKI).with_suffix(".html")
        text = source.read_text(encoding="utf-8-sig")
        text = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S).lstrip()
        env = {"source": source, "output": output, "pages": pages}
        tokens = prepare_tokens(text, env)
        title = next(token.content for token in tokens if token.type == "inline")
        body = md.renderer.render(tokens, md.options, env)
        root = posixpath.relpath(ROOT.as_posix(), output.parent.as_posix()) + "/"
        wiki = posixpath.relpath(OUTPUT.as_posix(), output.parent.as_posix())
        result = TEMPLATE.replace("%%TITLE%%", html.escape(title)).replace("%%ROOT%%", root)
        result = result.replace("%%WIKI%%", wiki + "/").replace("%%CONTENT%%", body)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result, encoding="utf-8", newline="\n")
    print(f"Wiki HTML: {len(pages)} pages")


if __name__ == "__main__":
    main()
