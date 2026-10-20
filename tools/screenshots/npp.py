"""Render source lines as a Notepad++ (default theme) editor screenshot."""
import html as H, re, os

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
        'param', 'source', 'track', 'wbr'}
PSEUDO = {'hover', 'focus', 'active', 'visited', 'link', 'checked', 'target', 'valid', 'invalid',
          'focus-within', 'focus-visible', 'first-child', 'last-child', 'nth-child', 'nth-of-type',
          'not', 'root', 'disabled', 'required', 'placeholder-shown', 'before', 'after',
          'first-letter', 'first-line', 'placeholder', 'marker', 'selection', 'empty', 'only-child'}


# ---------------------------------------------------------------- HTML lexer
def lex_html(src):
    out, i, n = [], 0, len(src)
    add = lambda st, s: out.append((st, s)) if s else None
    while i < n:
        if src.startswith('<!--', i):
            j = src.find('-->', i + 4); j = n if j < 0 else j + 3
            add('c', src[i:j]); i = j
        elif src.startswith('<!', i):
            j = src.find('>', i); j = n if j < 0 else j
            body = src[i + 2:j]
            m = re.match(r'([A-Za-z]+)(.*)', body, re.S)
            add('sg', '<!')
            if m:
                add('sgc', m.group(1))
                rest = m.group(2)
                lead = re.match(r'\s*', rest).group(0)
                add('sg', lead); add('sgp', rest[len(lead):])
            else:
                add('sg', body)
            add('sg', '>'); i = j + 1
        elif src[i] == '<' and i + 1 < n and (src[i + 1].isalpha() or src[i + 1] == '/'):
            m = re.match(r'</?[A-Za-z][\w-]*', src[i:])
            add('t', m.group(0)); i += len(m.group(0))
            while i < n:
                c = src[i]
                if src.startswith('/>', i):
                    add('t', '/>'); i += 2; break
                if c == '>':
                    add('t', '>'); i += 1; break
                if c.isspace():
                    j = i
                    while j < n and src[j].isspace(): j += 1
                    add('ws', src[i:j]); i = j
                elif c == '=':
                    add('o', '='); i += 1
                elif c in '"\'':
                    j = src.find(c, i + 1); j = n if j < 0 else j + 1
                    add('v', src[i:j]); i = j
                else:
                    m = re.match(r'[^\s=>"\'/]+', src[i:]) or re.match(r'.', src[i:], re.S)
                    add('a', m.group(0)); i += len(m.group(0))
        elif src[i] == '&':
            m = re.match(r'&#?\w+;', src[i:])
            if m:
                add('e', m.group(0)); i += len(m.group(0))
            else:
                add('d', '&'); i += 1
        else:
            j = i + 1
            while j < n and src[j] not in '<&': j += 1
            add('d', src[i:j]); i = j
    return out


def folds_html(src):
    """Return list of (start_line, end_line) 1-based fold ranges."""
    lines = src.split('\n')
    pos2line = []
    ln = 1
    for ch in src:
        pos2line.append(ln)
        if ch == '\n': ln += 1
    ranges, stack, i, n = [], [], 0, len(src)
    while i < n:
        if src.startswith('<!--', i):
            j = src.find('-->', i); j = n - 1 if j < 0 else j + 2
            if pos2line[j] > pos2line[i]: ranges.append((pos2line[i], pos2line[j]))
            i = j + 1; continue
        m = re.match(r'<(/?)([A-Za-z][\w-]*)', src[i:i + 40])
        if m:
            k = src.find('>', i)
            selfclose = src[k - 1] == '/'
            name = m.group(2).lower()
            if m.group(1):
                for idx in range(len(stack) - 1, -1, -1):
                    if stack[idx][0] == name:
                        s = stack[idx][1]; del stack[idx:]
                        if pos2line[i] > s: ranges.append((s, pos2line[i]))
                        break
            elif name not in VOID and not selfclose:
                stack.append((name, pos2line[i]))
            i = k + 1; continue
        i += 1
    return ranges


