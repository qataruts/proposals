# proposals

Static publishing repo for investment proposals (GitHub Pages).
Each proposal lives in its own unguessable folder; access is by direct link only.

## Single source of truth

Never edit the published folders directly. The only editable files are:

```
src/<name>/template.html   <- ALL text/design edits happen here
src/<name>/img/            <- optimized photos ({{IMG:file.jpg}} placeholders)
build.py                   <- per-proposal output paths & slugs
```

## Workflow (one edit updates everything)

```bash
# 1. edit src/<name>/template.html
python3 build.py <name>        # regenerates: web folder + email .html + AR/EN PDFs
git add -A && git commit -m "update <name>" && git push   # publishes the web version
```

## Current proposals

| name    | live URL                                            | email/PDF outputs                          |
|---------|-----------------------------------------------------|--------------------------------------------|
| mesaieed | https://qataruts.github.io/proposals/mesaieed-factory-k7x2/ | v-study/proposals/TORONTO/ (UTS-*)   |
