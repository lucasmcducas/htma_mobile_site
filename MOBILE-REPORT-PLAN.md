# HTMA Labs Mobile — Report Scope & Learn Tab Plan

**Updated 2026-10-09.** Supersedes the four-report assumption in
`HANDOFF-report-pipeline.md`.

## Decision: TWO reports, not four

The canonical tuple is `VALID_TYPES = ("htma", "program", "supplement",
"advanced")` in `upload-reports.py:44`. Shipped scope is **two**:

| Report | Contents | Where it lives |
|---|---|---|
| **Supplement** | The dosage sheet — product, AM/NOON/PM amount — plus a short explanation of what each supplement does and why | In-app screen + downloadable PDF |
| **HTMA** | Major patterns and trends: oxidation rate, Na/K ratio, bowel pattern, calcium shell, and comparison against the previous test | In-app screen + downloadable PDF |

**Program is no longer a report.** It becomes the **Learn tab**.

`advanced` is left in the constant but has no producer and is not in
scope. Do not add a producer without Luke saying so.

### The HTMA report's "trends from last test"

Comparison against the prior panel is **derived data**, not matrix
content: it is a diff of two classifications the server already produced.
It therefore inherits no new secrecy burden — the matrix still never
crosses to the device.

Implementation needs a lookup of the patient's previous completed panel
and a per-pattern delta. Not yet built.

## Learn tab

Replaces the program report. Content is the existing
`htmapro.com/learn` library, re-presented mobile-natively rather than
linked out.

**Verified live 2026-10-09 — 109 articles across 8 categories:**

| Category | Slug | Articles |
|---|---|---|
| HTMA Fundamentals | `/learn/category/htma-fundamentals` | 16 |
| Nutritional Balancing | `/learn/category/nutritional-balancing` | 16 |
| Detoxification | `/learn/category/detoxification` | 14 |
| Mineral Patterns | `/learn/category/mineral-patterns` | 23 |
| Health Conditions | `/learn/category/health-conditions` | 15 |
| Advanced Topics | `/learn/category/advanced-topics` | 8 |
| Spiritual Development | `/learn/category/spiritual-development` | 7 |
| Parenting & Autism | `/learn/category/parenting-autism` | 10 |

Articles live at `/learn/article/<slug>`.

### Why this is better than a program PDF

The program content was *reference material* — diet, sauna, coffee enemas,
meditation, detox protocol. A PDF is read once and lost. A browsable,
searchable, category-navigable library gets revisited, and it is the one
part of the product that grows without anyone regenerating a report.

### Build notes

- **Render in-app from Markdown, do not WebView the site.** A WebView makes
  the phone a browser and inherits the site's nav, cookie banner and
  layout. Fetch article Markdown, render with `flutter_markdown` or
  `markdown_widget`.
- **Mini menu:** a category grid on open, then a drill-down. The 8
  categories with counts above are the natural tiles — no new taxonomy
  needed. Search across all 109 titles is high value and cheap.
- **Content source:** articles must be exposed as Markdown/JSON by the
  htmapro CMS or served as static files. The current site is a JS SPA and
  the article list is **not** reachable by plain `curl` — it needs the
  rendered DOM or a new content endpoint. **This is the one blocker.**
- Deep links back to `htmapro.com/learn` can be offered as a secondary
  "open in browser" affordance, not the primary UX.

## PDF generation — verified stack

Generated **on-device** with `pdf: ^3.13.1` (already locked), not
server-side. The app already reads `mobile.htma_supplement_protocols` over
RLS, so resolved per-patient doses are on the phone by design; the
**matrix** is what must never cross, and it doesn't.

Toolchain verified against the repo: AGP 9.0.1 / Kotlin 2.3.20 /
Gradle 9.1.0, Dart 3.12.2 / Flutter 3.44.2.

### Hard rules (each one verified against installed source)

1. **Always pass `maxPages` to `pw.MultiPage`.** Default is 20 and the
   check is inside `assert()` — `pdf-3.13.1/lib/src/widgets/multi_page.dart:184,217,292`
   literally says *"This is not checked with a Release build."* A 21-page
   report throws in debug and silently paginates unbounded in release.