# ---------------------------------------------------------------- CSS lexer
def lex_css(src):
    out, i, n = [], 0, len(src)
    add = lambda st, s: out.append((st, s)) if s else None
    stack = []           # 'sel' or 'decl' contexts for each open brace
    mode = 'sel'         # current mode
    prelude_is_at = False
    in_value = False
    while i < n:
        c = src[i]
        if src.startswith('/*', i):
            j = src.find('*/', i + 2); j = n if j < 0 else j + 2
            add('cc', src[i:j]); i = j; continue
        if c.isspace():
            j = i
            while j < n and src[j].isspace(): j += 1
            add('ws', src[i:j]); i = j; continue
        if mode == 'sel':
            if c == '@':
                m = re.match(r'@[\w-]+', src[i:]); add('dir', m.group(0)); i += len(m.group(0))
                prelude_is_at = True; at_name = m.group(0)
                # rest of prelude until { or ;
                while i < n and src[i] not in '{;':
                    if src[i] in '"\'':
                        j = src.find(src[i], i + 1) + 1; add('str', src[i:j]); i = j
                    elif src[i] in '():,':
                        add('op', src[i]); i += 1
                    elif src[i].isspace():
                        j = i
                        while j < n and src[j].isspace(): j += 1
                        add('ws', src[i:j]); i = j
                    else:
                        m = re.match(r'[^\s"\'():,{;]+', src[i:]); add('pre', m.group(0)); i += len(m.group(0))
                if i < n and src[i] == ';':
                    add('op', ';'); i += 1; prelude_is_at = False
                continue
            if c == '{':
                add('op', '{'); i += 1
                stack.append(mode)
                if prelude_is_at and at_name in ('@media', '@supports', '@keyframes', '@document'):
                    mode = 'sel'
                else:
                    mode = 'decl'
                prelude_is_at = False
                in_value = False
                continue
            if c == '}':
                add('op', '}'); i += 1
                mode = stack.pop() if stack else 'sel'; continue
            if c == '.':
                m = re.match(r'\.[\w-]+', src[i:]); add('op', '.'); add('cls', m.group(0)[1:]); i += len(m.group(0)); continue
            if c == '#':
                m = re.match(r'#[\w-]+', src[i:]); add('op0', '#'); add('id', m.group(0)[1:]); i += len(m.group(0)); continue
            if c == ':':
                m = re.match(r'::?([\w-]+)', src[i:])
                add('op', m.group(0)[:len(m.group(0)) - len(m.group(1))])
                add('ps' if m.group(1) in PSEUDO else 'ups', m.group(1)); i += len(m.group(0)); continue
            if c == '[':
                j = src.find(']', i) + 1; add('attr', src[i:j]); i = j; continue
            if c in '>~+,*()':
                add('op', c); i += 1; continue
            m = re.match(r'[\w%-]+', src[i:])
            if m:
                add('tag', m.group(0)); i += len(m.group(0)); continue
            add('def', c); i += 1; continue
        # declaration mode
        if c == '}':
            add('op', '}'); i += 1; mode = stack.pop() if stack else 'sel'; in_value = False; continue
        if c == '{':
            add('op', '{'); i += 1; stack.append(mode); continue
        if not in_value:
            if c == ':':
                add('op', ':'); i += 1; in_value = True; continue
            if c == ';':
                add('op', ';'); i += 1; continue
            m = re.match(r'[\w-]+', src[i:])
            if m:
                add('prop', m.group(0)); i += len(m.group(0)); continue
            add('def', c); i += 1; continue
        # in value
        if c == ';':
            add('op', ';'); i += 1; in_value = False; continue
        if c in '"\'':
            j = src.find(c, i + 1) + 1; add('str', src[i:j]); i = j; continue
        if src.startswith('!important', i):
            add('imp', '!important'); i += 10; continue
        m = re.match(r'[^;"\'}\s/]+|/(?!\*)', src[i:])
        add('val', m.group(0)); i += len(m.group(0))
    return out


