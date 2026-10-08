#!/usr/bin/env python3
"""Assemble the restructure preview from the real index.html.

The hero (including the phone mockup) is copied VERBATIM — the preview
exists to show a different middle, so the top must not drift. Only the
slice between the store CTA and the footer is replaced.

usage: build_preview.py <index.html> <preview-out.html>
"""
import re, sys

src, dst = sys.argv[1], sys.argv[2]
h = open(src, encoding="utf-8").read()

head = h[:h.find("</style>")]

top_start = h.find('<section class="hero">')
foot_start = h.find("<footer")

# The middle boundary MOVES as the middle is rewritten. The old page used
# <section class="section" id="reads">; the current one uses the r* namespaced
# <section class="rsec rsec--paper" id="reads">. Accept either, and fail loudly
# if neither is found — a silent find() == -1 makes `top` swallow the entire
# middle and then re-inject a second copy (an 80k-char page from a 63k source).
MID_MARKERS = (
    '<section class="rsec rsec--paper" id="reads">',
    '<section class="section" id="reads">',
)
mid_start = -1
for m in MID_MARKERS:
    if m in h:
        mid_start = h.find(m)
        break
if not (0 <= top_start < mid_start < foot_start):
    sys.exit(f"slice markers out of order: top={top_start} mid={mid_start} "
             f"footer={foot_start} — refusing to build")

top = h[top_start:mid_start]        # hero + store CTA — verbatim
tail = h[foot_start:]               # footer onwards

# ── fonts ──────────────────────────────────────────────────────────
# Instrument Serif is a high-contrast editorial face; Bitter is a warm
# slab with actual presence. Both are quiet on Google Fonts, which is
# precisely why generated pages reach for Inter and Newsreader instead.
head = re.sub(
    r'<link href="https://fonts\.googleapis\.com/css2\?[^"]*"',
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Newsreader:ital,opsz,wght@0,6..72,200..500;1,6..72,200..400'
    '&family=Instrument+Serif:ital@0;1'
    '&family=Bitter:ital,wght@0,300;0,400;0,500;0,700;1,400'
    '&family=Space+Grotesk:wght@400;500;700'
    '&display=swap"',
    head, count=1)

# Do NOT redefine --serif or --label: the hero above inherits them, and
# pointing them at the preview fonts silently restyles the top. Leave the
# page's own variables exactly as index.html defines them and give the
# preview sections their own namespaced stacks instead.
head = head.replace(':root{', ':root{\n  --rserif:"Instrument Serif","Newsreader",Georgia,serif;\n'
                                  '  --rslab:"Bitter",Georgia,serif;\n'
                                  '  --rsans:"Space Grotesk",-apple-system,"Segoe UI",Roboto,sans-serif;')

