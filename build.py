#!/usr/bin/env python3
"""SolutionHub static site generator.

Builds every page from one template so the header, footer, SEO tags and
design stay identical everywhere. Run: python3 build.py
Output: the repo root (index.html, guides/*.html, legal pages, sitemap,
robots.txt, ads.txt) plus assets/style.css.
"""
import html
import os
import re
import sys

from guides_content import GUIDES

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://solutionhub.vercel.app"
SITE_NAME = "SolutionHub"
ADS_TXT_LINE = "google.com, pub-2231619318636842, DIRECT, f08c47fec0942fa"

TOOLS = {
    "pdf": ("PDF Tools Hub", "https://pdf-tools-hub-nine-lac.vercel.app"),
    "ai": ("AI Studio", "https://ai-studio-sandy-sigma.vercel.app"),
    "clipper": ("AI Video Clipper", "https://ai-video-clipper-dipeshkarki8292-3476s-projects.vercel.app"),
    "leads": ("LeadsForceGen", "https://leadsforcegen.vercel.app"),
}

CSS = """/* SolutionHub — clean light design, mobile-first. No frameworks. */
:root{
  --ink:#1f2937; --muted:#5b6b7a; --line:#e5e9ee; --bg:#ffffff;
  --soft:#f4f7f9; --accent:#0f766e; --accent-dark:#0b5d57; --gold:#b45309;
}
*{box-sizing:border-box}
html{font-size:16px}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.65}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
.prose{max-width:760px}
header.site{border-bottom:1px solid var(--line);background:#fff;position:sticky;top:0;z-index:10}
.nav{display:flex;align-items:center;gap:18px;min-height:60px;flex-wrap:wrap;padding-top:8px;padding-bottom:8px}
.brand{font-size:1.35rem;font-weight:800;color:var(--ink);letter-spacing:-.02em}
.brand span{color:var(--accent)}
nav.main{display:flex;gap:16px;margin-left:auto;flex-wrap:wrap}
nav.main a{color:var(--ink);font-weight:600;font-size:.95rem}
nav.main a:hover{color:var(--accent)}
.hero{background:var(--soft);border-bottom:1px solid var(--line);padding:44px 0 38px}
.hero h1{font-size:2.1rem;line-height:1.2;margin:0 0 12px;letter-spacing:-.02em}
.hero p{font-size:1.1rem;color:var(--muted);margin:0 0 20px;max-width:640px}
.btn{display:inline-block;background:var(--accent);color:#fff;font-weight:700;padding:11px 22px;border-radius:8px}
.btn:hover{background:var(--accent-dark);text-decoration:none}
main{padding:32px 0 56px}
h1{font-size:1.9rem;line-height:1.25;letter-spacing:-.02em;margin:0 0 14px}
h2{font-size:1.35rem;margin:34px 0 10px;letter-spacing:-.01em}
h3{font-size:1.1rem;margin:24px 0 8px}
p{margin:0 0 14px}
.lede{font-size:1.12rem;color:var(--muted)}
ul,ol{margin:0 0 16px;padding-left:24px}
li{margin-bottom:6px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin:24px 0}
.card{border:1px solid var(--line);border-radius:12px;padding:18px 20px;background:#fff}
.card h3{margin:0 0 6px;font-size:1.05rem}
.card h3 a{color:var(--ink)}
.card h3 a:hover{color:var(--accent)}
.card p{color:var(--muted);font-size:.95rem;margin:0 0 10px}
.tag{display:inline-block;font-size:.75rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--accent);background:#e6f4f2;border-radius:999px;padding:3px 10px;margin-bottom:8px}
.toolbox{border:1px solid #c9e8e4;background:#effaf8;border-radius:12px;padding:18px 20px;margin:26px 0}
.toolbox h2{margin-top:0}
.faq h3{margin-top:18px}
.note{background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px 16px;margin:20px 0}
.note p{margin:0}
.breadcrumb{font-size:.9rem;color:var(--muted);margin-bottom:14px}
.breadcrumb a{color:var(--muted)}
footer.site{border-top:1px solid var(--line);background:var(--soft);padding:28px 0;color:var(--muted);font-size:.92rem}
footer.site .cols{display:flex;gap:32px;flex-wrap:wrap;justify-content:space-between}
footer.site a{color:var(--muted)}
footer.site strong{color:var(--ink)}
@media (max-width:640px){
  .hero h1{font-size:1.65rem}
  h1{font-size:1.55rem}
  nav.main{gap:12px}
}
"""

def esc(s):
    return html.escape(s, quote=True)

def page(title, description, body, path, canonical):
    """Render one full HTML page. path is the output path relative to ROOT."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header class="site"><div class="wrap nav">
<a class="brand" href="/">Solution<span>Hub</span></a>
<nav class="main" aria-label="Main navigation">
<a href="/">Home</a>
<a href="/guides/">Guides</a>
<a href="/about.html">About</a>
<a href="/contact.html">Contact</a>
</nav>
</div></header>
<main><div class="wrap prose">
{body}
</div></main>
<footer class="site"><div class="wrap cols">
<div><strong>SolutionHub</strong><br>Plain, practical how-to guides.<br>Free tools, honest advice, no hype.</div>
<div><strong>Guides</strong><br><a href="/guides/">All guides</a><br><a href="/guides/edit-pdf-text.html">Edit PDF text</a><br><a href="/guides/find-business-leads-free.html">Find business leads</a></div>
<div><strong>Site</strong><br><a href="/about.html">About</a><br><a href="/contact.html">Contact</a><br><a href="/privacy.html">Privacy Policy</a><br><a href="/terms.html">Terms of Use</a><br><a href="/disclaimer.html">Disclaimer</a></div>
</div><div class="wrap" style="margin-top:18px">&copy; 2026 SolutionHub. All guides are original work written by the SolutionHub team.</div></footer>
</body>
</html>
"""

