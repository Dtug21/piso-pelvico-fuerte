"""Genera las figuras de los ejercicios con Blender + MPFB (persona 3D libre, CC0).

Uso:  blender -b --python tools/render_figs.py -- <carpeta_salida> <sexo h|m> [ids...]
Cada ejercicio se renderiza en N cuadros (inicio -> final) con la misma cámara,
y se guarda como tira WebP (un cuadro al lado del otro) + un JSON con la posición
de la pelvis en cada cuadro (para el brillo del piso pélvico en la app).
"""
import bpy, sys, os, math, json
from mathutils import Vector, Euler, Matrix
from bl_ext.blender_org.mpfb.services.humanservice import HumanService
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index('--') + 1:]
OUT, SEX = argv[0], argv[1]
ONLY = set(argv[2:])
FRAMES = 7
W, H = 600, 400
ASSETS = os.environ.get('MPFB_ASSETS', '')

D = math.radians
AD = {'upperarm01.L': (-15, 0, -40), 'upperarm01.R': (-15, 0, 40), 'lowerarm01.L': (-40, 0, 0), 'lowerarm01.R': (-40, 0, 0)}          # brazos a los lados
KB = {'upperleg01.L': (-55, 0, 0), 'upperleg01.R': (-55, 0, 0), 'lowerleg01.L': (105, 0, 0), 'lowerleg01.R': (105, 0, 0)}  # rodillas dobladas


def M(*ds):
    r = {}
    for d in ds:
        r.update(d)
    return r


def both(bone, x=0, y=0, z=0, zr=None):
    """Misma rotación en ambos lados (la abducción Z va con signo opuesto)."""
    return {bone + '.L': (x, y, z), bone + '.R': (x, y, -z if zr is None else zr)}


STR = {'lowerarm01.L': (0, 0, 0), 'lowerarm01.R': (0, 0, 0)}       # codos rectos
TABLE = M(both('upperleg01', -90), both('lowerleg01', 90))           # piernas en mesa (90/90)
QUAD = M(both('upperleg01', -90), both('lowerleg01', 90), both('upperarm01', 80, 0, -6), STR)  # cuatro apoyos
SIT = M(both('upperleg01', -90), both('lowerleg01', 90), both('upperarm01', 0, 0, -40), both('lowerarm01', 78))
SUP, PRO, SIDE = (-90, 0, 0), (90, 0, 0), (-90, 90, 0)
STAND = (0, 0, 0)

