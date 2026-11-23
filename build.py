#!/usr/bin/env python3
"""SolutionHub static site generator.

Builds every page from one template so the header, footer, SEO tags and
design stay identical everywhere. Run: python3 build.py
Output: the repo root (index.html, guides/*.html, legal pages, sitemap,
robots.txt, ads.txt, 404.html, vercel.json) plus assets/style.css.

CSS IS SINGLE-SOURCED: the stylesheet lives ONLY as the CSS string in this
file. build.py writes it to assets/style.css on every run — never hand-edit
assets/style.css, your edit will be overwritten. The same goes for every
generated HTML file: edit build.py / guides_content.py, then re-run build.py.
"""
import html
import json
import os
import re
import sys
from datetime import date

from guides_content import GUIDES

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://solutionhub-two.vercel.app"
SITE_NAME = "SolutionHub"
ADS_TXT_LINE = "google.com, pub-2231619318636842, DIRECT, f08c47fec0942fa"

TOOLS = {
    "pdf": ("PDF Tools Hub", "https://pdf-tools-hub-nine-lac.vercel.app"),
    "ai": ("AI Studio", "https://ai-studio-sandy-sigma.vercel.app"),
    "clipper": ("AI Video Clipper", "https://ai-video-clipper-dipeshkarki8292-3476s-projects.vercel.app"),
    "leads": ("LeadsForceGen", "https://leadsforcegen.vercel.app"),
    "sah": ("Student Assignment Helper", "https://student-assignment-helper.vercel.app"),
}
# Deep links are per guide (g["tool_url"]); TOOLS holds the fallback homepage.
BUILD_DATE = "2026-11-23"  # dateModified for pages rebuilt by this run

