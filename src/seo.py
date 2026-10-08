"""Search-engine and AI metadata for the preview pages.

Everything here is derived from facts that are visible on the site (or on her
public Google profile): business data, services and prices, FAQ answers and
videos. FAQ and video data are read from the page HTML, so the structured data
stays in sync with the visible content.
"""
import html
import json
import pathlib
import re

SRC = pathlib.Path(__file__).resolve().parent

# The preview must not compete with viktoria-langjahr.de in search results.
PREVIEW = True

GOOGLE_MAPS = "https://www.google.com/maps?cid=14350894553348031286"
# her YouTube channel is a mixed personal channel and is deliberately not linked
SAME_AS = [
    GOOGLE_MAPS,
    "https://www.instagram.com/viktorialangjahr/",
    "https://www.facebook.com/viktorialangjahrcoaching/",
]
PHONE = "+49 1577 4277896"
EMAIL = "viktorialangjahr@gmx.de"
WEBSITE = "https://viktoria-langjahr.de/"

TITLES = {
    "index.html": "Psychoemotionale Praxis in Olpe – Viktoria Langjahr",
    "coaching-kinder.html": "Coaching für Kinder & Jugendliche in Olpe – Viktoria Langjahr",
    "coaching-eltern.html": "Coaching für Eltern in Olpe & online – Viktoria Langjahr",
    "coaching-paare.html": "Coaching für Paare in Olpe & online – Viktoria Langjahr",
    "coaching-erwachsene.html": "Coaching für Erwachsene in Olpe & online – Viktoria Langjahr",
    "so-arbeite-ich.html": "So arbeite ich: Methode, Ablauf & Kosten – Viktoria Langjahr",
    "kurse.html": "Kurse für Eltern & Fachkräfte – Viktoria Langjahr",
    "ueber-mich.html": "Über mich – Viktoria Langjahr, psychoemotionale Begleitung",
    "sos-elternkurs.html": "SOS-Elternkurs online: Kind bei Ängsten begleiten",
    "akademie.html": "Akademie für psycho-emotionale Lösungen – Zertifikatskurs",
    "kontakt.html": "Kontakt & Erstgespräch – Viktoria Langjahr, Olpe",
}

DESCRIPTIONS = {
    "index.html": "Psychoemotionale Begleitung für Kinder, Jugendliche, Eltern, Paare und Erwachsene bei Ängsten, Stress und emotionalen Belastungen – in Olpe und online.",
    "coaching-kinder.html": "Ängste, starke Gefühle, Schulprobleme? Spielerisches Coaching für Kinder & Jugendliche mit Bildern und Vorstellungskraft – in Olpe und online.",
    "coaching-eltern.html": "Wenn dein Kind keine Hilfe möchte, beginnen wir bei dir: Coaching für Eltern für mehr Ruhe, Sicherheit und Verbindung in der Familie – in Olpe & online.",
    "coaching-paare.html": "Paar-Coaching: verstehen, was hinter euren Konflikten liegt, und wieder zueinanderfinden – für mehr Nähe und Verständnis. In Olpe und online.",
    "coaching-erwachsene.html": "Coaching für Erwachsene bei Ängsten, Panik, innerer Unruhe und Selbstzweifeln: Wir verändern, wie du Belastendes innerlich erlebst. In Olpe & online.",
    "so-arbeite-ich.html": "Psychoemotionale Begleitung mit Visualisierung und Chirotrance: Ablauf, Anzahl der Sitzungen, Kosten pro 90-Minuten-Sitzung und Infos zur Krankenkasse.",
    "kurse.html": "Minikurs und SOS-Elternkurs für Eltern, 1:1-Begleitung „Meine Erfolgsgeschichte“ und Zertifikatskurs der Akademie für psycho-emotionale Lösungen.",
    "ueber-mich.html": "Viktoria Langjahr: Studium der Sozialen Arbeit & Sozialpädagogik, eigene Praxis seit 2018, Akademie seit 2024. Begleitung auf Deutsch und Russisch.",
    "sos-elternkurs.html": "Online-Kurs für Eltern: In 4 Wochen lernst du, dein Kind bei Ängsten und starken Emotionen zu verstehen und sicher zu begleiten. Ab 299 €.",
    "akademie.html": "4-monatiger Online-Zertifikatskurs in psycho-emotionaler, lösungsorientierter Kurzzeitbegleitung für Coaches, Berater, Pädagogen und Psychologen.",
    "kontakt.html": "Erstgespräch vereinbaren: unverbindlich, ca. 15 Minuten, telefonisch oder online. Am schnellsten per WhatsApp – oder per E-Mail.",
}

