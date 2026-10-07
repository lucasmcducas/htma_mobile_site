# htma.mobile — landing site

Marketing site for **HTMA Mobile**, the iOS/Android app that reads
hair-tissue mineral charts.

Static HTML, CSS and about 40 lines of vanilla JS. No framework, no build
step, no package manager, no external calls except Google Fonts.

```
index.html   the entire site
```

## Local preview

```bash
python3 -m http.server 8899
# http://localhost:8899
```

## Deploy

GitHub Pages, served from the `gh-pages` branch:

```bash
./deploy.sh
```

Requires `gh auth login` first — see **Auth** below.

## Auth

Do **not** put a token in the remote URL. It ends up in `.git/config` in
plain text and leaks into logs and screenshots.

```bash
gh auth login -h github.com     # once; token goes to the GNOME keyring
gh auth setup-git               # tells git to ask gh instead of the URL
```

The remote should read:

```
https://github.com/lucasmcducas/htma_mobile_site.git
```

with no `user:token@` prefix.

## Before this site goes live

Three things are placeholders and are marked `TODO` in the source:

1. **Store links** (`index.html`, `.store` elements) — both buttons are
   inert and read "Publishing soon". There is no Android keystore and no
   store listing yet, so there is nothing to link to. Replace `href="#"`
   and drop `aria-disabled="true"` when the build is published.

2. **Contact form** (`index.html`, `<form>`) — falls back to
   `mailto:hello@htma.mobile`. Needs a real endpoint.

3. **Privacy policy and terms** (`index.html`, `.foot__legal`) — currently
   one placeholder paragraph covering both. These must be written properly
   before the app is published anywhere.

The landscape in the hero is an inline SVG placeholder, not photography.
Swap `.hero__bg` for an `<img>` when real photography exists.

## The in-phone demo

The device in the hero is not a screenshot. It runs a small working demo:
tap any two minerals and it computes the ratio and shows what that ratio
means in plain language.

That is deliberate — the product's whole claim is that the *relationships*
between values are the information, not the values. A screenshot could not
demonstrate that; a live ratio can.

Values are illustrative. Thresholds follow the standard HTMA reading of
Na/K and Ca/P. It is a demonstration, not advice.

## Related

- Wiki: `~/openclaw/workspace/memory-htma-mobile/concepts/web-design-anti-ai.md`
  — why this looks the way it does, and the constraints it holds to
- Parent site: <https://htmapro.com>