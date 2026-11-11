# SolutionHub

Plain, practical how-to guides for everyday problems — PDFs, photos, audio,
video, business leads, emails, CVs, and online safety. Written in original
words, tested against the real tools they recommend.

**Live site:** https://solutionhub.vercel.app (deployment handled separately)

## What this is

A static website. No database, no auth, no login, no JavaScript framework.
Pages are generated from `build.py` + `guides_content.py` into plain HTML
in the repo root, so any static host can serve it.

## Pages

- Home (`index.html`) + Guides index (`guides/index.html`)
- 12 original guides in `guides/` (700–1200 words each, with steps, tips, and FAQ)
- About, Contact, Privacy Policy, Terms of Use, Disclaimer
- `sitemap.xml`, `robots.txt`, `ads.txt` (AdSense publisher verification line)

## The guides

1. How to edit text in a PDF for free → PDF Tools Hub
2. How to merge PDF files for free → PDF Tools Hub
3. How to compress a PDF without losing quality → PDF Tools Hub
4. How to turn photos into a PDF → PDF Tools Hub
5. How to enhance an old or blurry photo for free → AI Studio
6. How to remove background noise from audio for free → AI Studio
7. How to generate AI images for free → AI Studio
8. How to turn a long video into Shorts and Reels → AI Video Clipper
9. How to find real business leads for free → LeadsForceGen
10. How to write a follow-up email that gets replies
11. How to make a professional CV for free
12. How to check if a link is safe before you click it

## Honesty rules (kept in the guides)

- Photo colorize/restore do NOT work in AI Studio right now — never presented as working.
- YouTube link import is NOT visitor-usable in AI Video Clipper — guides say "upload your video".
- No "guaranteed" claims, no earnings promises, anywhere.
- No ad code on the site. AdSense code is added only after Google approves the site.

## Build

```bash
python3 build.py        # regenerates all HTML + sitemap/robots/ads.txt
python3 -m http.server 8130   # preview at http://127.0.0.1:8130
```

## License

All guide text is original work by SolutionHub. Tools linked from the guides
are separate projects with their own terms.
