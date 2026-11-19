"""Check that the published entry, slides, and Wiki links resolve on a static host."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.anchors = Counter()
        self.links = []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get("id"):
            self.anchors[attrs["id"]] += 1
        key = {"a": "href", "link": "href", "img": "src", "script": "src"}.get(tag)
        if key and attrs.get(key):
            self.links.append(attrs[key])


def check():
    files = [ROOT / "index.html"]
    files.extend(sorted((ROOT / "slides").glob("*/index.html")))
    files.extend(sorted((ROOT / "wiki-html").rglob("*.html")))
    pages = {path: Page(path) for path in files}
    issues = []
    links = anchors = 0
    for source, page in pages.items():
        label = source.relative_to(ROOT)
        for anchor, count in page.anchors.items():
            if count > 1:
                issues.append(f"{label}: duplicate ID {anchor}")
        for href in page.links:
            url = urlsplit(href)
            if url.scheme or url.netloc:
                continue
            links += 1
            path = unquote(url.path)
            target = (source.parent / path).resolve() if path else source
            if path.startswith("/") or not target.is_relative_to(ROOT):
                issues.append(f"{label}: link is not relative to the site: {href}")
                continue
            if target.is_relative_to(ROOT / "raw"):
                issues.append(f"{label}: link points to raw: {href}")
                continue
            if not target.is_file():
                issues.append(f"{label}: missing target: {href}")
                continue
            if url.fragment and target.suffix == ".html":
                slug = unquote(url.fragment)
                if target not in pages:
                    pages_for_target = Page(target)
                else:
                    pages_for_target = pages[target]
                anchors += 1
                if slug not in pages_for_target.anchors:
                    issues.append(f"{label}: missing anchor: {href}")
    print(f"Static links: {len(pages)} pages, {links} local links/assets, {anchors} HTML anchors")
    for issue in issues:
        print(issue)
    print(f"{'FAIL' if issues else 'PASS'} ({len(issues)} issues)")
    return bool(issues)


if __name__ == "__main__":
    raise SystemExit(check())
