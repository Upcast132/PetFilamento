# PetFilamento

Máquina escolar que convierte tiras de botellas PET en filamento de 1.75 mm
para impresión 3D. La tira se jala a través de la boquilla caliente de una
pistola de silicón, montada en un soporte impreso y con la boquilla perforada
a 1.6 mm. El filamento se enrolla en un tambor de 74 mm de diámetro. Lo mueve
un motor NEMA 17 a través de un reductor impreso de engranajes de módulo 2,
con una relación total de **60:1** en tres etapas (8→32, 12→36 y 11→55).

- **Versión base (la actual):** un Arduino Uno **controla la velocidad del
  motor** según un potenciómetro. La pistola se enchufa directo y se calienta
  sola con su PTC, como cualquier pistola de silicón.
- **Mejora opcional:** un **tope de seguridad de temperatura** con termistor y
  relé que corta la pistola si la boquilla se pasa de un límite. Ya está
  escrito en el firmware, pero viene desactivado. Ver
  [Mejora opcional: tope de temperatura](#mejora-opcional-tope-de-temperatura).

> **Estado:** firmware **sin probar en hardware**. Compila para Arduino Uno
> (ATmega328P), pero todavía no se ha probado con la máquina real. Sigue
> [docs/puesta-en-marcha.md](docs/puesta-en-marcha.md) antes de usarla.

Licencia: MIT (ver [LICENSE](LICENSE)). Cubre el firmware y la documentación
de este repositorio.

---

## Estructura

```
PetFilamento/
├── README.md
├── LICENSE
├── firmware/PetFilamento/PetFilamento.ino
├── cad/                     # modelos 3D propios (STL y archivos fuente)
├── informe/                 # informe técnico para la feria (HTML y PDF)
└── docs/
    ├── cableado.md          # conexiones detalladas
    ├── puesta-en-marcha.md  # pruebas y calibración paso a paso
    └── feria-2026.md        # requisitos y rúbrica de la feria
```

## Componentes (versión base)

| Cant. | Componente | Notas |
|---|---|---|
| 1 | Arduino Uno (ATmega328P) | 12 V por el jack (centro positivo; el Uno acepta de 7 a 12 V) o por VIN |
| 1 | Adaptador de 12 V | Alimenta el Uno (jack o VIN) y el motor (VMOT) |
| 1 | Driver A4988 | En medio paso (MS1 a 5 V, MS2 y MS3 a GND) |
| 1 | Condensador electrolítico de 100 µF (≥ 25 V) | Entre VMOT y GND, junto al A4988 |
| 1 | Resistencia de 10 kΩ | Pull-up de ENABLE a 5 V |
| 1 | Motor NEMA 17 bipolar | 200 pasos por vuelta |
| 1 | Potenciómetro B50K | Lineal |
| 1 | Pistola de silicón grande, nueva, de 110 V | Con su propio cable y su PTC, enchufada directo |
| — | Piezas impresas (diseño propio) | Reductor 60:1 de módulo 2, tambor de 74 mm, soporte de la pistola y soportes |

Para la mejora opcional del tope de temperatura hacen falta, además, un
termistor, un relé y una caja para la parte de 110 V. La lista está en
[Mejora opcional: tope de temperatura](#mejora-opcional-tope-de-temperatura).

### Piezas no impresas

| Cant. | Pieza | Notas |
|---|---|---|
| 3 | Varillas roscadas M8, con tuercas y arandelas | Estructura y ejes |
| 2 | Rodamientos 608 | 8 mm de diámetro interior, para las varillas M8 |
| 4 | Tornillos M3 de 8 a 10 mm | Fijación del NEMA 17 |
| 8 | Tornillos M4 | Unen el tambor al engranaje grande. El largo se mide al armar |
| 1 | Base de madera | Para montar todo |
| 1 | Cinta Kapton | Aislamiento térmico; con la mejora opcional, fija el termistor a la boquilla |
| 1 | Broca de 1.6 mm | Para perforar la boquilla |
| 1 | Cortador de botellas con cuchilla | Para sacar las tiras |

## Mecánica y velocidades

| Etapa | Motriz → conducido | Relación |
|---|---|---|
| 1 | 8 → 32 dientes | 4:1 |
| 2 | 12 → 36 dientes | 3:1 |
| 3 | 11 → 55 dientes | 5:1 |
| **Total** | | **60:1** |

Con el A4988 en medio paso, una vuelta del tambor son 200 × 2 × 60 = 24 000
pasos.

| rpm del tambor | Pasos/s del motor | Velocidad lineal (tambor vacío) |
|---|---|---|
| 0.5 (mínimo por defecto) | 200 | 0.12 m/min |
| 4.0 (máximo por defecto) | 1600 | 0.93 m/min |
| 5.0 (límite del firmware) | 2000 | 1.16 m/min |

La velocidad lineal es rpm × π × 74 mm / 1000. La línea de Serial la muestra
solo como dato informativo; no se usa en el control.

## Pines

| Pin del Uno | Conectado a | Función |
|---|---|---|
| D2 | A4988 STEP | Pulsos de paso |
| D3 | A4988 DIR | Dirección (la maneja AccelStepper) |
| D4 | A4988 ENABLE | Activo en bajo, pull-up de 10k a 5 V (arranca deshabilitado) |
| A0 | Cursor del potenciómetro | Velocidad |
| D5 | Relé IN | *Solo con la mejora opcional.* Relé activado = pistola cortada |
| A1 | Divisor del termistor | *Solo con la mejora opcional.* Temperatura de la boquilla |
| 5V | A4988 VDD, potenciómetro (y divisor y relé, con la mejora) | Lógica |
| Jack o VIN | +12 V del adaptador | Alimentación del Uno (usa uno de los dos, no ambos) |
| GND | GND común | Todas las tierras unidas |

## Diagrama de cableado (versión base)

Detalle completo, incluida la mejora opcional, en [docs/cableado.md](docs/cableado.md).

```
                 +12 V (adaptador) ─────────┬──────────────────────┐
                                            │                      │
                                         [100 µF]                  │
                                            │                      │
  ┌──────────── ARDUINO UNO ────────┐    ┌──┴─────── A4988 ─────┐  │
  │ VIN ◄──── +12 V ────────────────┼────┼──────────────────────┼──┘
  │ GND ─────── GND común ──────────┼────┤ GND (lógica y motor) │
  │                                 │    │ VMOT ◄── +12 V       │
  │ 5V ──┬──────────────────────────┼────┤ VDD                  │
  │      │      ┌─[10k]─────────────┼────┤ ENABLE               │
  │ D4 ──┼──────┴───────────────────┼────┘                      │
  │ D2 ──┼──────────────────────────┼────► STEP          1A/1B ─┼──► bobina A ┐
  │ D3 ──┼──────────────────────────┼────► DIR           2A/2B ─┼──► bobina B ┤ NEMA 17
  │      │                          │      MS1 ─────── 5 V      │             ┘
  │      │                          │      MS2, MS3 ── GND      │
  │      │                          │      RESET ── SLEEP       │
  │      │                          │    └──────────────────────┘
  │      │   POTENCIÓMETRO B50K     │
  │      ├──── extremo 1            │
  │ A0 ◄─┼──── cursor               │
  │ GND ─┴──── extremo 2            │
  └─────────────────────────────────┘

  PISTOLA DE SILICÓN: enchufada directo a 110 V con su propio cable.
```

En lugar del pin VIN, el Uno también puede alimentarse por su jack de 12 V
(centro positivo). VMOT siempre se toma directo del adaptador, nunca del pin
VIN del Uno.

## Compilar y flashear

### Arduino IDE

1. Instala la librería **AccelStepper** (Herramientas → Administrar
   bibliotecas → busca "AccelStepper", de Mike McCauley).
2. Abre `firmware/PetFilamento/PetFilamento.ino`.
3. Placa: **Arduino Uno**.
4. Elige el puerto y sube el sketch (ver "Programación por USB" más abajo).
5. Abre el Monitor Serie a **115200** baudios.

### arduino-cli

```bash
arduino-cli lib install AccelStepper

arduino-cli compile --fqbn arduino:avr:uno firmware/PetFilamento
arduino-cli upload  --fqbn arduino:avr:uno -p /dev/ttyACM0 firmware/PetFilamento

# Monitor serie
arduino-cli monitor -p /dev/ttyACM0 -c baudrate=115200
```

En Linux el puerto suele ser `/dev/ttyACM0` en el Uno original y
`/dev/ttyUSB0` en clones con chip CH340. En Windows es `COMx`.

### Programación por USB

- **Uno original:** conmuta solo entre USB y fuente externa. Puedes conectar
  el USB con el adaptador de 12 V enchufado.
- **Clon:** puede no tener ese circuito de conmutación. **Apaga la máquina**
  (desenchufa el adaptador de 12 V) **antes de conectar el USB.**
- Desenchufa también la pistola mientras programas. Con la mejora opcional es
  obligatorio: durante la subida el tope de temperatura no funciona.

### Opciones de compilación

Están al inicio del `.ino`:

- `// #define USAR_TOPE_TEMPERATURA` (desactivada): activa la mejora opcional
  del tope de temperatura. **Actívala solo si el termistor y el relé están
  conectados.** Sin termistor, A1 queda al aire, el firmware lo toma como
  sensor dañado, entra en FALLA y no deja arrancar el motor.
- `#define DEBUG_SERIAL` (activa por defecto): imprime una línea de estado
  cada 500 ms.
- `// #define USAR_WATCHDOG` (desactivada): watchdog de 2 s. El Uno con
  Optiboot lo soporta, pero hay que probarlo en banco antes de activarlo.
  Algunos clones traen otro bootloader y pueden quedar en un bucle de
  reinicios tras un reset por watchdog.

Ejemplo de la línea de estado en la versión base:

```
rpm_obj=2.35 v=0.55m/min pot=520 driver=ON
```

Con la mejora opcional se agregan la temperatura, el estado del relé y la
falla:

```
rpm_obj=2.35 v=0.55m/min pot=520 T=187.4C rele=normal driver=ON falla=NO
```

## Constantes de calibración

Todas están agrupadas al inicio del `.ino`. Las marcadas **CALIBRAR** necesitan
una medición.

| Constante | Valor inicial | Qué medir |
|---|---|---|
| `VELOCIDAD_MIN_RPM_CARRETE` | 0.5 rpm | La velocidad más baja útil, buscada en la prueba de la tira |
| `VELOCIDAD_MAX_RPM_CARRETE` | 4.0 rpm | La velocidad más alta a la que la tira todavía forma filamento redondo sin romperse |
| `ACELERACION_PASOS_S2` | 100 pasos/s² | Subirla hasta que el motor pierda pasos al arrancar y luego dejarla en la mitad |
| `DIRECCION_INVERTIDA` | `false` | Si el tambor gira al revés, cambiar a `true` |

Las demás constantes son fijas o de la hoja de datos: `RELACION_REDUCCION`
(60, del reductor de tres etapas), `DIAMETRO_TAMBOR_MM` (74), `MICROPASOS`
(2, medio paso), `ZONA_MUERTA_ADC` (15) y el filtro EMA (alfa 0.1). Las
constantes del tope de temperatura están en la sección de la mejora opcional.

## Seguridad (versión base)

- **No quites el PTC ni el termostato de la pistola.** Son su protección. En la
  versión base, la pistola se usa como un aparato normal enchufado a la pared.
- **Fija bien la pistola en su soporte impreso** para que no se caiga ni se
  mueva al jalar la tira.
- **Ventila el lugar.** El PET caliente desprende vapores. Trabaja con ventana
  abierta o con extractor, y nunca quemes el plástico.
- **No dejes la máquina encendida sin supervisión.**
- La boquilla quema. Toca la tira solo con pinzas y desenchufa la pistola para
  cualquier ajuste mecánico.

## Mejora opcional: tope de temperatura

Agrega una segunda protección a la de la pistola: si la boquilla se pasa de
`TEMP_TOPE_C`, un relé corta la pistola. El Uno **nunca** enciende la pistola
ni regula su temperatura (no hay PID). Solo la corta si se pasa.

Para activarla:

1. Conecta el termistor y el relé (ver
   [docs/cableado.md](docs/cableado.md#5-mejora-opcional-tope-de-temperatura)).
2. Descomenta `#define USAR_TOPE_TEMPERATURA` en el `.ino`.
3. Sigue los pasos opcionales de [docs/puesta-en-marcha.md](docs/puesta-en-marcha.md).

### Componentes adicionales

| Cant. | Componente | Notas |
|---|---|---|
| 1 | Termistor NTC 100k, B 3950 | Pegado con Kapton a la boquilla |
| 1 | Resistencia de 4.7 kΩ | Divisor del termistor |
| 1 | Condensador cerámico de 100 nF | En paralelo al termistor |
| 1 | Módulo de relé de 5 V, 1 canal | Por COM y NC en la línea viva de la pistola |
| 1 | Caja cerrada para la parte de 110 V | Revisada por un profesor o electricista |

### Constantes de calibración de la mejora

| Constante | Valor inicial | Qué medir |
|---|---|---|
| `RELE_NIVEL_ACTIVO` | `LOW` | Con el multímetro, si el relé conmuta con IN en bajo o en alto |
| `R_PULLUP` | 4700 Ω | La resistencia real de 4.7k, medida con el multímetro antes de soldarla |
| `TEMP_OFFSET_C` | 0.0 °C | La diferencia entre la lectura por Serial y un termómetro de referencia |
| `TEMP_TOPE_C` | 230 °C | La temperatura máxima que alcanza la pistola sola, más un margen |

Fijas: `R0_TERMISTOR` (100 kΩ), `T0_TERMISTOR_C` (25 °C), `BETA_TERMISTOR`
(3950), `TEMP_HISTERESIS_C` (5 °C), `TIEMPO_MIN_REACTIVAR_MS` (10 s),
`TEMP_FALLA_C` (300 °C).

### Cómo funciona

- Se evalúa cada 250 ms.
- Si **T ≥ TEMP_TOPE_C**, el relé se activa de inmediato y la pistola queda
  cortada.
- Se suelta cuando **T ≤ TEMP_TOPE_C − TEMP_HISTERESIS_C** y han pasado al
  menos **TIEMPO_MIN_REACTIVAR_MS** desde el corte. El tiempo mínimo solo
  aplica a reactivar. El corte nunca espera.
- Si la lectura del termistor está fuera de rango (ADC > 1015 = abierto,
  ADC < 5 = corto), la pistola se corta enseguida. Si sigue así durante 3
  evaluaciones seguidas, o si T supera **TEMP_FALLA_C**, entra en **FALLA
  enclavada**: relé activo, motor frenado con rampa y deshabilitado, y un aviso
  por Serial cada 2 s. Solo sale reiniciando el Uno.

### Seguridad de la mejora

- **Por qué el relé va por NC.** La pistola funciona sola con su PTC. El
  Arduino es una protección adicional, no el control principal. Con el relé en
  reposo (NC cerrado), la pistola funciona como si el Arduino no existiera. El
  relé solo se activa para cortar, así que la bobina pasa la mayor parte del
  tiempo apagada. Además, un fallo del Arduino o del relé deja la pistola como
  una pistola normal, que se protege sola. La contrapartida es que **si el Uno
  se apaga o se cuelga, el tope deja de funcionar**, así que las protecciones
  propias de la pistola siguen siendo imprescindibles.
- **Los 110 V van en una caja cerrada**: relé, empalmes y cable de la pistola,
  con alivio de tensión en los cables y sin partes vivas al alcance. **Un
  profesor o un electricista debe revisar el cableado antes de enchufarlo por
  primera vez.**
- **El NTC pierde exactitud a 200 °C.** La ecuación Beta con un solo valor de B
  se aleja de la temperatura real a alta temperatura, y un NTC de 100k tiene
  muy poca resolución de ADC en esa zona. Además, el termistor mide la
  superficie de la boquilla, no el interior. Toma la temperatura mostrada como
  una referencia, no como un valor exacto.

## Limitaciones conocidas

- **La velocidad lineal sube al llenarse el tambor.** El motor gira a rpm
  constantes, pero el radio efectivo del tambor crece con cada vuelta, así que
  el filamento se jala cada vez más rápido y puede adelgazarse. Sigue sin
  compensarse: hay que ir bajando el potenciómetro a mano. La velocidad que
  muestra el Serial corresponde al tambor vacío.
- **Cada botella da un tramo corto.** Para formar un rollo hay que empalmar
  los tramos de varias botellas.
- **Puede que la pistola no llegue a la temperatura de formado de la tira.**
  Las pistolas de silicón están pensadas para unos 150–200 °C, y el PET suele
  necesitar más. Por eso la prueba de la tira (paso 4 de la puesta en marcha)
  es lo primero que hay que validar con la máquina.

## Roadmap

- **Tope de temperatura en hardware:** el firmware ya lo tiene (mejora
  opcional); falta montar el termistor, el relé y la caja de 110 V.
- **Caja impresa para la electrónica:** para guardar el Uno, el A4988 y el
  resto de módulos, con el potenciómetro accesible desde fuera.
- **Compensación del radio del tambor:** estimar el radio a partir de las
  vueltas dadas (o medirlo) y ajustar las rpm para mantener constante la
  velocidad lineal del filamento.
