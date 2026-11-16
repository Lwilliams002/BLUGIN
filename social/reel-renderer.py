import math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = '/Users/lezdev/Desktop/Williams/blu-gin/'
F = '/private/tmp/claude-501/-Users-lezdev-Desktop-Williams/6b0fffbc-3610-42c9-93c3-bbe93fd63083/scratchpad/fonts/'
OUT = sys.argv[1]
W, H, FPS = 1080, 1920, 30
BG = (10, 11, 15); GOLD = (210, 178, 108); INK = (243, 240, 232); MUTED = (182, 179, 171); BTN_INK = (26, 21, 7)

def font(name, size, var=None):
    f = ImageFont.truetype(F + name, size)
    if var: f.set_variation_by_name(var)
    return f

F_BRAND = font('Playfair.ttf', 150); F_BRAND_S = font('Playfair.ttf', 96)
F_SUB = font('Jost.ttf', 30, 'Regular'); F_KICK = font('Jost.ttf', 30, 'Regular')
F_H = font('Jost.ttf', 92, 'Regular'); F_H2 = font('Jost.ttf', 74, 'Regular')
F_IT = font('PlayfairItalic.ttf', 54); F_BODY = font('Jost.ttf', 40, 'Light')
F_PRICE = font('Playfair.ttf', 52); F_BTN = font('Jost.ttf', 30, 'Medium'); F_SMALL = font('Jost.ttf', 34, 'Regular')

# easing
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_in_out(t): t = clamp(t); return t * t * (3 - 2 * t)
def back_out(t): t = clamp(t); c = 1.70158; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
def clamp(t): return max(0.0, min(1.0, t))
def seg(t, a, b): return clamp((t - a) / (b - a)) if b > a else 1.0

_cache = {}
def photo(name):
    if name not in _cache:
        _cache[name] = Image.open(ROOT + 'assets/img/web/' + name).convert('RGB')
    return _cache[name]

def cover(im, w, h, zoom=1.0, px=0.5, py=0.5):
    """Cover-crop im into w×h at a zoom, with focal point (px,py)."""
    r = max(w / im.width, h / im.height) * zoom
    sw, sh = int(im.width * r), int(im.height * r)
    s = im.resize((sw, sh), Image.BILINEAR)
    x = int((sw - w) * px); y = int((sh - h) * py)
    return s.crop((x, y, x + w, y + h))

def darken(im, k):
    return Image.blend(im, Image.new('RGB', im.size, BG), 1 - k)

def rounded_mask(w, h, r):
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m

def perimeter_points(x0, y0, x1, y1, r, n=400):
    """Points along a rounded rect perimeter starting at top centre, clockwise."""
    pts = []
    w, h = x1 - x0, y1 - y0
    straight = 2 * (w - 2 * r) + 2 * (h - 2 * r); arcs = 2 * math.pi * r; total = straight + arcs
    segs = [('line', (x0 + w / 2, y0), (x1 - r, y0)), ('arc', (x1 - r, y0 + r), -90, 0), ('line', (x1, y0 + r), (x1, y1 - r)), ('arc', (x1 - r, y1 - r), 0, 90), ('line', (x1 - r, y1), (x0 + r, y1)), ('arc', (x0 + r, y1 - r), 90, 180), ('line', (x0, y1 - r), (x0, y0 + r)), ('arc', (x0 + r, y0 + r), 180, 270), ('line', (x0 + r, y0), (x0 + w / 2, y0))]
    for s in segs:
        if s[0] == 'line':
            (ax, ay), (bx, by) = s[1], s[2]; L = math.hypot(bx - ax, by - ay); k = max(2, int(n * L / total))
            pts += [(ax + (bx - ax) * i / k, ay + (by - ay) * i / k) for i in range(k)]
        else:
            (cx, cy), a0, a1 = s[1], s[2], s[3]; k = max(2, int(n * (math.pi * r / 2) / total))
            pts += [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / k)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / k))) for i in range(k)]
    return pts

