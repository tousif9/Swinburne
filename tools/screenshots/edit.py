"""Apply only the requested changes to the user's final report."""
import re, html, zipfile, os, sys

SRC, OUT = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(SRC)
doc = zin.read('word/document.xml').decode('utf-8')
sty = zin.read('word/styles.xml').decode('utf-8')
log = []

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def ptext(p):
    return html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)</w:t>', p)))

# ---------------------------------------------------------------- 1. italic -> normal
# direct italics on runs
n_before = len(re.findall(r'<w:i/>', doc))
doc = doc.replace('<w:i/><w:iCs/>', '').replace('<w:i/>', '')
log.append(f'direct italic runs removed: {n_before}')
# Heading 3 style is italic by definition
h3 = re.search(r'<w:style [^>]*w:styleId="Heading3".*?</w:style>', sty, re.S).group(0)
sty = sty.replace(h3, h3.replace('<w:i/>', ''))
# ---------------------------------------------------------------- 2. captions normal text (not italic, 11 pt)
cap = re.search(r'<w:style [^>]*w:styleId="Caption".*?</w:style>', sty, re.S).group(0)
cap2 = (cap.replace('<w:i/><w:iCs/>', '')
           .replace('<w:sz w:val="19"/><w:szCs w:val="19"/>', '<w:sz w:val="22"/><w:szCs w:val="22"/>'))
assert cap2 != cap and '<w:i/>' not in cap2 and 'w:val="22"' in cap2
sty = sty.replace(cap, cap2)

# ---------------------------------------------------------------- 3. code captions in the given format
CAPS = {
    'index.html code lines from 1 - 69': 'index.html code lines from 1 to 69',
    'index.html code lines from 73–137': 'index.html code lines from 73 to 137',
    'index.html code lines from 139 to 217 ': 'index.html code lines from 139 to 217',
    'explore.html code lines from 256 to 605': 'explore.html code lines from 330 to 349, 499 to 547 and 572 to 605',
    'explore.html code lines from 607 to 811': 'explore.html code lines from 620 to 637, 729 to 751 and 757 to 761',
    'explore1.html code lines from 375 to 482': 'explore1.html code lines from 381 to 385 and 475 to 481',
    ' explore2.html code lines 175–286': 'explore2.html code lines from 175 to 286',
    'identify.html lines code from 117 to 246': 'identify.html code lines from 117 to 246',
    'contributor.html code lines from 117 to 262': 'contributor.html code lines from 117 to 188',
    'enhancement.html code lines from 117 to 178': 'enhancement1.html code lines from 117 to 178',
    'code lines from 1 to 55 of style.css.': 'style.css code lines from 1 to 55',
    'style.css code from lines 171 to 224 and 379 to 447': 'style.css code lines from 171 to 224 and 379 to 447',
    'style.css coding lines 896 from 1016': 'style.css code lines from 896 to 1016',
    'style.css code from lines 1562 to 1581': 'style.css code lines from 1562 to 1581',
    'style.css code lines 1030 to 1092': 'style.css code lines from 1030 to 1092',
    ' style.css code lines from 2323 to 2357': 'style.css code lines from 2323 to 2357',
    'Code – style.css lines 26–40 and 379–385 (sticky menu bar)': 'style.css code lines from 26 to 40 and 379 to 385',
    'Code – explore.html lines 504–508 and 757–761, style.css lines 1419–1470 (gallery and lightbox)':
        'explore.html code lines from 504 to 508 and 757 to 761 and style.css code lines from 1419 to 1470',
    'Code – index.html lines 279–303 and style.css lines 2131–2193 (flip cards)':
        'index.html code lines from 279 to 303 and style.css code lines from 2131 to 2193',
    'Code – explore.html lines 736–748 and style.css lines 2246–2280 (star rating)':
        'explore.html code lines from 736 to 748 and style.css code lines from 2246 to 2280',
}
done_caps = set()

def fix_caption(m):
    p = m.group(0)
    if '<w:pStyle w:val="Caption"/>' not in p:
        return p
    t = ptext(p)
    if t not in CAPS:
        return p
    runs = re.findall(r'<w:r[ >].*?</w:r>', p, re.S)
    rpr = re.search(r'<w:rPr>.*?</w:rPr>', runs[0], re.S)
    rpr = rpr.group(0) if rpr else ''
    new_run = f'<w:r>{rpr}<w:t xml:space="preserve">{esc(CAPS[t])}</w:t></w:r>'
    first = p.index(runs[0]); last = p.rindex(runs[-1]) + len(runs[-1])
    done_caps.add(t)
    log.append(f'caption: {t!r} -> {CAPS[t]!r}')
    return p[:first] + new_run + p[last:]

doc = re.sub(r'<w:p[ >].*?</w:p>', fix_caption, doc, flags=re.S)
assert done_caps == set(CAPS), set(CAPS) - done_caps

