# Portfolio site

Personal portfolio for Aras Vakilimafakheri (Mechanical & Aerospace Engineering, UC Irvine),
served by GitHub Pages at <https://arasvakilimafakheri.github.io>.

The owner is new to web development and git. Explain changes in plain language and
avoid introducing tooling that has to be understood before the site can be edited.

## Stack

Plain HTML and CSS. No framework, no build step, no dependencies — what is in the
repo is exactly what GitHub Pages serves. Pushing to `main` deploys in about a
minute.

Keep it that way unless there is a strong reason not to. The value of a no-build
site here is that the owner can open any file and see what the page is.

## Layout

```
index.html            grid of image tiles (home)
about.html            personal page, reached from the nav only
itt-cannon.html       \
rocket-liquids.html   /  one page per project, flat at the root
style.css             all styling; palette as CSS variables at the top
resume.pdf            linked from the nav and the About page
images/               web-ready images (currently placeholder SVGs)
tools/                optimize_images.py, video_to_tile.py
.claude/skills/       add-project skill
```

All HTML sits flat at the repo root. Do not introduce a `projects/` subfolder —
mixed depths mean relative links (`style.css`, `images/...`) need different
prefixes per page, which breaks in ways that are easy to miss.

## Design

Image-led, in the manner of a photography portfolio: large pictures carry the
page, text stays minimal. The home page is a three-column grid of 4:5 tiles.

**Tiles** — each carries a permanent colour tint with its title always visible,
and lifts about 10px with a shadow on hover. The tint rotates through the palette
by `:nth-child(4n + …)`, which in a three-column grid keeps neighbours different
in both directions. Because it is positional, **reordering or inserting a tile
reshuffles every colour after it** — that is fine, but do not expect a given
project to keep its colour.

Add `tile--light-media` to a tile whose picture is a plot or screenshot on
white. Those leave the scrim far less to darken than a photograph does — the
airfoil figure measured 3.4:1 behind its caption on the standard treatment, and
5.2:1 with the modifier.

The scrim is two layers: the palette tint at 50%, and a neutral darkening over
it. The darkening is not decoration. The lighter palette colours over a bright
photograph leave cream text almost unreadable, so the tint alone cannot carry it.
Measured over the current media, the composite gives 4.4–8.5:1 contrast on
average and about 3.4:1 against the brightest individual pixels, which is what
the text-shadow on `.tile-title` / `.tile-meta` is there to cover. If the tint
opacity or the darkening changes, re-measure rather than eyeballing it — bright
smoke and pale sky are the cases that fail.

**Palette** — terracotta `#c05c35`, amber `#eda24e`, cream `#f7eddb` (background),
sage `#a1b076`, olive `#536036` (body text). Defined once as CSS variables; use
`var(--terracotta)` rather than pasting hex values.

**Fonts** — Cormorant Garamond for display type (nav, headings, tile captions),
uppercase with wide letter-spacing. Karla for body copy.

**Header** — the wordmark is absolutely centred on the page, with the nav on the
left and icons on the right, and the whole thing stacks into a centred column
below 1260px. That breakpoint is high because "Aras Vakilimafakheri" set at
1.55rem is a wide piece of type: measured, the wordmark reaches the nav links at
about 1240px. If the name, its size or the nav items change, re-measure and move
the breakpoint rather than assuming it still holds. Avoid going back to a
three-column `1fr auto 1fr` grid — it forces both side columns to match the wider
one, wasting roughly 260px and pushing the collision point past most laptops.

**No Experience section.** This was an explicit decision: the resume covers
employment history, and the site is for showing work. ITT Cannon appears as a
project tile, not as a CV entry.

## Working on the site

**Adding or updating a project**: use the `add-project` skill in
`.claude/skills/add-project/`. It covers image optimization, the page template,
and the grid tile.