def draw_border(d, box, r, progress, width=3, color=GOLD):
    pts = perimeter_points(*box, r)
    k = int(len(pts) * clamp(progress))
    if k > 1: d.line(pts[:k], fill=color, width=width, joint='curve')

def text_center(d, y, text, f, fill, alpha=1.0, dx=0, spacing=0):
    if alpha <= 0: return
    if spacing:
        text = (' ' * spacing).join(text)
    w = d.textlength(text, font=f)
    col = tuple(int(c * alpha + b * (1 - alpha)) for c, b in zip(fill, BG)) if alpha < 1 else fill
    d.text(((W - w) / 2 + dx, y), text, font=f, fill=col)

def paste_alpha(base, layer, pos, alpha):
    if alpha <= 0: return
    if alpha >= 1: base.paste(layer[0], pos, layer[1]); return
    m = layer[1].point(lambda v: int(v * alpha)); base.paste(layer[0], pos, m)

def framed_photo(name, w, h, zoom, px=0.5, py=0.5, dark=0.7, r=40):
    im = darken(cover(photo(name), w, h, zoom, px, py), dark)
    return (im, rounded_mask(w, h, r))

def gold_button(d, cx, cy, text, alpha=1.0, scale=1.0):
    bw, bh = int(480 * scale), int(80 * scale)
    if alpha <= 0 or scale <= 0: return
    col = tuple(int(c * alpha + b * (1 - alpha)) for c, b in zip(GOLD, BG))
    d.rounded_rectangle((cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2), 14, fill=col)
    t = (' ' * 2).join(text); tw = d.textlength(t, font=F_BTN)
    d.text((cx - tw / 2, cy - 18), t, font=F_BTN, fill=BTN_INK)

# ---------- scenes ----------
def scene_intro(t, img, d):
    # 0–3.2s: wordmark grows in, sub line, rule draws
    a = ease_out(seg(t, 0.2, 1.2)); s = 0.9 + 0.1 * back_out(seg(t, 0.2, 1.4))
    f = font('Playfair.ttf', int(150 * s))
    text_center(d, H / 2 - 120 - (f.size - 150) / 2, 'Blu Gin', f, GOLD, a)
    text_center(d, H / 2 + 60, 'RESTAURANT & LOUNGE · MIAMI BEACH', F_SUB, GOLD, ease_out(seg(t, 1.0, 1.9)), spacing=1)
    p = ease_in_out(seg(t, 1.4, 2.4)); lw = int(300 * p)
    if lw > 2:
        d.line((W / 2 - 24 - lw, H / 2 + 150, W / 2 - 24, H / 2 + 150), fill=GOLD, width=2)
        d.line((W / 2 + 24, H / 2 + 150, W / 2 + 24 + lw, H / 2 + 150), fill=GOLD, width=2)
    dp = back_out(seg(t, 1.9, 2.5)) * 12
    if dp > 0: d.polygon([(W / 2, H / 2 + 150 - dp), (W / 2 + dp, H / 2 + 150), (W / 2, H / 2 + 150 + dp), (W / 2 - dp, H / 2 + 150)], fill=GOLD)
    text_center(d, H / 2 + 200, 'Upscale dining in Miami Beach', F_IT, INK, ease_out(seg(t, 2.2, 3.0)))

