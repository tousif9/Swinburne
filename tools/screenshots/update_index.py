"""Make the report match the index.html in Website.zip: screenshots, captions, line numbers, code text."""
import sys, os, re, io, html, zipfile
from PIL import Image
sys.path.insert(0, os.path.abspath('../fin6')); sys.path.insert(0, os.path.abspath('../fin5'))
from imgs import drawings

SRC, OUT = sys.argv[1], sys.argv[2]
REF = '../fin5/doc/FINAL11_Report_COS10005_TousifAkhand.docx'   # my build: drawing order -> image names
EMU_IN = 914400; TEXT_W = 9026 * 635; MAX_H = int(8.3 * EMU_IN)
log = []

zin = zipfile.ZipFile(SRC)
doc = zin.read('word/document.xml').decode('utf-8')
rels = zin.read('word/_rels/document.xml.rels').decode('utf-8')

def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def ptext(p): return html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>([^<]*)</w:t>', p)))

# ------------------------------------------------ 1. swap the index.html code screenshots
names = [x[1].split('/')[-1].rsplit('.', 1)[0] for x in drawings(REF)]
NEW = ['c1_1', 'c1_2', 'c3_1', 'c3_2', 'c5_1', 'c5_2', 'c7_1', 'c7_2', 'c9_1', 'c9_2', 'c9_3', 'c9_4', 'c75_1', 'c81_1']
targets = {names.index('code_' + n): n for n in NEW}
assert len(targets) == 14
blocks = list(re.finditer(r'<w:drawing>.*?</w:drawing>', doc, re.S))
assert len(blocks) == len(names) == 166
pid = max(int(x) for x in re.findall(r'<wp:docPr id="(\d+)"', doc)) + 1
media, new_rels, old_rids = {}, [], []
out, last = [], 0
for i, m in enumerate(blocks):
    if i not in targets: continue
    n = targets[i]; blk = m.group(0)
    im = Image.open(f'code/{n}.png'); w, h = im.size
    q = im.convert('RGB').quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    buf = io.BytesIO(); q.save(buf, 'PNG', optimize=True)
    fname = f'media/index_{n}.png'; rid = f'rIdIdx{n}'
    media['word/' + fname] = buf.getvalue()
    new_rels.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{fname}"/>')
    old_cx = int(re.search(r'<wp:extent cx="(\d+)"', blk).group(1))
    cx = old_cx; cy = int(cx * h / w)                     # same width as the image it replaces
    if cy > MAX_H: cy = MAX_H; cx = int(cy * w / h)
    old_rid = re.search(r'r:embed="([^"]+)"', blk).group(1); old_rids.append(old_rid)
    nb = re.sub(r'r:embed="[^"]+"', f'r:embed="{rid}"', blk)
    nb = re.sub(r'<wp:extent cx="\d+" cy="\d+"/>', f'<wp:extent cx="{cx}" cy="{cy}"/>', nb)
    nb = re.sub(r'<a:ext cx="\d+" cy="\d+"/>', f'<a:ext cx="{cx}" cy="{cy}"/>', nb)
    nb = re.sub(r'<wp:docPr id="\d+" name="[^"]*"', f'<wp:docPr id="{pid}" name="Picture {pid}"', nb)
    nb = re.sub(r'<pic:cNvPr id="\d+" name="[^"]*"', f'<pic:cNvPr id="{pid}" name="index_{n}.png"', nb)
    pid += 1
    out.append(doc[last:m.start()]); out.append(nb); last = m.end()
    log.append(f'image {i}: {names[i]} -> new {n} ({cx}x{cy} EMU)')
out.append(doc[last:]); doc = ''.join(out)
# drop relationships/media no longer used anywhere
drop_media = []
for rid in set(old_rids):
    if f'r:embed="{rid}"' in doc or f'r:id="{rid}"' in doc: continue
    tgt = re.search(rf'<Relationship [^>]*Id="{rid}"[^>]*/>', rels).group(0)
    drop_media.append('word/' + re.search(r'Target="([^"]+)"', tgt).group(1))
    rels = rels.replace(tgt, '')
