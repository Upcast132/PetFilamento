# PetFilamento. Diseño del equipo, generado con asistencia de IA (Claude, de Anthropic)
# a partir de la especificación del equipo. Licencia MIT.
#
# Uso: blender -b -P generar_caja.py
# Genera caja_electronica.blend, caja_base.stl, caja_tapa_a.stl y caja_tapa_b.stl junto a este script.
#
# Coordenadas de la especificación: origen en la esquina interior superior izquierda de la
# sección A, sobre el piso. X a la derecha, Y hacia abajo, Z arriba.
# En Blender: x = X, y = -Y, z = Z + piso. Vista superior: pared del USB arriba, X a la derecha.

import math
import os

import bmesh
import bpy

P = {
    # General
    "interior_x": 132.0,
    "interior_z": 36.0,
    "seccion_a_y": (0.0, 108.0),
    "seccion_b_y": (110.4, 186.4),
    "pared": 2.4,
    "piso": 2.4,
    "radio_aristas": 3.0,
    "segmentos": 64,
    # Tapas
    "espesor_tapa": 2.4,
    "tapa_a_y": (-2.4, 110.3),
    "tapa_b_y": (110.5, 188.8),
    "diam_agujero_tapa": 3.4,
    "diam_avellanado_tapa": 6.5,
    # Postes de las tapas: (centro X, centro Y, esquina X, esquina Y) para el relleno de 4 x 4
    "postes_tapa_a": [(4, 4, 0, 0), (128, 4, 132, 0), (4, 104, 0, 108), (128, 104, 132, 108)],
    "postes_tapa_b": [(4, 114.4, 0, 110.4), (128, 114.4, 132, 110.4),
                      (4, 182.4, 0, 186.4), (128, 182.4, 132, 186.4)],
    "diam_poste_tapa": 7.0,
    "diam_guia_poste_tapa": 2.6,
    "prof_guia_poste_tapa": 12.0,
    # Sección A: Arduino Uno
    "postes_arduino": [(10.5, 21.0), (58.7, 22.3), (15.6, 73.1), (43.5, 73.1)],
    "diam_poste_arduino": 6.5,
    "alto_poste_arduino": 5.0,
    "diam_guia_arduino": 2.6,
    "prof_guia_arduino": 4.0,
    # Sección A: protoboard media (x0, x1, y0, y1 de la zona interior del marco)
    "zona_proto": (67.5, 124.0, 2.0, 87.0),
    "marco_alto": 1.0,
    "marco_ancho": 1.2,
    # Sección A: aberturas
    "USB_X": 45.0,
    "usb_z": 12.1,
    "usb_ancho": 13.5,
    "usb_alto": 12.0,
    "diam_potenciometro": 7.2,
    "pot_y": 90.0,
    "pot_z": 18.0,
    "ranura_motor_y": 14.0,
    "ranura_motor_z": 8.0,
    "ranura_motor_centro": (94.0, 10.0),  # Y, Z en la pared derecha
    "ranura_motor_radio": 2.0,
    "amarra_motor_centro": (123.0, 94.0),
    "amarra_motor_tam": (10.0, 6.0),  # X, Y (túnel a lo largo de Y)
    "diam_paso_cables": 10.0,
    "paso_cables": (105.0, 12.0),  # X, Z en la pared divisoria
    # Puentes para amarra (comunes)
    "amarra_alto": 5.0,
    "tunel_ancho": 3.0,
    "tunel_alto": 2.0,
    # Sección B: carrete
    "carrete_centro": (46.0, 148.4),
    "diam_nucleo": 42.0,
    "diam_anillo_ext": 66.0,
    "pared_anillo": 2.0,
    "alto_carrete": 28.0,
    "ancho_abertura_anillo": 8.0,
    "angulos_pestanas": [30, 90, 150, 210, 270, 330],
    "pestana_ancho_arco": 12.0,      # medido sobre la cara interior del anillo
    "pestana_saliente": 4.0,         # desde la cara interior del anillo hacia el canal
    "pestana_z": (28.0, 33.0),
    "pestana_punta": 1.0,            # espesor de la punta, cara inferior a 45°
    # Sección B: entrada del cargador
    "diam_cargador": 7.0,
    "cargador": (148.4, 8.0),  # Y, Z en la pared izquierda
    "amarra_cargador_centro": (4.5, 148.4),
    "amarra_cargador_tam": (6.0, 10.0),  # X, Y (túnel a lo largo de Y)
    # Sección B: módulo buck (zona interior del marco)
    "buck_ancho_x": 38.0,
    "buck_x_der": 124.0,
    "buck_y": (114.4, 182.4),
    # Orejas
    "oreja_largo": 16.0,
    "oreja_salida": 12.0,
    "oreja_espesor": 4.0,
    "diam_oreja": 4.5,
    "diam_avellanado_oreja": 9.0,
    "oreja_dist_pared": 7.0,
    "orejas_izquierda_y": [14.0, 56.0, 172.0],
    "orejas_derecha_y": [14.0, 60.0, 150.0],
    # Ventilación
    "vent_a": {"tam": (2.0, 20.0), "filas": [([12, 17, 22, 27, 32], 22.0),
                                             ([87.5, 92.5, 97.5, 102.5, 107.5], 35.0)]},
    "vent_b": {"tam": (2.0, 30.0), "filas": [([94, 102, 110, 118], 148.4)]},
}

