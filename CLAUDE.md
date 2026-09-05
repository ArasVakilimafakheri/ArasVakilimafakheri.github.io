# Portfolio site

Personal portfolio for Aras Vakilimafakheri (Mechanical & Aerospace Engineering,
UC Irvine), served by GitHub Pages at <https://arasvakilimafakheri.github.io>.

The owner is new to web development and git. Explain changes in plain language,
and avoid introducing tooling that has to be understood before the site can be
edited.

**Tell him to hard refresh.** GitHub Pages serves CSS with `Cache-Control:
max-age=600`, so for ten minutes after a push his browser keeps the old
stylesheet and the change looks like it never shipped. This has already caught
him once. `Ctrl`+`Shift`+`R`.

---

## Stack

Plain HTML and CSS. No framework, no build step, no dependencies — what is in
the repo is exactly what GitHub Pages serves. Pushing to `main` deploys in about
a minute.

Keep it that way unless there is a strong reason not to. The value of a no-build
site here is that the owner can open any file and see what the page is.

## Layout

```
index.html                grid of image tiles (home)
about.html                personal page, reached from the nav only
itt-cannon.html           \
rocket-liquids.html        |  one page per project,
pinn-research.html         |  flat at the repo root
autonomous-rover.html     /
style.css                 all styling; palette as CSS variables at the top
resume.pdf                linked from the nav and the About page
rover-design-report.pdf   embedded in autonomous-rover.html
aiaa-2026-0590-…lift.pdf  embedded in pinn-research.html
images/                   tile and page media
tools/                    optimize_images.py, video_to_tile.py
.claude/skills/           add-project skill
```

All HTML sits flat at the repo root. Do not introduce a `projects/` subfolder —
mixed depths mean relative links (`style.css`, `images/...`) need different
prefixes per page, which breaks in ways that are easy to miss.

---

## Design

Image-led, in the manner of a photography portfolio: large pictures carry the
page, text stays minimal. The home page is a three-column grid of 4:5 tiles.

**Palette** — terracotta `#c05c35`, amber `#eda24e`, cream `#f7eddb`
(background), sage `#a1b076`, olive `#536036` (body text). Defined once as CSS
variables; use `var(--terracotta)` rather than pasting hex values.

**Fonts** — Cormorant Garamond for display type (nav, headings, tile captions),
uppercase with wide letter-spacing. Karla for body copy.

**No Experience section.** An explicit decision: the resume covers employment
history, and the site is for showing work. ITT Cannon appears as a project tile,
not as a CV entry. The About page was likewise stripped back to who he is — the
technical paragraphs were removed on purpose.

### Tiles

Each tile carries a permanent colour tint with its title always visible, and
lifts about 10px with a shadow on hover. The lift is dropped under
`prefers-reduced-motion`; the shadow stays so hover is still answered.

The tint rotates through the palette by `:nth-child(4n + …)`, which in a
three-column grid keeps neighbours different in both directions. Because it is
positional, **reordering or inserting a tile reshuffles every colour after it** —
fine in itself, but do not expect a project to keep its colour.

The scrim is two layers: the palette tint at 50%, and a neutral darkening over
it. The darkening is not decoration — the lighter palette colours over a bright
picture leave cream text almost unreadable, so the tint cannot carry it alone.

Add `tile--light-media` to any tile whose picture is a plot, screenshot, or
object on white. Those give the scrim far less to darken. Currently on the ADC
Lab and Autonomous Rover tiles.

Measured over the current media, captions read at **4.4–9.8:1**, and about 5:1
against the brightest individual pixels. **Re-measure rather than eyeballing** if
the tint opacity, the darkening, or a tile image changes. The method: draw the
image to a canvas, average the band behind the caption, composite the two scrim
layers over it, and compare luminance against the cream `#f7eddb`.

**Fitting pictures to the 4:5 tile.** Photographs that fill the frame get
`object-fit: cover` and nothing else. Anything that cannot survive a crop —
a landscape object, a plot with axes — is instead scaled to fit and centred on a
white canvas at 900×1125 before being saved. Do not crop a plot's axes off, and
do not centre-crop a wide object; both were tried and rejected.

### Header

The wordmark is absolutely centred on the page, nav on the left, icons on the
right, and the whole thing stacks into a centred column below 1260px. That
breakpoint is high because "Aras Vakilimafakheri" set at 1.55rem is a wide piece
of type: measured, the wordmark reaches the nav links at about 1240px. If the
name, its size, or the nav items change, re-measure and move the breakpoint
rather than assuming it still holds.

Avoid going back to a three-column `1fr auto 1fr` grid — it forces both side
columns to match the wider one, wasting roughly 260px and pushing the collision
point past most laptops.

**The nav bar is duplicated in every HTML file** — the cost of having no template
engine. Change it in one page and it must change in all of them.

---

## Working on the site

**Adding or updating a project**: use the `add-project` skill in
`.claude/skills/add-project/`.

**Preview locally** rather than guessing: `.claude/launch.json` defines a
`portfolio-site` server on port 8080.

> Screenshots of pages containing an embedded PDF often fail to composite, and
> the preview pane sometimes returns blank frames after scrolling. When that
> happens, verify through the DOM (`read_page`, or measuring in
> `javascript_tool`) instead of retrying screenshots.

**Images**: run `py tools/optimize_images.py <folder>` before committing photos.
It resizes, compresses, and strips EXIF — phone photos carry GPS coordinates
that should not be published. Raw camera files committed by mistake stay in git
history permanently.

