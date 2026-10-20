"""Website screenshots for the report (desktop 1760 wide, page only; phone = iPhone 12 Pro)."""
import os, sys
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = 'file://' + os.path.abspath(os.environ.get('SITE') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'A1-final', 'tousifakhand_assign1', 'assign1')) + '/'
OUT = os.path.join(BASE, 'web')
GF = os.path.join(os.path.dirname(BASE), 'gfonts')
W, VH = 1760, 900
os.makedirs(OUT, exist_ok=True)


def fonts(route):
    u = route.request.url
    if 'googleapis' in u:
        route.fulfill(path=os.path.join(GF, 'fonts.css'), content_type='text/css')
    else:
        route.fulfill(path=os.path.join(GF, 'assign1/styles/fonts', u.rsplit('/', 1)[1]), content_type='font/woff2')


class Shooter:
    def __init__(self, p):
        self.b = p.chromium.launch(executable_path=os.environ.get('CHROME_PATH') or None)

    def open(self, page, h=VH, phone=False, wait=3500):
        if phone:
            ctx = self.b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                                     is_mobile=True, has_touch=True)
        else:
            ctx = self.b.new_context(viewport={'width': W, 'height': h}, device_scale_factor=1)
        ctx.route('**/fonts.googleapis.com/**', fonts)
        ctx.route('**/fonts.gstatic.com/**', fonts)
        ctx.route('**/maps.google.com/**', lambda r: r.abort())
        pg = ctx.new_page()
        pg.goto(SITE + page)
        pg.evaluate("document.documentElement.style.scrollBehavior='auto'")
        pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
        pg.wait_for_function("[...document.images].every(i=>i.complete)", timeout=20000)
        pg.evaluate('document.fonts.ready')
        pg.wait_for_timeout(wait)
        self.pg, self.ctx = pg, ctx
        return pg

    def close(self):
        self.ctx.close()

    def box(self, sel, nth=0):
        return self.pg.locator(sel).nth(nth).evaluate(
            "e=>{const r=e.getBoundingClientRect();return [r.left+scrollX,r.top+scrollY,r.width,r.height]}")

    def nav_h(self):
        return self.pg.evaluate("document.getElementById('main-nav').getBoundingClientRect().height")

    def region(self, name, top, bottom, pad=24, hover=None, before=None, x0=0, x1=None, pt=None, pb=None):
        """top/bottom: page Y coords. Uses a tall viewport so the region shows below the sticky menu."""
        pg = self.pg
        nh = self.nav_h()
        pt = pad if pt is None else pt
        pb = pad if pb is None else pb
        top = top - pt + pad
        h = bottom - top + pad + pb
        vh = int(h + nh + 200)
        pg.set_viewport_size({'width': W, 'height': max(VH, vh)})
        pg.wait_for_timeout(300)
        y = top - pad - nh - 2
        pg.evaluate(f"window.scrollTo(0,{max(0, y)})")
        pg.wait_for_timeout(400)
        if before: before()
        if hover:
            pg.locator(hover[0]).nth(hover[1] if len(hover) > 1 else 0).hover()
            pg.wait_for_timeout(1200)
        self.steady()
        sy = pg.evaluate('scrollY')
        vhh = pg.viewport_size['height']
        assert 0 <= top - pad - sy and top - pad - sy + h <= vhh + 1, (name, top, pad, sy, h, vhh)
        clip = {'x': x0, 'y': top - pad - sy, 'width': (x1 or W) - x0, 'height': h}
        pg.screenshot(path=os.path.join(OUT, name + '.png'), clip=clip)
        pg.set_viewport_size({'width': W, 'height': VH})

    def sec(self, name, sel_top, sel_bottom=None, pad=24, nth_top=0, nth_bottom=0, extra=0, **kw):
        t = self.box(sel_top, nth_top)
        bsel = sel_bottom or sel_top
        b = self.box(bsel, nth_bottom if sel_bottom else nth_top)
        self.region(name, t[1], b[1] + b[3] + extra, pad=pad, **kw)

    def steady(self, sel='.rotator-words'):
        """Wait until the rotating banner word is fully still (not mid-slide)."""
        pg = self.pg
        for _ in range(80):
            r = pg.evaluate(f"(()=>{{const e=document.querySelector('{sel}');if(!e)return null;const r=e.getBoundingClientRect();return [r.left,r.top,r.width,r.height]}})()")
            if not r or r[1] + r[3] < 0 or r[1] > pg.viewport_size['height']:
                return
            clip = {'x': max(0, r[0] - 40), 'y': max(0, r[1] - 10), 'width': r[2] + 80, 'height': r[3] + 20}
            a = pg.screenshot(clip=clip); pg.wait_for_timeout(250); b = pg.screenshot(clip=clip)
            if a == b:
                pg.wait_for_timeout(50); return
            pg.wait_for_timeout(150)

    def view(self, name, clip_h=None, scroll=None):
        pg = self.pg
        if scroll is not None:
            pg.evaluate(f"window.scrollTo(0,{scroll})"); pg.wait_for_timeout(500)
        self.steady()
        vs = pg.viewport_size
        pg.screenshot(path=os.path.join(OUT, name + '.png'),
                      clip={'x': 0, 'y': 0, 'width': vs['width'], 'height': clip_h or vs['height']})


