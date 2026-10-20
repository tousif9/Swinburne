# CHAT HISTORY – everything done in the cloud session (read with HANDOVER.md)

This is a step-by-step record of the long Claude Code cloud session with Tousif Akhand (ID 105822937) for
COS10005 Web Development, Assignment 1 ("Pl@netMatrix"), plus the start of Assignment 2 (JavaScript).
HANDOVER.md has the rules and the file map. This file has the story: what was sent, what was decided, what was done.

---

## 0. How the student likes to work (most important)

- "Ask me every time" before doing anything. When I once started tools without asking, the student stopped me
  ("stop brother relax"). Since then: explain the plan, wait for "yes".
- "Don't do anything by yourself – only do exactly what the assignment instructs."
- "Ask every time before creating a ZIP."
- Report edits: "don't ever touch one word other than that". After every edit I diffed the document paragraph by
  paragraph and reported exactly what changed.
- "Put exactly what I gave" – the student's wording goes in verbatim even with small errors (warn first).
- The student once said "you did more than what was asked" – keep answers and changes to the scope asked.
- The student prefers clear, short answers: "yes/no", then the list of items.

## 1. Early work (before the final report) – files in the repo root

- Built and refined the Pl@netMatrix site with the student (the old draft is in `assign1/` at the repo root).
- Wrote `PlanetMatrix-Project-Report.docx` and `PlanetMatrix-Report-Editable.docx` (natural-tone editable report).
- The student asked to trim the report "exactly as the brief says", then to explain the key features and
  enhancements in detail.
- Made a plain (no colour) site map: `sitemap-plain.png`, and explained how to capture one.
- Wrote `Video-Presentation-Guide.docx` and an 11–12 minute script `PlanetMatrix-Video-Script.docx`.
  Explained how to show the phone view (Microsoft Edge DevTools → device toolbar).
- Plant description documents: `Plant-Descriptions.docx`, `Plant-Descriptions-Safe.docx`.

## 2. Audits of the student's zips

