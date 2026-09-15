#!/usr/bin/env python3
"""Build the preview site.

src/shell.html      head, styles, header, footer (taken from the homepage)
src/extra.css       additional component styles
src/fonts/          self-hosted woff2 files + fonts.css
src/pages/*.html    page bodies (<main> content); first line <!--TITLE:...-->
src/assets/img_*.*  source images, referenced in pages as __IMG_<key>__

Output (repo root): one HTML file per page, assets/site.css (shared, cached),
fonts/, and responsive WebP images in assets/.
"""
import hashlib
import pathlib
import re
import shutil

from PIL import Image

SRC = pathlib.Path(__file__).resolve().parent
OUT = SRC.parent
SITE_URL = "https://ihor-pysak.github.io/vl-vorschau/"

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

DESCRIPTIONS = {
    "index.html": "Psychoemotionale Begleitung für Kinder, Jugendliche und Erwachsene: Viktoria Langjahr hilft bei Ängsten, Stress und emotionalen Belastungen – vor Ort und online.",
    "coaching-kinder.html": "Coaching für Kinder & Jugendliche: spielerisch mit Bildern, Gefühlen und Vorstellungskraft bei Ängsten, starken Emotionen und Schulproblemen.",
    "coaching-eltern.html": "Coaching für Eltern: Wenn dein Kind keine Hilfe möchte, beginnen wir bei dir – für mehr Ruhe, Sicherheit und Verbindung in der Familie.",
    "coaching-paare.html": "Paar-Coaching: verstehen, was hinter euren Konflikten liegt – für wieder mehr Nähe, Verständnis und Verbindung. Kostenloses Erstgespräch.",
    "coaching-erwachsene.html": "Coaching für Erwachsene bei Ängsten, Panik, innerer Unruhe und Selbstzweifeln – wir verändern dein emotionales Erleben.",
    "so-arbeite-ich.html": "So arbeite ich: psychoemotionale Begleitung mit Visualisierung und Somax – Ablauf, Sitzungen, Ergebnisse und Kosten auf einen Blick.",
    "kurse.html": "Kurse & Programme: Minikurs und SOS-Elternkurs für Eltern, 1:1-Begleitung „Meine Erfolgsgeschichte“ und Ausbildung in der Akademie.",
    "ueber-mich.html": "Über Viktoria Langjahr: Studium der Sozialen Arbeit, eigene Praxis seit 2018, Akademie seit 2024 – Begleitung auf Deutsch und Russisch.",
    "kontakt.html": "Kontakt zu Viktoria Langjahr: kostenloses Erstgespräch vereinbaren, Termin buchen oder per WhatsApp, Telefon und E-Mail schreiben.",
}

IMG_SIZES = "(max-width: 900px) 92vw, 560px"
LOGO_W = 280


def minify_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};])\s*", r"\1", css)
    return css.replace(";}", "}").strip()


def build_images(out_assets):
    """Write WebP variants; return {key: info} for <img> rewriting."""
    info = {}
    for f in sorted((SRC / "assets").iterdir()):
        m = re.fullmatch(r"img_(.+)\.(jpg|png)", f.name)
        if not m:
            continue
        key, ext = m.groups()
        im = Image.open(f)
        w, h = im.size
        if ext == "png":  # logos (transparent)
            lh = round(LOGO_W * h / w)
            name = f"img_{key}-{LOGO_W}.webp"
            im.convert("RGBA").resize((LOGO_W, lh), Image.LANCZOS).save(out_assets / name, "WEBP", quality=90)
            info[key] = {"logo": True, "src": name, "w": LOGO_W, "h": lh}
            continue
        im = im.convert("RGB")
        widths = sorted({min(640, w), min(1100, w)})
        variants = []
        for vw in widths:
            vh = round(vw * h / w)
            name = f"img_{key}-{vw}.webp"
            im.resize((vw, vh), Image.LANCZOS).save(out_assets / name, "WEBP", quality=78, method=6)
            variants.append((vw, name))
        info[key] = {"logo": False, "variants": variants, "w": w, "h": h}
    return info


