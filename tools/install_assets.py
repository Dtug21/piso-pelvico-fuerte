"""Instala en MPFB los paquetes de recursos CC0 descargados (zip) y lista lo disponible.
Uso: blender -b --python tools/install_assets.py -- <carpeta_con_zips>"""
import sys, os, glob, zipfile
from bl_ext.blender_org.mpfb.services.locationservice import LocationService
from bl_ext.blender_org.mpfb.services.assetservice import AssetService
src = sys.argv[sys.argv.index('--') + 1]
data_dir = LocationService.get_user_data()
print('DATA', data_dir)
for z in sorted(glob.glob(os.path.join(src, '*.zip'))):
    with zipfile.ZipFile(z) as zf:
        zf.extractall(data_dir)
    print('INSTALLED', os.path.basename(z))
AssetService.update_all_asset_lists()
for kind in ('clothes', 'hair', 'shoes', 'skins', 'eyes', 'eyebrows', 'eyelashes', 'proxymeshes'):
    d = os.path.join(data_dir, kind)
    if os.path.isdir(d):
        names = sorted(os.listdir(d))
        print('LIST', kind, len(names), names[:60])
