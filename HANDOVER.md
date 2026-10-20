# HANDOVER – read this first

Student: **Tousif Akhand**, ID **105822937**, student email 105822937@students.swinburne.edu.my
Unit: **COS10005 Web Development**, Swinburne Sarawak, Semester 2 2026.
Website: **Pl@netMatrix** – a citizen-science site about Malaysian plants
(2 families: Dipterocarpaceae and Lauraceae, 4 genera, 8 species).

## Rules the student set (always follow)

1. **Ask before every action.** Explain what you will do and wait for "yes".
2. **Only do exactly what the brief / the student asks** – nothing extra, no "improvements" on your own.
3. When the student gives wording, **put it in exactly as given** (warn first if there is a mistake, then still use their words).
4. When editing the report: **do not touch any word** other than what was asked. Verify with a paragraph-by-paragraph diff afterwards.
5. **Ask before creating any zip.** Never push without being asked.
6. Use the friend's sample report (see below) **for layout only – never copy its wording** (plagiarism risk).

## What is where

| Path | What it is |
|---|---|
| `A1-final/tousifakhand_assign1/assign1/` | **Final Assignment 1 website** (exact copy of the student's last Website.zip, 120 files). Already in the folder layout the brief requires. |
| `A1-final/Report_105822937_TousifAkhand.docx` | **Final Assignment 1 report** as submitted by the student. |
| `assign1/` (repo root) | Older draft of the site from earlier work – **not** the final version. |
| `*.docx`, `sitemap-plain.png` (repo root) | Earlier drafts: project report, editable report, video script, video guide, plant descriptions. |
| `A2/materials/` | Assignment 2 (JavaScript) class materials received so far (see below). |
| `tools/screenshots/` | Tools that made the report screenshots (see "Tools"). |
| `tools/gfonts/` | Local copies of the site's Google Fonts, used when taking website screenshots offline. |

## Assignment 1 – DONE

- HTML5 + CSS3 only. 12 pages: index, explore, explore1 (Families), explore2 (Genera), explore3 (Species),
  identify, contributor, contribute, enquiry, profile, enhancement1, acknowledgement; one `styles/style.css`.
- Validated: 0 errors / 0 warnings (W3C Nu validator, HTML + CSS). No broken links. YouTube video link in every footer.
- The page is named **enhancement1.html** (the student chose to follow the brief's Section Three name).
- index.html has **no** self-closing `/>` (483 lines). The report's index.html line numbers and code screenshots match this.
- Submission naming the brief requires: folder **`assign1/`** (case sensitive) inside **`tousifakhand_assign1.zip`**.
- Report format that the student liked: cover (unit/code/semester + Member Name/ID table), Contents, numbered sections,
  Notepad++-style code screenshots with line numbers, clean website screenshots, a caption under each image
  (code captions: `<file> code lines from A to B`, normal text, no "Figure" word), tables explaining code by line
  number, IEEE references `[1] …`, footer with page number only, "I/my" (not "we/our").

## Assignment 2 – JavaScript (in progress, brief NOT received yet)

The student will send the A2 brief + marking scheme later. Assignment 2 most likely builds on the Pl@netMatrix site.
When the brief arrives: make a requirement checklist, map what exists vs what is needed, and **ask before coding**.

### Class conventions to follow (from the lecture materials in `A2/materials/`)

**Week 7 (`week7/`)** – external JS only: `<script src="file.js"></script>` in `<head>`.
JS header comment block on every file:
```
/* Filename: ...
   Purpose : ...
   Target html: ...
   Author: Tousif Akhand
   Date written: ...
*/
```
plus a one-line comment above each function.
Start-up with `window.onload = init;` (no brackets) and `function init() { ... }`.
Get elements with `var x = document.getElementById("id");`.
Events in DOM-property style: `x.onclick = handlerName;` (no brackets).
Output with `prompt()`, `alert()`, `element.textContent = ...`.
Handout slips not to copy: "getInputInfor" typo; `outputMessage` used without `var`.

**Week 8 Demo 1 (`week8_demo1/`)** – string concatenation with `+`, parameters, `return`, variable scope
(`var` inside a function = local; no `var` = global).

**Week 8 Demo 2 (`week8_demo2/`)** – `if/else`, `else if` chains, `&&` / `||`, `switch` with `break` and `default`,
`while`, `do...while`, `for`, `for...in`, arrays (`new Array(...)`, `.length`), nested loops, `"\n"`, `Math.random()`.

House style for A2 code: always declare with `var`; convert `prompt()` input with `Number()` before comparing;
keep all JS in separate `.js` files (no inline JS, no `onclick=""` attributes in HTML).

### Report plan for A2 (student wants it MORE detailed than the friend's sample)

The friend's sample (COS10026, a different unit, PHP group project) was laid out as:
cover + Member Name/ID → Contents → Introduction → The Website → Contribution (one sub-heading per file:
screenshot + paragraph) → Key/Innovative features (code screenshots + paragraph) → Reflection → Discussion
(privacy/security) → Conclusion. It had no line numbers, no code tables, no references.
The sample file itself was **not** saved to the repo on purpose (someone else's work).

For the student's report, keep everything from the A1 report format above, follow the A2 brief's required sections
first, and add: each JS function explained (trigger → elements read → checks → output), testing evidence
(screenshots of valid and invalid input), a mapping of features to the brief's requirements, and a reflection
with real problems that were solved.

## Tools (`tools/screenshots/`)

Python 3 + Playwright (`pip install playwright pillow`, then `playwright install chromium`, or set `CHROME_PATH`
to an existing Chrome/Chromium). The site path defaults to `A1-final/tousifakhand_assign1/assign1`;
set env `SITE=<folder>` to point at another version (for example the A2 site).

- `npp.py` – draws code exactly like Notepad++'s default theme (line numbers, fold margin, tab bar, HTML/CSS colours).
  Uses `fonts/CourierPrime*.woff2` as a stand-in for Courier New. It does **not** colour JavaScript yet – add a
  `lex_js` (keywords blue bold, strings grey, comments green, numbers orange, operators bold) before using it for A2.
- `shot_code.py` – `render([(name, file, first_line, last_line), ...], out_dir)` → PNG per code chunk (1100 px wide at 2× scale).
- `code_jobs.py` – which line ranges went into which A1 report placeholder; `chunks()` splits long ranges (max 56 lines) at clean breaks.
- `shot_web.py` – website screenshots: desktop 1760 px wide, phone = iPhone 12 Pro (390×844 @2×) with rounded corners on #3A3A3A.
  Google Fonts are served from `tools/gfonts`; it turns off smooth scrolling and lazy loading before capturing.
- `build_doc.py`, `edit.py`, `update_index.py`, `imgs.py` – the scripts used to put images into the A1 report and make the
  requested edits (kept as reference; they point at old temporary paths).

Validator: the W3C Nu checker (`vnu.jar`) is not stored here (60 MB). Get it from
https://github.com/validator/validator/releases (or `npm i vnu-jar`) and run
`java -jar vnu.jar --also-check-css *.html styles/style.css`.

Word files: edit `word/document.xml` directly and keep everything else byte-identical; check afterwards with a
paragraph diff and the docx validator. LibreOffice could not open files in the old environment.