rels = rels.replace('</Relationships>', ''.join(new_rels) + '</Relationships>')
log.append(f'old media removed: {len(drop_media)}')

# ------------------------------------------------ generic in-paragraph text replace (handles text split over runs)
def replace_in_par(p, old, new):
    nodes = list(re.finditer(r'(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)', p))
    texts = [html.unescape(n.group(2)) for n in nodes]
    full = ''.join(texts)
    a = full.find(old)
    if a < 0: return p, False
    b = a + len(old)
    bounds = []; pos = 0
    for t in texts: bounds.append((pos, pos + len(t))); pos += len(t)
    nt = list(texts)
    for j, (s, e) in enumerate(bounds):
        if s < e and s < b and a < e:
            lo, hi = max(a, s) - s, min(b, e) - s
            nt[j] = nt[j][:lo] + (new if s <= a else '') + nt[j][hi:]
    res, last = [], 0
    for n, o, t in zip(nodes, texts, nt):
        res.append(p[last:n.start()])
        res.append(n.group(0) if o == t else n.group(1).replace('<w:t>', '<w:t xml:space="preserve">') + esc(t) + n.group(3))
        last = n.end()
    res.append(p[last:])
    return ''.join(res), True

# ------------------------------------------------ 2. captions
CAPS = {
    'index.html code lines from 1 to 69': 'index.html code lines from 1 to 65',
    'index.html code lines from 73 to 137': 'index.html code lines from 69 to 132',
    'index.html code lines from 402 to 492': 'index.html code lines from 393 to 483',
    'index.html code lines from 139 to 217': 'index.html code lines from 134 to 212',
    'index.html code lines from 219 to 402': 'index.html code lines from 214 to 393',
    'index.html code lines from 38 to 59 and style.css code lines from 171 to 224':
        'index.html code lines from 35 to 56 and style.css code lines from 171 to 224',
    'index.html code lines from 279 to 303 and style.css code lines from 2131 to 2193':
        'index.html code lines from 274 to 297 and style.css code lines from 2131 to 2193',
}
seen = set()
def cap(m):
    p = m.group(0)
    if '<w:pStyle w:val="Caption"/>' in p and ptext(p) in CAPS:
        t = ptext(p); seen.add(t)
        p2, ok = replace_in_par(p, t, CAPS[t]); assert ok
        log.append(f'caption: {t} -> {CAPS[t]}'); return p2
    return p
doc = re.sub(r'<w:p[ >].*?</w:p>', cap, doc, flags=re.S)
assert seen == set(CAPS), set(CAPS) - seen

# ------------------------------------------------ 3. line numbers in Tables 2, 3, 4 and 15
CELL = {  # Lines column, exact cell text
    2: {'12–30': '12–27', '35': '32', '38–41': '35–38', '42–59': '39–56', '61–69': '58–65', '73–116': '69–111', '121–137': '116–132'},
    3: {'406': '397', '407–409': '398–400', '411–476': '402–467', '478–483': '469–474', '488–490': '479–481'},
    4: {'139': '134', '140–178': '135–173', '180–182': '175–177', '186–195': '181–190', '199–217': '194–212',
        '219': '214', '223–266': '218–261', '270–388': '265–379', '390–401': '381–392'},
}
INLINE = {
    2: [('lines 25 to 28', 'lines 23 to 25'), ('at line 29', 'at line 26'), ('line 38 has', 'line 35 has'),
        ('on line 39', 'on line 36'), ('line 43 is', 'line 40 is'), ('line 61 is', 'line 58 is'),
        ('on 64th line', 'on 60th line'), ('lines 91 to 113', 'lines 86 to 108'), ('lines 123 to 130', 'lines 118 to 125')],
    4: [('lines 142 to 148', 'lines 137 to 143'), ('lines 152 to 160', 'lines 147 to 155'), ('lines 163-167', 'lines 158-162')],
    15: [('index.html (code lines from 25 to 28)', 'index.html (code lines from 23 to 25)')],
}
KEYS = {2: 'Firstly, by virtue of the DOCTYPE', 3: 'site-footer', 4: 'unique to this page', 15: 'COLOUR SCHEME'}
tables = list(re.finditer(r'<w:tbl>.*?</w:tbl>', doc, re.S))
found = {}
for k, key in KEYS.items():
    hits = [m for m in tables if key in html.unescape(re.sub(r'<[^>]+>', '', m.group(0)))]
    found[k] = hits[0]
    assert len(hits) >= 1, k