CARPETA = os.path.dirname(os.path.abspath(__file__))
E = 1.0  # sobrante de los cortadores para evitar caras coplanares


# ---------- utilidades ----------

def a_blender(x, y, z):
    return (x, -y, z + P["piso"])


def malla_desde_capas(nombre, capas, cerrada_en_anillo=True):
    """capas: anillos de vértices 3D con el mismo número de puntos. Cierra los extremos."""
    bm = bmesh.new()
    anillos = [[bm.verts.new(v) for v in anillo] for anillo in capas]
    n = len(capas[0])
    bm.faces.new(list(reversed(anillos[0])))
    bm.faces.new(anillos[-1])
    for a, b in zip(anillos[:-1], anillos[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.collection.objects.link(ob)
    return ob


def prisma_z(nombre, perfil, z0, z1):
    """Perfil 2D (X, Y) de la especificación extruido entre z0 y z1 de la especificación."""
    return malla_desde_capas(nombre, [[a_blender(x, y, z0) for x, y in perfil],
                                      [a_blender(x, y, z1) for x, y in perfil]])


def prisma_pared(nombre, perfil, eje, d0, d1):
    """Perfil 2D (u, w) con w = Z. eje 'y': u = X y se extruye en Y. eje 'x': u = Y y se extruye en X."""
    def p(u, w, d):
        return a_blender(u, d, w) if eje == "y" else a_blender(d, u, w)
    return malla_desde_capas(nombre, [[p(u, w, d0) for u, w in perfil],
                                      [p(u, w, d1) for u, w in perfil]])


def cono_z(nombre, cx, cy, z0, r0, z1, r1):
    n = P["segmentos"]
    def anillo(z, r):
        return [a_blender(cx + r * math.cos(2 * math.pi * i / n),
                          cy + r * math.sin(2 * math.pi * i / n), z) for i in range(n)]
    return malla_desde_capas(nombre, [anillo(z0, r0), anillo(z1, r1)])


def circulo(cx, cy, r, n=None):
    n = n or P["segmentos"]
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rect_redondeado(x0, x1, y0, y1, radios, n=16):
    """radios: número o (r[x1,y0], r[x1,y1], r[x0,y1], r[x0,y0]). Radio 0 = esquina recta."""
    if not isinstance(radios, (list, tuple)):
        radios = (radios,) * 4
    pts = []
    esquinas = [(x1, y0, -1, 1, -90), (x1, y1, -1, -1, 0), (x0, y1, 1, -1, 90), (x0, y0, 1, 1, 180)]
    for (ex, ey, sx, sy, a0), r in zip(esquinas, radios):
        if r <= 0:
            pts.append((ex, ey))
            continue
        cx, cy = ex + sx * r, ey + sy * r
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def gota_recortada(cu, cw, r):
    """Círculo con techo a 45° recortado en w = cw + r. Imprime sin soportes en paredes verticales."""
    n = P["segmentos"]
    k = r / math.sqrt(2)
    pts = [(cu + k, cw + k), (cu + r * (math.sqrt(2) - 1), cw + r),
           (cu - r * (math.sqrt(2) - 1), cw + r), (cu - k, cw + k)]
    pasos = int(n * 0.75)
    for i in range(1, pasos):
        a = math.radians(135 + 270 * i / pasos)
        pts.append((cu + r * math.cos(a), cw + r * math.sin(a)))
    return pts


def barrido_angular(nombre, cx, cy, perfil_rz, a0, a1, pasos=12):
    """Barre un perfil (r, z) alrededor de (cx, cy) entre los ángulos a0 y a1 (radianes)."""
    capas = []
    for i in range(pasos + 1):
        a = a0 + (a1 - a0) * i / pasos
        capas.append([a_blender(cx + r * math.cos(a), cy + r * math.sin(a), z) for r, z in perfil_rz])
    return malla_desde_capas(nombre, capas)


def booleana(objetivo, herramienta, operacion):
    m = objetivo.modifiers.new("bool", "BOOLEAN")
    m.operation = operacion
    m.solver = "EXACT"
    m.object = herramienta
    bpy.context.view_layer.objects.active = objetivo
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(herramienta, do_unlink=True)


def puente_amarra(cx, cy, tam_x, tam_y):
    """Bloque con túnel a lo largo de Y. El piso del túnel es el piso de la caja."""
    alto, ta, th = P["amarra_alto"], P["tunel_ancho"], P["tunel_alto"]
    b = prisma_z("puente", rect(cx - tam_x / 2, cx + tam_x / 2, cy - tam_y / 2, cy + tam_y / 2), -E, alto)
    booleana(b, prisma_z("tunel", rect(cx - ta / 2, cx + ta / 2, cy - tam_y / 2 - E, cy + tam_y / 2 + E),
                         -2 * E, th), "DIFFERENCE")
    return b


# ---------- escena ----------

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version = 0  # sin copias .blend1
us = bpy.context.scene.unit_settings
us.system = "METRIC"
us.scale_length = 0.001
us.length_unit = "MILLIMETERS"

ix, iz = P["interior_x"], P["interior_z"]
t, fz, R = P["pared"], P["piso"], P["radio_aristas"]
ya0, ya1 = P["seccion_a_y"]
yb0, yb1 = P["seccion_b_y"]

# ---------- base ----------

# Los postes de las tapas y su relleno de 4 x 4 se restan del cortador del interior, así
# nacen dentro del casco sin uniones de caras coplanares en Z = 36.
base = prisma_z("caja_base", rect_redondeado(-t, ix + t, ya0 - t, yb1 + t, R), -fz, iz)
rp = P["diam_poste_tapa"] / 2
postes_tapa = P["postes_tapa_a"] + P["postes_tapa_b"]
for nombre, (y0, y1) in (("interior_a", (ya0, ya1)), ("interior_b", (yb0, yb1))):
    hueco = prisma_z(nombre, rect(0, ix, y0, y1), 0, iz + E)
    for x, y, ex, ey in postes_tapa:
        if not (y0 < y < y1):
            continue
        booleana(hueco, prisma_z("poste", circulo(x, y, rp), -E, iz + 2 * E), "DIFFERENCE")
        rx0, rx1 = sorted((x, ex + (E if ex > x else -E)))
        ry0, ry1 = sorted((y, ey + (E if ey > y else -E)))
        booleana(hueco, prisma_z("relleno_poste", rect(rx0, rx1, ry0, ry1), -E, iz + 2 * E), "DIFFERENCE")
    booleana(base, hueco, "DIFFERENCE")

uniones = []

ra = P["diam_poste_arduino"] / 2
for x, y in P["postes_arduino"]:
    uniones.append(prisma_z("poste_ard", circulo(x, y, ra), -E, P["alto_poste_arduino"]))

def marco(x0, x1, y0, y1):
    w, h = P["marco_ancho"], P["marco_alto"]
    for b in (rect(x0 - w, x1 + w, y0 - w, y0), rect(x0 - w, x1 + w, y1, y1 + w),
              rect(x0 - w, x0, y0, y1), rect(x1, x1 + w, y0, y1)):
        uniones.append(prisma_z("marco", b, -E, h))

marco(*P["zona_proto"])
by0, by1 = P["buck_y"]
marco(P["buck_x_der"] - P["buck_ancho_x"], P["buck_x_der"], by0, by1)

uniones.append(puente_amarra(*P["amarra_motor_centro"], *P["amarra_motor_tam"]))
uniones.append(puente_amarra(*P["amarra_cargador_centro"], *P["amarra_cargador_tam"]))

# carrete: núcleo macizo y anillo con 2 aberturas y 6 pestañas
ccx, ccy = P["carrete_centro"]
hc = P["alto_carrete"]
r_ext = P["diam_anillo_ext"] / 2
r_int = r_ext - P["pared_anillo"]
uniones.append(prisma_z("nucleo", circulo(ccx, ccy, P["diam_nucleo"] / 2, 128), -E, hc))
anillo = prisma_z("anillo", circulo(ccx, ccy, r_ext, 128), -E, hc)
booleana(anillo, prisma_z("anillo_hueco", circulo(ccx, ccy, r_int, 128), -2 * E, hc + E), "DIFFERENCE")
wa = P["ancho_abertura_anillo"]
booleana(anillo, prisma_z("aberturas", rect(ccx - r_ext - E, ccx + r_ext + E, ccy - wa / 2, ccy + wa / 2),
                          -2 * E, hc + E), "DIFFERENCE")
pz0, pz1 = P["pestana_z"]
r_punta = r_int - P["pestana_saliente"]
z_punta = pz1 - P["pestana_punta"]
# La pestaña se mete 0.5 en el anillo (parte enterrada con chaflanes a 45°). Su cara exterior
# queda 0.02 por dentro de r_ext y la cuña pasa exactamente por (r_int, Z=28) a 45°, así no
# coincide con las caras facetadas del anillo y no deja astillas con voladizo.
d = 0.02
assert abs((z_punta - (pz0 - d)) - (r_int + d - r_punta)) < 1e-6, "la cara inferior debe ir a 45°"
perfil = [(r_ext - d, pz1), (r_ext - d, pz0), (r_ext - 0.5 - d, pz0 - 0.5), (r_int + 0.5, pz0 - 0.5),
          (r_int + d, pz0 - d), (r_punta, z_punta), (r_punta, pz1)]
media = P["pestana_ancho_arco"] / 2 / r_int
for ang in P["angulos_pestanas"]:
    a = math.radians(ang)
    booleana(anillo, barrido_angular("pestana", ccx, ccy, perfil, a - media, a + media), "UNION")
uniones.append(anillo)

ol, os_, oe = P["oreja_largo"], P["oreja_salida"], P["oreja_espesor"]
orejas = []
for y in P["orejas_izquierda_y"]:
    orejas.append((-t - P["oreja_dist_pared"], y))
    uniones.append(prisma_z("oreja", rect(-t - os_, -t + 0.4, y - ol / 2, y + ol / 2), -fz, -fz + oe))
for y in P["orejas_derecha_y"]:
    orejas.append((ix + t + P["oreja_dist_pared"], y))
    uniones.append(prisma_z("oreja", rect(ix + t - 0.4, ix + t + os_, y - ol / 2, y + ol / 2), -fz, -fz + oe))

for u in uniones:
    booleana(base, u, "UNION")

cortes = []
rg = P["diam_guia_poste_tapa"] / 2
for x, y, _, _ in postes_tapa:
    cortes.append(prisma_z("guia", circulo(x, y, rg), iz - P["prof_guia_poste_tapa"], iz + E))
rga = P["diam_guia_arduino"] / 2
for x, y in P["postes_arduino"]:
    cortes.append(prisma_z("guia_ard", circulo(x, y, rga),
                           P["alto_poste_arduino"] - P["prof_guia_arduino"], P["alto_poste_arduino"] + E))

r1, r2 = P["diam_oreja"] / 2, P["diam_avellanado_oreja"] / 2
zsup = -fz + oe
for x, y in orejas:
    cortes.append(prisma_z("agujero_oreja", circulo(x, y, r1), -fz - E, zsup + E))
    cortes.append(cono_z("avellanado_oreja", x, y, zsup - (r2 - r1), r1, zsup + E, r2 + E))

# pared de arriba: USB-B
ux, uz, ua, uh = P["USB_X"], P["usb_z"], P["usb_ancho"], P["usb_alto"]
cortes.append(prisma_pared("usb", rect(ux - ua / 2, ux + ua / 2, uz - uh / 2, uz + uh / 2),
                           "y", ya0 - t - E, ya0 + E))
# pared izquierda: potenciómetro y cargador
cortes.append(prisma_pared("pot", gota_recortada(P["pot_y"], P["pot_z"], P["diam_potenciometro"] / 2),
                           "x", -t - E, E))
cortes.append(prisma_pared("cargador", gota_recortada(*P["cargador"], P["diam_cargador"] / 2),
                           "x", -t - E, E))
# pared derecha: ranura del motor
my, mz = P["ranura_motor_centro"]
mw, mh = P["ranura_motor_y"], P["ranura_motor_z"]
cortes.append(prisma_pared("motor", rect_redondeado(my - mw / 2, my + mw / 2, mz - mh / 2, mz + mh / 2,
                                                    P["ranura_motor_radio"]), "x", ix - E, ix + t + E))
# pared divisoria: paso de cables
cortes.append(prisma_pared("paso_cables", gota_recortada(*P["paso_cables"], P["diam_paso_cables"] / 2),
                           "y", ya1 - E, yb0 + E))

for c in cortes:
    booleana(base, c, "DIFFERENCE")

# ---------- tapas (en el .blend quedan montadas sobre la base) ----------

et = P["espesor_tapa"]
zext = iz + et


def hacer_tapa(nombre, y0, y1, radios, postes, vent):
    tapa = prisma_z(nombre, rect_redondeado(-t, ix + t, y0, y1, radios), iz, zext)
    r1, r2 = P["diam_agujero_tapa"] / 2, P["diam_avellanado_tapa"] / 2
    cortes = []
    for x, y, _, _ in postes:
        cortes.append(prisma_z("agujero_tapa", circulo(x, y, r1), iz - E, zext + E))
        cortes.append(cono_z("avellanado_tapa", x, y, zext - (r2 - r1), r1, zext + E, r2 + E))
    vx, vy = vent["tam"]
    for xs, yc in vent["filas"]:
        for x in xs:
            cortes.append(prisma_z("vent", rect(x - vx / 2, x + vx / 2, yc - vy / 2, yc + vy / 2),
                                   iz - E, zext + E))
    for c in cortes:
        booleana(tapa, c, "DIFFERENCE")
    return tapa


# radios en orden (x1,y0), (x1,y1), (x0,y1), (x0,y0). En la junta las esquinas son rectas.
tapa_a = hacer_tapa("caja_tapa_a", *P["tapa_a_y"], (R, 0, 0, R), P["postes_tapa_a"], P["vent_a"])
tapa_b = hacer_tapa("caja_tapa_b", *P["tapa_b_y"], (0, R, R, 0), P["postes_tapa_b"], P["vent_b"])

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CARPETA, "caja_electronica.blend"))

