---
name: add-project
description: Add or update a project on the portfolio site — builds the project page, optimizes the photos, and wires up the grid tile on the home page. Use this whenever the user supplies photos of a project, asks to add a new project or placard, wants to swap placeholder images for real ones, asks to reorder or remove tiles, or wants to change what a project page says. Also use it when they hand over a folder of images and say something like "these are from the solar car" — that is a request to build or update that project's page even if they never say the word "project".
---

# Adding a project to the portfolio

This site is a static, no-build HTML site: what is in the repo is exactly what
GitHub Pages serves. There is no framework, no template engine, and no partials —
so shared markup like the nav bar exists as a literal copy in every page. That
tradeoff keeps the site easy for a beginner to read and impossible to break with
a bad build, but it means edits to shared elements have to be repeated by hand.

## The shape of the site

```
index.html          the grid of tiles (the home page)
about.html          personal page, reached from the nav only
<project>.html      one page per project, flat at the repo root
style.css           all styling, palette defined as CSS variables at the top
resume.pdf
images/             web-ready images, one or more per project
tools/optimize_images.py
```

Everything stays flat at the root. Do not create a `projects/` subfolder — the
moment pages sit at different depths, every relative link (`style.css`,
`images/...`) needs a different prefix, which is exactly the kind of breakage
that is hard to spot and annoying to debug.

## Steps

### 1. Optimize the photos before anything else

Raw camera files are 4–12 MB each. Committing them makes the site slow and
bloats the repo permanently, because git stores every version of a binary file
forever — you cannot undo it later by replacing the image.

```bash
py tools/optimize_images.py <source-folder>
```

This resizes to 1800px wide, compresses, and strips EXIF metadata (phone photos
embed the GPS coordinates of where they were taken, which must not go on a
public site). It writes web-ready files into `images/`.

Add `--max-width 1200` for images that will only ever appear as grid tiles.

Then rename the outputs to something descriptive and slug-like:
`solar-car-trailing-arm.jpg`, not `img-4471.jpg`. Filenames are the only labels
you will have when picking images months from now.

### 2. Choose the slug

The slug is the page filename and the image prefix, and it becomes a public URL,
so keep it short and readable: `solar-car-suspension`, `didymos-mission`. Match
the existing pattern — lowercase, hyphens, no dates.

### 3. Build the project page

Copy `rocket-liquids.html` as the starting point. It is the reference
implementation: nav, header, hero figure, body sections, back link, footer.

Replace, in order:
- `<title>` and `<meta name="description">`
- `<h1>` project name and `.project-meta` (role · dates, or org · context)
- `.lede` — one or two sentences on what the project is
- the `.project-figure` image, alt text, and caption
- the `.project-text` sections

Write the body as prose, not resume bullets. The user was explicit that the
resume covers the bullet-point version — these pages exist to give a project
room to breathe. Two to four short `<h2>` sections works well: what the problem
was, what you designed, what happened when it was tested.

For extra images, repeat the `.project-figure` block between sections. Every
image needs real alt text describing what is pictured, both because screen
readers depend on it and because it is what shows if an image fails to load.

### 4. Add the tile to the grid

In `index.html`, add inside `<div class="grid">`:

```html
<a class="tile" href="<slug>.html">
  <img src="images/<slug>.jpg" alt="<what the photo shows>">
  <span class="tile-caption">
    <span class="tile-title">Project Name</span>
    <span class="tile-meta">Role or context · Year</span>
  </span>
</a>
```

Tiles are cropped to 4:5 portrait by `object-fit: cover`, so any photo works
without pre-cropping — but check the result, since cover crops from the centre
and can decapitate people or cut off the subject of a wide landscape shot.

Grid order is source order. Strongest work goes first: the top row is what a
recruiter sees before scrolling.

### 5. Verify before committing

Start the preview server and actually look at the page:

```bash
# .claude/launch.json defines this; use preview_start with name "portfolio-site"
```

Check: the tile links to the right page, images load, hover caption reads well
over the photo, and the page looks right at mobile width. Broken image links are
invisible in the source and obvious to visitors.

### 6. Commit

Push once it looks right — GitHub Pages redeploys automatically, in about a
minute.

## Conventions worth preserving

**Palette** — defined once as CSS variables at the top of `style.css`:
terracotta `#c05c35`, amber `#eda24e`, cream `#f7eddb`, sage `#a1b076`,
olive `#536036`. Use `var(--terracotta)` and friends rather than pasting hex
values, so the palette stays changeable in one place.

**Fonts** — Cormorant Garamond for display type (nav, headings, captions),
uppercase with wide letter-spacing; Karla for body text.

**The nav bar is duplicated in every HTML file.** If it changes — a new link, a
renamed item — update every page, or the site develops inconsistent navigation
that is easy to miss because each page looks fine on its own.

**Text-free tiles.** The tile caption supplies the title on hover, so the images
themselves should not have text baked in. The current placeholder SVGs do, but
only because they are placeholders.

## Things to raise with the user rather than decide alone

- **Photos from an employer's site**, especially defense work. Company policy or
  an NDA usually prohibits publishing them, and that is not something to assume
  either way — ask.
- **Photos containing other people**, e.g. team shots. Worth a quick check that
  they are fine with being on a public site.
- **Which projects earn a tile.** A portfolio is stronger curated than complete;
  if a project is weak next to the others, say so rather than adding it silently.
