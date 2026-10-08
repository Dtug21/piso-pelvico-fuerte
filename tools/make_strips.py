"""Une los cuadros renderizados en una tira WebP por ejercicio y sexo, y junta el JSON de pelvis.
Uso: python tools/make_strips.py <carpeta_renders> <carpeta_salida>"""
import sys, os, json, glob
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
FW, FH = 480, 320
meta = {}
total = 0
for sex in ('h', 'm'):
    m = json.load(open(os.path.join(src, f'meta_{sex}.json')))
    for pid, info in m.items():
        n = info['n']
        strip = Image.new('RGBA', (FW * n, FH), (0, 0, 0, 0))
        for i in range(n):
            im = Image.open(os.path.join(src, f'{pid}_{sex}_{i}.png')).convert('RGBA').resize((FW, FH), Image.LANCZOS)
            strip.paste(im, (FW * i, 0))
        f = os.path.join(out, f'{pid}_{sex}.webp')
        strip.save(f, 'WEBP', quality=80, method=6)
        total += os.path.getsize(f)
        meta.setdefault(pid, {})[sex] = {'n': n, 'p': info['pelvis']}
json.dump(meta, open(os.path.join(out, 'figs.json'), 'w'), separators=(',', ':'))
print('ok', len(meta), 'ejercicios', round(total / 1024), 'KB')
