import zipfile,re,hashlib
def drawings(path):
    z=zipfile.ZipFile(path)
    d=z.read('word/document.xml').decode(); r=z.read('word/_rels/document.xml.rels').decode()
    rel={a:b for a,b in re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"',r)}
    rel.update({a:b for b,a in re.findall(r'Target="([^"]+)"[^>]*Id="([^"]+)"',r)})
    out=[]
    for m in re.finditer(r'<w:drawing>.*?</w:drawing>',d,re.S):
        e=re.search(r'r:embed="([^"]+)"',m.group(0)).group(1)
        ext=re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"',m.group(0)).groups()
        data=z.read('word/'+rel[e]); out.append((hashlib.md5(data).hexdigest(),rel[e],ext,m.start()))
    return out