def folds_css(src):
    pos2line = []
    ln = 1
    for ch in src:
        pos2line.append(ln)
        if ch == '\n': ln += 1
    ranges, stack, i, n = [], [], 0, len(src)
    while i < n:
        if src.startswith('/*', i):
            j = src.find('*/', i); j = n - 1 if j < 0 else j + 1
            if pos2line[j] > pos2line[i]: ranges.append((pos2line[i], pos2line[j]))
            i = j + 1; continue
        if src[i] in '"\'':
            j = src.find(src[i], i + 1); i = (j if j > 0 else n) + 1; continue
        if src[i] == '{': stack.append(pos2line[i])
        elif src[i] == '}' and stack:
            s = stack.pop()
            if pos2line[i] > s: ranges.append((s, pos2line[i]))
        i += 1
    return ranges


# ---------------------------------------------------------------- rendering
def split_lines(spans):
    lines, cur = [[]], None
    for st, s in spans:
        parts = s.split('\n')
        for k, p in enumerate(parts):
            if k: lines.append([])
            if p: lines[-1].append((st, p))
    return lines


def fold_state(ranges, nlines):
    """Per line: (is_start, is_end, inside_before, inside_after)."""
    depth_before = [0] * (nlines + 2)
    start = [0] * (nlines + 2); end = [0] * (nlines + 2)
    for s, e in ranges:
        start[s] += 1; end[e] += 1
    out = {}
    d = 0
    for ln in range(1, nlines + 1):
        before = d
        d = d + start[ln] - end[ln]
        out[ln] = (start[ln] > 0, end[ln] > 0, before, d)
    return out


def fold_svg(st):
    is_start, is_end, before, after = st
    W, Hh, cx, cy = 16, 18, 8.5, 9.5
    parts = []
    col = '#808080'
    if is_start:
        if before > 0 or (is_end and before > 0):
            parts.append(f'<line x1="{cx}" y1="0" x2="{cx}" y2="5" stroke="{col}"/>')
        parts.append(f'<rect x="4.5" y="5.5" width="8" height="8" fill="#fff" stroke="{col}"/>')
        parts.append(f'<line x1="6.5" y1="9.5" x2="10.5" y2="9.5" stroke="{col}"/>')
        if after > 0:
            parts.append(f'<line x1="{cx}" y1="14" x2="{cx}" y2="{Hh}" stroke="{col}"/>')
    elif is_end:
        parts.append(f'<line x1="{cx}" y1="0" x2="{cx}" y2="{cy}" stroke="{col}"/>')
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{W}" y2="{cy}" stroke="{col}"/>')
        if after > 0:
            parts.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{Hh}" stroke="{col}"/>')
    elif before > 0:
        parts.append(f'<line x1="{cx}" y1="0" x2="{cx}" y2="{Hh}" stroke="{col}"/>')
    if not parts: return ''
    return f'<svg width="{W}" height="{Hh}" shape-rendering="crispEdges">{"".join(parts)}</svg>'


TABS = ['acknowledgement.html', 'contribute.html', 'contributor.html', 'enhancement1.html',
        'enquiry.html', 'explore.html', 'explore1.html', 'explore2.html', 'explore3.html',
        'identify.html', 'index.html', 'profile.html', 'style.css']

FLOPPY = ('<svg width="16" height="16" viewBox="0 0 16 16"><rect x="0.5" y="0.5" width="15" height="15" rx="2" '
          'fill="{b}" stroke="{bs}"/><rect x="3.5" y="1" width="9" height="5" fill="#E8F1FB"/>'
          '<rect x="2.5" y="9" width="11" height="6" fill="{g}"/></svg>')
PIN = ('<svg width="14" height="14" viewBox="0 0 14 14"><path d="M8 1 L13 6 L11 6.5 L8.5 9 L8.5 11.5 L7.5 12.5 '
       'L1.5 6.5 L2.5 5.5 L5 5.5 L7.5 3 Z M4.5 9.5 L1 13" fill="none" stroke="#000" stroke-width="1"/></svg>')
CLOSE = ('<svg width="16" height="16" viewBox="0 0 16 16"><rect x="1" y="1" width="14" height="14" fill="#C47F8E"/>'
         '<path d="M4.5 4.5 L11.5 11.5 M11.5 4.5 L4.5 11.5" stroke="#fff" stroke-width="2.2"/></svg>')