The student sent several zips (1bf2e9d7, 9b24365c, 19dc5cdf, 3ad7925c, 5800bbe9, then 21a9a986). For each:
checked the brief, marking scheme, case study, PlantsData file and sample profile.
- Confirmed using `<link>` for Google Fonts (not `@import`) – the student asked if `@import` was allowed.
- W3C validation: 0 errors / 0 warnings (the student validated too).
- Acknowledgement credit counts matched (103 / 28 / 5 / 7 / 25).
- Risks pointed out (student's choice to keep): Monotes and Cryptocarya are not in PlantsData; phone styles are in
  the single style.css (no separate mobile CSS).

## 3. Putting screenshots into the student's final report (FINAL11_Report_COS10005_TousifAkhand.docx)

Request: "don't change anything inside the report, just put the images", code images must look exactly like the
student's Notepad++ screenshots, website shots clean like the student's example, "take as much time as you need".
- Filled all 86 placeholders ("INSERT CODE/WEBSITE SCREENSHOT N HERE").
  - 89 Notepad++-style code images (`tools/screenshots/npp.py`).
  - 66 website screenshots (desktop 1760 px wide; phone = iPhone 12 Pro).
- The student supplied the screenshots that could not be automated:
  - 30a and 30b: the Google Map.
  - 36: the native dropdown.
  - 4: the search box.
  - 74a and 74b: the identify page on a phone.
  - 85: search suggestions.
  - 87: the map with the back-to-top button.
  - 58 reuses 30a and 30b.
- Many crops were redone until clean (cut paragraphs, sticky-nav overlap, rotating banner word mid-slide, etc.).
- Then audited the report against all PDFs.
  - Fixed the @import mismatch using 3 sentences the student humanised and gave back.
  - Removed "COS10005 Assignment 1 · Tousif Akhand (105822937)" from the footer; kept page numbers only.
  - Word showed `{ TOC … }`: that's a field-code view setting. Fix: Alt+F9, or right-click → Update Field.
- Naming: the brief says both "enhancement1.html" and "enhancements.html". Final decision by the student:
  "do as the brief says" → keep **enhancement1.html**.

## 4. Final report edits (student's own rewritten file 1dd249be…_1_1.docx)

The student rewrote much of the text, then asked for exactly these changes (all done and diff-verified):
1. Italic → normal everywhere. This covered 10 italic runs and the Heading 3 style.
2. Table numbers/captions → normal text: Caption style set to not italic, 11 pt.
3. Code captions in the student's format: `index.html code lines from 38 to 59`, with no word "Figure".
   - The student had already added captions; I normalised all of them.
   - 4 captions claimed ranges the images did not show, so I corrected them to match the images.
   - "enhancement.html" in a caption became enhancement1.html.
4. References → IEEE style `[1]…[7]`, keeping the current order (there are no in-text citations), "Accessed: Sep. 2026".
5. "we" → "I" and "our" → "my" (51 places, "we are" → "I am").
   - Left website quotes unchanged: "Where Our Photos Come From", "How should we reply?", "Why We Credit Sources".
   - "us" was not changed.
6. Writing check (tell only, don't change). I gave a list of wrong facts, unclear sentences and typos.

## 5. The student switched the final website to Website.zip

- Only `index.html` differed: the self-closing `/>` endings were removed, so it went from 492 to 483 lines and is still valid.
- The student: "you have to consider website.zip". So I:
  - re-rendered the 14 index.html code images and updated 7 captions
  - updated about 30 index.html line numbers in Tables 2, 3, 4 and 15
  - removed `/>` from 3 code lines in Tables 28, 31 and 32
- No other wording was touched; this was confirmed to the student.

## 6. The four mistakes that could cost marks (the student fixed them in Word)

1. Table 1: enhancement.html → **enhancement1.html**. The student first typed "Enhancement1.html" and then fixed it to lowercase.
2. Table 2: style/style.css → **styles/style.css**.
3. Table 28 row 1: the menu is listed **after** the checkbox (that's why `~` works). The first fix duplicated a clause; that was fixed too.
4. Intro paragraph 2 ended with a comma → now "…named Lauraceae. The former has winged fruits while the latter has fleshy berries."

Still in the report on purpose or as a minor point:
- One "We will also find that…" in Table 4. Harmless; the student was told.
- Other smaller writing issues from the writing check. The student was told they're unlikely to cost marks.

## 7. Final check (last files: Website.zip c61de96e…, Report_105822937_TousifAkhand.docx 51f2465f…)

- Website matches every marking-scheme row:
  - index: menu, header, footer mailto; CSS background, menu colour, footer italic and centred.
  - Identify, Explorer + explore1–3, and Contributor: h1/h2, ol, dl, 2+ sections, aside, table, figure + figcaption.
  - CSS: aside 30vw, float right, coloured border; h1 font shorthand; footer 100% wide.
  - Contribute: fieldsets and validation.
  - Enquiry: radio, checkbox, select, email/tel/date.
  - Profile: table and mailto.
  - style.css: all selector types, valid.
  - 15 enhancements.
  - No inline styles; alt text on every image; credits page.
- W3C: 0 errors / 0 warnings on all 12 HTML pages and style.css. No broken links. The video link is in all 12 footers.
- Report: all four fixes in, 166 images intact, Word validation passed, no tracked changes or comments.
- Open items told to the student:
  - The zip's inner folder must be **assign1** and the zip **tousifakhand_assign1.zip**. The uploaded one used a folder called "Website".
  - Update the Contents page in Word.
  - Submit each form once to check the Swinburne test page shows all values.
  - Check the YouTube link works logged out.
  - Print the report, marking scheme and cover sheet, and fill in the Declaration.
- The final website and final report are saved in `A1-final/`.

## 8. Assignment 2 (JavaScript) – started

- The student will send the A2 brief and marking scheme when received. Materials so far are in `A2/materials/`:
  Week 7 (external JS, header comment, window.onload = init, getElementById, onclick, prompt/alert/textContent),
  Week 8 Demo 1 (functions, parameters, return, scope) and Demo 2 (if/else, switch, loops, arrays).
  Details are in HANDOVER.md.
- A friend's sample report was sent as a layout example for the A2 report. It's from COS10026, a PHP group project.
  The layout is described in HANDOVER.md. The file was not saved to the repo, and its wording must never be copied.
  The student wants their own report to be more enhanced, advanced and detailed than the sample.
- Next step when the brief arrives: make a checklist of every requirement, say what the current site already
  covers and what is new, and **ask before writing any code**.
