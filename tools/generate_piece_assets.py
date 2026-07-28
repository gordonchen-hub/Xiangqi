from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "game" / "images" / "pieces"
FONT = ROOT / "game" / "fonts" / "辰宇落雁體.ttf"
if not FONT.exists():
    FONT = ROOT / "game" / "SourceHanSansLite.ttf"

SIZE = 104
SCALE = 4
CANVAS = SIZE * SCALE

PIECES = {
    "red_king": ("帥", (244, 54, 64), (255, 225, 194), (72, 9, 14)),
    "red_advisor": ("仕", (244, 54, 64), (255, 225, 194), (72, 9, 14)),
    "red_elephant": ("相", (244, 54, 64), (255, 225, 194), (72, 9, 14)),
    "red_horse": ("馬", (244, 54, 64), (255, 225, 194), (72, 9, 14)),
    "red_rook": ("車", (244, 54, 64), (255, 225, 194), (72, 9, 14)),
    "red_cannon": ("炮", (244, 54, 64), (255, 225, 194), (72, 9, 14)),
    "red_pawn": ("兵", (244, 54, 64), (255, 225, 194), (72, 9, 14)),
    "black_king": ("將", (65, 170, 255), (218, 237, 255), (7, 26, 51)),
    "black_advisor": ("士", (65, 170, 255), (218, 237, 255), (7, 26, 51)),
    "black_elephant": ("象", (65, 170, 255), (218, 237, 255), (7, 26, 51)),
    "black_horse": ("馬", (65, 170, 255), (218, 237, 255), (7, 26, 51)),
    "black_rook": ("車", (65, 170, 255), (218, 237, 255), (7, 26, 51)),
    "black_cannon": ("砲", (65, 170, 255), (218, 237, 255), (7, 26, 51)),
    "black_pawn": ("卒", (65, 170, 255), (218, 237, 255), (7, 26, 51)),
}


def circle_mask(radius_pad=0):
    mask = Image.new("L", (CANVAS, CANVAS), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (radius_pad, radius_pad, CANVAS - radius_pad, CANVAS - radius_pad),
        fill=255,
    )
    return mask


def radial_fill(center, edge):
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    pix = img.load()
    cx = cy = CANVAS / 2
    max_d = CANVAS / 2
    for y in range(CANVAS):
        for x in range(CANVAS):
            d = min(1.0, (((x - cx) ** 2 + (y - cy) ** 2) ** 0.5) / max_d)
            t = d * d
            r = int(center[0] * (1 - t) + edge[0] * t)
            g = int(center[1] * (1 - t) + edge[1] * t)
            b = int(center[2] * (1 - t) + edge[2] * t)
            pix[x, y] = (r, g, b, 255)
    return img


def make_piece(name, char, accent, center, edge):
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))

    glow = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((28, 28, CANVAS - 28, CANVAS - 28), fill=accent + (150,))
    glow = glow.filter(ImageFilter.GaussianBlur(26))
    img.alpha_composite(glow)

    shadow = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse((43, 49, CANVAS - 35, CANVAS - 27), fill=(0, 0, 0, 115))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(shadow)

    base = radial_fill(center, edge)
    base.putalpha(circle_mask(22))
    img.alpha_composite(base)

    draw = ImageDraw.Draw(img)
    for width, alpha in ((18, 110), (10, 210), (4, 255)):
        draw.ellipse(
            (33, 33, CANVAS - 33, CANVAS - 33),
            outline=accent + (alpha,),
            width=width,
        )
    draw.ellipse(
        (70, 70, CANVAS - 70, CANVAS - 70),
        outline=(255, 255, 255, 70),
        width=4,
    )
    draw.arc(
        (58, 46, CANVAS - 58, CANVAS - 58),
        205,
        310,
        fill=(255, 255, 255, 95),
        width=8,
    )

    fallback_font = ROOT / "game" / "SourceHanSansLite.ttf"
    try:
        font = ImageFont.truetype(str(FONT), 54 * SCALE, layout_engine=ImageFont.Layout.BASIC)
        bbox = draw.textbbox((0, 0), char, font=font, stroke_width=2 * SCALE)
    except Exception:
        font = ImageFont.truetype(str(fallback_font), 54 * SCALE)
        bbox = draw.textbbox((0, 0), char, font=font, stroke_width=2 * SCALE)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (CANVAS - tw) / 2 - bbox[0]
    ty = (CANVAS - th) / 2 - bbox[1] - 8

    draw.text(
        (tx + 4, ty + 7),
        char,
        font=font,
        fill=(0, 0, 0, 120),
        stroke_width=3 * SCALE,
        stroke_fill=(0, 0, 0, 90),
    )
    draw.text(
        (tx, ty),
        char,
        font=font,
        fill=accent + (255,),
        stroke_width=2 * SCALE,
        stroke_fill=(255, 255, 255, 230),
    )

    img = img.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    img.save(OUT / f"{name}.png")


def make_ring(name, color, width=7, blur=7):
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    glow = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((36, 36, CANVAS - 36, CANVAS - 36), outline=color + (180,), width=width * SCALE)
    glow = glow.filter(ImageFilter.GaussianBlur(blur * SCALE))
    img.alpha_composite(glow)

    draw = ImageDraw.Draw(img)
    draw.ellipse((44, 44, CANVAS - 44, CANVAS - 44), outline=color + (255,), width=max(2, width // 2) * SCALE)
    img = img.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    img.save(OUT / f"{name}.png")


def make_empty_marker():
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = CANVAS // 2
    color = (160, 210, 255, 80)
    draw.line((c - 18, c, c + 18, c), fill=color, width=3 * SCALE)
    draw.line((c, c - 18, c, c + 18), fill=color, width=3 * SCALE)
    img = img.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    img.save(OUT / "empty_marker.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, args in PIECES.items():
        make_piece(name, *args)

    make_ring("ring_select", (84, 255, 175), width=9, blur=8)
    make_ring("ring_last", (255, 224, 88), width=7, blur=7)
    make_ring("ring_check", (255, 45, 82), width=10, blur=11)
    make_ring("ring_capture", (255, 120, 45), width=11, blur=12)
    make_ring("ring_hover", (255, 255, 255), width=5, blur=5)
    make_empty_marker()
    print(f"Generated {len(PIECES) + 6} assets in {OUT}")


if __name__ == "__main__":
    main()