**Camera RAW**: the owner shoots RAW (`.NEF`), which browsers cannot display.
Convert with `rawpy` (installed): `raw.postprocess(use_camera_wb=True)` into a
Pillow image, then crop and save. Building the image from raw pixels this way
carries no EXIF at all, so there is nothing to strip.

**Images**: always run `py tools/optimize_images.py <folder>` before committing
photos. It resizes, compresses, and strips EXIF — phone photos carry GPS
coordinates that should not be published. Raw camera files committed by mistake
stay in git history permanently.

**Video clips**: `py tools/video_to_tile.py <video> --name <slug> --aspect 4:5`
crops and encodes tile media. Add `--start`/`--end` for a cut, or omit both for
the whole video; `--mp4-only` skips the GIF, and `--crf`, `--width` and
`--mp4-fps` trade quality against size. It uses the ffmpeg bundled with the
`imageio-ffmpeg` package, so nothing has to be installed system-wide. Keep source
video out of the repo — only the output belongs in `images/`.

Watch the weight. Tile video autoplays on the home page, so seconds cost
kilobytes: the 0.9s rocket clip is 163 KB while the 28.6s ITT reel is 1.9 MB even
at 640px, 20fps and CRF 31. A short loop is usually the better answer than a
long one compressed hard.

**The nav bar is duplicated in every HTML file** — the cost of having no template
engine. Change it in one page and it must change in all of them.

**Preview locally** rather than guessing: `.claude/launch.json` defines a
`portfolio-site` server on port 8080.

## Privacy decisions already made

- The public contact address is `arasvakili@gmail.com`, not the git account email.
- The phone number appears in `resume.pdf` but deliberately nowhere in the page
  text, to keep it away from scrapers.
- Git commits use the GitHub `users.noreply.github.com` address.
- ITT Cannon is defense-adjacent work. The page text stays within what is already
  on the public resume, and the specific program name is omitted. Photographs from
  that site need employer approval before they go anywhere near the repo.

## Current state

`rocket-liquids` and `itt-cannon` have real media: both tiles are looping muted
MP4s (`<video autoplay muted loop playsinline>` with a poster frame) and both
pages use a still from the same footage. The ITT clip is ITT's own public brand
reel, supplied by the owner, so it shows the company rather than his own work.
`pinn-research` has a page too, built around the published paper: the ADC Lab
tile is a modelled velocity field, cropped inside the axes so no title, tick
labels or colourbar ride along. The page embeds `aiaa-2026-0590-variational-theory-of-lift.pdf` in an iframe with
a plain download link beneath, since phone browsers routinely refuse to render a
PDF in a frame. That PDF is 7.4 MB and will not compress — its figures are
vector, so re-saving achieves nothing. Do not rasterise it; it is the published
document of record.

**The paper's author order is genuinely inconsistent**, so do not "correct" the
citation without checking. The typeset author line reads Elmaradny, Abdelrazek,
Vakilimafakheri, Taha — but the PDF's own document metadata, the Crossref record
and the owner's resume all read Elmaradny, Vakilimafakheri, Abdelrazek, Taha. The
site follows Crossref, because that is what indexes and Google Scholar will show.

The remaining six tiles still show generated placeholder SVGs labeled "PHOTO
PENDING" and link to pages that have not been written yet, so those links 404
until the photos arrive.

**PDF handling** uses `pymupdf` (installed): `page.get_pixmap(dpi=…, clip=Rect)`
renders a region, which is how the ADC tile was cut out of a multi-panel figure.

**Tile motion uses video, not GIF.** On the hot-fire footage the GIF came out 24x
the size of the equivalent MP4 (5.2 MB against 215 KB for one second) because GIF
is capped at 256 colours and has no interframe compression. A muted autoplaying
MP4 looks the same on the page. The small script at the bottom of `index.html`
pauses tile video when the visitor has "reduce motion" set, and retries playback
on first interaction for browsers that block autoplay until then.

Source video lives outside the repo, under
`Desktop/Media For Portfolio/`, along with rejected clip options.