def make_icons(out_assets, logo_png, hero_jpg):
    """Favicon + touch icon from the wing in the logo; OG image from the hero photo."""
    logo = Image.open(logo_png).convert("RGBA")
    w, h = logo.size
    left = logo.crop((0, 0, int(w * 0.42), h))
    px = left.load()
    # copy only light, saturated wing feathers; the dark wordmark next to the wing is dropped
    mask_img = Image.new("RGBA", left.size, (0, 0, 0, 0))
    mpx = mask_img.load()
    xs, ys = [], []
    for y in range(left.height):
        for x in range(left.width):
            r, g, b, a = px[x, y]
            hi, lo = max(r, g, b), min(r, g, b)
            if a > 40 and hi > 120 and (hi - lo) / hi > 0.22:
                mpx[x, y] = (r, g, b, a)
                xs.append(x)
                ys.append(y)
    wing = mask_img.crop((min(xs), min(ys), max(xs) + 1, max(ys) + 1))
    side = int(max(wing.size) * 1.18)
    for size, name, bg in ((64, "favicon.png", (0, 0, 0, 0)), (180, "apple-touch-icon.png", (248, 245, 249, 255))):
        canvas = Image.new("RGBA", (side, side), bg)
        canvas.paste(wing, ((side - wing.width) // 2, (side - wing.height) // 2), wing)
        canvas.resize((size, size), Image.LANCZOS).save(out_assets / name)
    hero = Image.open(hero_jpg).convert("RGB")
    tw, th = 1200, 630
    scale = max(tw / hero.width, th / hero.height)
    hero = hero.resize((round(hero.width * scale), round(hero.height * scale)), Image.LANCZOS)
    top = int((hero.height - th) * 0.28)
    left_x = (hero.width - tw) // 2
    hero.crop((left_x, top, left_x + tw, top + th)).save(out_assets / "og.jpg", quality=82)


def rewrite_imgs(html, info):
    seen_main_img = False
    main_start = html.find('<main id="top">')

    def rep(m):
        nonlocal seen_main_img
        tag = m.group(0)
        sm = re.search(r'src="assets/img_([^"]+)\.(?:jpg|png)"', tag)
        if not sm or sm.group(1) not in info:
            return tag
        d = info[sm.group(1)]
        attrs = re.sub(r'\s*src="[^"]*"', "", tag[4:-1]).strip()
        if d["logo"]:
            in_header = m.start() < main_start
            load = 'fetchpriority="high"' if in_header else 'loading="lazy" decoding="async"'
            return f'<img src="assets/{d["src"]}" width="{d["w"]}" height="{d["h"]}" {load} {attrs}>'
        biggest = d["variants"][-1][1]
        srcset = ", ".join(f"assets/{n} {vw}w" for vw, n in d["variants"])
        in_main = m.start() > main_start
        if in_main and not seen_main_img:
            seen_main_img = True
            load = 'fetchpriority="high" decoding="async"'
        else:
            load = 'loading="lazy" decoding="async"'
        return (f'<img src="assets/{biggest}" srcset="{srcset}" sizes="{IMG_SIZES}" '
                f'width="{d["w"]}" height="{d["h"]}" {load} {attrs}>')

    return re.sub(r"<img\b[^>]*>", rep, html)


def build():
    shell = (SRC / "shell.html").read_text()

    # ---- shared stylesheet ----
    css = "".join(re.findall(r"<style>(.*?)</style>", shell, re.S))
    css += (SRC / "extra.css").read_text()
    css = (SRC / "fonts" / "fonts.css").read_text() + css
    css = minify_css(css)
    css_hash = hashlib.md5(css.encode()).hexdigest()[:8]

    out_assets = OUT / "assets"
    if out_assets.exists():
        shutil.rmtree(out_assets)
    out_assets.mkdir()
    (out_assets / "site.css").write_text(css)

    out_fonts = OUT / "fonts"
    out_fonts.mkdir(exist_ok=True)
    for f in (SRC / "fonts").glob("*.woff2"):
        shutil.copy2(f, out_fonts / f.name)

    info = build_images(out_assets)
    make_icons(out_assets, SRC / "assets" / "img_bf41d504.png", SRC / "assets" / "img_56a67b52.jpg")

    shell = re.sub(r"<style>.*?</style>\s*", "", shell, count=1, flags=re.S)
    head, rest = shell.split('<main id="top">', 1)
    _, foot = rest.split("</main>", 1)

    for frag in sorted((SRC / "pages").glob("*.html")):
        name = frag.name
        body = frag.read_text()
        tm = re.match(r"<!--TITLE:(.*?)-->\s*", body, re.S)
        title = tm.group(1) if tm else "Viktoria Langjahr"
        body = body[tm.end():] if tm else body
        desc = DESCRIPTIONS.get(name, DESCRIPTIONS["index.html"])

        head_assets = "\n".join([
            f'<meta name="description" content="{desc}">',
            '<meta name="theme-color" content="#F8F5F9">',
            '<meta property="og:type" content="website">',
            '<meta property="og:locale" content="de_DE">',
            f'<meta property="og:title" content="{title}">',
            f'<meta property="og:description" content="{desc}">',
            f'<meta property="og:image" content="{SITE_URL}assets/og.jpg">',
            f'<meta property="og:url" content="{SITE_URL}{"" if name == "index.html" else name}">',
            '<link rel="icon" href="assets/favicon.png" type="image/png">',
            '<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">',
            '<link rel="preload" href="fonts/Fraunces-latin.woff2" as="font" type="font/woff2" crossorigin>',
            '<link rel="preload" href="fonts/DMSans-latin.woff2" as="font" type="font/woff2" crossorigin>',
            f'<link rel="stylesheet" href="assets/site.css?v={css_hash}">',
        ])

        h = head if name == "index.html" else head.replace('href="#top"', 'href="index.html"')
        h = h.replace("<!--HEAD-ASSETS-->", head_assets)
        page = h + '<main id="top">\n' + body.strip() + "\n</main>" + foot
        page = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", page, count=1)
        if name in ACTIVE:
            tgt = ACTIVE[name]
            page = page.replace(f'<a href="{tgt}">', f'<a class="active" href="{tgt}">', 1)

        def resolve(mm):
            key = mm.group(1)
            src = next((SRC / "assets").glob(f"img_{key}.*"), None)
            if src is None:
                raise SystemExit(f"{name}: no asset for __IMG_{key}__")
            return f"assets/{src.name}"

        page = re.sub(r"__IMG_([A-Za-z0-9-]+)__", resolve, page)
        left = re.findall(r"__[A-Z][A-Z_0-9]*__", page)
        if left:
            raise SystemExit(f"{name}: unresolved placeholders {left}")
        page = rewrite_imgs(page, info)
        (OUT / name).write_text(page)
        print(f"{name:28} {len(page) // 1024:>4} KB")

    total = sum(f.stat().st_size for f in out_assets.iterdir())
    print(f"assets/ {total // 1024} KB  (site.css {len(css) // 1024} KB, v={css_hash})")


if __name__ == "__main__":
    build()