# breadcrumb names (Startseite is always first)
CRUMBS = {
    "coaching-kinder.html": [("coaching-kinder.html", "Coaching für Kinder & Jugendliche")],
    "coaching-eltern.html": [("coaching-eltern.html", "Coaching für Eltern")],
    "coaching-paare.html": [("coaching-paare.html", "Coaching für Paare")],
    "coaching-erwachsene.html": [("coaching-erwachsene.html", "Coaching für Erwachsene")],
    "so-arbeite-ich.html": [("so-arbeite-ich.html", "So arbeite ich")],
    "kurse.html": [("kurse.html", "Kurse & Programme")],
    "ueber-mich.html": [("ueber-mich.html", "Über mich")],
    "kontakt.html": [("kontakt.html", "Kontakt")],
    "sos-elternkurs.html": [("kurse.html", "Kurse & Programme"), ("sos-elternkurs.html", "SOS-Elternkurs")],
    "akademie.html": [("kurse.html", "Kurse & Programme"), ("akademie.html", "Akademie")],
}

SESSION_PRICE = {"Kinder und Jugendliche": 400, "Erwachsene": 490}

SERVICES = {
    "coaching-kinder.html": ("Coaching für Kinder & Jugendliche", "Kinder und Jugendliche", 400),
    "coaching-eltern.html": ("Coaching für Eltern", "Eltern", None),
    "coaching-paare.html": ("Coaching für Paare", "Paare", None),
    "coaching-erwachsene.html": ("Coaching für Erwachsene", "Erwachsene", 490),
}


def _clean(fragment):
    fragment = re.sub(r"<svg\b.*?</svg>", "", fragment, flags=re.S)
    fragment = re.sub(r"<br\s*/?>|</p>\s*<p[^>]*>", " ", fragment)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def _iso_duration(seconds):
    m, s = divmod(int(seconds), 60)
    return f"PT{m}M{s}S" if m else f"PT{s}S"


def _session_offer(price, audience):
    return {
        "@type": "Offer",
        "name": f"Sitzung für {audience} (90 Minuten)",
        "priceSpecification": {
            "@type": "UnitPriceSpecification",
            "price": price,
            "priceCurrency": "EUR",
            "referenceQuantity": {"@type": "QuantitativeValue", "value": 90, "unitCode": "MIN"},
        },
    }


