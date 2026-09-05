# Portfolio site

Personal portfolio for Aras Vakili (Mechanical & Aerospace Engineering, UC Irvine),
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
tools/                optimize_images.py, clip_to_gif.py
.claude/skills/       add-project skill
```

All HTML sits flat at the repo root. Do not introduce a `projects/` subfolder —
mixed depths mean relative links (`style.css`, `images/...`) need different
prefixes per page, which breaks in ways that are easy to miss.

## Design

Image-led, in the manner of a photography portfolio: large pictures carry the
page, text stays minimal. The home page is a three-column grid of 4:5 tiles whose
captions appear on hover (and stay visible on touch devices, which have no hover).

**Palette** — terracotta `#c05c35`, amber `#eda24e`, cream `#f7eddb` (background),
sage `#a1b076`, olive `#536036` (body text). Defined once as CSS variables; use
`var(--terracotta)` rather than pasting hex values.

**Fonts** — Cormorant Garamond for display type (nav, headings, tile captions),
uppercase with wide letter-spacing. Karla for body copy.

**No Experience section.** This was an explicit decision: the resume covers
employment history, and the site is for showing work. ITT Cannon appears as a
project tile, not as a CV entry.

## Working on the site

**Adding or updating a project**: use the `add-project` skill in
`.claude/skills/add-project/`. It covers image optimization, the page template,
and the grid tile.

**Images**: always run `py tools/optimize_images.py <folder>` before committing
photos. It resizes, compresses, and strips EXIF — phone photos carry GPS
coordinates that should not be published. Raw camera files committed by mistake
stay in git history permanently.

**Video clips**: `py tools/clip_to_gif.py <video> --start 0:12 --end 0:16 --name <slug>`
cuts a clip and writes both a GIF and an MP4 so their sizes can be compared. It
uses the ffmpeg bundled with the `imageio-ffmpeg` package, so nothing has to be
installed system-wide. Keep source video out of the repo — only the output
belongs in `images/`.

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

Every tile still shows a generated placeholder SVG labeled "PHOTO PENDING". Real
photographs are the main outstanding work. Project pages exist for `itt-cannon`
and `rocket-liquids`; the remaining tiles link to pages that have not been written
yet, so those links 404 until the photos arrive.