**Camera RAW**: he shoots `.NEF`, which browsers cannot display. Convert with
`rawpy` (installed): `raw.postprocess(use_camera_wb=True)` into a Pillow image,
then crop and save. Built from raw pixels this way, there is no EXIF to strip.

**PDFs**: `pymupdf` (installed). `page.get_pixmap(dpi=…, clip=Rect)` renders a
region; `doc.rewrite_images(dpi_threshold=…, dpi_target=…, quality=…)` downsamples
embedded images, which is where nearly all the weight usually sits — it took the
rover report from 9.9 MB to 3.2 MB with no visible loss. **Only do that to his
own documents.** The AIAA paper is a published document of record: leave it
intact, and note it will not compress anyway because its figures are vector.

**Video clips**: `py tools/video_to_tile.py <video> --name <slug> --aspect 4:5`
crops and encodes tile media. `--start`/`--end` for a cut, or omit both for the
whole video; `--anchor left|center|right` positions the crop; `--mp4-only` skips
the GIF; `--crf`, `--width`, `--mp4-fps` trade quality against size. Uses the
ffmpeg bundled with `imageio-ffmpeg`, so nothing is installed system-wide.

Keep source video out of the repo — only the output belongs in `images/`.

**Tile motion uses video, not GIF.** On the hot-fire footage the GIF came out 24×
the size of the equivalent MP4 (5.2 MB against 215 KB for one second): GIF is
capped at 256 colours and has no interframe compression. A muted autoplaying MP4
looks the same on the page. The small script at the bottom of `index.html` pauses
tile video under `prefers-reduced-motion`, and retries playback on first
interaction for browsers that block autoplay until then.

**Watch the weight.** Tile video autoplays on the home page, so seconds cost
kilobytes: the 0.9s rocket clip is 163 KB while the 28.6s ITT reel is 1.9 MB even
at 640px, 20fps and CRF 31. A short loop beats a long one compressed hard. He was
told the ITT tile is the expensive one and chose to keep it full length.

---

## Rights and privacy decisions already made

- Public contact address is `arasvakili@gmail.com`, not the git account email.
- The phone number is in `resume.pdf` but deliberately nowhere in the page text,
  to keep it away from scrapers.
- Git commits use the GitHub `users.noreply.github.com` address. His git author
  name and GitHub profile still read "Aras Vakili" — left alone deliberately,
  since changing the git identity affects every repo on his machine.
- **ITT Cannon is defense-adjacent.** The page text stays within what is already
  on his public resume, and the Minuteman III program name is deliberately
  omitted. The tile video is ITT's own public brand reel, which he supplied.
  Photographs from inside that site need employer approval.
- **Do not download from YouTube.** He asked for a tile loop cut from his
  friend's YouTube video; the answer was to ask his friend for the source file
  instead. He has since dropped the idea. The video is embedded on the rover page
  via `youtube-nocookie.com`, which is fine.
- **The AIAA paper's author order is genuinely inconsistent** — do not "correct"
  the citation without checking. The typeset author line reads Elmaradny,
  Abdelrazek, Vakilimafakheri, Taha; the PDF's own metadata, the Crossref record,
  and his resume all read Elmaradny, Vakilimafakheri, Abdelrazek, Taha. The site
  follows Crossref, because that is what Google Scholar and the indexes show. He
  has been told to raise it with his advisor.

---

## Current state

Four of the nine tiles are finished. Each finished tile has a page; the rest
still show a generated placeholder SVG labelled "PHOTO PENDING" and link to pages
that **do not exist yet, so those links 404**.

| # | Tile title | Caption | Media | Page |
|---|---|---|---|---|
| 1 | ITT Cannon | Manufacturing Engineering | 28.6s brand reel, MP4 | ✅ `itt-cannon.html` |
| 2 | UCI Rocket Project — Liquids | Propulsion · Project Management | 0.9s hot-fire loop, MP4 | ✅ `rocket-liquids.html` |
| 3 | UC Irvine Aeronautics, Dynamics, and Control Lab | Physics-Informed Neural Networks | velocity-field plot | ✅ `pinn-research.html` |
| 4 | UCI Solar Car | Suspension | placeholder | ❌ 404 |
| 5 | Single-Engine Aircraft Design | CAD & Flow Simulation | placeholder | ❌ 404 |
| 6 | Orbital Mechanics | Didymos Mission Analysis | placeholder | ❌ 404 |
| 7 | Autonomous Rover | Class Project | rover photograph | ✅ `autonomous-rover.html` |
| 8 | RC Rover | Class Project | placeholder | ❌ 404 |
| 9 | Life Tank Prototype | Prototype Design | placeholder | ❌ 404 |

The MATLAB Rainfall Predictor repo was deliberately left off the grid as the
weakest item. Easy to add back if he asks.

**Page shapes that have settled.** Project pages lead with the organisation as
the `<h1>` and the role plus dates as `.project-meta` beneath it — the rover page
uses the project name because there is no organisation. `pinn-research.html`
links its title to the lab site and lists the PI and PhD advisor in a `.people`
list. Long-form documents are embedded in `.paper-frame` iframes with a plain
download link beneath, because phone browsers routinely refuse to render a framed
PDF.

## Where to pick up

1. **Media for the five unfinished tiles.** He drops files into
   `Desktop/Media For Portfolio/<Project>/Placard Photo|Placard Video/` and says
   so. That folder is outside the repo and stays there.
2. **Write the five missing project pages** as their media arrives. Copy an
   existing page for the nav, header and footer.
3. He has an unconfirmed LinkedIn URL on the site: `linkedin.com/in/aras-vakili`,
   inferred from the resume. Worth confirming.
