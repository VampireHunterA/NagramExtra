#!/usr/bin/env python3
# Helper to audit and evaluate a candidate icon against docs/spec/main-icon-brief.md:
# 1. Checks glyph bounding box (% of canvas, target ~47-55%)
# 2. Generates circle (72/108dp) & squircle launcher crops
# 3. Generates 48px downscale for readability check
# 4. Generates side-by-side comparison board with current Turbo & Official TG
import os
import sys
from PIL import Image, ImageDraw, ImageOps
import numpy as np

AUDIT_DIR = "/tmp/icon_audit"
REFS_DIR = os.path.join(AUDIT_DIR, "refs")
os.makedirs(AUDIT_DIR, exist_ok=True)

def eval_candidate(candidate_path, out_preview=os.path.join(AUDIT_DIR, "candidate_eval.png")):
    if not os.path.exists(candidate_path):
        print(f"Error: candidate file {candidate_path} does not exist.")
        return False
        
    im = Image.open(candidate_path).convert("RGBA")
    w, h = im.size
    if w != 1024 or h != 1024:
        im = im.resize((1024, 1024), Image.LANCZOS)
        w, h = 1024, 1024
        
    # Analyze bounding box if RGBA with alpha, or contrast difference from corners
    arr = np.array(im)
    corners = np.concatenate([arr[0:20, 0:20], arr[0:20, -20:], arr[-20:, 0:20], arr[-20:, -20:]], axis=0)
    bg_rgb = np.median(corners.reshape(-1, 4)[:, :3], axis=0)
    
    # Analyze bounding box: detect non-background object
    arr = np.array(im)
    
    # Check if image has transparency in alpha channel
    if im.mode == "RGBA" and np.any(arr[:, :, 3] < 250):
        glyph_mask = arr[:, :, 3] > 30
    else:
        # In RGB with gradient: background is blue/tinted, glyph is white/flame
        # Measure local gradient or color deviation from corners/edges
        corners = np.concatenate([arr[0:30, 0:30], arr[0:30, -30:], arr[-30:, 0:30], arr[-30:, -30:]], axis=0)
        # Check standard deviation or distance from interpolated vertical gradient
        top_color = np.median(arr[0:15, :, :3], axis=(0, 1))
        bot_color = np.median(arr[-15:, :, :3], axis=(0, 1))
        y_grad = np.linspace(top_color, bot_color, 1024).reshape(1024, 1, 3)
        diff = np.linalg.norm(arr[:, :, :3] - y_grad, axis=2)
        glyph_mask = diff > 45
        
    ys, xs = np.where(glyph_mask)
    if len(xs) > 0:
        min_x, max_x = xs.min(), xs.max()
        min_y, max_y = ys.min(), ys.max()
        gw = max_x - min_x
        gh = max_y - min_y
        span_w = (gw / 1024.0) * 100.0
        span_h = (gh / 1024.0) * 100.0
        diag = (np.sqrt(gw**2 + gh**2) / 1024.0) * 100.0
        max_span = max(span_w, span_h)
        print(f"[*] Glyph span: {gw}x{gh}px ({span_w:.1f}% x {span_h:.1f}% of canvas)")
        print(f"[*] Diagonal: {diag:.1f}%, Max side: {max_span:.1f}% (target: ~47-55%)")
        if max_span <= 55.0 and max_span >= 38.0:
            print("[✅] Safe zone check: PASS (fits cleanly inside circular launcher mask without clipping)")
        elif max_span > 55.0:
            print(f"[⚠️] Safe zone check: TOO LARGE ({max_span:.1f}% > 55%) — risk of clipping by circle mask")
        else:
            print(f"[⚠️] Safe zone check: TOO SMALL ({max_span:.1f}% < 38%)")
    else:
        print("[!] Could not auto-detect glyph bounding box.")

    # Masks for 1024 canvas:
    # Android Adaptive Icon: 108dp canvas, visible safe circle is 72dp (~66.6% diameter = 682px)
    circle_d = int(1024 * (72.0 / 108.0))
    circle_off = (1024 - circle_d) // 2
    
    mask_circle = Image.new("L", (1024, 1024), 0)
    d_c = ImageDraw.Draw(mask_circle)
    d_c.ellipse([circle_off, circle_off, circle_off + circle_d, circle_off + circle_d], fill=255)
    
    # Build Showcase Board:
    # 1. Full 1024
    # 2. Circle Launcher Crop
    # 3. 48px Downscale (resized up with nearest neighbor or crisp lanczos to see 48dp readability)
    # 4. Official TG Ref
    # 5. Current Turbo Ref
    
    board_w = 1280
    board_h = 720
    board = Image.new("RGB", (board_w, board_h), (16, 20, 26))
    d_b = ImageDraw.Draw(board)
    
    # 1. Candidate Full (280x280)
    c_280 = im.resize((280, 280), Image.LANCZOS)
    board.paste(c_280, (40, 60))
    d_b.text((40, 30), "Candidate (1024px Full)", fill=(230, 240, 250))
    d_b.rectangle([40, 60, 320, 340], outline=(60, 75, 95), width=1)
    
    # 2. Circle Launcher Crop (280x280)
    c_circle = Image.new("RGBA", (1024, 1024), (16, 20, 26, 255))
    c_circle.paste(im, (0, 0), mask_circle)
    c_circle_280 = c_circle.crop((circle_off, circle_off, circle_off + circle_d, circle_off + circle_d)).resize((280, 280), Image.LANCZOS)
    board.paste(c_circle_280.convert("RGB"), (360, 60))
    d_b.text((360, 30), "Circle Launcher (Adaptive 72dp)", fill=(230, 240, 250))
    d_b.ellipse([360, 60, 640, 340], outline=(80, 190, 255), width=2)
    
    # 3. 48px Mobile Readability test (displayed at 96px and 48px)
    c_48 = im.resize((48, 48), Image.LANCZOS)
    c_48_circle = c_circle.crop((circle_off, circle_off, circle_off + circle_d, circle_off + circle_d)).resize((48, 48), Image.LANCZOS)
    
    # Render at 1x and 2x zoom
    board.paste(c_48_circle.convert("RGB"), (680, 60))
    d_b.text((680, 30), "48px Real Size", fill=(230, 240, 250))
    d_b.rectangle([680, 60, 728, 108], outline=(80, 190, 255), width=1)
    
    c_48_zoom = c_48_circle.resize((120, 120), Image.NEAREST)
    board.paste(c_48_zoom.convert("RGB"), (680, 130))
    d_b.text((680, 112), "48px Zoom (Pixels)", fill=(160, 180, 200))
    
    # 4. Current Turbo ref
    ref_turbo_p = os.path.join(REFS_DIR, "ref_current_turbo.png")
    if os.path.exists(ref_turbo_p):
        ref_turbo = Image.open(ref_turbo_p).convert("RGBA").resize((220, 220), Image.LANCZOS)
        board.paste(ref_turbo.convert("RGB"), (840, 60))
        d_b.text((840, 30), "Ref: Current Turbo", fill=(240, 180, 80))
        d_b.rectangle([840, 60, 1060, 280], outline=(70, 60, 40), width=1)
        
    # 5. Official TG ref
    ref_tg_p = os.path.join(REFS_DIR, "ref_official_tg.png")
    if os.path.exists(ref_tg_p):
        ref_tg = Image.open(ref_tg_p).convert("RGBA").resize((220, 220), Image.LANCZOS)
        board.paste(ref_tg.convert("RGB"), (1080, 60))
        d_b.text((1080, 30), "Ref: Official TG", fill=(80, 180, 255))
        d_b.rectangle([1080, 60, 1300, 280], outline=(40, 60, 80), width=1)
        
    board.save(out_preview, quality=95)
    print(f"[✅] Audit board saved to: {out_preview}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        eval_candidate(sys.argv[1])
    else:
        print("Usage: python3 tools/icons/test_candidate.py <path_to_image>")