# orient: rotación del cuerpo entero (grados XYZ). tilt: inclinación extra en X del mundo.
# bones: rotaciones locales. props: accesorios. Los ejercicios sin 'b' son posiciones quietas.
POSES = {
    'acostado': {'a': {'orient': SUP, 'bones': M(AD, KB)}, 'props': ['mat']},
    'delado': {'a': {'orient': SIDE, 'bones': M(AD, both('upperleg01', -60), both('lowerleg01', 80))}, 'props': ['mat']},
    'sentado': {'a': {'orient': STAND, 'bones': SIT}, 'props': ['chair']},
    'depie': {'a': {'orient': STAND, 'bones': M(AD)}},
    'esfuerzo': {'a': {'orient': STAND, 'bones': SIT}, 'b': {'orient': STAND, 'bones': M(AD)}, 'props': ['chair']},
    'talon': {'a': {'orient': SUP, 'bones': M(AD, KB)}, 'b': {'orient': SUP, 'bones': M(AD, KB, {'upperleg01.L': (-4, 0, 0), 'lowerleg01.L': (4, 0, 0)})}, 'props': ['mat']},
    'apertura': {'a': {'orient': SUP, 'bones': M(AD, KB)}, 'b': {'orient': SUP, 'bones': M(AD, KB, {'upperleg01.L': (-55, 0, -42)})}, 'props': ['mat']},
    'puente': {'a': {'orient': SUP, 'bones': M(AD, KB)},
               'b': {'orient': (-116, 0, 0), 'bones': M(AD, both('upperleg01', -2), both('lowerleg01', 112))}, 'props': ['mat']},
    'puente1': {'a': {'orient': SUP, 'bones': M(AD, KB)},
                'b': {'orient': (-116, 0, 0), 'bones': M(AD, {'upperleg01.R': (-2, 0, 0), 'lowerleg01.R': (112, 0, 0), 'upperleg01.L': (-30, 0, 0), 'lowerleg01.L': (4, 0, 0)})}, 'props': ['mat']},
    'deadbug': {'a': {'orient': SUP, 'bones': M(TABLE, both('upperarm01', 92, 0, -8), STR)},
                'b': {'orient': SUP, 'bones': M(TABLE, both('upperarm01', 92, 0, -8), STR, {'upperleg01.L': (-12, 0, 0), 'lowerleg01.L': (4, 0, 0), 'upperarm01.R': (172, 0, 8)})}, 'props': ['mat']},
    'toques': {'a': {'orient': SUP, 'bones': M(AD, TABLE)}, 'b': {'orient': SUP, 'bones': M(AD, TABLE, {'upperleg01.L': (-42, 0, 0), 'lowerleg01.L': (92, 0, 0)})}, 'props': ['mat']},
    'birddog': {'a': {'orient': PRO, 'bones': QUAD},
                'b': {'orient': PRO, 'bones': M(QUAD, {'upperleg01.L': (2, 0, 0), 'lowerleg01.L': (2, 0, 0), 'upperarm01.R': (172, 0, 6)})}, 'props': ['mat']},
    'plancha': {'a': {'orient': (82, 0, 0), 'bones': M(both('upperarm01', 34, 0, -6), both('lowerarm01', 96))}, 'props': ['mat']},
    'plancharod': {'a': {'orient': (74, 0, 0), 'bones': M(both('upperarm01', 28, 0, -6), both('lowerarm01', 96), both('lowerleg01', 100))}, 'props': ['mat']},
    'lateral': {'a': {'orient': SIDE, 'bones': {'upperarm01.L': (0, 0, 42), 'lowerarm01.L': (95, 0, 0), 'upperarm01.R': (-15, 0, 40), 'lowerarm01.R': (-40, 0, 0)}},
                'b': {'orient': SIDE, 'tilt': 20, 'bones': {'upperarm01.L': (0, 0, 62), 'lowerarm01.L': (95, 0, 0), 'upperarm01.R': (-15, 0, 40), 'lowerarm01.R': (-40, 0, 0)}}, 'props': ['mat']},
    'hollow': {'a': {'orient': SUP, 'bones': M(both('upperarm01', 168, 0, -4), STR)},
               'b': {'orient': SUP, 'bones': M(both('upperarm01', 150, 0, -4), STR, {'spine03': (12, 0, 0), 'spine02': (12, 0, 0), 'neck01': (18, 0, 0)}, both('upperleg01', -28))}, 'props': ['mat']},
    'piernas': {'a': {'orient': SUP, 'bones': M(AD, both('upperleg01', -88))}, 'b': {'orient': SUP, 'bones': M(AD, both('upperleg01', -22))}, 'props': ['mat']},
    'situp': {'a': {'orient': SUP, 'bones': M(KB, both('upperarm01', 150, 0, -25), both('lowerarm01', 130))},
              'b': {'orient': SUP, 'bones': M(KB, both('upperarm01', 150, 0, -25), both('lowerarm01', 130), {'spine04': (18, 0, 0), 'spine03': (18, 0, 0), 'spine02': (14, 0, 0), 'neck01': (20, 0, 0)})}, 'props': ['mat']},
    'sentadilla': {'a': {'orient': STAND, 'bones': M(both('upperarm01', 40, 0, -20), both('lowerarm01', 115))},
                   'b': {'orient': STAND, 'bones': M(both('upperarm01', 55, 0, -20), both('lowerarm01', 115), {'spine03': (25, 0, 0)}, both('upperleg01', -95), both('lowerleg01', 105), both('foot', -15))}, 'props': ['dumbbell']},
    'rumano': {'a': {'orient': STAND, 'bones': M(both('upperarm01', 0, 0, -40), STR)},
               'b': {'orient': (68, 0, 0), 'bones': M(both('upperarm01', 68, 0, -40), STR, both('upperleg01', -68), both('lowerleg01', 14))}, 'props': ['barbell']},
    'caminar': {'a': {'orient': STAND, 'bones': {'upperleg01.L': (-24, 0, 0), 'lowerleg01.L': (8, 0, 0), 'upperleg01.R': (16, 0, 0), 'lowerleg01.R': (22, 0, 0),
                                                 'upperarm01.L': (-22, 0, -40), 'upperarm01.R': (24, 0, 40), 'lowerarm01.L': (-10, 0, 0), 'lowerarm01.R': (30, 0, 0)}},
                'b': {'orient': STAND, 'bones': {'upperleg01.R': (-24, 0, 0), 'lowerleg01.R': (8, 0, 0), 'upperleg01.L': (16, 0, 0), 'lowerleg01.L': (22, 0, 0),
                                                 'upperarm01.R': (-22, 0, 40), 'upperarm01.L': (24, 0, -40), 'lowerarm01.R': (-10, 0, 0), 'lowerarm01.L': (30, 0, 0)}}},
    'tabla': {'a': {'orient': STAND, 'tilt': -4, 'bones': M(both('upperarm01', 0, 0, 38), STR, both('upperleg01', -20), both('lowerleg01', 30))},
              'b': {'orient': STAND, 'tilt': 4, 'bones': M(both('upperarm01', 0, 0, 38), STR, both('upperleg01', -20), both('lowerleg01', 30))}, 'props': ['board']},
    'unpie': {'a': {'orient': STAND, 'bones': M(AD)}, 'b': {'orient': STAND, 'bones': M(both('upperarm01', 0, 0, 20), STR, {'upperleg01.L': (-85, 0, 0), 'lowerleg01.L': (95, 0, 0)})}},
}