# ── the middle ─────────────────────────────────────────────────────
# What read as generated was structural, not cosmetic: five sections
# that each led with the same eyebrow + headline + right-hand paragraph,
# stacked in one column. A different typeface cannot fix repetition of
# layout — that repetition is the tell. So:
#
#   · only two sections use a head pattern; the rest lead with content,
#     an oversized figure, or a statement
#   · "does" breaks the column with a margin note in the gutter
#   · "method" is the one full-bleed dark beat, on the strongest line
#   · three families, each with one job: serif display, slab for the
#     numbered feature titles, sans for anything informational
MID = r'''
<!-- ══ reads — the chart as a document ═════════════════════════ -->
<section class="rsec rsec--paper" id="reads">
  <div class="rwrap">
    <p class="reye">What it reads</p>
    <h2 class="rh2 rh2--wide">A snapshot tells you what is moving. A chart tells you what is stored.</h2>

    <div class="rpanelwrap">
      <table class="rpanel">
        <caption>Sample panel — 31 values, 5 shown</caption>
        <thead><tr>
          <th scope="col">Element</th>
          <th scope="col" class="num">Reference</th>
          <th scope="col" class="num">Reading</th>
          <th scope="col">Flag</th>
        </tr></thead>
        <tbody>
          <tr><th scope="row">Sodium</th>   <td class="num">70 — 200</td><td class="num">118</td><td><span class="rflag rflag--hi">Fast mixed</span></td></tr>
          <tr><th scope="row">Calcium</th>  <td class="num">80 — 200</td><td class="num">96</td> <td><span class="rflag rflag--ok">In range</span></td></tr>
          <tr><th scope="row">Magnesium</th><td class="num">28 — 100</td><td class="num">22</td> <td><span class="rflag rflag--lo">Low</span></td></tr>
          <tr><th scope="row">Zinc</th>     <td class="num">60 — 180</td><td class="num">71</td> <td><span class="rflag rflag--ok">In range</span></td></tr>
          <tr><th scope="row">Copper</th>   <td class="num">50 — 170</td><td class="num">188</td><td><span class="rflag rflag--hi">High</span></td></tr>
        </tbody>
      </table>

      <aside class="rnote">
        <p>Hair tissue mineral analysis records deposition over roughly three
        months of growth. The app reads the relationships between the numbers,
        which is the only part that means anything.</p>
      </aside>
    </div>
  </div>
</section>

<!-- ══ does — gutter note + slab titles, no headline pairing ═════ -->
<section class="rsec rsec--card" id="does">
  <div class="rwrap">
    <div class="rdoes">
      <div class="rdoes__head">
        <p class="reye">What it does</p>
        <p class="rdoes__note">A chart with forty numbers on it is not
        information. The app finds the patterns, tells you which are worth
        acting on, and keeps tracking them across retests.</p>
      </div>

      <ol class="rsteps">
        <li>
          <span class="rnum">01</span>
          <h3>Read your chart</h3>
          <p>Upload a report from any lab, or have one sent to you directly.
          No re-keying forty values by hand.</p>
        </li>
        <li>
          <span class="rnum">02</span>
          <h3>See the patterns</h3>
          <p>Ratio patterns like Four Lows and adrenal or thyroid groupings,
          flagged in plain language rather than mineral shorthand.</p>
        </li>
        <li>
          <span class="rnum">03</span>
          <h3>Follow a protocol</h3>
          <p>Recommendations drawn from your own results, with supplement
          doses and a day-to-day plan you can actually keep.</p>
        </li>
        <li>
          <span class="rnum">04</span>
          <h3>Send it on</h3>
          <p>Share the report with your practitioner in one tap, and compare
          side by side across retests.</p>
        </li>
      </ol>
    </div>
  </div>
</section>

<!-- ══ blood — a straight two-up, no head pairing ════════════════ -->
<section class="rsec rsec--sage" id="blood">
  <div class="rwrap">
    <p class="reye">Why hair</p>
    <div class="rcompare">
      <div class="rcompare__side">
        <h3>Blood</h3>
        <p class="rcompare__big">A moment</p>
        <p>Accurate, cheap and fast. But it only catches what has changed in
        the last few hours or days, so an early deficiency can look normal.</p>
      </div>
      <div class="rcompare__side rcompare__side--hi">
        <h3>Hair</h3>
        <p class="rcompare__big">Three months</p>
        <p>Records deposition as the hair grows, so a pattern that blood
        misses becomes visible. Harder to interpret — and useless without
        someone who knows how to read it.</p>
      </div>
    </div>
  </div>
</section>

<!-- ══ method — the page's one dark beat, on its strongest line ═══ -->
<section class="rsec rsec--warm">
  <div class="rwrap">
    <p class="reye">The method</p>
    <p class="rstatement">Forty years old.<br><em>Not a trend.</em></p>
    <dl class="rnotes">
      <div><dt>Sample</dt><dd>A lock of hair, cut close to the scalp. No needle, no fasting, no preparation.</dd></div>
      <div><dt>Window</dt><dd>Roughly three months of deposition — long enough for a pattern, short enough to show change after a retest.</dd></div>
      <div><dt>Method</dt><dd>ICP-MS spectrometry, the same technique used for soil and water testing.</dd></div>
    </dl>
  </div>
</section>

<!-- ══ contact — the disclaimer becomes the heading ══════════════ -->
<section class="rsec rsec--paper rsec--last" id="contact">
  <div class="rwrap">
    <p class="reye">Contact</p>
    <h2 class="rh2">Screening and record-keeping.<br>Not a diagnosis.</h2>

    <div class="rcontact">
      <p class="rlede">Every number on a mineral chart is a measurement, not a
      verdict. For interpretation, talk to the practitioner who ordered your
      test. If the app is showing you a wrong number, say so.</p>
      <form class="rform" onsubmit="event.preventDefault()">
        <label for="pv-em">Email</label>
        <input id="pv-em" type="email" placeholder="you@example.com">
        <label for="pv-ms">Message</label>
        <textarea id="pv-ms" rows="3" placeholder="What happened?"></textarea>
        <button type="submit">Send</button>
      </form>
    </div>
  </div>
</section>
'''