def main(only=None):
    with sync_playwright() as p:
        s = Shooter(p)
        def want(k): return not only or k in only

        # ---------------- index.html
        if any(want(k) for k in ['2', '6', '8', '10', '44', '56', '76', '82', '52']):
            pg = s.open('index.html', wait=5000)
            if want('44'):
                b = s.box('#hero'); s.view('44', clip_h=int(b[1] + b[3] + 24))
            if want('56'):
                s.sec('56', '#hero')
            if want('8'):
                t = s.box('#hero'); a = s.box('#about'); asd = s.box('main aside')
                s.region('8', t[1], max(a[1] + a[3], asd[1] + asd[3]))
            if want('10'):
                s.sec('10a', '#features')
                s.sec('10b', '#flip-cards', hover=('.flip-card', 1))
                s.sec('10c', '#get-involved')
            if want('82'):
                s.sec('82', '#flip-cards', hover=('.flip-card', 2))
            if want('76') or want('2'):
                pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(400)
                if want('76'): s.view('76a')
                pg.click('label.menu-button'); pg.wait_for_timeout(900)
                if want('2'): s.view('2')
                if want('76'): s.view('76b')
                pg.click('label.menu-close'); pg.wait_for_timeout(600)
            if want('6'):
                f = s.box('#site-footer')
                vh = int(max(VH, f[3] + 140)); pg.set_viewport_size({'width': W, 'height': vh})
                pg.evaluate('window.scrollTo(0,document.body.scrollHeight)'); pg.wait_for_timeout(700)
                pg.screenshot(path=os.path.join(OUT, '6.png'),
                              clip={'x': 0, 'y': vh - f[3] - 40, 'width': W, 'height': f[3] + 40})
                pg.set_viewport_size({'width': W, 'height': VH})
            s.close()

        # ---------------- explore.html
        if any(want(k) for k in ['12', '14', '16', '48', '62', '64', '84', '86']):
            pg = s.open('explore.html')
            if want('12'):
                s.sec('12a', '#family-tree')
                it = s.box('#intro'); asd = s.box('main aside')
                s.region('12b', min(it[1], asd[1]), max(it[1] + it[3], asd[1] + asd[3]))
                s.sec('12c', '#link-map')
            if want('14'):
                s.sec('14a', '#levels', '#quick-links')
                s.sec('14b', '#flip-gallery', hover=('#flip-gallery .flip-card', 0))
                s.sec('14c', '#photo-gallery')
                s.sec('14d', '#featured-plants')
            if want('62'):
                s.sec('62a', '#link-map')
                s.sec('62b', '#quick-links')
            if want('16') or want('64') or want('86'):
                pg.locator('#quiz summary').nth(0).click(); pg.wait_for_timeout(500)
                if want('16'): s.sec('16a', '#quiz')
                if want('86'): s.sec('86', '#quiz .quiz-card', nth_top=0, pad=20)
                pg.locator('#quiz summary').nth(0).click()
                pg.locator('#quiz summary').nth(1).click(); pg.wait_for_timeout(500)
                if want('64'): s.sec('64', '#quiz')
                pg.locator('#quiz summary').nth(1).click(); pg.wait_for_timeout(300)
            if want('16') or want('84'):
                hv = ('.stars label[for="star4"]', 0)
                if want('16'): s.sec('16b', '#rate-page', hover=hv)
                if want('84'): s.sec('84', '#rate-page', hover=hv, pad=20)
            if want('48'):
                pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(400)
                pg.hover('#main-nav .has-submenu > a'); pg.wait_for_timeout(800)
                sub = pg.locator('#main-nav .submenu').evaluate('e=>e.getBoundingClientRect().bottom')
                h2 = pg.locator('#family-tree h2').evaluate('e=>e.getBoundingClientRect().bottom')
                s.view('48', clip_h=int(max(sub, h2) + 16))
            if want('16'):
                pg.goto(SITE + 'explore.html#view-exp-1'); pg.evaluate("document.documentElement.style.scrollBehavior='auto'"); pg.wait_for_timeout(1500)
                s.view('16c')
            s.close()

        # ---------------- explore1.html
        if any(want(k) for k in ['18', '20', '22', '49', '63', '80']):
            pg = s.open('explore1.html')
            if want('18'):
                m = s.box('main'); asd = s.box('main aside'); nv = s.box('#intro')
                s.region('18a', m[1], max(nv[1] + nv[3], asd[1] + asd[3]), pt=0, pb=24)
                s.sec('18b', '#steps', '#summary')
            if want('20') or want('63'):
                art = '#dipterocarpaceae'
                if want('20'):
                    s.sec('20a', art, f'{art} .plant-features', pad=20)
                    s.sec('20b', f'{art} .plant-gallery', pad=20)
                if want('63'):
                    s.sec('63a', f'{art} .plant-facts', pad=20)
                    s.sec('63b', f'{art} .plant-gallery', pad=20)
                    s.sec('63c', '.explore-pager', pad=24)
            if want('22'):
                s.sec('22b', '.explore-pager', pad=24)
            if want('49'):
                pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(300)
                pg.click('label.menu-button'); pg.wait_for_timeout(900); s.view('49')
                pg.click('label.menu-close'); pg.wait_for_timeout(500)
            if want('22'):
                pg.goto(SITE + 'explore1.html#view-dipterocarpaceae-1'); pg.wait_for_timeout(1500); s.view('22a')
            s.close()

        # ---------------- explore2.html
        if want('24'):
            pg = s.open('explore2.html')
            s.sec('24a', '#summary')
            s.sec('24b', '#dipterocarpus', '#dipterocarpus .plant-features', pad=20)
            s.sec('24c', '#dipterocarpus .plant-gallery', pad=20)
            s.close()

        # ---------------- explore3.html
        if any(want(k) for k in ['26', '78', '80']):
            pg = s.open('explore3.html')
            if want('26'):
                s.sec('26a', '#d-alatus', '#d-alatus .plant-facts', pad=20)
                s.sec('26b', '#d-alatus .plant-gallery', pad=20)
            if want('80'):
                s.sec('80a', '#d-alatus .plant-gallery', pad=20)
            if want('78'):
                pg.set_viewport_size({'width': W, 'height': VH})
                y = s.box('#m-glaber')[1]
                pg.evaluate(f'window.scrollTo(0,{y - 120})'); pg.wait_for_timeout(700)
                s.view('78')
            if want('80'):
                lb = pg.locator('#d-alatus .plant-gallery a').nth(0).get_attribute('href')
                pg.goto(SITE + 'explore3.html' + lb); pg.wait_for_timeout(1500); s.view('80b')
            s.close()

        # ---------------- identify.html
        if want('28'):
            pg = s.open('identify.html')
            m = s.box('main'); asd = s.box('main aside'); tips = s.box('#photo-tips')
            s.region('28a', m[1], max(tips[1] + tips[3], asd[1] + asd[3]), pt=0, pb=24)
            s.sec('28b', '#search')
            s.close()

        # ---------------- contributor.html
        if any(want(k) for k in ['32', '66', '52']):
            pg = s.open('contributor.html')
            if want('32'):
                asd = s.box('main aside'); intro = s.box('#contributor-intro')
                c6 = s.box('#contribution-cards .card', 5)
                s.region('32', min(asd[1], intro[1]), c6[1] + c6[3])
            if want('66'):
                a6 = s.box('main aside'); g6 = s.box('#contribution-cards .card-grid')
                s.region('66', a6[1] + a6[3] + 4, g6[1] + g6[3], pt=0, pb=24)
            if want('52'):
                f = s.box('#site-footer')
                vh = int(max(VH, f[3] + 140)); pg.set_viewport_size({'width': W, 'height': vh})
                pg.evaluate('window.scrollTo(0,document.body.scrollHeight)'); pg.wait_for_timeout(700)
                pg.screenshot(path=os.path.join(OUT, '52.png'),
                              clip={'x': 0, 'y': vh - f[3] - 40, 'width': W, 'height': f[3] + 40})
            s.close()

        # ---------------- contribute.html
        if want('34') or want('54'):
            pg = s.open('contribute.html')
            if want('34'):
                pg.fill('#contributorName', 'Tousif Akhand')
                pg.fill('#plantName', 'Plant 123')
                fm = s.box('#contribute-form'); asd = s.box('main aside')
                ftop = min(fm[1], asd[1]); fbot = max(fm[1] + fm[3], asd[1] + asd[3])
                s.region('34', ftop, fbot, before=lambda: pg.focus('#plantName'))
            if want('54'):
                pg.fill('#contributorName', 'Tousif Akhand'); pg.fill('#plantName', 'Plant 123')
                fm = s.box('#contribute-form'); asd = s.box('main aside')
                ftop = min(fm[1], asd[1]); fbot = max(fm[1] + fm[3], asd[1] + asd[3])
                s.region('54a', ftop, fbot, before=lambda: pg.focus('#contributorName'))
                s.region('54b', ftop, fbot, before=lambda: pg.focus('#plantName'))
            s.close()

        # ---------------- profile.html
        if want('38') or want('60'):
            pg = s.open('profile.html')
            if want('38'):
                m = s.box('main'); ab = s.box('#profile-about')
                s.region('38a', m[1], ab[1] + ab[3], pad=10)
                d = s.box('#profile-details'); e = s.box('.email-me')
                s.region('38b', d[1], e[1] + e[3])
            if want('60'):
                m = s.box('main'); r = s.box('.profile-table tr', 2)
                s.region('60a', m[1], r[1] + r[3], pt=0, pb=2)
                last = s.box('.profile-table tbody tr:last-child'); e = s.box('.email-me')
                s.region('60b', last[1], e[1] + e[3], pt=1, pb=24)
            s.close()

        # ---------------- enhancement1.html
        if want('40'):
            pg = s.open('enhancement1.html')
            s.sec('40', '#enhancements-intro', '#enh-fluid')
            s.close()

        # ---------------- acknowledgement.html
        if want('42') or want('68'):
            pg = s.open('acknowledgement.html')
            if want('42'):
                s.sec('42', '#ack-intro', '#ack-photos .credit-group', nth_bottom=0)
            if want('68'):
                s.sec('68', '#ack-icons')
            s.close()

        # ---------------- phone
        if any(want(k) for k in ['45', '71', '72', '73']):
            if want('45') or want('71'):
                pg = s.open('index.html', phone=True, wait=5000)
                if want('45'): s.view('45')
                if want('71'):
                    nav = pg.evaluate("document.getElementById('main-nav').getBoundingClientRect().bottom")
                    s.view('71', clip_h=int(nav + 14))
                s.close()
            if want('72'):
                pg = s.open('explore1.html', phone=True)
                nh = s.nav_h()
                y = s.box('.breadcrumb')[1]; pg.evaluate(f'window.scrollTo(0,{y - nh - 12})'); pg.wait_for_timeout(500); s.view('72a')
                y = s.box('#dipterocarpaceae .plant-facts')[1]; pg.evaluate(f'window.scrollTo(0,{y - nh - 14})'); pg.wait_for_timeout(500); s.view('72b')
                y = s.box('.explore-pager')[1]; pg.evaluate(f'window.scrollTo(0,{y - 420})'); pg.wait_for_timeout(500); s.view('72c')
                s.close()
            if want('73'):
                pg = s.open('explore3.html', phone=True)
                nh = s.nav_h()
                y = s.box('#d-alatus .plant-gallery')[1]; pg.evaluate(f'window.scrollTo(0,{y - nh - 14})'); pg.wait_for_timeout(600); s.view('73')
                s.close()
        s.b.close()


if __name__ == '__main__':
    main(set(sys.argv[1:]) or None)
