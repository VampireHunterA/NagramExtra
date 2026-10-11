#!/usr/bin/env python3
# Re-mount the six modern-variant foregrounds: the one-off build (9c683b9aac)
# bbox-centered the glyphs, losing the sa icons' optical mass compensation
# (plane reads right-shifted). Modern art sources are not in the repo, so the
# shipped xxxhdpi lossless webp is the master; each glyph is re-placed at its
# upstream sa icon's bbox offset, scaled to the modern glyph size.
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RES = f"{ROOT}/TMessagesProj/src/main/res"
DENSITIES = [("mdpi", 1), ("hdpi", 1.5), ("xhdpi", 2), ("xxhdpi", 3), ("xxxhdpi", 4)]
BASE = 108

MODERN_TO_UPSTREAM = {
    "telegram": "icon_foreground_sa",
    "aqua": "icon_foreground_sa",
    "nox": "icon_foreground_sa",
    "vintage": "icon_6_foreground_sa",
    "premium": "icon_3_foreground_sa",
    "classic": "icon_5_foreground_sa",
}

def alpha_bbox(im, thresh=25):
    return im.getchannel("A").point(lambda p: 255 if p > thresh else 0).getbbox()

def mass_center_offset(im, thresh=25):
    a = im.getchannel("A").point(lambda p: p if p > thresh else 0)
    w, h = im.size
    px = a.load()
    tot = sx = sy = 0
    for y in range(h):
        for x in range(w):
            v = px[x, y]
            if v:
                tot += v
                sx += x * v
                sy += y * v
    return sx / tot - w / 2, sy / tot - h / 2

def main():
    size = BASE * 4
    for slug, upstream in MODERN_TO_UPSTREAM.items():
        modern = Image.open(f"{RES}/drawable-xxxhdpi/ic_{slug}_modern_foreground.webp").convert("RGBA")
        ref = Image.open(f"{RES}/mipmap-xxxhdpi/{upstream}.png").convert("RGBA")
        mcore = modern.crop(alpha_bbox(modern))
        rbb = alpha_bbox(ref)
        rcore_w, rcore_h = rbb[2] - rbb[0], rbb[3] - rbb[1]
        r_cx = (rbb[0] + rbb[2]) / 2 - ref.width / 2
        r_cy = (rbb[1] + rbb[3]) / 2 - ref.height / 2
        # isotropic scale: one ratio for both axes keeps the 2D offset direction
        ratio = ((mcore.width / rcore_w) + (mcore.height / rcore_h)) / 2
        t_cx = r_cx * ratio
        t_cy = r_cy * ratio
        out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        left = round(size / 2 + t_cx - mcore.width / 2)
        top = round(size / 2 + t_cy - mcore.height / 2)
        out.alpha_composite(mcore, (left, top))
        for dpi, mult in DENSITIES:
            px = int(BASE * mult)
            layer = out if px == size else out.resize((px, px), Image.LANCZOS)
            layer.save(f"{RES}/drawable-{dpi}/ic_{slug}_modern_foreground.webp", "WEBP", lossless=True)
        mo = mass_center_offset(out)
        print(f"{slug:<9} ratio {ratio:.3f}  mount bboxC {t_cx:+6.1f}/{t_cy:+6.1f}  massC {mo[0]:+6.1f}/{mo[1]:+6.1f}")

if __name__ == "__main__":
    main()