def scene_room(t, img, d):
    # photo slides up into frame, border draws, text enters
    pw, ph = W - 120, 1150
    rise = (1 - ease_out(seg(t, 0, 1.0))) * 260
    y0 = 300 + int(rise)
    zoom = 1.08 + 0.06 * seg(t, 0, 4.0)
    layer = framed_photo('room-blue.jpg', pw, ph, zoom, 0.55, 0.5, 0.75)
    paste_alpha(img, layer, (60, y0), ease_out(seg(t, 0, 0.8)))
    d = ImageDraw.Draw(img)
    draw_border(d, (60 + 28, y0 + 28, 60 + pw - 28, y0 + ph - 28), 30, seg(t, 0.5, 2.0))
    text_center(d, 150, 'OCEANFRONT AT THE CASTLE BEACH CLUB', F_KICK, INK, ease_out(seg(t, 1.0, 1.8)), spacing=1)
    dx = (1 - ease_out(seg(t, 1.3, 2.2))) * -120
    text_center(d, 1500, 'Dinner by the ocean,', F_H2, INK, ease_out(seg(t, 1.3, 2.2)), dx)
    dx2 = (1 - ease_out(seg(t, 1.7, 2.6))) * 120
    text_center(d, 1595, 'the lounge after dark.', F_H2, GOLD, ease_out(seg(t, 1.7, 2.6)), dx2)