def guide_card(g):
    return (f'<article class="card"><span class="tag">{esc(g["category"])}</span>'
            f'<h3><a href="/guides/{g["slug"]}.html">{esc(g["title"])}</a></h3>'
            f'<p>{esc(g["description"])}</p>'
            f'<a href="/guides/{g["slug"]}.html">Read the guide &rarr;</a></article>')

def guide_page(g):
    tool_box = ""
    if g.get("tool"):
        tname, turl = TOOLS[g["tool"]]
        tool_box = (f'<aside class="toolbox"><h2>Try the free tool</h2>'
                    f'<p>Do this right now with <strong>{esc(tname)}</strong> — '
                    f'free to try, no install needed.</p>'
                    f'<p><a class="btn" href="{esc(turl)}">Open {esc(tname)} &rarr;</a></p></aside>')
    body = (f'<p class="breadcrumb"><a href="/">Home</a> &rsaquo; '
            f'<a href="/guides/">Guides</a> &rsaquo; {esc(g["category"])}</p>'
            f'<h1>{esc(g["title"])}</h1>'
            f'<p class="lede">{esc(g["description"])}</p>'
            f'{g["body"]}'
            f'{tool_box}'
            f'<p><a href="/guides/">&larr; Back to all guides</a></p>')
    return page(f'{g["title"]} | SolutionHub', g["description"], body,
                f'guides/{g["slug"]}.html', f'{SITE_URL}/guides/{g["slug"]}.html')

# ---------------------------------------------------------------- static pages
def home_body(cards):
    return f"""<section class="hero" style="margin:-32px -20px 0;padding-left:20px;padding-right:20px">
<h1>Solve it yourself, step by step.</h1>
<p>SolutionHub publishes plain, practical how-to guides for everyday
problems — PDFs, photos, audio, video, leads, emails, CVs and online safety.
No jargon, no hype, no paid tricks. Just the steps that work.</p>
<p><a class="btn" href="/guides/">Browse all 12 guides &rarr;</a></p>
</section>
<h2>Latest guides</h2>
<div class="cards">
{cards}
</div>
<h2>How SolutionHub works</h2>
<p>Every guide is written in original words by our team, tested against the
real tool it recommends, and kept short enough to finish in one sitting.
Where a guide points to a free tool, that tool is one we run ourselves —
<a href="https://pdf-tools-hub-nine-lac.vercel.app">PDF Tools Hub</a>,
<a href="https://ai-studio-sandy-sigma.vercel.app">AI Studio</a>,
<a href="https://ai-video-clipper-dipeshkarki8292-3476s-projects.vercel.app">AI Video Clipper</a> and
<a href="https://leadsforcegen.vercel.app">LeadsForceGen</a>. We never
recommend a tool we have not used, and we say plainly when something does
not work yet.</p>
<h2>Start with the most-read guides</h2>
<ul>
<li><a href="/guides/edit-pdf-text.html">How to edit text in a PDF for free</a> — fix a typo without the original file.</li>
<li><a href="/guides/merge-pdf-files.html">How to merge PDF files for free</a> — combine pages into one file.</li>
<li><a href="/guides/long-video-to-shorts.html">How to turn a long video into Shorts and Reels</a> — clips with captions, in minutes.</li>
<li><a href="/guides/check-link-safe.html">How to check if a link is safe before you click it</a> — a 30-second safety habit.</li>
</ul>"""

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
    for g in guides:
        wc = word_count(g["body"])
        print(f'guide {g["slug"]}: {wc} words')
        if wc < 700 or wc > 1200:
            print(f'  WARNING: word count outside 700-1200 for {g["slug"]}')
    # CSS
    write("assets/style.css", CSS)
    # Home
    cards = "\n".join(guide_card(g) for g in guides)
    home = page("SolutionHub — Plain, Practical How-To Guides",
                "SolutionHub publishes plain, practical how-to guides for everyday problems: PDFs, photos, audio, video, leads, emails, CVs and online safety.",
                home_body(cards), "index.html", SITE_URL + "/")
    write("index.html", home)
    # Guides index
    idx_body = ("<h1>All guides</h1>"
                '<p class="lede">Twelve practical guides, each tested against the '
                "tool it recommends. Pick a problem and follow the steps.</p>"
                '<div class="cards">\n' + cards + "\n</div>")
    write("guides/index.html", page("All Guides | SolutionHub",
          "Browse all 12 SolutionHub guides: PDFs, photos, audio, video, business leads, emails, CVs and online safety.",
          idx_body, "guides/index.html", SITE_URL + "/guides/"))
    # Guide pages
    for g in guides:
        write(f'guides/{g["slug"]}.html', guide_page(g))
    # Static pages
    for fname, title, desc, body in STATIC_PAGES:
        write(fname, page(title, desc, body, fname, f"{SITE_URL}/{fname}"))
    # ads.txt (exactly one line)
    write("ads.txt", ADS_TXT_LINE + "\n")
    # robots.txt
    write("robots.txt", "User-agent: *\nAllow: /\n"
          f"Sitemap: {SITE_URL}/sitemap.xml\n")
    # sitemap.xml
    urls = ["/", "/guides/"] + [f'/guides/{g["slug"]}.html' for g in guides] \
        + [f"/{f}" for f, _, _, _ in STATIC_PAGES]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"  <url><loc>{SITE_URL}{u}</loc></url>")
    sm.append("</urlset>")
    write("sitemap.xml", "\n".join(sm) + "\n")
    print(f"Built {len(urls)} pages + ads.txt + robots.txt + sitemap.xml")
    return 0

if __name__ == "__main__":
    sys.exit(main())