# ── preview-only stylesheet, namespaced so it cannot leak upward ────
EXTRA = r'''

/* ══ PREVIEW ONLY ══════════════════════════════════════════════════
   Restructure of the middle sections. The hero above is untouched.
   Every rule is namespaced (r*) so nothing reaches back into it.
   ═══════════════════════════════════════════════════════════════ */
.pvtag{
  position:fixed;inset:auto 0 0 0;z-index:99;
  font-family:var(--rsans);font-size:.7rem;letter-spacing:.1em;
  text-transform:uppercase;background:#141210;color:#F4F1EA;
  padding:8px 14px;text-align:center;
}
.rwrap{max-width:1320px;margin:0 auto;padding-inline:var(--g)}
.rsec{padding-block:clamp(56px,7vw,98px)}
.rsec--paper{background:var(--paper)}
.rsec--card{background:#FFFDF8}
.rsec--sage{background:#DDE4DC}
.rsec--warm{background:#E7E1D3;color:#141210}
.rsec--last{padding-bottom:clamp(80px,10vw,150px)}

.reye{
  font-family:var(--rsans);font-size:.71rem;font-weight:500;
  letter-spacing:.16em;text-transform:uppercase;color:var(--ink-faint);
  margin:0 0 18px;
}
.rsec--warm .reye{color:var(--ink-faint)}

/* ── reads ───────────────────────────────────────────────────────── */
.rh2{
  font-family:var(--rserif);font-weight:400;letter-spacing:-.016em;
  line-height:1.04;margin:0;
}
.rh2--wide{font-size:clamp(2.1rem,5.2vw,4rem);max-width:19ch}

.rpanelwrap{display:grid;gap:clamp(30px,4vw,64px);margin-top:clamp(38px,5vw,70px)}
@media(min-width:960px){
  .rpanelwrap{grid-template-columns:minmax(0,1.55fr) minmax(0,1fr)}
}
.rnote{
  font-family:var(--rsans);font-size:1rem;line-height:1.66;color:var(--ink-soft);
  align-self:end;border-top:1px solid var(--rule-strong);padding-top:22px;
}
.rnote p{margin:0;max-width:40ch}

.rpanel{width:100%;border-collapse:collapse;font-family:var(--rsans)}
.rpanel caption{
  text-align:left;font-family:var(--rsans);font-size:.7rem;font-weight:500;
  letter-spacing:.13em;text-transform:uppercase;color:var(--ink-faint);
  padding-bottom:18px;
}
.rpanel th,.rpanel td{
  padding:17px 16px 17px 0;border-bottom:1px solid var(--rule);
  font-weight:400;text-align:left;font-size:.95rem;
}
.rpanel thead th{
  font-size:.72rem;letter-spacing:.05em;color:var(--ink-faint);
  padding-bottom:11px;border-bottom-color:var(--rule-strong);
}
.rpanel tbody th{font-weight:500;color:var(--ink)}
.rpanel tbody tr:last-child th,.rpanel tbody tr:last-child td{border-bottom:0}
.rpanel .num{font-variant-numeric:tabular-nums;text-align:right;color:var(--ink-soft)}
.rflag{font-size:.79rem;letter-spacing:.02em;white-space:nowrap}
.rflag--hi{color:#9A5B12}
.rflag--ok{color:#2D6B4E}
.rflag--lo{color:#41607A}

/* ── does: margin note in the gutter, slab feature titles ────────── */
.rdoes{display:grid;gap:clamp(34px,4.4vw,72px)}
@media(min-width:940px){
  .rdoes{grid-template-columns:minmax(0,.82fr) minmax(0,2.4fr)}
}
.rdoes__head .reye{margin-bottom:20px}
.rdoes__note{
  font-family:var(--rsans);font-size:1rem;line-height:1.66;
  color:var(--ink-soft);margin:0;max-width:38ch;
  padding-left:18px;border-left:2px solid var(--accent);
}
.rsteps{list-style:none;margin:0;padding:0;display:grid;gap:clamp(30px,3.4vw,46px)}
@media(min-width:640px){.rsteps{grid-template-columns:1fr 1fr}}
.rsteps li{display:block}
.rsteps .rnum{
  display:block;font-family:var(--rsans);font-size:.71rem;font-weight:600;
  letter-spacing:.16em;color:var(--accent);
  padding-bottom:12px;margin-bottom:16px;border-bottom:1px solid var(--rule);
}
/* Bitter is a warm slab. Nothing else on the page uses it, so the four
   feature titles read as a set rather than as four more headlines. */
.rsteps h3{
  font-family:var(--rslab);font-weight:600;letter-spacing:-.012em;
  font-size:clamp(1.3rem,2.1vw,1.72rem);line-height:1.16;margin:0 0 10px;
}
.rsteps p{
  font-family:var(--rsans);font-size:.95rem;line-height:1.6;
  color:var(--ink-soft);margin:0;max-width:36ch;
}

/* ── blood: straight two-up, no eyebrow/headline pairing ──────────── */
.rcompare{display:grid;gap:clamp(34px,4.6vw,80px);margin-top:clamp(34px,4.6vw,64px)}
@media(min-width:820px){.rcompare{grid-template-columns:1fr 1fr}}
.rcompare__side h3{
  font-family:var(--rsans);font-size:.71rem;font-weight:500;
  letter-spacing:.15em;text-transform:uppercase;color:#4A5A50;
  margin:0 0 12px;
}
.rcompare__big{
  font-family:var(--rserif);font-size:clamp(2.2rem,5.6vw,3.9rem);
  letter-spacing:-.02em;line-height:1;margin:0 0 18px;color:#141210;
}
.rcompare__side--hi .rcompare__big{color:#1F5A48}
.rcompare__side > p:last-child{
  font-family:var(--rsans);font-size:1rem;line-height:1.64;
  color:#3E4A42;margin:0;max-width:42ch;
}

/* ── method: the dark statement ──────────────────────────────────── */
.rstatement{
  font-family:var(--rserif);font-weight:400;
  font-size:clamp(2.6rem,8vw,5.6rem);line-height:1.02;
  letter-spacing:-.024em;margin:0;color:#141210;
}
.rstatement em{font-style:italic;color:#1F5A48}
.rnotes{
  margin:clamp(38px,5vw,64px) 0 0;display:grid;gap:0;
  border-top:1px solid var(--rule-strong);
}
@media(min-width:880px){.rnotes{grid-template-columns:repeat(3,1fr)}}
.rnotes > div{padding:24px 0}
.rnotes dt{
  font-family:var(--rsans);font-size:.71rem;font-weight:500;
  letter-spacing:.14em;text-transform:uppercase;color:var(--ink-faint);margin:0 0 10px;
}
.rnotes dd{
  margin:0;font-family:var(--rsans);font-size:.96rem;line-height:1.6;
  color:var(--ink-soft);max-width:34ch;
}

/* ── contact ─────────────────────────────────────────────────────── */
.rcontact{
  display:grid;gap:clamp(30px,4vw,64px);margin-top:clamp(34px,4.4vw,58px);
}
@media(min-width:880px){.rcontact{grid-template-columns:1fr 1fr}}
.rlede{font-family:var(--rsans);font-size:1rem;line-height:1.64;color:var(--ink-soft);margin:0;max-width:44ch}
.rform{display:grid;gap:8px;max-width:440px}
.rform label{
  font-family:var(--rsans);font-size:.7rem;font-weight:500;
  letter-spacing:.13em;text-transform:uppercase;color:var(--ink-faint);margin-top:6px;
}
.rform input,.rform textarea{
  font-family:var(--rsans);font-size:.95rem;color:var(--ink);
  background:#FFFDF8;border:1px solid var(--rule);border-radius:0;padding:11px 13px;
}
.rform input:focus,.rform textarea:focus{outline:2px solid var(--accent);outline-offset:1px}
.rform button{
  justify-self:start;margin-top:12px;
  font-family:var(--rsans);font-size:.87rem;font-weight:600;
  background:var(--accent);color:#FFFDF8;border:0;
  padding:13px 30px;border-radius:999px;cursor:pointer;
}
.rform button:hover{background:#1F5A48}

@media(max-width:720px){
  .rpanel thead{display:none}
  .rpanel tbody th,.rpanel tbody td{padding:12px 8px 12px 0}
}
'''

