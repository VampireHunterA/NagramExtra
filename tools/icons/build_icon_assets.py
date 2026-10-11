#!/usr/bin/env python3
# NagramXTurbo icon asset pipeline: sources/<theme>/ -> res/ layers
# Per theme needs: foreground.png, background.jpg, monochrome.png, alpha_exact.png
# After regenerating, run crop_notification_glyphs.py --apply: this emits
# notification glyphs uncropped (fill 1.0) and the cropper brings them to 91%/83% (#140)
import os, sys
from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = f"{ROOT}/TMessagesProj/src/main/res"
DENSITIES = [("mdpi",1),("hdpi",1.5),("xhdpi",2),("xxhdpi",3),("xxxhdpi",4)]  # 108dp * dpi
BASE = 108  # adaptive canvas dp

THEMES = [
    "turbo", "sky", "sunset", "blue_night", "halloween",
    "paper_box", "paper_fire", "carbon",
    "gold", "matrix", "neon", "space", "hexagon", "pixel", "glitch",
]

def load(theme_dir, name):
    fg = Image.open(f"{theme_dir}/foreground.png").convert("RGBA")
    bg = Image.open(f"{theme_dir}/background.jpg").convert("RGB")
    mono_path = f"{theme_dir}/monochrome.png"
    mono = Image.open(mono_path).convert("RGBA") if os.path.exists(mono_path) else None
    return fg, bg, mono

def core_bbox(alpha, thresh=25):
    solid = alpha.point(lambda p: 255 if p > thresh else 0)
    return solid.getbbox()

def core_image(src, canvas=1024, fill=1.0, anchor=None, hshift=0, vshift=0):
    # fill<1 = adaptive safe-zone mount: launcher mask shows the central 72/108dp
    # of the canvas, so art larger than fill*canvas reads oversized/clipped on screen
    a = src.getchannel("A")
    bb = core_bbox(a)
    if not bb:
        raise ValueError("empty alpha")
    core = src.crop(bb)
    out = Image.new("RGBA", (canvas, canvas), (0,0,0,0))
    limit = canvas * fill
    if core.width > limit or core.height > limit:
        side = max(core.size)
        core = core.resize((int(core.width*limit/side), int(core.height*limit/side)), Image.LANCZOS)
    left = (canvas - core.width) // 2 + hshift
    top = (canvas - core.height) // 2 + vshift
    if anchor == "top_right":
        zone = canvas * (1 - VISIBLE_ZONE_INSET * 2)
        left = int(canvas * VISIBLE_ZONE_INSET + zone - core.width) + hshift
        top = int(canvas * VISIBLE_ZONE_INSET) + vshift
    out.alpha_composite(core, (left, top))
    return out

def cover(src, size):
    w, h = src.size
    s = max(size/w, size/h)
    src = src.resize((int(w*s), int(h*s)), Image.LANCZOS)
    x = (src.width - size)//2
    return src.crop((x, x, x+size, x+size)) if src.width >= src.height else src

def circle_mask(size, scale=1.0):
    m = Image.new("L", (size*4, size*4), 0)
    d = ImageDraw.Draw(m)
    side = int(size*4*scale)
    off = (size*4 - side)//2
    d.ellipse((off, off, off+side-1, off+side-1), fill=255)
    return m.resize((size,size), Image.LANCZOS)

def put(layer, folder, name, fmt="webp", **kw):
    d = os.path.join(OUT, folder)
    os.makedirs(d, exist_ok=True)
    layer.save(os.path.join(d, f"{name}.{fmt}"), fmt.upper(), lossless=True, **kw)

def emit(src_fullres, res_name, prefix_dir="drawable"):
    # scale master to density px and save
    for dpi, mult in DENSITIES:
        px = int(BASE * mult)
        im = src_fullres.resize((px, px), Image.LANCZOS)
        put(im, f"{prefix_dir}-{dpi}", res_name)

def emit_notification(src_fullres, res_name):
    for dpi, mult in DENSITIES:
        px = int(24 * mult)
        im = src_fullres.resize((px, px), Image.LANCZOS)
        put(im, f"drawable-{dpi}", res_name)

def white_by_alpha(alpha_src):
    a = alpha_src.getchannel("A")
    out = Image.new("RGBA", alpha_src.size, (0,0,0,0))
    white = Image.new("RGBA", alpha_src.size, (255,255,255,255))
    out.paste(white, (0,0), a)
    return out

# circle-mask safe: glyph bbox half-diagonal = fill*sqrt(2)/2 must stay under
# the launcher-visible radius 0.667/2 (54% clipped wing/flame corners on round
# launchers); VISIBLE_ZONE_INSET 0.17 below is the conservative rounding of 72/108
ADAPTIVE_SAFE_ZONE_FILL = 0.45

# one plane template across the family: every theme gets the same
# optical nudge off the bbox-center — flame length varies per theme,
# the plane stays on the same spot
ADAPTIVE_OPTICAL_SHIFT_H = -6
ADAPTIVE_OPTICAL_SHIFT_V = 5

# launchers draw themed icons with their own stroke that fattens the silhouette,
# so the monochrome core rides smaller to compensate
MONO_FILL_RATIO = 0.89

# user-directed per-theme core overrides: fill = core size (canvas fraction),
# anchor = core corner pinned to the same corner of the launcher-visible zone
MOUNT_OVERRIDES = {}

VISIBLE_ZONE_INSET = 0.17  # launcher mask shows the central 66% of the canvas

def build_theme(folder, slug):
    tdir = f"{HERE}/sources/{folder}"
    fg, bg, mono = load(tdir, slug)
    mount = MOUNT_OVERRIDES.get(slug, {})
    h = mount.get("h", ADAPTIVE_OPTICAL_SHIFT_H)
    v = mount.get("v", ADAPTIVE_OPTICAL_SHIFT_V)
    emit(core_image(fg, fill=mount.get("fill", ADAPTIVE_SAFE_ZONE_FILL), anchor=mount.get("anchor"), hshift=h, vshift=v), f"ic_{slug}_foreground")
    emit(cover(bg, 1024).convert("RGBA"), f"ic_{slug}_background")
    mono_fill = mount.get("fill", ADAPTIVE_SAFE_ZONE_FILL) * MONO_FILL_RATIO
    emit(core_image(white_by_alpha(mono), fill=mono_fill, anchor=mount.get("anchor"), hshift=h, vshift=v), f"ic_{slug}_monochrome")
    emit_notification(core_image(white_by_alpha(mono)), f"ic_notification_{slug}")
    sys.stdout.write(f"[{slug}] ok\n")

if __name__ == "__main__":
    for slug in THEMES:
        build_theme(slug, slug)
    sys.stdout.write("done\n")