def tabbar(active, width):
    usable = width - 46
    tw = [max(150, 26 + len(t) * 8 + 40 + (36 if t == active else 0)) for t in TABS]
    ai = TABS.index(active)
    # choose a window that ends a little after the active tab
    start = 0
    while True:
        tot, k = 0, start
        while k < len(TABS) and tot + tw[k] <= usable: tot += tw[k]; k += 1
        if ai < k - 1 or k == len(TABS): break
        start += 1
    html = []
    x = 0
    for k in range(start, len(TABS)):
        t = TABS[k]
        if x > usable: break
        act = t == active
        icon = FLOPPY.format(b='#4A8BD4' if act else '#7FA3C9', bs='#2F6CB0' if act else '#6C8FB5',
                             g='#7DC27D' if act else '#9DB89D')
        extra = f'<span class="pin">{PIN}</span><span class="clsb">{CLOSE}</span>' if act else ''
        html.append(f'<div class="tab{" act" if act else ""}" style="width:{tw[k]}px">{icon}'
                    f'<span class="tn">{H.escape(t)}</span>{extra}</div>')
        x += tw[k]
    return ''.join(html)


CSS = """
@font-face{font-family:CP;src:url(fonts/CourierPrime-normal-400.woff2)}
@font-face{font-family:CP;font-weight:700;src:url(fonts/CourierPrime-normal-700.woff2)}
@font-face{font-family:CP;font-style:italic;src:url(fonts/CourierPrime-italic-400.woff2)}
@font-face{font-family:TabUI;src:url(fonts/NotoSans-400.woff2)}
*{box-sizing:border-box}
body{margin:0;background:#fff}
#win{width:%(W)dpx;border:1px solid #9A9A9A;background:#fff;overflow:hidden}
#tabs{height:27px;background:#C0C0C0;display:flex;align-items:flex-end;position:relative;border-bottom:1px solid #6E6E6E;overflow:hidden}
.tab{height:24px;display:flex;align-items:center;gap:6px;padding:0 8px 0 6px;font:14px TabUI,'Segoe UI',sans-serif;
     color:#7A7A7A;border-right:1px solid #ADADAD;white-space:nowrap;overflow:hidden;flex:none}
.tab.act{background:#F0F0F0;color:#000;height:26px;border-top:3px solid #FAAA3C;border-left:1px solid #9A9A9A;border-right:1px solid #9A9A9A}
.tab .tn{flex:1}
.pin{display:flex;opacity:.85}.clsb{display:flex}
#arrows{position:absolute;right:0;top:2px;display:flex;gap:2px;padding-right:2px;background:#C0C0C0;height:25px;align-items:center}
#arrows div{width:20px;height:22px;background:#F7F7F7;border:1px solid #ADADAD;display:flex;align-items:center;justify-content:center;font-size:9px;color:#000}
#ed{display:flex;position:relative}
#ln{background:#E4E4E4;color:#808080;text-align:right;padding-right:%(LNPAD)dpx;width:%(LNW)dpx;flex:none}
#fm{width:16px;flex:none;background-color:#F3F3F3;
    background-image:linear-gradient(45deg,#E9E9E9 25%%,transparent 25%%,transparent 75%%,#E9E9E9 75%%),
                     linear-gradient(45deg,#E9E9E9 25%%,transparent 25%%,transparent 75%%,#E9E9E9 75%%);
    background-size:2px 2px;background-position:0 0,1px 1px}
#tx{flex:1;overflow:hidden;position:relative;padding-left:2px}
.l{height:18px;line-height:18px;font:15px/18px CP,'Courier New',monospace;white-space:pre;position:relative}
#ln .l{font-family:CP,'Courier New',monospace}
#fm .l{height:18px}
#fm svg{display:block}
#sb{width:17px;flex:none;background:#F0F0F0;position:relative;border-left:1px solid #E6E6E6}
#thumb{position:absolute;left:5px;width:6px;background:#858585;border-radius:3px}
.g{position:absolute;top:0;bottom:0;border-left:1px dotted #B0B0B0}
.t{color:#0000FF}.a{color:#FF0000}.o{color:#000}.v{color:#8000FF;font-weight:bold}.c{color:#008000}
.d{color:#000;font-weight:bold}.e{color:#000;font-style:italic;background:#FEFDE0}
.sg{color:#0000FF;background:#CFE2F7}.sgc{color:#0000DD;font-weight:bold;background:#CFE2F7}.sgp{color:#0000DD;background:#ECF4FC}
.tag{color:#0000FF}.cls{color:#FF0000}.id{color:#0080FF}.op{color:#000;font-weight:bold}.op0{color:#000}
.ps{color:#FF8000;font-weight:bold}.ups{color:#FF8080}.attr{color:#800000}
.prop{color:#8080C0;font-weight:bold}.val{color:#000;font-weight:bold}.str{color:#808080}.cc{color:#008000}
.imp{color:#FF0000;font-weight:bold}.dir{color:#0080FF}.pre{color:#000}.def{color:#000}
"""
CHAR = 9.0  # Courier Prime advance at 15px


