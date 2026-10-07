# Repaint plan: port the site palette to the Flutter app

Status: **plan only, nothing implemented.** Written 2026-10-07 while the
landing-site reskin was being verified. Source of truth for the design:
`index.html` in this repo, commit `4fd790a`.

## The gap

`htma_mobile_site` (this repo) is the **marketing site** — static HTML.

`htma_labs` (`~/.openclaw/workspace/htma_labs`) is the **Flutter app** —
a completely separate codebase. The app is a Flutter bundle and ships **no
`index.html`**, so the site reskin cannot appear in it by any push. This is
a port of a *design decision*, not a copy of files.

Package on device: `com.htmapro.htma_labs` v0.1.0.

## Why this is a cheap port

The colour change is unusually well-isolated. Measured, not assumed:

| Fact | Value |
|---|---|
| Files referencing `AppColors.` | **69** |
| Files with hardcoded `Color(0xFF…)` | **7** (22 occurrences) |
| Central colour definitions | `lib/core/theme/app_colors.dart` (69 lines) |
| Central theme | `lib/core/theme/app_theme.dart` |

So the bulk of the app inherits from one file. Repainting is mostly
editing constants, not hunting widgets.

## Target palette

Sampled and contrast-checked on the site. Cream paper rather than pure
white, because pure white reads as generic SaaS rather than health.

| Role | Current (app) | New | Contrast |
|---|---|---|---|
| Background | `#FAF8F5` | `#F4F1EA` | — |
| Surface | `#FFFFFF` | `#FFFDF8` | 1.11:1 vs bg |
| Surface variant | `#F2EFEA` | `#F1EFE8` | — |
| Primary / accent | `#8B7355` | `#2D7D5F` | **5.09:1** on surface |
| Text primary | `#2D2A26` | `#141210` | 18.4:1 |
| Text secondary | `#7A7268` | `#7A7367` | 4.62:1 |
| Border | `#E5E0D8` | `rgba(20,18,16,.11)` → `#E4E2DD` | — |

All pass WCAG AA. Low contrast is the most common real-world web failure
(WebAIM 2026: 83.9% of top-million home pages), so these were measured
rather than eyeballed.

`#2D7D5F` is hue 159° — green's health cue with blue's precision. It
replaces a muddy `#8B7355` earth tone. Note the app's existing
`accent = #C77D43` (orange) and `success = #6B8F6B` (green) are
**semantic** colours, not brand — decide separately whether they move,
because changing them would alter meaning (warning vs success).

## Typography — and a live bug found while writing this

The app already uses **Inter** as its body font, which matches the site.
So the body needs no change.

But **`Playfair Display` is referenced in 48 files and no font asset is
bundled.** `pubspec.yaml` has `uses-material-design: true` and *no*
`assets:` block, and `google_fonts` is not a dependency. Neither
`Playfair Display` nor `Inter` is declared anywhere. (The only `.ttf`/`.otf`
files in the tree sit under `android/app/build/` — stale build output, not
source. There are zero fonts in source.)

This is **known and deliberate**. `pubspec.yaml` already says so:

> Fonts (Playfair Display + Inter) are NOT shipped in this build — they
> were declared in v2's pubspec but not included as assets, which would
> fail a release build. The theme references fontFamily by name; on device
> the text falls back to the system font. Acceptable for this test build.

So the app's real typography is whatever Android substitutes; the 5
Playfair refs in `app_theme.dart` are currently decoration rather than
design. Bundle the fonts as part of this port. **Do it before the colour
work** — once real Playfair lands, every heading changes width and height,
and the contrast measurements in this document would need rechecking
against the type that actually renders.

## Steps

### 1 — Verify first
- Screenshot the running app; confirm whether Playfair/Inter actually resolve.
- `flutter analyze` for a clean baseline before touching anything.

### 2 — Fonts (do this first; it changes what everything else looks like)
- Add `google_fonts` **or** bundle `.ttf` files under `assets/fonts/`.
- Declare in `pubspec.yaml`. Bundle is preferable: `google_fonts` fetches
  at runtime and fails offline, which matters for a field app.

### 3 — Colour constants
- Rewrite `lib/core/theme/app_colors.dart` to the target palette above.
- Keep `success` / `warning` / `error` semantics intact.

### 4 — Theme wiring
- `app_theme.dart`: check `ColorScheme.light(...)` at line 12 passes
  explicit values that must be updated in step with `AppColors`, or the
  two will drift.
- `chartLine` / `chartFill` / `chartIdealBand` follow the accent.

### 5 — The 7 hardcoded files
`login_screen.dart`, `missing_file_fallback.dart`,
`share_upload_result.dart`, `share_upload_screen.dart`,
`minerva_persona.dart`, `panel_detail_screen.dart`,
`my_reports_screen.dart`.

Pull each hex up into `AppColors` rather than editing in place, so the
next repaint is one file again.

### 6 — Border case to check
`app_colors.dart` is "pulled from htma_parent v2 — same brand DNA."
If `htma_parent` and `htma_parent_v2` should stay visually identical to
this app, changing only `htma_labs` breaks that. **Decide this first** —
it changes the scope from one repo to three.

### 7 — Build and verify
```bash
cd ~/.openclaw/workspace/htma_labs
flutter analyze          # exit 2 with no errors == info only; do NOT panic
flutter build apk --debug
adb -r install -r build/app/outputs/flutter-apk/app-debug.apk
```
Install with `-r` to preserve app data. Screenshot before/after.

## Risks

- **Never flash a daily-use app over ADB without a screenshot check first.**
  A bad theme lands as an unreadable screen, and the user has to live with
  it until the next build.
- **Semantic colour drift.** Repainting `success` green to the new accent
  teal would make "good" and "brand" indistinguishable.
- **The shared-brand question (step 6) is a scope question, not a
  technical one.** Resolve it before writing code.

## Source of truth for the design

`index.html` in this repo — the `/* ══ PALETTE v2 ══ */` block holds the
exact values, and the commit message for `4fd790a` records why each was
chosen.