COL = {'eyes': (0.15, 0.12, 0.1, 1), 'skin': (0.86, 0.69, 0.58, 1), 'shirt': (0.05, 0.61, 0.56, 1), 'pants': (0.13, 0.17, 0.20, 1), 'shoes': (0.92, 0.92, 0.92, 1), 'hair': (0.16, 0.11, 0.08, 1)}


DATA = os.path.join(os.environ['APPDATA'], 'Blender Foundation', 'Blender', '5.2', 'extensions', '.user', 'blender_org', 'mpfb', 'data')
OUTFIT = {
    'h': [('clothes', 'elvs_crude_t-shirt_male', 'shirt'), ('clothes', 'cortu_jeans_shorts', 'pants'), ('clothes', 'shoes01', 'shoes'),
          ('hair', 'short02', 'hair'), ('eyebrows', 'eyebrow001', 'hair'), ('eyes', 'low-poly', 'eyes')],
    'm': [('clothes', 'female_sportsuit01', 'shirt'), ('clothes', 'shoes01', 'shoes'),
          ('hair', 'ponytail01', 'hair'), ('eyebrows', 'eyebrow002', 'hair'), ('eyes', 'low-poly', 'eyes')],
}
TYPES = {'clothes': 'Clothes', 'hair': 'Hair', 'eyebrows': 'Eyebrows', 'eyes': 'Eyes'}


def find_mhclo(kind, name):
    d = os.path.join(DATA, kind, name)
    for f in os.listdir(d):
        if f.endswith('.mhclo'):
            return os.path.join(d, f)
    raise FileNotFoundError(d)


