# Modelos 3D

> **Autoría:** los STL de `stl/` y el proyecto de `proyecto/` son de **3DRODV**:
> "Máquina para hacer Filamento PET", publicada en
> [Creality Cloud](https://www.crealitycloud.com/model-details/69b4bb67f6b153ff3e33209c)
> con licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> **Archivos sin modificar.** El docente asesor eligió este diseño base con el
> equipo, por su montaje nativo de NEMA 17 y su reducción de 60:1.

Piezas impresas de la máquina. El reglamento de la feria (Art. 2.1) exige
entregar los archivos de modelado originales (STL y CAD) junto con el informe.
Los archivos editables de las piezas propias del equipo (ver
[Piezas propias](#piezas-propias-pendientes)) irán en `fuente/`.

## Organización

```
cad/
├── stl/        # piezas de 3DRODV listas para imprimir (.stl), sin modificar
├── proyecto/   # proyecto de Creality Print (.3mf) de 3DRODV: hay que re-laminarlo para la Ender-3 V3 SE
└── fuente/     # .FCStd (FreeCAD) de las piezas propias del equipo (pendiente)
```

## Piezas

Las medidas, los dientes y los ajustes de las tablas son un análisis del equipo
sobre los STL de 3DRODV. Las dimensiones generales y los agujeros se midieron
con un script que corta las mallas y ajusta círculos.

| Archivo | Pieza | Medidas (mm) | Detalles medidos |
|---|---|---|---|
| `G51.stl` | Piñón del motor, 8 dientes | Ø 20 × 28 | Agujero en D: Ø 5.96, con el plano a 2.39 mm del centro (cota D = 5.39) |
| `G52.stl` | Rueda de 32 dientes + piñón de 12 | Ø 68 × 32 | Ø raíz medido 58.9 (32 d) y 18.9 (12 d). Agujero Ø 8.5 |
| `G53.stl` | Rueda de 36 dientes + piñón de 11 | Ø 76 × 32 | Ø raíz medido 66.9 (36 d) y 17.5 (11 d). Agujero Ø 8.5, rebaje Ø 15.9 |
| `G54.stl` | Rueda de 55 dientes | Ø 114 × 15 | Ø raíz medido 104.9. 8 agujeros Ø 4.56 en un círculo de Ø 64. Agujero Ø 8.5, rebaje Ø 95 |
| `G55.stl` | Tambor | Ø 74 × 60 | 8 agujeros pasantes Ø 2.55 en un círculo de Ø 64. Agujero central Ø 12 |
| `G56.stl` | Disco (pestaña) del tambor | Ø 114 × 4 | Agujero central Ø 54, perforaciones de Ø 6 y Ø 4.6 |
| `G48.stl`, `G49.stl` | Placas laterales (simétricas) | 150 × 102.6 × 7 | 3 agujeros Ø 8.0 para las varillas M8. 4 ranuras M3 (Ø 3.4) con el patrón NEMA 17 de 31 mm y 10 mm de recorrido |
| `G50.stl` | Soporte del motor | 80 × 60 × 40 | Patrón NEMA 17 con ranuras M3 (Ø 3.4). 2 agujeros M4 (Ø 4) avellanados a Ø 9 |
| `G46.stl` | Soporte con tubo para rodamiento | 50 × 49 × 28 | Tubo Ø 28 con alojamiento Ø 22.96 (rodamiento 608). 2 agujeros Ø 4 |
| `G47.stl` | Pieza alargada con 4 orejas de fijación | 125 × 34.4 × 12.1 | Función a confirmar por el equipo |

Los números de dientes (8, 32, 12, 36, 11, 55) y los diámetros exteriores
(20, 68, 28, 76, 26, 114) se comprobaron en los STL y coinciden con módulo 2
y la relación 60:1 del firmware.

## Ajustes a revisar

| Ajuste | Nominal | En el modelo | Observación |
|---|---|---|---|
| Piñón en el eje del NEMA 17 | Eje Ø 5 con plano (cota D 4.5) | Ø 5.96, cota D 5.39 | ~1 mm de holgura: el piñón puede bailar. Propuesta: Ø 5.2 y cota D 4.7 |
| Rodamiento 608 en G46 | Ø 22 | Ø 22.96 | ~1 mm de holgura: pegar el rodamiento o reimprimir el alojamiento a ~Ø 22.2 |
| Tornillos tambor–rueda | M3 autorroscantes | Rueda Ø 4.56 (paso), tambor Ø 2.55 (piloto) | Los tornillos pasan por la rueda y muerden el piloto del tambor. No hace falta rediseñarlo |
| Ruedas en las varillas M8 | Ø 8 | Ø 8.5 | +0.5 mm: giran libres. Correcto |
| Varillas M8 en las placas | Ø 8 | Ø 8.0 | Sin holgura: quedan fijas. Si no entran, repasar con broca de 8 mm |
| Motor en las placas y en G50 | Patrón de 31 mm, M3 | Ranuras Ø 3.4 de 10 mm | Permiten ajustar la distancia del engrane. Correcto |

## Piezas propias (pendientes)

Diseño del equipo en FreeCAD. Los `.FCStd` y los STL exportados de estas piezas
irán en `fuente/`, para no mezclarlos con los de 3DRODV. Licencia MIT.

| Pieza | Qué hay que hacer |
|---|---|
| Piñón corregido (reemplaza a `G51`) | Agujero en D de Ø 5.2 con el plano a 4.7 mm, para el eje de 5 mm del NEMA 17. **Rediseñar solo si la impresión de prueba de `G51` baila en el eje** |
| Alojamiento del 608 en `G46` | Ø 22.2 en lugar de Ø 22.96. **Rediseñar solo si la impresión de prueba queda floja** |
| Soporte de la pistola de silicón | Fija la pistola con su boquilla perforada a 1.6 mm |
| Caja de la electrónica | Arduino Uno (68.6 × 53.4 mm, agujeros de Ø 3.2), A4988, potenciómetro, entrada del adaptador de 12 V y salida de los cables del motor |

## Parámetros de impresión

Las piezas se imprimen en una **Creality Ender-3 V3 SE** (cama de 220 × 220 ×
250 mm). Todas caben: la más grande es la placa lateral, de 150 × 102.6 mm.

> El proyecto `.3mf` se laminó con un perfil de otra impresora (Creality K2) y
> trae ese G-code dentro. **Antes de imprimir, ábrelo en Creality Print, cambia
> la impresora a Ender-3 V3 SE y vuelve a laminar.** No envíes a la Ender el
> G-code que viene en el archivo.

| Parámetro | Valor |
|---|---|
| Impresora | Creality Ender-3 V3 SE, boquilla de 0.4 mm |
| Material | PLA |
| Altura de capa | 0.2 mm |
| Paredes | 2 |
| Relleno | 15 %, patrón grid |
| Capas superiores / inferiores | 5 / 3 |
| Soportes | Sí, tipo árbol (automático) |
| Peso total | ~278.5 g de PLA (estimado del laminador; casi no cambia con la impresora) |
| Tiempo total | Por calcular al re-laminar para la Ender-3 V3 SE |