# index.html already owns the r* middle styles, so appending EXTRA would
# duplicate every rule. Only inject rules that are not already present,
# and assert the result is single-valued afterwards.
import re as _re
extra = EXTRA
# Remove whole rules (not just their opening brace) that index.html
# already defines, so the preview cannot shadow them with a second copy.
# NB: these are LITERAL substrings for the `in` test. A raw regex like
# r"\.rsec--paper\{" never matches a plain string, so the de-dup silently
# did nothing and every rule shipped twice.
for _sel, _pat in ((".rsec--paper{", r"^\.rsec--paper\{[^}]*\}\n"),
                   (".rstatement{",    r"^\.rstatement\{[^}]*\}\n"),
                   (".pvtag{",         r"^\.pvtag\{[^}]*\}\n")):
    if _sel in head:
        extra = _re.sub(_pat, "", extra, count=1, flags=_re.M)

out = (head + extra + "\n</style>\n</head>\n<body>\n"
       + top + MID + tail
       + '\n<div class="pvtag">Structure preview — hero untouched · index.html not modified</div>\n')

for rule in (".rsec--paper{", ".rstatement{"):
    n = out.count(rule)
    if n != 1:
        sys.exit(f"rule {rule} appears {n}x in the built preview — aborting")
open(dst, "w", encoding="utf-8").write(out)
print(f"  wrote {dst}  ({len(out)} chars)")
print("  hero copied verbatim:", top == h[top_start:mid_start])
print("  phone present:", 'class="phone"' in out)
print("  footer present:", "<footer" in out)