def build_human():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    macro = {"gender": 1.0 if SEX == 'h' else 0.0, "age": 0.5, "muscle": 0.6, "weight": 0.45, "height": 0.5,
             "proportions": 0.5, "cupsize": 0.5, "firmness": 0.5, "race": {"african": 0.2, "asian": 0.2, "caucasian": 0.6}}
    human = HumanService.create_human(macro_detail_dict=macro)
    rig = HumanService.add_builtin_rig(human, "default")
    human.color = COL['skin']
    for kind, name, col in OUTFIT[SEX]:
        before = set(bpy.data.objects)
        try:
            HumanService.add_mhclo_asset(find_mhclo(kind, name), human, asset_type=TYPES[kind], subdiv_levels=0)
        except Exception as e:
            print('ASSET FAIL', kind, name, e)
            continue
        for o in set(bpy.data.objects) - before:
            o.color = COL.get(col, (0.1, 0.1, 0.1, 1))
    return human, rig


def set_pose(rig, pose):
    for pb in rig.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)
    for b, (x, y, z) in pose['bones'].items():
        if b in rig.pose.bones:
            rig.pose.bones[b].rotation_euler = (D(x), D(y), D(z))
    rot = Euler([D(v) for v in pose['orient']]).to_matrix().to_4x4()
    if pose.get('tilt'):
        rot = Matrix.Rotation(D(pose['tilt']), 4, 'X') @ rot
    rig.matrix_world = rot


def lerp_pose(a, b, t):
    keys = set(a['bones']) | set(b['bones'])
    bones = {k: tuple(a['bones'].get(k, (0, 0, 0))[i] + (b['bones'].get(k, (0, 0, 0))[i] - a['bones'].get(k, (0, 0, 0))[i]) * t for i in range(3)) for k in keys}
    orient = tuple(a['orient'][i] + (b['orient'][i] - a['orient'][i]) * t for i in range(3))
    tilt = a.get('tilt', 0) + (b.get('tilt', 0) - a.get('tilt', 0)) * t
    return {'bones': bones, 'orient': orient, 'tilt': tilt}


