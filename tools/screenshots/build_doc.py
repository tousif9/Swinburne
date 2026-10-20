"""Put the screenshots into the report's placeholders. Nothing else in the document is changed."""
import zipfile, re, io, os, html
from PIL import Image
import code_jobs

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'doc/original.docx')
OUT = os.path.join(BASE, 'doc/FINAL11_Report_COS10005_TousifAkhand.docx')

EMU_IN = 914400
TEXT_W = 9026 * 635            # text width between margins, in EMU (A4, 1" margins)
MAX_H = int(8.3 * EMU_IN)      # keep each image (plus caption) on one page
PHONE_W = int(2.9 * EMU_IN)

# ---------------------------------------------------------------- what goes where
W = lambda *n: [('web', x) for x in n]
U = lambda *n: [('user', x) for x in n]
PLAN = {
    2: W('2'), 4: U('4'), 6: W('6'), 8: W('8'), 10: W('10a', '10b', '10c'), 12: W('12a', '12b', '12c'),
    14: W('14a', '14b', '14c', '14d'), 16: W('16a', '16b', '16c'), 18: W('18a', '18b'), 20: W('20a', '20b'),
    22: W('22a', '22b'), 24: W('24a', '24b', '24c'), 26: W('26a', '26b'), 28: W('28a', '28b'),
    30: U('30a', '30b'), 32: W('32'), 34: W('34'), 36: U('36'), 38: W('38a', '38b'), 40: W('40'), 42: W('42'),
    44: W('44'), 45: W('45'), 48: W('48'), 49: W('49'), 52: W('52'), 54: W('54a', '54b'), 56: W('56'),
    58: U('30a', '30b'), 60: W('60a', '60b'), 62: W('62a', '62b'), 63: W('63a', '63b', '63c'), 64: W('64'),
    66: W('66'), 68: W('68'), 71: W('71'), 72: W('72a', '72b', '72c'), 73: W('73'), 74: U('74a', '74b'),
    76: W('76a', '76b'), 78: W('78'), 80: W('80a', '80b'), 82: W('82'), 84: W('84'), 85: U('85'), 86: W('86'),
    87: U('87'),
}
for job in code_jobs.jobs():
    PLAN.setdefault(job[4], []).append(('code', job[0]))
SIDE_BY_SIDE = {76}
PHONE = {'45', '71', '72a', '72b', '72c', '73', '74a', '74b'}


def load(kind, name):
    path = os.path.join(BASE, kind, name + '.png')
    im = Image.open(path)
    w, h = im.size
    buf = io.BytesIO()
    if kind == 'code':
        q = im.convert('RGB').quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        q.save(buf, 'PNG', optimize=True); ext = 'png'
    else:
        im.convert('RGB').save(buf, 'JPEG', quality=90, optimize=True); ext = 'jpeg'
    return buf.getvalue(), ext, w, h


def size_for(name, w, h, max_w):
    cw = min(max_w, PHONE_W) if name in PHONE else max_w
    ch = int(cw * h / w)
    if ch > MAX_H:
        ch = MAX_H; cw = int(ch * w / h)
    return cw, ch


def drawing(rid, pid, name, cx, cy):
    return (f'<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:docPr id="{pid}" name="Picture {pid}"/><wp:cNvGraphicFramePr>'
            f'<a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/>'
            f'</wp:cNvGraphicFramePr><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr>'
            f'<pic:cNvPr id="{pid}" name="{html.escape(name)}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill>'
            f'<a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm>'
            f'<a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/>'
            f'</a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing>')


def para(runs, keep_next):
    kn = '<w:keepNext/>' if keep_next else ''
    return (f'<w:p><w:pPr>{kn}<w:spacing w:before="120" w:after="60"/><w:jc w:val="center"/></w:pPr>'
            + ''.join(f'<w:r>{r}</w:r>' for r in runs) + '</w:p>')


def main():
    zin = zipfile.ZipFile(SRC)
    doc = zin.read('word/document.xml').decode('utf-8')
    rels = zin.read('word/_rels/document.xml.rels').decode('utf-8')
    ctypes = zin.read('[Content_Types].xml').decode('utf-8')

    media, rel_add = {}, []
    pid = [max(int(x) for x in re.findall(r'<wp:docPr id="(\d+)"', doc)) + 1]
    cache = {}

    def add_image(kind, name):
        key = (kind, name)
        if key not in cache:
            data, ext, w, h = load(kind, name)
            fname = f'media/{kind}_{name}.{ext}'
            rid = f'rIdShot{len(cache) + 1}'
            media['word/' + fname] = data
            rel_add.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/'
                           f'2006/relationships/image" Target="{fname}"/>')
            cache[key] = (rid, w, h, fname)
        return cache[key]

    done = []

    def repl(m):
        tbl = m.group(0)
        text = re.sub(r'<[^>]+>', '', tbl)
        mm = re.search(r'INSERT (CODE|WEBSITE) SCREENSHOT (\d+) HERE', text)
        if not mm:
            return tbl
        ph = int(mm.group(2))
        items = PLAN[ph]
        out = []
        if ph in SIDE_BY_SIDE:
            gap_w = int(0.15 * EMU_IN)
            half = (TEXT_W - gap_w) // 2
            runs = []
            for k, (kind, name) in enumerate(items):
                rid, w, h, fname = add_image(kind, name)
                cx, cy = size_for(name, w, h, half)
                runs.append(drawing(rid, pid[0], os.path.basename(fname), cx, cy)); pid[0] += 1
                if k == 0: runs.append('<w:t xml:space="preserve">  </w:t>')
            out.append(para(runs, True))
        else:
            for k, (kind, name) in enumerate(items):
                rid, w, h, fname = add_image(kind, name)
                cx, cy = size_for(name, w, h, TEXT_W)
                out.append(para([drawing(rid, pid[0], os.path.basename(fname), cx, cy)], k == len(items) - 1))
                pid[0] += 1
        done.append(ph)
        return ''.join(out)

    new_doc = re.sub(r'<w:tbl>.*?</w:tbl>', repl, doc, flags=re.S)
    expected = sorted(PLAN)
    assert sorted(done) == expected, (sorted(set(expected) - set(done)), sorted(set(done) - set(expected)))
    assert 'INSERT CODE SCREENSHOT' not in new_doc and 'INSERT WEBSITE SCREENSHOT' not in new_doc

    new_rels = rels.replace('</Relationships>', ''.join(rel_add) + '</Relationships>')
    if 'Extension="jpeg"' not in ctypes:
        ctypes = ctypes.replace('<Default Extension="png"', '<Default Extension="jpeg" ContentType="image/jpeg"/><Default Extension="png"')

    zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        if item.filename == 'word/document.xml':
            zout.writestr(item, new_doc.encode('utf-8'))
        elif item.filename == 'word/_rels/document.xml.rels':
            zout.writestr(item, new_rels.encode('utf-8'))
        elif item.filename == '[Content_Types].xml':
            zout.writestr(item, ctypes.encode('utf-8'))
        else:
            zout.writestr(item, zin.read(item.filename))
    for name, data in media.items():
        zout.writestr(name, data, compress_type=zipfile.ZIP_STORED)
    zout.close()
    print('placeholders filled:', len(done), '| images:', len(cache), '| size MB:', round(os.path.getsize(OUT) / 1e6, 1))


if __name__ == '__main__':
    main()