PLATES = [('whole-snapper.jpg', 'Whole Florida snapper', 'for two', '$59.99', 0.5, 0.5), ('lobster-paella.jpg', 'Seafood paella', 'Cuban style', '$32.99', 0.5, 0.55), ('shrimp-tower.jpg', 'Surf and turf', 'mignon', '$47.00', 0.5, 0.45)]
def scene_plates(t, img, d):
    each = 1.5; i = min(len(PLATES) - 1, int(t / each)); lt = t - i * each
    name, l1, l2, price, px, py = PLATES[i]
    size = 820; zoom = 1.0 + 0.12 * (lt / each)
    im = darken(cover(photo(name), size, size, zoom, px, py), 0.95)
    mask = Image.new('L', (size, size), 0); ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    sc = 0.85 + 0.15 * back_out(seg(lt, 0, 0.5)); s2 = int(size * sc)
    im2 = im.resize((s2, s2), Image.BILINEAR); m2 = mask.resize((s2, s2), Image.BILINEAR)
    cx, cy = W // 2, 760
    paste_alpha(img, (im2, m2), (cx - s2 // 2, cy - s2 // 2), ease_out(seg(lt, 0, 0.35)))
    d = ImageDraw.Draw(img)
    # ring
    rp = seg(lt, 0.1, 0.8); rr = s2 // 2 + 26
    if rp > 0: d.arc((cx - rr, cy - rr, cx + rr, cy + rr), -90, -90 + int(360 * rp), fill=GOLD, width=3)
    # price badge pop
    bs = back_out(seg(lt, 0.35, 0.8)); br = int(100 * bs)
    if br > 2:
        bx, by = cx + s2 // 2 - 60, cy - s2 // 2 + 60
        d.ellipse((bx - br, by - br, bx + br, by + br), fill=GOLD)
        f = font('Playfair.ttf', max(8, int(46 * bs))); tw = d.textlength(price, font=f)
        d.text((bx - tw / 2, by - f.size * 0.62), price, font=f, fill=BTN_INK)
    text_center(d, 180, 'SIGNATURE PLATES', F_KICK, GOLD, ease_out(seg(t, 0, 0.6)), spacing=1)
    a = ease_out(seg(lt, 0.3, 0.8)); dy = (1 - a) * 40
    text_center(d, 1290 + dy, l1, F_H2, INK, a)
    text_center(d, 1385 + dy, l2, F_IT, MUTED, ease_out(seg(lt, 0.45, 0.95)))
    dots_y = 1540
    for k in range(len(PLATES)):
        r = 9 if k == i else 6; col = GOLD if k == i else (70, 72, 80)
        d.ellipse((cx - 40 + k * 40 - r, dots_y - r, cx - 40 + k * 40 + r, dots_y + r), fill=col)

LOUNGE = ['Hookah on the pool deck', 'Fifteen house cocktails', "Francisco's wine list", 'Every night until midnight']
def scene_lounge(t, img, d):
    zoom = 1.22 - 0.14 * ease_out(seg(t, 0, 3.6))
    full = darken(cover(photo('pool-night.jpg'), W, H, zoom, 0.5, 0.55), 0.6)
    img.paste(full, (0, 0))
    # bottom scrim
    scrim = Image.new('L', (W, H), 0); sd = ImageDraw.Draw(scrim)
    for y in range(900, H): sd.line((0, y, W, y), fill=int(235 * ((y - 900) / (H - 900)) ** 1.2))
    img.paste(Image.new('RGB', (W, H), BG), (0, 0), scrim)
    d = ImageDraw.Draw(img)
    a = ease_out(seg(t, 0.2, 1.0)); dx = (1 - a) * -100
    text_center(d, 1180, 'After dark', font('Playfair.ttf', 120), GOLD, a, dx)
    for k, line in enumerate(LOUNGE):
        la = ease_out(seg(t, 0.9 + k * 0.28, 1.5 + k * 0.28)); ldx = (1 - la) * 60
        text_center(d, 1360 + k * 70, line, F_BODY, INK, la, ldx)
    draw_border(d, (50, 50, W - 50, H - 50), 36, seg(t, 0.1, 1.6), width=2)

def scene_end(t, img, d):
    a0 = ease_out(seg(t, 0, 0.6))
    text_center(d, 330, 'Blu Gin', F_BRAND_S, GOLD, a0)
    text_center(d, 470, 'RESTAURANT & LOUNGE · MIAMI BEACH', F_SUB, GOLD, ease_out(seg(t, 0.2, 0.9)), spacing=1)
    pw, ph = W - 160, 700; y0 = 580
    layer = framed_photo('room-window.jpg', pw, ph, 1.05 + 0.05 * seg(t, 0, 4), 0.5, 0.5, 0.7)
    paste_alpha(img, layer, (80, y0), ease_out(seg(t, 0.3, 1.0)))
    d = ImageDraw.Draw(img)
    draw_border(d, (80 + 26, y0 + 26, 80 + pw - 26, y0 + ph - 26), 28, seg(t, 0.6, 1.8))
    gold_button(d, W / 2, 1400, 'BOOK A TABLE', ease_out(seg(t, 1.0, 1.5)), back_out(seg(t, 1.0, 1.6)))
    text_center(d, 1520, '5445 COLLINS AVENUE, MIAMI BEACH', F_SMALL, INK, ease_out(seg(t, 1.4, 2.0)), spacing=1)
    text_center(d, 1580, '(305) 397-8687', F_SMALL, INK, ease_out(seg(t, 1.6, 2.2)), spacing=1)
    text_center(d, 1660, '@BLUGINMIAMI', F_SMALL, GOLD, ease_out(seg(t, 1.8, 2.4)), spacing=1)
    text_center(d, 1740, 'Open every day · 8:30 am to midnight', F_IT, MUTED, ease_out(seg(t, 2.0, 2.6)))

SCENES = [(scene_intro, 3.4), (scene_room, 4.2), (scene_plates, 4.5), (scene_lounge, 3.8), (scene_end, 4.0)]
XF = 0.5  # crossfade seconds

def render_scene(fn, t):
    img = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(img); fn(t, img, d); return img

def frame_at(T):
    acc = 0.0
    for i, (fn, dur) in enumerate(SCENES):
        if T < acc + dur or i == len(SCENES) - 1:
            lt = T - acc
            img = render_scene(fn, lt)
            # crossfade from previous scene start
            if i > 0 and lt < XF:
                pfn, pdur = SCENES[i - 1]
                prev = render_scene(pfn, pdur + lt)
                img = Image.blend(prev, img, ease_in_out(lt / XF))
            return img
        acc += dur

total = sum(d for _, d in SCENES)
n = int(total * FPS)
os.makedirs(OUT, exist_ok=True)
start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
end = int(sys.argv[3]) if len(sys.argv) > 3 else n
for k in range(start, end):
    frame_at(k / FPS).save(f'{OUT}/{k:04d}.jpg', quality=90)
print('frames', n, 'seconds', total)