def mesh_points(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ev.matrix_world
        vs = me.vertices
        pts += [mw @ vs[i].co for i in range(0, len(vs), 7)]
        ev.to_mesh_clear()
    return pts


def snap_to_floor(rig, objs):
    bpy.context.view_layer.update()
    z = min(p.z for p in mesh_points(objs))
    rig.location.z -= z
    bpy.context.view_layer.update()


def setup_scene():
    scn = bpy.context.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    scn.collection.objects.link(cam)
    cam.rotation_euler = (D(90), 0, D(90))
    cam.data.type = 'ORTHO'
    scn.camera = cam
    scn.render.engine = 'BLENDER_WORKBENCH'
    sh = scn.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'OBJECT'
    sh.show_cavity = True
    sh.cavity_type = 'BOTH'
    sh.show_object_outline = True
    sh.object_outline_color = (0.08, 0.1, 0.11)
    sh.show_shadows = False
    scn.render.resolution_x, scn.render.resolution_y = W, H
    scn.render.film_transparent = True
    scn.render.image_settings.file_format = 'PNG'
    scn.render.image_settings.color_mode = 'RGBA'
    return cam


PROP_COL = {'mat': (0.72, 0.87, 0.84, 1), 'chair': (0.58, 0.61, 0.63, 1), 'weight': (0.9, 0.5, 0.13, 1), 'bar': (0.35, 0.37, 0.4, 1), 'board': (0.9, 0.55, 0.2, 1)}


def box(name, size, loc, col, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    o.color = col
    return o


def cyl(name, r, depth, loc, col, rot=(0, D(90), 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=32)
    o = bpy.context.object
    o.name = name
    o.color = col
    return o


def bone_world(rig, name):
    return rig.matrix_world @ rig.pose.bones[name].head


def hands(rig):
    a, b = bone_world(rig, 'wrist.L'), bone_world(rig, 'wrist.R')
    return (a + b) / 2


def static_props(kinds, rig, ys):
    made = []
    if 'mat' in kinds:
        y0, y1 = min(ys), max(ys)
        made.append(box('mat', (0.62, (y1 - y0) + 0.25, 0.016), (0, (y0 + y1) / 2, -0.008), PROP_COL['mat']))
    if 'chair' in kinds:
        pv = bone_world(rig, 'root')
        top = pv.z - 0.07
        cy = pv.y + 0.06
        made.append(box('seat', (0.46, 0.44, 0.04), (0, cy, top - 0.02), PROP_COL['chair']))
        for dx in (-0.2, 0.2):
            for dy in (-0.19, 0.19):
                made.append(box('leg', (0.03, 0.03, top - 0.04), (dx, cy + dy, (top - 0.04) / 2), PROP_COL['chair']))
        made.append(box('back', (0.46, 0.03, 0.45), (0, cy + 0.215, top + 0.22), PROP_COL['chair']))
    return made


def frame_props(kinds, rig, pose):
    made = []
    if 'dumbbell' in kinds:
        c = hands(rig) + Vector((0, -0.05, 0))
        made.append(cyl('db', 0.022, 0.22, c, PROP_COL['bar']))
        for dx in (-0.1, 0.1):
            made.append(cyl('dbw', 0.06, 0.05, c + Vector((dx, 0, 0)), PROP_COL['weight']))
    if 'barbell' in kinds:
        c = hands(rig)
        made.append(cyl('bar', 0.016, 1.4, c, PROP_COL['bar']))
        for dx in (-0.56, 0.56):
            made.append(cyl('plate', 0.13, 0.04, c + Vector((dx, 0, 0)), PROP_COL['weight']))
    if 'board' in kinds:
        t = D(pose.get('tilt', 0))
        made.append(box('board', (0.36, 0.62, 0.03), (0, 0, 0.075), PROP_COL['board'], rot=(t, 0, 0)))
        made.append(cyl('pivot', 0.06, 0.34, (0, 0, 0.03), PROP_COL['chair']))
    return made


def clear(objs):
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    human, rig = build_human()
    objs = [o for o in bpy.data.objects if o.type == 'MESH']
    cam = setup_scene()
    meta = {}
    for pid, P in POSES.items():
        if ONLY and pid not in ONLY:
            continue
        a = P['a']
        b = P.get('b', a)
        n = FRAMES if 'b' in P else 1
        poses = [lerp_pose(a, b, i / (n - 1)) if n > 1 else a for i in range(n)]
        # encuadre común: caja de todos los cuadros
        ys, zs = [], []
        for ps in poses:
            set_pose(rig, ps)
            snap_to_floor(rig, objs)
            pts = mesh_points(objs)
            ys += [p.y for p in pts]
            zs += [p.z for p in pts]
        if 'board' in P.get('props', []):
            zs = [z + 0.09 for z in zs]
        cy, cz = (min(ys) + max(ys)) / 2, (max(zs)) / 2
        span = max(max(ys) - min(ys), (max(zs) - 0) * W / H) * 1.18
        cam.data.ortho_scale = span
        cam.location = (8, cy, max(zs) / 2 + span * H / W * 0.04)
        frames, pelv = [], []
        kinds = P.get('props', [])
        set_pose(rig, poses[0])
        snap_to_floor(rig, objs)
        fixed = static_props(kinds, rig, ys)
        for i, ps in enumerate(poses):
            set_pose(rig, ps)
            snap_to_floor(rig, objs)
            if 'board' in kinds:
                rig.location.z += 0.09
                bpy.context.view_layer.update()
            moving = frame_props(kinds, rig, ps)
            f = os.path.join(OUT, f'{pid}_{SEX}_{i}.png')
            bpy.context.scene.render.filepath = f
            bpy.ops.render.render(write_still=True)
            frames.append(f)
            clear(moving)
            pw = rig.matrix_world @ rig.pose.bones['root'].head
            c = world_to_camera_view(bpy.context.scene, cam, pw)
            pelv.append([round(c.x, 3), round(1 - c.y, 3)])
        clear(fixed)
        meta[pid] = {'n': n, 'pelvis': pelv}
        print('RENDER', pid, n)
    with open(os.path.join(OUT, f'meta_{SEX}.json'), 'w') as fh:
        json.dump(meta, fh)


main()