# Table 15 key also appears in the CSS code of other tables? take the one containing the index.html reference
found[15] = [m for m in tables if 'code lines from 25 to 28' in html.unescape(re.sub(r'<[^>]+>', '', m.group(0)))][0]
edits = []
for k in sorted(found, key=lambda k: found[k].start()):
    m = found[k]; t = m.group(0)
    def row(rm):

        r = rm.group(0)
        cells = list(re.finditer(r'<w:tc>.*?</w:tc>', r, re.S))
        first = cells[0].group(0); txt = ptext(first).strip()
        if k in CELL and txt in CELL[k]:
            nf, ok = replace_in_par(first, txt, CELL[k][txt]); assert ok
            r = r.replace(first, nf, 1); log.append(f'Table {k} Lines: {txt} -> {CELL[k][txt]}'); done.add((k, txt))
        for o, n in INLINE.get(k, []):
            for c in re.finditer(r'<w:p[ >].*?</w:p>', r, re.S):
                p2, ok = replace_in_par(c.group(0), o, n)
                if ok:
                    r = r.replace(c.group(0), p2, 1); log.append(f'Table {k} text: {o} -> {n}'); done.add((k, o)); break
        return r
    done = set()
    nt = re.sub(r'<w:tr[ >].*?</w:tr>', row, t, flags=re.S)
    want = {(k, x) for x in CELL.get(k, {})} | {(k, o) for o, _ in INLINE.get(k, [])}
    assert done == want, (k, want - done)
    edits.append((m.start(), m.end(), nt))
for s, e, nt in sorted(edits, reverse=True):
    doc = doc[:s] + nt + doc[e:]

# ------------------------------------------------ 4. code text copied from index.html (Tables 28, 31, 32)
pars = list(re.finditer(r'<w:p[ >].*?</w:p>', doc, re.S))
def ptxt(i): return ptext(pars[i].group(0))
ops = []   # (index, new_text or None to delete)
for i, m in enumerate(pars):
    if 'Consolas' not in m.group(0): continue
    t = ptxt(i)
    if t == '<input type="checkbox" id="menu-toggle" class="menu-toggle" />':
        ops.append((i, '<input type="checkbox" id="menu-toggle" class="menu-toggle">'))
    elif t.strip() == '/>' and ptxt(i - 1).endswith('alt="Red winged dipterocarp fruits on the forest floor"'):
        ops.append((i - 1, ptxt(i - 1) + '>')); ops.append((i, None))
    elif t == '/>' and ptxt(i - 1) == '  required':
        ops.append((i - 1, '  required>')); ops.append((i, None))
assert len(ops) == 5, ops
for i, new in sorted(ops, reverse=True):
    m = pars[i]; p = m.group(0)
    if new is None:
        doc = doc[:m.start()] + doc[m.end():]; log.append(f'code line removed: {ptxt(i)!r}')
    else:
        p2, ok = replace_in_par(p, ptxt(i), new); assert ok
        doc = doc[:m.start()] + p2 + doc[m.end():]; log.append(f'code line: {ptxt(i)!r} -> {new!r}')

# ------------------------------------------------ write
zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    if item.filename in drop_media: continue
    if item.filename == 'word/document.xml': zout.writestr(item, doc.encode('utf-8'))
    elif item.filename == 'word/_rels/document.xml.rels': zout.writestr(item, rels.encode('utf-8'))
    else: zout.writestr(item, zin.read(item.filename))
for n, data in media.items(): zout.writestr(n, data, compress_type=zipfile.ZIP_STORED)
zout.close()
print('\n'.join(log))