class Doc:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.src = open(path, encoding='utf-8').read()
        if self.name.endswith('.css'):
            spans, ranges = lex_css(self.src), folds_css(self.src)
        else:
            spans, ranges = lex_html(self.src), folds_html(self.src)
        self.lines = split_lines(spans)
        self.raw = self.src.split('\n')
        if self.raw and self.raw[-1] == '':
            self.raw = self.raw[:-1]
        self.n = len(self.raw)
        self.fold = fold_state(ranges, self.n)

    def indent(self, ln):
        s = self.raw[ln - 1]
        return len(s) - len(s.lstrip(' ')) if s.strip() else None

    def guide_cols(self, ln):
        ind = self.indent(ln)
        if ind is None:      # blank line: look both ways
            p = q = None
            for k in range(ln - 1, 0, -1):
                if self.indent(k) is not None: p = self.indent(k); break
            for k in range(ln + 1, self.n + 1):
                if self.indent(k) is not None: q = self.indent(k); break
            lim = max(p or 0, q or 0)
            return [c for c in range(4, lim + 1, 4)]
        return [c for c in range(4, ind, 4)]

    def page(self, a, b, width=1100):
        digits = max(len(str(self.n)), 3)
        lnw = 22 + digits * 9 + 14
        rows_ln, rows_fm, rows_tx = [], [], []
        for ln in range(a, b + 1):
            rows_ln.append(f'<div class="l">{ln}</div>')
            rows_fm.append(f'<div class="l">{fold_svg(self.fold[ln])}</div>')
            spans = ''.join(f'<span class="{st}">{H.escape(s)}</span>' if st != 'ws' else H.escape(s)
                            for st, s in (self.lines[ln - 1] if ln - 1 < len(self.lines) else []))
            guides = ''.join(f'<i class="g" style="left:{2 + c * CHAR:.1f}px"></i>' for c in self.guide_cols(ln))
            rows_tx.append(f'<div class="l">{guides}{spans or "&#8203;"}</div>')
        nvis = b - a + 1
        trackh = nvis * 18
        th = max(24, trackh * min(1, nvis / self.n))
        top = (trackh - th) * ((a - 1) / max(1, self.n - nvis)) if self.n > nvis else 0
        css = CSS % {'W': width, 'LNW': lnw, 'LNPAD': 22}
        return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>'
                f'<div id="win"><div id="tabs">{tabbar(self.name, width)}'
                f'<div id="arrows"><div>&#9664;</div><div>&#9654;</div></div></div>'
                f'<div id="ed"><div id="ln">{"".join(rows_ln)}</div><div id="fm">{"".join(rows_fm)}</div>'
                f'<div id="tx">{"".join(rows_tx)}</div>'
                f'<div id="sb"><div id="thumb" style="top:{top:.0f}px;height:{th:.0f}px"></div></div></div></div>'
                f'</body></html>')
