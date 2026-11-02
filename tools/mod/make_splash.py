"""Erzeugt das Mod-Startbild: Crealitys splash_logo.png + Eckband "MCP MOD" + Plakette."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, DST = sys.argv[1], sys.argv[2]
S = 3  # in dreifacher Groesse zeichnen, dann verkleinern (saubere Kanten)
FONT = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
GRAPHITE = (38, 42, 48, 255)
ORANGE = (255, 122, 26, 255)
WHITE = (255, 255, 255, 255)
GREY = (90, 96, 104, 255)

base = Image.open(SRC).convert("RGBA")
W, H = base.size
layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
f = lambda style, size: ImageFont.truetype(FONT.format(style), size * S)

# 1) Eckband oben rechts: Streifen unter 45 Grad
band = Image.new("RGBA", (360 * S, 46 * S), (0, 0, 0, 0))
bd = ImageDraw.Draw(band)
bd.rectangle([0, 0, 360 * S, 46 * S], fill=GRAPHITE)
bd.rectangle([0, 0, 360 * S, 3 * S], fill=ORANGE)
bd.rectangle([0, 43 * S, 360 * S, 46 * S], fill=ORANGE)
txt = "MCP MOD"
ft = f("Bold", 20)
tw = bd.textlength(txt, font=ft)
bd.text(((360 * S - tw) / 2, 9 * S), txt, font=ft, fill=WHITE)
band = band.rotate(-45, expand=True, resample=Image.BICUBIC)
shadow = Image.new("RGBA", band.size, (0, 0, 0, 0))
shadow.paste((0, 0, 0, 90), mask=band.split()[3])
shadow = shadow.filter(ImageFilter.GaussianBlur(6 * S))
cx, cy = (W - 62) * S, 62 * S  # Bandmitte nahe der Ecke
for img, off in ((shadow, 4 * S), (band, 0)):
    layer.alpha_composite(img, (int(cx - img.width / 2) + off, int(cy - img.height / 2) + off))

# 2) Plakette in der linken Leiste (unter Logo und Trennstrich, ueber dem Ladetext)
px, py, pw, ph = 32, 372, 196, 44
d.rounded_rectangle([px * S, py * S, (px + pw) * S, (py + ph) * S], radius=8 * S,
                    fill=(255, 255, 255, 235), outline=(220, 224, 228, 255), width=S)
d.rounded_rectangle([px * S, py * S, (px + 5) * S, (py + ph) * S], radius=3 * S, fill=ORANGE)
# Verbindungs-Symbol (zwei Knoten mit Linie) fuer "Model Context Protocol"
ix, iy = px + 22, py + ph // 2
d.line([(ix - 8) * S, iy * S, (ix + 8) * S, iy * S], fill=GRAPHITE, width=2 * S)
for x in (ix - 8, ix + 8):
    d.ellipse([(x - 4) * S, (iy - 4) * S, (x + 4) * S, (iy + 4) * S], fill=WHITE, outline=GRAPHITE, width=2 * S)
d.ellipse([(ix - 2) * S, (iy - 2) * S, (ix + 2) * S, (iy + 2) * S], fill=ORANGE)
d.text(((px + 40) * S, (py + 7) * S), "Inoffizielle MCP-Mod", font=f("SemiBold", 12), fill=GRAPHITE)
d.text(((px + 40) * S, (py + 24) * S), "by R0g3rT · nicht von Creality", font=f("Regular", 10), fill=GREY)

out = base.copy()
out.alpha_composite(layer.resize((W, H), Image.LANCZOS))
out.save(DST, optimize=True)
print("ok", out.size)