class Site:
    def __init__(self, base):
        self.base = base
        self.biz = base + "#business"
        self.person = base + "#viktoria"
        self.website = base + "#website"
        self.videos = json.loads((SRC / "videos.json").read_text())

    def url(self, name):
        return self.base if name == "index.html" else self.base + name

    # ---- shared entities -------------------------------------------------
    def business(self):
        return {
            "@type": "ProfessionalService",
            "@id": self.biz,
            "name": "Psychoemotionale Praxis für Kinder & Erwachsene – Viktoria Langjahr",
            "alternateName": ["Viktoria Langjahr Coaching", "Viktoria Langjahr"],
            "description": DESCRIPTIONS["index.html"],
            "url": WEBSITE,
            "image": self.base + "assets/og.jpg",
            "logo": self.base + "assets/img_bf41d504-280.webp",
            "telephone": PHONE,
            "email": EMAIL,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Rhoder Weg 4",
                "postalCode": "57462",
                "addressLocality": "Olpe",
                "addressRegion": "Nordrhein-Westfalen",
                "addressCountry": "DE",
            },
            "geo": {"@type": "GeoCoordinates", "latitude": 51.0362173, "longitude": 7.8517374},
            "hasMap": GOOGLE_MAPS,
            "areaServed": [
                {"@type": "City", "name": "Olpe"},
                {"@type": "AdministrativeArea", "name": "Kreis Olpe"},
                {"@type": "Country", "name": "Deutschland"},
            ],
            "contactPoint": {"@type": "ContactPoint", "contactType": "Erstgespräch & Terminvereinbarung",
                             "telephone": PHONE, "email": EMAIL, "availableLanguage": ["de", "ru"],
                             "url": "https://wa.me/4915774277896"},
            "priceRange": "400–490 € pro Sitzung",
            "founder": {"@id": self.person},
            "sameAs": SAME_AS,
            "knowsAbout": [
                "Psychoemotionale Begleitung", "Ängste bei Kindern und Jugendlichen", "Panik und innere Unruhe",
                "Starke Emotionen", "Psychosomatische Beschwerden", "Elternbegleitung", "Paarbegleitung",
                "Visualisierung", "Chirotrance",
            ],
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": "Angebote",
                "itemListElement": [
                    {"@type": "Offer", "itemOffered": {"@id": self.url(p) + "#service"}} for p in SERVICES
                ] + [
                    {"@type": "Offer", "itemOffered": {"@id": self.url("sos-elternkurs.html") + "#course"}},
                    {"@type": "Offer", "itemOffered": {"@id": self.url("akademie.html") + "#course"}},
                ],
            },
        }

    def person_entity(self):
        return {
            "@type": "Person",
            "@id": self.person,
            "name": "Viktoria Langjahr",
            "jobTitle": "Coach für psychoemotionale Begleitung",
            "description": "Psychoemotionale Begleitung für Kinder, Jugendliche, Eltern, Paare und Erwachsene. "
                           "Studium der Sozialen Arbeit & Sozialpädagogik, eigene Praxis seit 2018, Akademie seit 2024.",
            "image": self.base + "assets/og.jpg",
            "url": self.url("ueber-mich.html"),
            "knowsLanguage": ["de", "ru"],
            "worksFor": {"@id": self.biz},
            "sameAs": SAME_AS[1:],
        }

    def website_entity(self):
        return {
            "@type": "WebSite",
            "@id": self.website,
            "url": self.base,
            "name": "Viktoria Langjahr",
            "inLanguage": "de-DE",
            "publisher": {"@id": self.biz},
        }

    # ---- per-page entities -----------------------------------------------
    def faq(self, name, body):
        qa = re.findall(r"<summary>(.*?)</summary>\s*<div class=\"ans\">(.*?)</div>\s*</details>", body, re.S)
        if not qa:
            return None
        return {
            "@type": "FAQPage",
            "@id": self.url(name) + "#faq",
            "mainEntity": [
                {"@type": "Question", "name": _clean(q),
                 "acceptedAnswer": {"@type": "Answer", "text": _clean(a)}} for q, a in qa
            ],
        }

    def video_objects(self, name, page_html):
        out = []
        for m in re.finditer(r'<button class="video-poster[^"]*"[^>]*data-video="([^"]+)"[^>]*aria-label="([^"]+)"[^>]*>(.*?)</button>'
                             r'(?:\s*<figcaption><b>(.*?)</b>)?', page_html, re.S):
            vid, label, inner, caption = m.groups()
            meta = self.videos.get(vid)
            if not meta:
                raise SystemExit(f"{name}: no metadata for video {vid} in src/videos.json")
            label = html.unescape(label).replace("Video abspielen: ", "")
            label = re.sub(r"\s*\(\d+:\d\d\)$", "", label)
            img = re.search(r'src="([^"]+)"', inner)
            thumbs = ([self.base + img.group(1)] if img else []) + [f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"]
            out.append({
                "@type": "VideoObject",
                "@id": f"{self.url(name)}#video-{vid}",
                "name": html.unescape(caption) if caption else label,
                "description": label,
                "thumbnailUrl": thumbs,
                "uploadDate": meta["uploadDate"],
                "duration": _iso_duration(meta["seconds"]),
                "embedUrl": f"https://www.youtube-nocookie.com/embed/{vid}",
                "url": f"https://www.youtube.com/watch?v={vid}",
                "inLanguage": "de",
                "publisher": {"@id": self.biz},
            })
        return out

    def service(self, name):
        title, audience, price = SERVICES[name]
        s = {
            "@type": "Service",
            "@id": self.url(name) + "#service",
            "name": title,
            "serviceType": "Psychoemotionale Begleitung (Coaching)",
            "description": DESCRIPTIONS[name],
            "url": self.url(name),
            "provider": {"@id": self.biz},
            "areaServed": [{"@type": "City", "name": "Olpe"}, {"@type": "Country", "name": "Deutschland"}],
            "audience": {"@type": "PeopleAudience", "audienceType": audience},
            "availableChannel": {"@type": "ServiceChannel", "name": "Vor Ort in Olpe oder online",
                                 "servicePhone": PHONE, "serviceUrl": self.url("kontakt.html"),
                                 "availableLanguage": ["de", "ru"]},
        }
        if price:
            s["offers"] = _session_offer(price, audience)
        return s

    def courses(self, name):
        provider = {"@id": self.biz}
        if name == "sos-elternkurs.html":
            return [{
                "@type": "Course",
                "@id": self.url(name) + "#course",
                "name": "SOS-Elternkurs",
                "description": DESCRIPTIONS[name],
                "url": self.url(name),
                "provider": provider,
                "inLanguage": "de",
                "audience": {"@type": "Audience", "audienceType": "Eltern und Pädagogen"},
                "timeRequired": "P4W",
                "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "online",
                                      "instructor": {"@id": self.person}},
                "offers": [
                    {"@type": "Offer", "name": "SOS-Elternkurs", "price": 299, "priceCurrency": "EUR", "category": "Paid"},
                    {"@type": "Offer", "name": "SOS-Elternkurs PLUS", "price": 380, "priceCurrency": "EUR", "category": "Paid"},
                ],
            }]
        if name == "akademie.html":
            return [{
                "@type": "Course",
                "@id": self.url(name) + "#course",
                "name": "Zertifikatskurs: Psycho-emotionale lösungsorientierte Kurzzeitbegleitung",
                "description": DESCRIPTIONS[name],
                "url": self.url(name),
                "provider": {"@type": "EducationalOrganization", "name": "Akademie für psycho-emotionale Lösungen",
                             "founder": {"@id": self.person}, "parentOrganization": {"@id": self.biz}},
                "inLanguage": "de",
                "audience": {"@type": "Audience", "audienceType": "Heilpraktiker für Psychotherapie, Pädagogen, Berater, Psychologen, Coaches"},
                "timeRequired": "P4M",
                "educationalCredentialAwarded": "Abschlusszertifikat der Akademie (keine staatlich anerkannte Ausbildung)",
                "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "online",
                                      "instructor": {"@id": self.person}},
            }]
        if name == "kurse.html":
            return [{
                "@type": "Course",
                "@id": self.url(name) + "#minikurs",
                "name": "Minikurs: Gelassen durch Kindersorgen",
                "description": "Online-Minikurs für Eltern, die sich Sorgen um ihr Kind machen: Sorgen verstehen, innere Sicherheit gewinnen und gelassener werden.",
                "url": self.url(name),
                "provider": provider,
                "inLanguage": "de",
                "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "online"},
                "offers": {"@type": "Offer", "price": 9.90, "priceCurrency": "EUR", "category": "Paid"},
            }]
        return []

    def breadcrumb(self, name):
        if name not in CRUMBS:
            return None
        items = [("index.html", "Startseite")] + CRUMBS[name]
        return {
            "@type": "BreadcrumbList",
            "@id": self.url(name) + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n, "item": self.url(p)}
                for i, (p, n) in enumerate(items)
            ],
        }

    def graph(self, name, page_html):
        page_type = {"kontakt.html": "ContactPage", "ueber-mich.html": "ProfilePage"}.get(name, "WebPage")
        webpage = {
            "@type": page_type,
            "@id": self.url(name) + "#webpage",
            "url": self.url(name),
            "name": TITLES[name],
            "description": DESCRIPTIONS[name],
            "inLanguage": "de-DE",
            "isPartOf": {"@id": self.website},
            "about": {"@id": self.person if name == "ueber-mich.html" else self.biz},
        }
        if name == "ueber-mich.html":
            webpage["mainEntity"] = {"@id": self.person}
        nodes = [webpage, self.business(), self.person_entity(), self.website_entity()]
        crumb = self.breadcrumb(name)
        if crumb:
            webpage["breadcrumb"] = {"@id": crumb["@id"]}
            nodes.append(crumb)
        if name in SERVICES:
            nodes.append(self.service(name))
        nodes += self.courses(name)
        faq = self.faq(name, page_html)
        if faq:
            nodes.append(faq)
        vids = self.video_objects(name, page_html)
        if vids:
            webpage["video"] = [{"@id": v["@id"]} for v in vids]
            nodes += vids
        data = {"@context": "https://schema.org", "@graph": nodes}
        js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        return f'<script type="application/ld+json">{js}</script>'

    # ---- llms.txt ----------------------------------------------------------
    def llms_txt(self):
        p = self.url
        return f"""# Psychoemotionale Praxis für Kinder & Erwachsene – Viktoria Langjahr

> Psychoemotionale Begleitung (Coaching) für Kinder, Jugendliche, Eltern, Paare und Erwachsene bei Ängsten, Panik, innerer Unruhe, starken Emotionen, Schulproblemen und psychosomatischen Beschwerden. Praxis in Olpe (Rhoder Weg 4, 57462 Olpe, NRW) und online. Begleitung auf Deutsch und Russisch. 5,0 Sterne bei Google (88 Bewertungen, Stand Oktober 2026).

## Wichtige Fakten

- Ansatz: Arbeit am emotionalen Erleben statt nur am Verstehen – mit Visualisierung (Bilder und Vorstellungskraft) und Chirotrance (nonverbal).
- Sitzungen: 90 Minuten, vor Ort in Olpe oder online. Kinder & Jugendliche 400 € pro Sitzung, Erwachsene 490 € pro Sitzung.
- Dauer: meist wenige Sitzungen – bei Kindern häufig 2–4, bei Erwachsenen häufig 3–6.
- Krankenkasse: keine Kassenleistung, private Zahlung; dafür keine Wartezeit auf einen Therapieplatz und keine Diagnose an die Krankenkasse.
- Erstgespräch: unverbindlich, ca. 15 Minuten, telefonisch oder online.
- Online-Coaching für Kinder in der Regel ab etwa 7–8 Jahren.
- Das Coaching ersetzt keine notwendige medizinische oder psychotherapeutische Behandlung.
- Qualifikation: Studium der Sozialen Arbeit & Sozialpädagogik, eigene Praxis seit 2018, Akademie seit 2024.

## Kontakt

- WhatsApp (am schnellsten): https://wa.me/4915774277896
- Telefon: {PHONE}
- E-Mail: {EMAIL}
- Google-Profil: {GOOGLE_MAPS}

## Seiten

- [Startseite]({p("index.html")}): Überblick, Video-Erfahrungen und Google-Bewertungen
- [Coaching für Kinder & Jugendliche]({p("coaching-kinder.html")}): Ängste, starke Gefühle, Schule, psychosomatische Beschwerden
- [Coaching für Eltern]({p("coaching-eltern.html")}): wenn das Kind keine Hilfe möchte, beginnt die Arbeit bei den Eltern
- [Coaching für Paare]({p("coaching-paare.html")}): Konflikte verstehen und wieder zueinanderfinden
- [Coaching für Erwachsene]({p("coaching-erwachsene.html")}): Ängste, Panik, innere Unruhe, Selbstzweifel
- [So arbeite ich]({p("so-arbeite-ich.html")}): Methode, Ablauf, Kosten, Krankenkasse
- [Kurse & Programme]({p("kurse.html")}): Minikurs (9,90 €), SOS-Elternkurs, 1:1-Begleitung, Akademie
- [SOS-Elternkurs]({p("sos-elternkurs.html")}): 4 Wochen online, 299 € bzw. PLUS 380 €, Geld-zurück-Garantie nach den ersten 2 Einheiten
- [Akademie]({p("akademie.html")}): 4-monatiger Online-Zertifikatskurs für Fachpersonen; Starttermin und Preis auf Anfrage
- [Über mich]({p("ueber-mich.html")}): Werdegang von Viktoria Langjahr
- [Kontakt]({p("kontakt.html")}): Erstgespräch vereinbaren, Termin buchen
"""
