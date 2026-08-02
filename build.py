#!/usr/bin/env python3
"""
Single-source-of-truth builder for proposal pages.

The ONLY file you edit is  src/<name>/template.html  (+ images in src/<name>/img/).
One run regenerates every output from it:

  1. Web version   ->  <slug>/index.html + <slug>/img/   (for GitHub Pages)
  2. Email version ->  one self-contained .html with base64-embedded images
  3. PDFs          ->  Arabic + English exports (headless Chrome)

Usage:
  python3 build.py toronto            # build everything for 'toronto'
  python3 build.py toronto --no-pdf   # skip PDF export
  python3 build.py --all              # build every proposal

After building, publish with:  git add -A && git commit -m "..." && git push
"""
import base64, mimetypes, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PROPOSALS = {
    "toronto": {
        "slug": "toronto-k7x2",  # published folder -> https://qataruts.github.io/proposals/toronto-k7x2/
        "email_out": "/Volumes/data/new-projects/v-study/proposals/TORONTO/Toronto-Petroleum-Proposal.html",
        "pdf_ar":    "/Volumes/data/new-projects/v-study/proposals/TORONTO/Toronto-Petroleum-Proposal-AR.pdf",
        "pdf_en":    "/Volumes/data/new-projects/v-study/proposals/TORONTO/Toronto-Petroleum-Proposal-EN.pdf",
    },
}

IMG_RE = re.compile(r"\{\{IMG:([^}]+)\}\}")
LANG_RE = re.compile(r'<html lang="ar" dir="rtl" data-lang="ar">')


def build(name, make_pdf=True):
    cfg = PROPOSALS[name]
    src_dir = os.path.join(ROOT, "src", name)
    img_dir = os.path.join(src_dir, "img")
    template = open(os.path.join(src_dir, "template.html"), encoding="utf-8").read()

    used = sorted(set(IMG_RE.findall(template)))
    missing = [f for f in used if not os.path.exists(os.path.join(img_dir, f))]
    if missing:
        sys.exit(f"[{name}] missing images: {missing}")

    # 1) web version (relative img/ paths)
    web_dir = os.path.join(ROOT, cfg["slug"])
    os.makedirs(os.path.join(web_dir, "img"), exist_ok=True)
    web_html = IMG_RE.sub(lambda m: "img/" + m.group(1), template)
    open(os.path.join(web_dir, "index.html"), "w", encoding="utf-8").write(web_html)
    for f in used:
        shutil.copy2(os.path.join(img_dir, f), os.path.join(web_dir, "img", f))
    print(f"[{name}] web    -> {cfg['slug']}/index.html  ({len(used)} images)")

    # 2) email version (self-contained, base64)
    def as_data_uri(m):
        fn = m.group(1)
        mime = mimetypes.guess_type(fn)[0] or "image/jpeg"
        data = base64.b64encode(open(os.path.join(img_dir, fn), "rb").read()).decode()
        return f"data:{mime};base64,{data}"
    email_html = IMG_RE.sub(as_data_uri, template)
    os.makedirs(os.path.dirname(cfg["email_out"]), exist_ok=True)
    open(cfg["email_out"], "w", encoding="utf-8").write(email_html)
    print(f"[{name}] email  -> {cfg['email_out']}  ({os.path.getsize(cfg['email_out'])/1e6:.1f} MB)")

    # 3) PDFs (AR = as-is; EN = default language flipped)
    if make_pdf and os.path.exists(CHROME):
        def print_pdf(html_text, out_path):
            with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as t:
                t.write(html_text); tmp = t.name
            subprocess.run([CHROME, "--headless", "--disable-gpu",
                            f"--print-to-pdf={out_path}", "--no-pdf-header-footer",
                            f"file://{tmp}"], capture_output=True)
            os.unlink(tmp)
            print(f"[{name}] pdf    -> {out_path}")
        print_pdf(email_html, cfg["pdf_ar"])
        en_html = LANG_RE.sub('<html lang="en" dir="ltr" data-lang="en">', email_html, count=1)
        print_pdf(en_html, cfg["pdf_en"])


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    make_pdf = "--no-pdf" not in sys.argv
    names = PROPOSALS.keys() if "--all" in sys.argv else args
    if not names:
        sys.exit(__doc__)
    for n in names:
        build(n, make_pdf)
