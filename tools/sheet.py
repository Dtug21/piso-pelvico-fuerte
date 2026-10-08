"""Hoja de revisión: junta todos los PNG de una carpeta en una grilla con su nombre."""
import sys, glob, os
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
files = sorted(glob.glob(os.path.join(src, '*.png')))
files = [f for f in files if not f.endswith(out)]
cols, tw, th = 5, 300, 200
rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (cols * tw, rows * (th + 16)), (242, 243, 245))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGBA')
    im.thumbnail((tw, th))
    x, y = (i % cols) * tw, (i // cols) * (th + 16)
    sheet.paste(im, (x, y + 16), im)
    d.text((x + 4, y + 2), os.path.basename(f)[:-4], fill=(40, 40, 40))
sheet.save(out)
print(out, len(files))