CSS = """/* SolutionHub — repair-manual / workshop-notebook design.
   Single source of truth: this string in build.py generates assets/style.css.
   No frameworks, no webfonts, no JS. Paper + ink + teal + gold.
   Type: serif display (guide titles), system sans (labels/UI), mono
   (step numbers, stamps, kickers). No gradients, no glass, no card grid. */
:root{
  --paper:#fbf7ec; --bg:#fffdf6; --ink:#2a251c; --muted:#6d6353;
  --line:#ddd3bd; --line-soft:#e9e1cd;
  --accent:#0f766e; --accent-dark:#0b5d57; --gold:#b45309; --gold-soft:#fdf3e0;
  --serif:Georgia,"Noto Serif","Times New Roman",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,"SF Mono","DejaVu Sans Mono",Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
html{font-size:16px}
body{margin:0;font-family:var(--sans);color:var(--ink);background:var(--paper);line-height:1.65}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
:focus-visible{outline:3px solid var(--gold);outline-offset:2px;border-radius:2px}
.skip{position:absolute;left:-9999px;top:0;background:var(--ink);color:#fff;padding:10px 16px;font-weight:700;z-index:20}
.skip:focus{left:8px;top:8px;color:#fff}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
.prose{max-width:760px}
.manual{max-width:860px}
header.site{border-bottom:2px solid var(--ink);background:var(--bg);position:sticky;top:0;z-index:10}
.nav{display:flex;align-items:center;gap:18px;min-height:60px;flex-wrap:wrap;padding-top:8px;padding-bottom:8px}
.brand{font-family:var(--serif);font-size:1.4rem;font-weight:700;color:var(--ink);letter-spacing:-.01em}
.brand span{color:var(--accent)}
.brand .rule{display:inline-block;width:26px;border-bottom:3px solid var(--gold);margin-left:2px;vertical-align:baseline}
nav.main{display:flex;gap:16px;margin-left:auto;flex-wrap:wrap}
nav.main a{color:var(--ink);font-weight:600;font-size:.95rem}
nav.main a:hover{color:var(--accent)}
main{padding:32px 0 56px}
h1{font-family:var(--serif);font-size:2rem;line-height:1.25;letter-spacing:-.01em;margin:0 0 14px}
h2{font-family:var(--serif);font-size:1.4rem;margin:34px 0 10px;letter-spacing:-.01em}
h3{font-size:1.1rem;margin:24px 0 8px}
p{margin:0 0 14px}
.lede{font-size:1.12rem;color:var(--muted)}
ul,ol{margin:0 0 16px;padding-left:24px}
li{margin-bottom:6px}
.kicker{font-family:var(--mono);font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);margin:0 0 10px}
.btn{display:inline-block;background:var(--accent);color:#fff;font-family:var(--sans);font-weight:700;padding:11px 22px;border-radius:8px}
.btn:hover{background:var(--accent-dark);text-decoration:none}
/* --- manual cover (home) --- */
.cover{border-top:4px solid var(--ink);border-bottom:1px solid var(--ink);padding:28px 0 24px;margin-bottom:8px}
.cover h1{font-size:2.4rem;margin-bottom:10px}
.cover .lede{max-width:640px}
.cover .colophon{font-family:var(--mono);font-size:.8rem;color:var(--muted);margin:18px 0 0}
.start-here{border:1px solid var(--line);border-left:4px solid var(--gold);background:var(--bg);padding:18px 20px;margin:26px 0}
.start-here h2{margin:0 0 6px}
.start-here ol{margin:8px 0 0}
.start-here li{margin-bottom:8px}
/* --- contents index: numbered ledger rows, grouped by problem --- */
.contents{list-style:none;margin:18px 0 8px;padding:0;counter-reset:entry}
.contents li.entry{display:flex;gap:14px;align-items:baseline;padding:13px 2px;border-bottom:1px dotted var(--line)}
.contents li.entry .no{font-family:var(--mono);font-size:.85rem;color:var(--gold);min-width:2ch}
.contents li.entry h3{margin:0;font-family:var(--serif);font-size:1.15rem;font-weight:700}
.contents li.entry h3 a{color:var(--ink)}
.contents li.entry h3 a:hover{color:var(--accent)}
.contents li.entry p{color:var(--muted);font-size:.95rem;margin:2px 0 0}
.contents li.entry .tag{margin-left:auto;flex:none}
.group-head{font-family:var(--mono);font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:30px 0 0;padding-bottom:6px;border-bottom:2px solid var(--ink)}
/* --- guides index search: plain filter, no backend --- */
.guide-search{margin:22px 0 4px}
.guide-search label{display:block;font-family:var(--mono);font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}
.guide-search input{width:100%;max-width:560px;padding:11px 14px;font:inherit;font-size:1rem;color:var(--ink);background:var(--bg);border:2px solid var(--ink);border-radius:2px}
.guide-search input::placeholder{color:var(--muted)}
.guide-count{font-family:var(--mono);font-size:.8rem;color:var(--muted);margin:8px 0 0}
.guide-empty{margin:24px 0;padding:14px 16px;border:2px solid var(--gold);background:var(--gold-soft);font-weight:600}
.tag{display:inline-block;font-family:var(--mono);font-size:.72rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);background:#e6f4f2;border:1px solid #c9e8e4;border-radius:999px;padding:3px 10px}
/* --- guide pages: step ledger, checklist, margin notes --- */
.guide-meta{font-family:var(--mono);font-size:.8rem;color:var(--muted);margin:0 0 20px;padding-bottom:12px;border-bottom:1px solid var(--line)}
h2.step{margin-top:30px}
h2.step .step-no{display:inline-block;font-family:var(--mono);font-size:.85rem;font-weight:700;color:var(--gold);border:2px solid var(--gold);border-radius:4px;padding:1px 8px;margin-right:10px;vertical-align:2px}
h2.needs + ul{list-style:none;padding-left:0}
h2.needs + ul li{position:relative;padding-left:30px;margin-bottom:8px}
h2.needs + ul li::before{content:"";position:absolute;left:2px;top:5px;width:14px;height:14px;border:2px solid var(--gold);border-radius:2px;background:var(--bg)}
.note{background:var(--gold-soft);border:1px solid #f0d9a8;border-left:4px solid var(--gold);border-radius:0 6px 6px 0;padding:14px 16px;margin:20px 0}
.note::before{content:"Margin note";display:block;font-family:var(--mono);font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-bottom:4px}
.note p{margin:0}
.see-also{font-size:.95rem;border-top:1px solid var(--line-soft);padding-top:12px}
.toolbox{border:1px solid #c9e8e4;background:#effaf8;border-radius:12px;padding:18px 20px;margin:26px 0}
.toolbox h2{margin-top:0}
.faq h3{margin-top:18px}
/* --- Tested stamp: evidence of human testing, per guide --- */
.tested{border:2px solid var(--gold);outline:1px solid var(--gold);outline-offset:4px;border-radius:4px;background:var(--bg);padding:16px 18px;margin:24px 0;transform:rotate(-.5deg)}
.tested .stamp-head{font-family:var(--mono);font-size:.8rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);margin:0 0 8px}
.tested dl{margin:0;display:grid;grid-template-columns:auto 1fr;gap:2px 14px;font-size:.95rem}
.tested dt{font-family:var(--mono);font-size:.78rem;text-transform:uppercase;color:var(--muted);padding-top:2px}
.tested dd{margin:0}
.updates{border-top:2px solid var(--ink);margin-top:36px;padding-top:6px;font-size:.95rem}
.updates h2{font-size:1.15rem}
.prevnext{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;border-top:1px solid var(--line);margin-top:32px;padding-top:16px;font-size:.95rem}
.prevnext .next{text-align:right;margin-left:auto}
.related{margin-top:28px}
.related h2{font-size:1.15rem}
.related ul{margin:8px 0 0}
.breadcrumb{font-family:var(--mono);font-size:.82rem;color:var(--muted);margin-bottom:14px}
.breadcrumb a{color:var(--muted)}
footer.site{border-top:2px solid var(--ink);background:var(--bg);padding:28px 0;color:var(--muted);font-size:.92rem}
footer.site .cols{display:flex;gap:32px;flex-wrap:wrap;justify-content:space-between}
footer.site a{color:var(--muted)}
footer.site strong{color:var(--ink)}
footer.site .fine{margin-top:18px}
@media (min-width:641px) and (max-width:1024px){
  .cover h1{font-size:2.1rem}
  .contents li.entry .tag{display:none}
}
@media (max-width:640px){
  .cover h1{font-size:1.8rem}
  h1{font-size:1.55rem}
  nav.main{gap:12px}
  .tested{transform:none}
  .tested dl{grid-template-columns:1fr}
  .tested dt{padding-top:6px}
  .contents li.entry{flex-wrap:wrap}
  .contents li.entry .tag{margin-left:0}
}
@media (prefers-reduced-motion:reduce){
  .tested{transform:none}
}
@media print{
  header.site nav.main,.skip,.toolbox .btn,.prevnext,.guide-search{display:none}
  body{background:#fff}
  main{padding:0}
  a{color:var(--ink)}
}
"""

