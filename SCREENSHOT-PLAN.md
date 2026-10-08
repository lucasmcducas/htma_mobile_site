# Screenshot plan: a small phone in each middle section

Status: **plan only, nothing built.** Written 2026-10-07 while the middle
sections were being re-pointed from the report to the program.

Goal: each section of `htma.mobile` below the store buttons gets a small
phone mockup — like the hero, but sized down — showing a real screenshot
of the tab whose functionality matches that section.

Package on device: `com.htmapro.htma_labs` (HTMA Labs), not
`com.htmapro.htma_mobile`. Both are installed; the marketing site depicts
the labs app.

## The blocker: four of seven tabs are empty

Measured on the phone 2026-10-07, all seven tabs tapped and read:

| tab | state |
|---|---|
| Today | "No results yet" — upload / order prompt |
| HTMA | "No HTMA report yet" |
| Supps | "No HTMA report yet" — *"your practitioner's protocol will appear here"* |
| Plan | "No HTMA report yet" |
| **Ask** | populated — "Ask your data", 3 suggestion cards |
| **Life** | populated — Sleep 21:00 / 7.0h, Daily Practices toggles, sauna slider |
| **Group** | populated — real community posts |

Mapped to the sections:

| section | needs | usable |
|---|---|---|
| Track | Today / Supps | ❌ empty |
| Ask | Ask | ✅ |
| Program | Plan | ❌ empty |
| Why hair | HTMA | ❌ empty |
| Contact | — | n/a |

**Only one of four has a usable screenshot.** The empty states say
*"No HTMA report yet"* — the opposite of what those sections claim, so
shipping them as-is would undercut the copy beside them.

## Options

**A. Seed a panel.** Upload a synthetic report so Today / HTMA / Supps /
Plan all populate. Use obviously-fake values; delete after capture.
Only option that covers all five sections.

**B. Fixture/demo mode** if one exists in the Flutter app — cleaner, no
pollution of the real account. Not yet confirmed to exist.

**C. Screenshot only what exists** — phone in Ask and Life, typography
elsewhere. Honest, but the three sections doing the selling lose their
visual proof.

## Capture recipe that works

`uiautomator dump` returns nothing — Flutter renders to a canvas, so there
are no accessibility nodes to read. Coordinate taps plus a vision call is
the working path.

```bash
S=100.116.78.53:5555          # Tailscale IP, adb-tailscale skill
adb -s $S exec-out screencap -p > /tmp/appcaps/x.png
```

**The tab bar is at y ≈ 2058–2160, not 2200.** My first attempt tapped
2200 and produced three byte-identical images — md5 equality is the tell
that a tap missed. Verify each capture differs before reading it.

Tab centres across 1080px width (7 tabs): 77 · 231 · 386 · 540 · 694 ·
849 · 1003, tapped at y=2110.

Two things to expect:

- `monkey -p …LAUNCHER` reported success but left the notification shade
  focused. Start with `am start -n <pkg>/.MainActivity` and confirm with
  `dumpsys window | grep mCurrentFocus` instead.
- A ~15KB screencap means a blank or splash screen, not a failure. Real
  screens run 110–260KB.

## Screenshots already captured

`/tmp/appcaps/` — `t-Ask`, `t-Life` (as `t-Supps`), `t-Plan`, `t-Group`,
`t-Today`, `labs.png`. Ephemeral; re-capture rather than rely on these.

## Still to capture once data exists

- **Today** with a populated protocol and a non-zero streak — the section
  claims "doses ticked off", so the screenshot must show ticks, not an
  empty 0/8
- **HTMA** with a real panel — the chart view, for "Why hair"
- **Supps** with a practitioner's protocol
- **Program** with a plan
- **Ask** voice/dictation in the listening state — this is the one thing
  worth proving for the "type or say it" step, and the only way to show
  voice exists at all

## Notes

The hero phone is a hand-built HTML mockup, not a screenshot. These would
be real pixels, so the mockup and the captures will not match exactly —
worth deciding whether that reads as inconsistency. The mockup's seven tab
labels match the app's seven, so the bar itself will line up.