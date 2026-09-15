#!/usr/bin/env python3
"""Build the preview site.

src/shell.html      head, styles, header, footer (taken from the homepage)
src/extra.css       additional component styles, appended to the shell
src/pages/*.html    page bodies (<main> content); first line <!--TITLE:...-->
src/assets/img_*.*  images, referenced in pages as __IMG_<key>__

Output: one HTML file per page in the repo root, images copied to assets/.
"""
import pathlib
import re
import shutil

SRC = pathlib.Path(__file__).resolve().parent
OUT = SRC.parent

# coaching subpages highlight the "Coaching" top-level menu link
ACTIVE = {
    "coaching-kinder.html": "coaching-kinder.html",
    "coaching-eltern.html": "coaching-kinder.html",
    "coaching-paare.html": "coaching-kinder.html",
    "coaching-erwachsene.html": "coaching-kinder.html",
    "so-arbeite-ich.html": "so-arbeite-ich.html",
    "kurse.html": "kurse.html",
    "ueber-mich.html": "ueber-mich.html",
    "kontakt.html": "kontakt.html",
}


def build():
    shell = (SRC / "shell.html").read_text()
    extra = SRC / "extra.css"
    if extra.exists():
        shell = shell.replace("</style>", extra.read_text() + "\n</style>", 1)
    head, rest = shell.split('<main id="top">', 1)
    _, foot = rest.split("</main>", 1)

    out_assets = OUT / "assets"
    out_assets.mkdir(exist_ok=True)
    assets = {}
    for f in sorted((SRC / "assets").iterdir()):
        m = re.fullmatch(r"img_(.+)\.(jpg|png)", f.name)
        if m:
            assets[m.group(1)] = f.name
            shutil.copy2(f, out_assets / f.name)

    def resolve(html, page):
        def rep(m):
            key = m.group(1)
            if key not in assets:
                raise SystemExit(f"{page}: no asset for __IMG_{key}__")
            return f"assets/{assets[key]}"
        html = re.sub(r"__IMG_([A-Za-z0-9-]+(?:_[A-Za-z0-9-]+)*)__", rep, html)
        left = re.findall(r"__[A-Z][A-Z_0-9]*__", html)
        if left:
            raise SystemExit(f"{page}: unresolved placeholders {left}")
        return html

    for frag in sorted((SRC / "pages").glob("*.html")):
        name = frag.name
        body = frag.read_text()
        tm = re.match(r"<!--TITLE:(.*?)-->\s*", body, re.S)
        title = tm.group(1) if tm else "Viktoria Langjahr"
        body = body[tm.end():] if tm else body

        h = head if name == "index.html" else head.replace('href="#top"', 'href="index.html"')
        page = h + '<main id="top">\n' + body.strip() + "\n</main>" + foot
        page = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", page, count=1)
        if name in ACTIVE:
            tgt = ACTIVE[name]
            page = page.replace(f'<a href="{tgt}">', f'<a class="active" href="{tgt}">', 1)

        (OUT / name).write_text(resolve(page, name))
        print(f"{name:28} {len(page) // 1024:>4} KB")


if __name__ == "__main__":
    build()