def esc(s):
    return html.escape(s, quote=True)

def human_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return date(y, m, d).strftime("%d %b %Y")

def ld_script(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, indent=2) + '\n</script>')

def page(title, description, body, path, canonical, json_ld=None, wide=False,
         og_type="website"):
    """Render one full HTML page. path is the output path relative to ROOT."""
    main_cls = "wrap manual" if wide else "wrap prose"
    ld = ("\n" + ld_script(json_ld)) if json_ld else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:site_name" content="SolutionHub">
<meta property="og:image" content="{SITE_URL}/assets/og.png">
<meta property="og:image:alt" content="SolutionHub — plain, practical how-to guides">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{SITE_URL}/assets/og.png">{ld}
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap nav">
<a class="brand" href="/">Solution<span>Hub</span><span class="rule" aria-hidden="true"></span></a>
<nav class="main" aria-label="Main navigation">
<a href="/">Home</a>
<a href="/guides/">Guides</a>
<a href="/about.html">About</a>
<a href="/contact.html">Contact</a>
</nav>
</div></header>
<main id="main"><div class="{main_cls}">
{body}
</div></main>
<footer class="site"><div class="wrap cols">
<div><strong>SolutionHub</strong><br>Plain, practical how-to guides.<br>Free tools, honest advice, no hype.</div>
<div><strong>Guides</strong><br><a href="/guides/">All guides</a><br><a href="/guides/edit-pdf-text.html">Edit PDF text</a><br><a href="/guides/find-business-leads-free.html">Find business leads</a><br><a href="/contact.html">Suggest a guide</a></div>
<div><strong>Site</strong><br><a href="/about.html">About</a><br><a href="/contact.html">Contact</a><br><a href="/privacy.html">Privacy Policy</a><br><a href="/terms.html">Terms of Use</a><br><a href="/disclaimer.html">Disclaimer</a><br><a href="/sitemap.xml">Sitemap</a></div>
</div><div class="wrap fine">&copy; 2026 SolutionHub. All guides are original work written by the SolutionHub team.</div></footer>
</body>
</html>
"""

def strip_tags(text):
    return html.unescape(re.sub(r"<[^>]+>", " ", text)).strip()

def extract_steps(body):
    """Step headings -> HowTo steps (name + short text from the heading)."""
    return [strip_tags(t) for t in
            re.findall(r"<h2>Step \d+: ([^<]+)</h2>", body)]

def extract_faq(body):
    """FAQ h3+p pairs inside the .faq div."""
    m = re.search(r'<div class="faq">(.*?)</div>\s*$', body, re.S)
    if not m:
        return []
    return [(strip_tags(q), strip_tags(a)) for q, a in
            re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", m.group(1), re.S)]

def guide_json_ld(g, canonical):
    steps = [{"@type": "HowToStep", "name": s, "text": s}
             for s in extract_steps(g["body"])]
    faq = [{"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}}
           for q, a in extract_faq(g["body"])]
    out = [{
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": g["title"],
        "description": g["description"],
        "datePublished": g.get("published", "2026-11-11"),
        "dateModified": g.get("modified", BUILD_DATE),
        "step": steps,
    }]
    if faq:
        out.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq,
        })
    return out

def reading_time(body):
    return max(1, round(word_count(body) / 200))

def guide_row(g, n):
    """One numbered ledger row in the manual's contents (home + /guides/).
    Category is shown once, as the group heading — not repeated per row."""
    return (f'<li class="entry"><span class="no">{n:02d}</span>'
            f'<div><h3><a href="/guides/{g["slug"]}.html">{esc(g["title"])}</a></h3>'
            f'<p>{esc(g["description"])}</p></div></li>')

def contents_by_category(guides, start=1):
    """Contents grouped by problem category, numbered continuously."""
    seen, out, n = {}, [], start
    for g in guides:
        if g["category"] not in seen:
            seen[g["category"]] = True
            out.append(f'<h2 class="group-head">{esc(g["category"])}</h2>'
                       '<ol class="contents">')
        out.append(guide_row(g, n))
        n += 1
        # close the list when the next guide changes category (or at the end)
        idx = guides.index(g)
        if idx == len(guides) - 1 or guides[idx + 1]["category"] != g["category"]:
            out.append("</ol>")
    return "\n".join(out)

def mark_steps(body):
    """Number the step ledger: <h2>Step N: …</h2> gets a mono step number;
    'What you need' gets the checklist class."""
    body = re.sub(r"<h2>Step (\d+): ([^<]+)</h2>",
                  r'<h2 class="step"><span class="step-no">\1</span> \2</h2>', body)
    return body.replace("<h2>What you need</h2>",
                        '<h2 class="needs">What you need</h2>')

def guide_page(g, guides):
    idx = guides.index(g)
    prev_g = guides[idx - 1] if idx > 0 else None
    next_g = guides[idx + 1] if idx < len(guides) - 1 else None
    # Related: an explicit list on the guide wins (used where the category
    # has only one guide and list order would pick unrelated ones); then
    # same category first, then the rest, up to 3.
    by_slug = {x["slug"]: x for x in guides}
    picked = [by_slug[s] for s in g.get("related", []) if s in by_slug and by_slug[s] is not g]
    rest = [x for x in guides if x is not g and x not in picked]
    same = [x for x in rest if x["category"] == g["category"]]
    other = [x for x in rest if x["category"] != g["category"]]
    related = (picked + same + other)[:3]
    tool_box = ""
    if g.get("tool"):
        tname, turl = TOOLS[g["tool"]]
        deep = g.get("tool_url") or turl
        tool_box = (f'<aside class="toolbox"><h2>Try the free tool</h2>'
                    f'<p>Do this right now with <strong>{esc(tname)}</strong> — '
                    f'free to try, no install needed.</p>'
                    f'<p><a class="btn" href="{esc(deep)}">Open {esc(tname)} &rarr;</a></p></aside>')
    elif g["slug"] == "check-link-safe":
        tool_box = ('<aside class="toolbox"><h2>No tool needed</h2>'
                    '<p>This guide needs nothing but your browser and thirty '
                    'seconds. The related guides below cover the other '
                    'everyday jobs on this site.</p></aside>')
    tested = (f'<aside class="tested" aria-label="Tested note">'
              f'<p class="stamp-head">Tested &mdash; {esc(g.get("tested_date", "11 Nov 2026"))}</p>'
              '<dl>'
              f'<dt>Tool</dt><dd>{esc(g.get("tested_tool", ""))}</dd>'
              f'<dt>Result</dt><dd>{esc(g.get("tested_result", ""))}</dd>'
              f'<dt>Limit</dt><dd>{esc(g.get("tested_limit", ""))}</dd>'
              '</dl></aside>')
    meta = (f'<p class="guide-meta">Published {human_date(g.get("published", "2026-11-11"))}'
            f' &middot; Updated {human_date(g.get("modified", BUILD_DATE))}'
            f' &middot; {reading_time(g["body"])} min read'
            f' &middot; {esc(g["category"])}</p>')
    prevnext = '<nav class="prevnext" aria-label="More guides">'
    if prev_g:
        prevnext += (f'<a href="/guides/{prev_g["slug"]}.html">&larr; {esc(prev_g["title"])}</a>')
    if next_g:
        prevnext += (f'<a class="next" href="/guides/{next_g["slug"]}.html">{esc(next_g["title"])} &rarr;</a>')
    prevnext += "</nav>"
    related_html = ('<section class="related"><h2>Related guides</h2><ul>'
                    + "".join(f'<li><a href="/guides/{r["slug"]}.html">{esc(r["title"])}</a></li>'
                              for r in related)
                    + "</ul></section>")
    updates = ('<section class="updates"><h2>Updates to this guide</h2>'
               f'<p>Published {human_date(g.get("published", "2026-11-11"))}. '
               'No corrections yet. If a step stops working the way it is '
               'described here, tell us through the '
               '<a href="/contact.html">contact page</a> and the fix will be '
               'noted here with its date.</p></section>')
    body = (f'<nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a> &rsaquo; '
            f'<a href="/guides/">Guides</a> &rsaquo; {esc(g["category"])}</nav>'
            f'<h1>{esc(g["title"])}</h1>'
            f'{meta}'
            f'<p class="lede">{esc(g["description"])}</p>'
            f'{tested}'
            f'{mark_steps(g["body"])}'
            f'{tool_box}'
            f'{related_html}'
            f'{updates}'
            f'{prevnext}'
            f'<p><a href="/guides/">&larr; Back to all guides</a></p>')
    canonical = f'{SITE_URL}/guides/{g["slug"]}.html'
    return page(f'{g["title"]} | SolutionHub', g["description"], body,
                f'guides/{g["slug"]}.html', canonical,
                json_ld=guide_json_ld(g, canonical), og_type="article")

# ---------------------------------------------------------------- static pages
START_HERE = ["edit-pdf-text", "merge-pdf-files", "long-video-to-shorts",
              "check-link-safe"]

def home_body(guides):
    n = len(guides)
    by_slug = {g["slug"]: g for g in guides}
    start_items = "".join(
        f'<li><a href="/guides/{s}.html">{esc(by_slug[s]["title"])}</a> — '
        f'{esc(by_slug[s]["description"])}</li>' for s in START_HERE)
    return f"""<section class="cover">