2. **Bundle a `.ttf` as an asset.** The default theme is Type1
   Helvetica/Times/Courier, which silently drop `µ ≥ ± ° →` — exactly the
   notation used in dosing (`mg`, `mcg`, `iu`).
3. **Never use `PdfGoogleFonts`** for anything that must work offline; it
   fetches over the network at render time.
4. **`fl_chart` cannot render into a PDF.** It is a Flutter painting
   widget. Use `pw.BarChart` for the mineral chart with ideal-range bands.
5. **Never write the shared file into `cacheDir/share_plus`** — cleared at
   the start of every share, and the call throws.
6. **Add `ACTION_SEND` + `application/pdf` to the existing `<queries>`
   block** so Android 11+ package visibility lets share targets read the
   URI.
7. **`share_plus` is locked at 10.1.4** and `panel_export_repository.dart:146`
   uses the deprecated `Share.share()`. 13.3.1 is current and wants
   `SharePlus.instance.share(ShareParams(...))`; the AGP/Kotlin gate
   (>=8.12.1 / >=8.13 / 2.2.0) is cleared by this project.
8. `printing` is **not** in `pubspec.lock` — there is no preview/print
   path yet. Only add it if in-app preview is wanted; it is a heavy dep.

Text is vector and searchable (fonts are subsetted), so a 20–30 page
clinical report lands ~200 KB–1.5 MB — fine for WhatsApp and email.

## Matrix confidentiality

`github.com/lucasmcducas/htma-decision-matrix` was **public** until
2026-10-09 and served dose tables (`cal-mag-fusion 4·4·4`,
`slowox 1·0·0`, `thyro-spark 1·0·0`) plus thresholds `Ca<40, Mg<6, Na<25,
K<10` to anonymous curl. Now private; verified 404 from outside. Zero
forks.

Two exposures remain and are **not** fixed by repo privacy:

- **Git history** still contains every dose table. Only a rewrite removes
  them, and it needs a force-push. Clones taken before 2026-10-09 keep
  their copy permanently.
- **Thresholds are separately in the APK** —
  `htma_labs/lib/core/wilson/*.dart` (729 LOC) and
  `supabase/functions/htma-context/wilson_patterns.ts`. Classification
  was never secret. Only the dose layer was, and it is what leaked.

`tests/fixtures/` holds three real patient panels
(`anna_halquist_549762`, `luke_pryor_525969`, `phillips_850100`). Now
protected by repo privacy, but they travel with the repo if it is ever
shared or a collaborator added.

**Luke is not concerned about his name appearing in the matrix** — do not
raise it again. He is concerned about the dose values.

## Interpreter

`lab_pipeline/interpreter_service` requires `INTERPRETER_SHARED_SECRET`
for any off-box request and **refuses when it is unset** rather than
failing open. Loopback is exempt via the socket peer, never
`X-Forwarded-For`. Verified against a real socket on `0.0.0.0`: no secret
401, wrong secret 401, correct secret 200, `/healthz` 200. The 401 body
carries no `patient_report` key, so a refusal cannot leak a protocol.

## Enforcement invariant

`program_sections.py::_assert_no_dosing` bans any number followed by
caps/capsules/mg(?!%)/mcg/iu/units/drops/tablets/tsp/tbsp/ml/oz/grams —
`mg%` deliberately exempted. 6 of 17 sections are deliberately unwritten
(water, saunaTherapy, singleLightSpotTherapy, coffeeEnemas,
reflexology, spinalTwist).

A renderer should bind dose data and narrative data to **separate
sources** so the regex is a backstop, not the only defence.

## Still open

- **Learn content endpoint** — articles are not reachable by plain HTTP
  from the SPA. Blocks the Learn tab.
- **Previous-test diff** — the HTMA report's trend section needs it.
- **Report version stamping** — the writer upserts idempotently, so a
  regenerated report is indistinguishable from one a practitioner signed
  off on. Add a matrix-version stamp or content hash before selling to
  clinicians.