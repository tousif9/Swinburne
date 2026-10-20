import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import npp
from playwright.sync_api import sync_playwright
BASE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get('SITE') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'A1-final', 'tousifakhand_assign1', 'assign1')
def render(jobs, out_dir, width=1100, scale=2):
    os.makedirs(out_dir, exist_ok=True)
    docs = {}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get('CHROME_PATH') or None)
        pg = b.new_page(viewport={'width': width + 2, 'height': 400}, device_scale_factor=scale)
        for name, f, a, z in jobs:
            path = os.path.join(SITE, 'styles', f) if f.endswith('.css') else os.path.join(SITE, f)
            d = docs.setdefault(path, npp.Doc(path))
            htmlfile = os.path.join(BASE, '_code.html')
            open(htmlfile, 'w', encoding='utf-8').write(d.page(a, z, width))
            pg.goto('file://' + htmlfile); pg.wait_for_timeout(150)
            pg.evaluate('document.fonts.ready')
            pg.locator('#win').screenshot(path=os.path.join(out_dir, name + '.png'))
        b.close()
if __name__ == '__main__':
    render([('t_html', 'explore.html', 1, 38), ('t_css', 'style.css', 25, 72)], os.path.join(BASE, 'test'))