<p class="kicker">SolutionHub &middot; A repair manual for everyday digital jobs</p>
<h1>Solve it yourself, step by step.</h1>
<p class="lede">Plain, practical how-to guides for the problems that land at
11 pm: PDFs that will not behave, photos that need saving, audio full of
hiss, videos to cut down, leads to find, emails to answer, a CV to write,
an assignment to check, a link you are not sure about. No jargon, no hype,
no paid tricks. Just the steps that work — each one tested against the real
tool it recommends, with the test written on the page.</p>
<p class="colophon">{n} guides &middot; tested Nov 2026 &middot; no accounts,
no tracking, no ads yet</p>
</section>
<section class="start-here">
<h2>Start here</h2>
<p>New here? These four solve the problems people search for most. Read one,
do the steps, and you will know how the whole manual works.</p>
<ol>
{start_items}
</ol>
</section>
<h2>Contents, by problem</h2>
<p>Find your problem below and follow the steps. Every guide says what you
need first, then the steps in order, then what it cannot do — because an
honest limit saves you more time than a promise.</p>
{contents_by_category(guides)}
<h2>How SolutionHub works</h2>
<p>Every guide is written in original words by our team, tested against the
real tool it recommends, and kept short enough to finish in one sitting.
The test is stamped on each guide page — the date, the tool, what happened,
and one honest limit. Where a guide points to a free tool, that tool is one
we run ourselves —
<a href="https://pdf-tools-hub-nine-lac.vercel.app">PDF Tools Hub</a>,
<a href="https://ai-studio-sandy-sigma.vercel.app">AI Studio</a>,
<a href="https://ai-video-clipper-dipeshkarki8292-3476s-projects.vercel.app">AI Video Clipper</a>,
<a href="https://leadsforcegen.vercel.app">LeadsForceGen</a> and
<a href="https://student-assignment-helper.vercel.app">Student Assignment Helper</a>.
We never recommend a tool we have not used, and we say plainly when something
does not work yet. Found a step that is wrong? Tell us on the
<a href="/contact.html">contact page</a> — corrections are noted at the
bottom of the guide.</p>"""

ABOUT_BODY = """<h1>About SolutionHub</h1>
<p class="lede">SolutionHub is a small, independent how-to website. We write
practical guides that solve real problems — the kind you search for at
11 pm when something needs fixing now.</p>
<h2>What we do</h2>
<p>We publish step-by-step guides for everyday digital tasks: working with
PDFs, improving photos and audio, editing video, finding business leads,
writing better emails, building a CV, and staying safe online. Each guide
is written in our own words, in plain English, and tested against the tool
it recommends.</p>
<h2>What we do not do</h2>
<p>We do not copy content from other websites. We do not promise results we
cannot deliver. We do not guarantee earnings, rankings, or outcomes of any
kind. When a tool has a limit, we say so in the guide instead of hiding it.</p>
<h2>Who runs SolutionHub</h2>
<p>SolutionHub is run by Dipesh Karki, an independent maker from Nepal who
also builds the free tools our guides recommend: PDF Tools Hub, AI Studio,
AI Video Clipper and LeadsForceGen. The guides and the tools are made by the
same person, which is why the guides describe the tools honestly — limits
included.</p>
<h2>How the site is funded</h2>
<p>SolutionHub is free to read. In future, it may show advertisements
through Google AdSense, clearly marked as ads. Advertising never changes
what a guide says, and we never sell a guide placement to a tool.</p>
<p>Questions or corrections? See our <a href="/contact.html">contact page</a>.</p>"""

CONTACT_BODY = """<h1>Contact SolutionHub</h1>
<p class="lede">Found a mistake in a guide, have a problem you want us to
cover, or want to say hello? We read every message.</p>
<h2>Email</h2>
<p>The fastest way to reach us is email:
<a href="mailto:dipeshkarki8292@gmail.com">dipeshkarki8292@gmail.com</a>.
Please include the guide title and the step number if you are reporting an
error, so we can fix it quickly.</p>
<h2>What to expect</h2>
<p>We answer as soon as we can, usually within a few days. We cannot offer
one-to-one tech support for other people's products, and we cannot help with
account, password or payment issues for the tools — those go to the tool's
own support. But if a guide is wrong or out of date, tell us and we will
correct it.</p>
<h2>Correction policy</h2>
<p>If a guide is wrong, we fix it and note the change at the bottom of the
page. If a tool stops working the way a guide describes, we update the guide
to say so instead of deleting the warning.</p>"""

PRIVACY_BODY = """<h1>Privacy Policy</h1>
<p class="lede">Last updated: 11 November 2026. SolutionHub is a simple
reading website. We collect almost nothing.</p>
<h2>What we collect</h2>
<p><strong>We do not run accounts, logins, or sign-ups.</strong> You can read
every guide without giving us your name, email, or any personal information.</p>
<p>When you email us, we receive your email address and the contents of your
message. We use that only to reply to you. We do not sell, rent, or share
your email address with anyone.</p>
<h2>Cookies and analytics</h2>
<p>SolutionHub itself sets no tracking cookies. The site is hosted on Vercel,
which may collect basic, anonymised server logs (such as pages visited and
general location) to keep the site running securely. We do not use that data
to identify you.</p>
<h2>Third-party tools</h2>
<p>Our guides link to free tools we operate (PDF Tools Hub, AI Studio, AI
Video Clipper, LeadsForceGen). Those tools have their own privacy policies.
When you click a link and use a tool, that tool's policy applies. PDF Tools
Hub processes files in your browser; AI Studio and the other tools explain
their data handling on their own sites.</p>
<h2>Advertising</h2>
<p>SolutionHub may show advertisements through Google AdSense in the future.
Google may use cookies to show ads. You can opt out of personalised
advertising at any time through Google's Ad Settings. We will update this
page before any advertising starts.</p>
<h2>Children</h2>
<p>SolutionHub is written for general audiences. It is not directed at
children under 13, and we do not knowingly collect information from children.</p>
<h2>Changes</h2>
<p>If this policy changes, we will update the date above. Questions:
<a href="mailto:dipeshkarki8292@gmail.com">dipeshkarki8292@gmail.com</a>.</p>"""

TERMS_BODY = """<h1>Terms of Use</h1>
<p class="lede">Last updated: 11 November 2026. By using SolutionHub, you
agree to these terms.</p>
<h2>1. Free guides</h2>
<p>All guides on SolutionHub are free to read. You may share a link to any
guide. You may not copy a guide's text onto another website without our
written permission.</p>
<h2>2. No warranties</h2>
<p>Guides are provided "as is", for general information only. We test the
steps we describe, but software changes, and your device, browser, or file
may behave differently. We do not guarantee that any guide will work for
your specific case, and we are not liable for lost files, lost data, or any
other loss that follows from using a guide. Always keep a backup copy of
important files before editing them.</p>
<h2>3. Third-party tools</h2>
<p>Guides link to tools operated by us and, occasionally, to other websites.
We are not responsible for the content, availability, or policies of
third-party websites. Tools have their own terms, which apply when you use
them.</p>
<h2>4. Acceptable use</h2>
<p>Do not use SolutionHub to break the law, to mislead others, or to harm
anyone. Do not scrape the site in bulk or try to disrupt it.</p>
<h2>5. Changes</h2>
<p>We may update these terms at any time by posting a new version here with a
new date. Continued use of the site after a change means you accept the new
terms.</p>
<h2>6. Contact</h2>
<p>Questions about these terms:
<a href="mailto:dipeshkarki8292@gmail.com">dipeshkarki8292@gmail.com</a>.</p>"""

DISCLAIMER_BODY = """<h1>Disclaimer</h1>
<p class="lede">Last updated: 11 November 2026.</p>
<h2>General information only</h2>
<p>Everything on SolutionHub is general information, not professional advice.
Our guides explain how to do a task; they are not legal, financial, medical,
or tax advice. If you need professional advice, talk to a qualified
professional.</p>
<h2>No guarantees</h2>
<p>We never guarantee a result. A guide describes steps that worked for us at
the time of writing. Results depend on your files, your device, and the
tools involved, all of which change over time. We do not promise earnings,
traffic, rankings, approvals, or any other outcome.</p>
<h2>Tools and links</h2>
<p>Guides recommend tools we operate, and describe their limits honestly.
Tool features, prices, and free limits can change. Always check the tool's
own page for its current terms before relying on it for important work.</p>
<h2>External links</h2>
<p>Links to other websites are provided for convenience. We do not control
those sites and are not responsible for their content or their practices.</p>
<h2>Your responsibility</h2>
<p>Keep backup copies of important files before editing, converting, or
compressing them. Check the output before sharing or sending it. If a guide
is out of date, please tell us through the
<a href="/contact.html">contact page</a> and we will correct it.</p>"""

STATIC_PAGES = [
    ("about.html", "About | SolutionHub",
     "About SolutionHub: an independent how-to website publishing plain, practical guides for everyday problems.",
     ABOUT_BODY),
    ("contact.html", "Contact SolutionHub",
     "Contact SolutionHub by email. Report a mistake in a guide, suggest a topic, or ask a question.",
     CONTACT_BODY),
    ("privacy.html", "Privacy Policy | SolutionHub",
     "SolutionHub privacy policy: no accounts, no tracking cookies, and what happens when you email us.",
     PRIVACY_BODY),
    ("terms.html", "Terms of Use | SolutionHub",
     "SolutionHub terms of use: free guides, no warranties, acceptable use, and contact details.",
     TERMS_BODY),
    ("disclaimer.html", "Disclaimer | SolutionHub",
     "SolutionHub disclaimer: general information only, no guarantees, and your responsibility to keep backups.",
     DISCLAIMER_BODY),
]

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return full

def word_count(html_text):
    text = re.sub(r"<[^>]+>", " ", html_text)
    text = html.unescape(text)
    return len([w for w in re.split(r"\s+", text) if w])

def main():
    # Guides are defined in guides_content.py.
    guides = GUIDES
    n = len(guides)
    for g in guides:
        wc = word_count(g["body"])
        print(f'guide {g["slug"]}: {wc} words')
        if wc < 700 or wc > 1200:
            print(f'  WARNING: word count outside 700-1200 for {g["slug"]}')
    # CSS (single source: this file -> assets/style.css)
    write("assets/style.css", CSS)
    # Home — manual cover + contents index (full width, no .prose cap)
    home_ld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "SolutionHub",
        "url": SITE_URL + "/",
        "description": "Plain, practical how-to guides for everyday problems: PDFs, photos, audio, video, leads, emails, CVs, assignments and online safety.",
    }
    home = page("SolutionHub — Plain, Practical How-To Guides",
                "SolutionHub publishes plain, practical how-to guides for everyday problems: PDFs, photos, audio, video, leads, emails, CVs, assignments and online safety.",
                home_body(guides), "index.html", SITE_URL + "/",
                json_ld=home_ld, wide=True)
    write("index.html", home)
    # Guides index — full contents, grouped by problem, with search/filter
    idx_body = ("<h1>All guides</h1>"
                f'<p class="lede">{n} practical guides, each tested against the '
                "tool it recommends. Pick a problem and follow the steps.</p>"
                '<div class="guide-search">'
                '<label for="guide-search">Search the guides</label>'
                '<input id="guide-search" type="search" placeholder="Try “PDF”, “CV”, “photo”…" autocomplete="off">'
                f'<p class="guide-count" id="guide-count" role="status">Showing {n} of {n} guides</p>'
                "</div>"
                '<p class="guide-empty" id="guide-empty" hidden>No guide matches that search — try a different word.</p>'
                + contents_by_category(guides)
                + '<script src="/assets/guides-search.js" defer></script>')
    write("guides/index.html", page("All Guides | SolutionHub",
          f"Browse all {n} SolutionHub guides: PDFs, photos, audio, video, business leads, emails, CVs, assignments and online safety.",
          idx_body, "guides/index.html", SITE_URL + "/guides/", wide=True))
    # Guide pages
    for g in guides:
        write(f'guides/{g["slug"]}.html', guide_page(g, guides))
    # Static pages
    for fname, title, desc, body in STATIC_PAGES:
        static_ld = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "description": desc,
            "url": f"{SITE_URL}/{fname}",
            "dateModified": BUILD_DATE,
        }
        write(fname, page(title, desc, body, fname, f"{SITE_URL}/{fname}",
                          json_ld=static_ld))
    # Branded 404 (Vercel serves 404.html for unknown paths)
    not_found = page("Page not found | SolutionHub",
        "That page does not exist on SolutionHub. Here is the way back to the guides.",
        ("<h1>That page is not in the manual.</h1>"
         '<p class="lede">The address may be mistyped, or the guide may have '
         "moved. Start again from the contents below.</p>"
         '<p><a class="btn" href="/guides/">Browse all guides &rarr;</a></p>'
         f"{contents_by_category(guides)}"),
        "404.html", SITE_URL + "/404.html", wide=True)
    write("404.html", not_found)
    # vercel.json: clean URLs + security headers. The site has one same-origin
    # script (assets/guides-search.js, loaded by /guides/) and zero third-party
    # resources, so default-src 'self' covers it — no 'unsafe-inline' needed.
    vercel = {
        "cleanUrls": True,
        "headers": [{
            "source": "/(.*)",
            "headers": [
                {"key": "Content-Security-Policy",
                 "value": "default-src 'self'; img-src 'self' data:; style-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"},
                {"key": "X-Content-Type-Options", "value": "nosniff"},
                {"key": "X-Frame-Options", "value": "DENY"},
                {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
            ],
        }],
    }
    write("vercel.json", json.dumps(vercel, indent=2) + "\n")
    # ads.txt (exactly one line)
    write("ads.txt", ADS_TXT_LINE + "\n")
    # robots.txt
    write("robots.txt", "User-agent: *\nAllow: /\n"
          f"Sitemap: {SITE_URL}/sitemap.xml\n")
    # sitemap.xml (with lastmod: guides use their modified date, the rest
    # use this build's date)
    urls = [("/", BUILD_DATE), ("/guides/", BUILD_DATE)] \
        + [(f'/guides/{g["slug"]}.html', g.get("modified", BUILD_DATE)) for g in guides] \
        + [(f"/{f}", BUILD_DATE) for f, _, _, _ in STATIC_PAGES]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, lastmod in urls:
        sm.append(f"  <url><loc>{SITE_URL}{u}</loc><lastmod>{lastmod}</lastmod></url>")
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")
    print(f"Built {len(urls)} pages + 404 + vercel.json + ads.txt + robots.txt + sitemap.xml")
    return 0

if __name__ == "__main__":
    sys.exit(main())