# ---------- exportación STL ----------

from mathutils import Matrix


def exportar(ob, ruta):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    if bpy.app.version >= (4, 1, 0):
        bpy.ops.wm.stl_export(filepath=ruta, export_selected_objects=True, ascii_format=False,
                              apply_modifiers=True, global_scale=1.0, use_scene_unit=False)
    else:
        bpy.ops.export_mesh.stl(filepath=ruta, use_selection=True, ascii=False,
                                use_mesh_modifiers=True, global_scale=1.0, use_scene_unit=False)


exportar(base, os.path.join(CARPETA, "caja_base.stl"))  # el piso ya está en z = 0


def exportar_tapa_volteada(ob, y0, y1, ruta):
    # 180° alrededor de un eje paralelo a X por el centro de la tapa, y cara exterior a z = 0
    yc = -(y0 + y1) / 2
    zc = iz + fz + et / 2
    giro = Matrix.Translation((0, yc, zc)) @ Matrix.Rotation(math.pi, 4, "X") @ Matrix.Translation((0, -yc, -zc))
    ob.matrix_world = Matrix.Translation((0, 0, -(iz + fz))) @ giro
    bpy.context.view_layer.update()
    exportar(ob, ruta)


exportar_tapa_volteada(tapa_a, *P["tapa_a_y"], os.path.join(CARPETA, "caja_tapa_a.stl"))
exportar_tapa_volteada(tapa_b, *P["tapa_b_y"], os.path.join(CARPETA, "caja_tapa_b.stl"))
print("LISTO")
