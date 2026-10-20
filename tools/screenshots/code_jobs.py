import math, os
SITE = os.environ.get('SITE') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'A1-final', 'tousifakhand_assign1', 'assign1')
# placeholder -> list of (file, first_line, last_line) exactly as the report states
SPEC = {
 1: [('index.html', 1, 69)],
 3: [('index.html', 73, 137)],
 5: [('index.html', 402, 492)],
 7: [('index.html', 139, 217)],
 9: [('index.html', 219, 402)],
 11: [('explore.html', 117, 250)],
 13: [('explore.html', 330, 349), ('explore.html', 499, 547), ('explore.html', 572, 605)],
 15: [('explore.html', 620, 637), ('explore.html', 729, 751), ('explore.html', 757, 761)],
 17: [('explore1.html', 116, 186)],
 19: [('explore1.html', 194, 280)],
 21: [('explore1.html', 381, 385), ('explore1.html', 475, 481)],
 23: [('explore2.html', 175, 286)],
 25: [('explore3.html', 208, 300)],
 27: [('identify.html', 117, 246)],
 29: [('identify.html', 248, 382)],
 31: [('contributor.html', 117, 188)],
 33: [('contribute.html', 150, 214)],
 35: [('enquiry.html', 150, 245)],
 37: [('profile.html', 117, 239)],
 39: [('enhancement1.html', 117, 178)],
 41: [('acknowledgement.html', 117, 201)],
 46: [('style.css', 1, 55)],
 47: [('style.css', 171, 224), ('style.css', 379, 447)],
 50: [('style.css', 636, 766)],
 51: [('style.css', 772, 881)],
 53: [('style.css', 896, 1016)],
 55: [('style.css', 1562, 1581)],
 57: [('style.css', 1030, 1092)],
 59: [('style.css', 1098, 1194)],
 61: [('style.css', 1372, 1439)],
 65: [('style.css', 1500, 1513)],
 67: [('style.css', 2323, 2357)],
 69: [('style.css', 2457, 2500)],
 70: [('style.css', 2503, 2733)],
 75: [('index.html', 38, 59), ('style.css', 171, 224)],
 77: [('style.css', 26, 40), ('style.css', 379, 385)],
 79: [('explore.html', 504, 508), ('explore.html', 757, 761), ('style.css', 1419, 1470)],
 81: [('index.html', 279, 303), ('style.css', 2131, 2193)],
 83: [('explore.html', 736, 748), ('style.css', 2246, 2280)],
}
MAX = 56

def lines_of(f):
    p = os.path.join(SITE, 'styles', f) if f.endswith('.css') else os.path.join(SITE, f)
    return open(p, encoding='utf-8').read().split('\n')

def good_break(text):
    t = text.strip()
    return t == '' or t.startswith('</') or t == '}' or t.endswith('-->') or t.endswith('*/')

def chunks(f, a, b):
    n = b - a + 1
    if n <= MAX: return [(a, b)]
    k = math.ceil(n / MAX); L = lines_of(f); out = []; s = a
    for i in range(1, k):
        ideal = a + round(n * i / k) - 1          # last line of chunk i
        best = None
        for d in range(0, 9):
            for c in (ideal - d, ideal + d):
                if s + 10 <= c < b and c - s + 1 <= MAX and b - c <= MAX * (k - i) and good_break(L[c - 1]):
                    best = c; break
            if best: break
        best = best or min(ideal, s + MAX - 1)
        out.append((s, best)); s = best + 1
    rem = b - s + 1
    if rem > MAX:   # safety
        out.append((s, s + MAX - 1)); s += MAX
    out.append((s, b))
    return out

def jobs():
    res = []
    for ph, parts in SPEC.items():
        k = 0
        for f, a, b in parts:
            for c in chunks(f, a, b):
                k += 1
                res.append((f'c{ph}_{k}', f, c[0], c[1], ph))
    return res

if __name__ == '__main__':
    J = jobs(); print(len(J), 'images')
    for j in J: print(j[0], j[1], j[2], j[3], j[3] - j[2] + 1)