# ---------------------------------------------------------------- 4. references in IEEE style
REFS = [
    ('Google (2026) Google Fonts.', 'Google, “Google Fonts,” Google. Accessed: Sep. 2026. [Online]. Available: https://fonts.google.com/'),
    ('iNaturalist (2026) iNaturalist.', 'iNaturalist, “iNaturalist,” iNaturalist. Accessed: Sep. 2026. [Online]. Available: https://www.inaturalist.org/'),
    ('Pl@ntNet (2026) Pl@ntNet Identify.', 'Pl@ntNet, “Pl@ntNet Identify,” Pl@ntNet. Accessed: Sep. 2026. [Online]. Available: https://identify.plantnet.org/'),
    ('Royal Botanic Gardens, Kew (2026)', 'Royal Botanic Gardens, Kew, “Plants of the World Online,” POWO. Accessed: Sep. 2026. [Online]. Available: https://powo.science.kew.org/'),
    ('W3Schools (2026) CSS Tutorial.', 'W3Schools, “CSS Tutorial,” W3Schools. Accessed: Sep. 2026. [Online]. Available: https://www.w3schools.com/css/'),
    ('W3Schools (2026) HTML Tutorial.', 'W3Schools, “HTML Tutorial,” W3Schools. Accessed: Sep. 2026. [Online]. Available: https://www.w3schools.com/html/'),
    ('Wikipedia contributors (2026)', 'Wikipedia contributors, “Dipterocarpaceae, Lauraceae and related genus and species articles,” Wikipedia, The Free Encyclopedia. Accessed: Sep. 2026. [Online]. Available: https://en.wikipedia.org/'),
]
ref_done = []

def fix_ref(m):
    p = m.group(0)
    t = ptext(p)
    for k, (start, new) in enumerate(REFS):
        if t.startswith(start) and '(Accessed: September 2026)' in t:
            runs = re.findall(r'<w:r[ >].*?</w:r>', p, re.S)
            first = p.index(runs[0]); last = p.rindex(runs[-1]) + len(runs[-1])
            new_runs = (f'<w:r><w:t xml:space="preserve">[{k + 1}]</w:t></w:r><w:r><w:tab/></w:r>'
                        f'<w:r><w:t xml:space="preserve">{esc(new)}</w:t></w:r>')
            ref_done.append(k)
            log.append(f'ref [{k+1}]: {new}')
            return p[:first] + new_runs + p[last:]
    return p

doc = re.sub(r'<w:p[ >].*?</w:p>', fix_ref, doc, flags=re.S)
assert sorted(ref_done) == list(range(7)), ref_done

# ---------------------------------------------------------------- 5. we -> I, our -> my (prose only)
KEEP = ['Where Our Photos Come From', 'How should we reply?', 'Why We Credit Sources']  # quotes of website text
PAIRS = [(r'\bwe are\b', 'I am'), (r'\bWe are\b', 'I am'),
         (r'\bwe\b', 'I'), (r'\bWe\b', 'I'), (r'\bour\b', 'my'), (r'\bOur\b', 'My')]

def fix_we(m):
    p = m.group(0)
    if 'Consolas' in p:          # code listings are never touched
        return p
    nodes = list(re.finditer(r'(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)', p))
    if not nodes:
        return p
    texts = [html.unescape(n.group(2)) for n in nodes]
    full = ''.join(texts)
    protected = []
    for k in KEEP:
        for mm in re.finditer(re.escape(k), full):
            protected.append((mm.start(), mm.end()))
    edits = []   # (start, end, replacement) in full-text coordinates
    taken = [False] * len(full)
    for pat, rep in PAIRS:
        for mm in re.finditer(pat, full):
            a, b = mm.start(), mm.end()
            if any(x <= a < y for x, y in protected) or any(taken[a:b]):
                continue
            for i in range(a, b): taken[i] = True
            edits.append((a, b, rep))
    if not edits:
        return p
    # map edits back into the individual text nodes
    bounds = []; pos = 0
    for t in texts:
        bounds.append((pos, pos + len(t))); pos += len(t)
    new_texts = list(texts)
    for a, b, rep in sorted(edits, reverse=True):
        # the replacement goes where the match starts; any part of the match in later runs is removed
        for j, (s, e) in enumerate(bounds):
            if s < e and s < b and a < e:
                lo, hi = max(a, s) - s, min(b, e) - s
                t = new_texts[j]
                new_texts[j] = t[:lo] + (rep if s <= a else '') + t[hi:]
        log.append(f'we/our: …{full[max(0,a-30):a]}[{full[a:b]} -> {rep}]{full[b:b+25]}…')
    out = []; last = 0
    for n, old, new in zip(nodes, texts, new_texts):
        out.append(p[last:n.start()])
        if old == new:
            out.append(n.group(0))
        else:
            out.append(n.group(1).replace('<w:t>', '<w:t xml:space="preserve">') + esc(new) + n.group(3))
        last = n.end()
    out.append(p[last:])
    return ''.join(out)

doc = re.sub(r'<w:p[ >].*?</w:p>', fix_we, doc, flags=re.S)

# ---------------------------------------------------------------- write
zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    if item.filename == 'word/document.xml':
        zout.writestr(item, doc.encode('utf-8'))
    elif item.filename == 'word/styles.xml':
        zout.writestr(item, sty.encode('utf-8'))
    else:
        zout.writestr(item, zin.read(item.filename))
zout.close()
open(os.path.join(os.path.dirname(OUT) or '.', 'edit_log.txt'), 'w').write('\n'.join(log))
print('\n'.join(log))
