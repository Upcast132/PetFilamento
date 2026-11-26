# PetFilamento

Máquina escolar que convierte tiras de botellas PET en filamento de 1.75 mm
para impresión 3D. La tira se jala a través de la boquilla caliente de una
pistola de silicón. Un carrete, movido por un motor NEMA 17 con un reductor de
engranajes impreso, enrolla el filamento. La mecánica es la del **PetPull-2**
de Sapienz.

Un Arduino Nano hace dos cosas:

1. **Controla la velocidad del motor** según un potenciómetro.
2. **Es un tope de seguridad de temperatura**: si la boquilla se pasa de la
   temperatura límite, un relé corta la pistola. El Nano **no** controla el
   calentamiento normal. La pistola se calienta sola con su PTC.

> **Estado:** firmware **sin probar en hardware**. Compila para Arduino Nano
> (ATmega328P), pero todavía no se ha probado con la máquina real. Sigue
> [docs/puesta-en-marcha.md](docs/puesta-en-marcha.md) antes de usarla.

Licencia: por definir.

---

## Estructura

```
PetFilamento/
├── README.md
├── firmware/PetFilamento/PetFilamento.ino
└── docs/
    ├── cableado.md          # conexiones detalladas
    └── puesta-en-marcha.md  # pruebas y calibración paso a paso
```

## Componentes

| Cant. | Componente | Notas |
|---|---|---|
| 1 | Arduino Nano (ATmega328P) | Alimentado por VIN con 12 V |
| 1 | Adaptador de 12 V | Alimenta el Nano (VIN) y el motor (VMOT) |
| 1 | Driver A4988 | En 1/8 de paso (MS1 y MS2 en alto, MS3 en bajo) |
| 1 | Condensador electrolítico de 100 µF (≥ 25 V) | Entre VMOT y GND, junto al A4988 |
| 1 | Resistencia de 10 kΩ | Pull-up de ENABLE a 5 V |
| 1 | Motor NEMA 17 bipolar | 200 pasos por vuelta |
| 1 | Potenciómetro B50K | Lineal |
| 1 | Termistor NTC 100k, B 3950 | Pegado con Kapton a la boquilla |
| 1 | Resistencia de 4.7 kΩ | Divisor del termistor |
| 1 | Condensador cerámico de 100 nF | En paralelo al termistor |
| 1 | Módulo de relé de 5 V, 1 canal | Por COM y NC en la línea viva de la pistola |
| 1 | Pistola de silicón grande, nueva, de 110 V | Con su propio cable y su PTC |
| 1 | Caja cerrada para la parte de 110 V | Ver la sección Seguridad |
| — | Piezas impresas del PetPull-2 | Carrete, reductor y soportes |

## Pines

| Pin del Nano | Conectado a | Función |
|---|---|---|
| D2 | A4988 STEP | Pulsos de paso |
| D3 | A4988 DIR | Dirección (la maneja AccelStepper) |
| D4 | A4988 ENABLE | Activo en bajo, pull-up de 10k a 5 V (arranca deshabilitado) |
| D5 | Relé IN | Relé activado = pistola cortada |
| A0 | Cursor del potenciómetro | Velocidad |
| A1 | Divisor del termistor | Temperatura de la boquilla |
| 5V | A4988 VDD, potenciómetro, divisor, relé VCC | Lógica |
| VIN | +12 V del adaptador | Alimentación del Nano |
| GND | GND común | Todas las tierras unidas |

## Diagrama de cableado

Detalle completo en [docs/cableado.md](docs/cableado.md).

```
                 +12 V (adaptador) ─────────┬──────────────────────┐
                                            │                      │
                                         [100 µF]                  │
                                            │                      │
  ┌──────────── ARDUINO NANO ───────┐    ┌──┴─────── A4988 ─────┐  │
  │ VIN ◄──── +12 V ────────────────┼────┼──────────────────────┼──┘
  │ GND ─────── GND común ──────────┼────┤ GND (lógica y motor) │
  │                                 │    │ VMOT ◄── +12 V       │
  │ 5V ──┬──────────────────────────┼────┤ VDD                  │
  │      │      ┌─[10k]─────────────┼────┤ ENABLE               │
  │ D4 ──┼──────┴───────────────────┼────┘                      │
  │ D2 ──┼──────────────────────────┼────► STEP          1A/1B ─┼──► bobina A ┐
  │ D3 ──┼──────────────────────────┼────► DIR           2A/2B ─┼──► bobina B ┤ NEMA 17
  │      │                          │      MS1, MS2 ── 5 V      │             ┘
  │      │                          │      MS3 ─────── GND      │
  │      │                          │      RESET ── SLEEP       │
  │      │                          │    └──────────────────────┘
  │      │   POTENCIÓMETRO B50K     │
  │      ├──── extremo 1            │
  │ A0 ◄─┼──── cursor               │
  │ GND ─┼──── extremo 2            │
  │      │                          │
  │      │   TERMISTOR NTC 100k     │
  │      ├──[4.7k]──┬───────────────┼─► A1
  │      │          ├── NTC ──┐     │
  │      │          └─[100nF]─┴─────┼── GND
  │      │                          │
  │      │   MÓDULO DE RELÉ 5 V     │
  │      ├──── VCC                  │
  │ D5 ──┼───► IN                   │
  │ GND ─┴──── GND                  │
  └─────────────────────────────────┘

  LADO DE 110 V (dentro de caja cerrada):

  Enchufe ── FASE ───► COM ─┐ relé    ┌─ NC ───► FASE de la pistola
                            └─────────┘
  Enchufe ── NEUTRO ─────────────────────────► NEUTRO de la pistola
  (NO usar el contacto NO)
```

## Compilar y flashear

### Arduino IDE

1. Instala la librería **AccelStepper** (Herramientas → Administrar
   bibliotecas → busca "AccelStepper", de Mike McCauley).
2. Abre `firmware/PetFilamento/PetFilamento.ino`.
3. Placa: **Arduino Nano**. Procesador: **ATmega328P (Old Bootloader)**. Si
   falla la subida, prueba con **ATmega328P** (bootloader nuevo).
4. Elige el puerto y sube el sketch.
5. Abre el Monitor Serie a **115200** baudios.

### arduino-cli

```bash
arduino-cli lib install AccelStepper

# Bootloader viejo (la mayoría de los clones):
arduino-cli compile --fqbn arduino:avr:nano:cpu=atmega328old firmware/PetFilamento
arduino-cli upload  --fqbn arduino:avr:nano:cpu=atmega328old -p /dev/ttyUSB0 firmware/PetFilamento

# Bootloader nuevo: usa cpu=atmega328
arduino-cli compile --fqbn arduino:avr:nano:cpu=atmega328 firmware/PetFilamento

# Monitor serie
arduino-cli monitor -p /dev/ttyUSB0 -c baudrate=115200
```

El puerto puede ser `/dev/ttyUSB0` o `/dev/ttyACM0` en Linux y `COMx` en
Windows.

### Opciones de compilación

Están al inicio del `.ino`:

- `#define DEBUG_SERIAL` (activa por defecto): imprime una línea de estado
  cada 500 ms. Los mensajes de falla se envían siempre.
- `// #define USAR_WATCHDOG` (desactivada): watchdog de 2 s. Está desactivado
  porque, con el bootloader viejo, un reinicio por watchdog puede dejar el
  Nano en un bucle de reinicios.

Ejemplo de la línea de estado:

```
rpm_obj=2.35 pot=520 T=187.4C rele=normal driver=ON falla=NO
```

## Constantes de calibración

Todas están agrupadas al inicio del `.ino`. Las marcadas **CALIBRAR** necesitan
una medición.

| Constante | Valor inicial | Qué medir |
|---|---|---|
| `RELE_NIVEL_ACTIVO` | `LOW` | Con el multímetro, si el relé conmuta con IN en bajo o en alto (paso 1 de la puesta en marcha) |
| `R_PULLUP` | 4700 Ω | La resistencia real de 4.7k, medida con el multímetro antes de soldarla |
| `TEMP_OFFSET_C` | 0.0 °C | La diferencia entre la lectura por Serial y un termómetro de referencia |
| `TEMP_TOPE_C` | 230 °C | La temperatura máxima que alcanza la pistola sola, más un margen. El tope debe quedar por encima de la temperatura de trabajo y por debajo de lo que daña el plástico o la boquilla |
| `RELACION_REDUCCION` | 1.0 | Los dientes de cada engranaje del reductor: producto de (conducido / motriz) de cada etapa |
| `VELOCIDAD_MIN_RPM_CARRETE` | 0.5 rpm | La velocidad más baja útil, buscada en la prueba de la tira |
| `VELOCIDAD_MAX_RPM_CARRETE` | 4.0 rpm | La velocidad más alta a la que la tira todavía forma filamento redondo sin romperse |
| `ACELERACION_PASOS_S2` | 100 pasos/s² | Subirla hasta que el motor pierda pasos al arrancar y luego dejarla en la mitad |
| `DIRECCION_INVERTIDA` | `false` | Si el carrete gira al revés, cambiar a `true` |

Las demás constantes son fijas o de la hoja de datos. Puedes ajustarlas si
cambias el hardware: `R0_TERMISTOR` (100 kΩ), `T0_TERMISTOR_C` (25 °C),
`BETA_TERMISTOR` (3950), `TEMP_HISTERESIS_C` (5 °C),
`TIEMPO_MIN_REACTIVAR_MS` (10 s), `TEMP_FALLA_C` (300 °C), `ZONA_MUERTA_ADC`
(15) y los filtros EMA (alfa 0.1).

## Cómo funciona el tope de temperatura

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
  por Serial cada 2 s. Solo sale reiniciando el Nano.

## Seguridad

- **Por qué el relé va por NC.** La pistola es un aparato que funciona solo
  con su PTC. El Arduino es una protección adicional, no el control principal.
  Con el relé en reposo (NC cerrado), la pistola funciona como si el Arduino no
  existiera. El relé solo se activa para cortar. Así, la bobina pasa la mayor
  parte del tiempo apagada y no se calienta. Además, un fallo del Arduino o del
  relé deja la pistola como una pistola normal, que se protege sola. La
  contrapartida es que **si el Nano se apaga o se cuelga, el tope deja de
  funcionar**. Por eso las protecciones propias de la pistola son
  imprescindibles.
- **No quites el PTC ni el termostato de la pistola.** Son la protección
  principal. Este proyecto no los reemplaza.
- **Los 110 V van en una caja cerrada**: relé, empalmes y cable de la pistola,
  con alivio de tensión en los cables y sin partes vivas al alcance. **Un
  profesor o un electricista debe revisar el cableado antes de enchufarlo por
  primera vez.**
- **Ventila el lugar.** El PET caliente desprende vapores. Trabaja con ventana
  abierta o con extractor, y nunca quemes el plástico.
- **No dejes la máquina encendida sin supervisión.**
- La boquilla quema. Toca la tira solo con pinzas y desenchufa la pistola para
  cualquier ajuste mecánico.

## Limitaciones conocidas

- **La velocidad lineal sube al llenarse el carrete.** El motor gira a rpm
  constantes, pero el radio del carrete crece con cada vuelta, así que el
  filamento se jala cada vez más rápido y puede adelgazarse. La v1 no lo
  compensa: hay que ir bajando el potenciómetro a mano.
- **El NTC pierde exactitud a 200 °C.** La ecuación Beta con un solo valor de B
  se aleja de la temperatura real a alta temperatura, y un NTC de 100k tiene
  muy poca resolución de ADC en esa zona. Además, el termistor mide la
  superficie de la boquilla, no el interior. Toma la temperatura mostrada como
  una referencia, no como un valor exacto.
- **Puede que la pistola no llegue a la temperatura de formado de la tira.**
  Las pistolas de silicón están pensadas para unos 150–200 °C, y el PET suele
  necesitar más. Por eso la prueba de la tira (paso 6) es lo primero que hay
  que validar con la máquina.

## Roadmap

- **Compensación del radio del carrete**: estimar el radio a partir de las
  vueltas dadas (o medirlo) y ajustar las rpm para mantener constante la
  velocidad lineal del filamento.

## Créditos

- **PetPull-2**, de Sapienz: [Thingiverse 4900782](https://www.thingiverse.com/thing:4900782).
  Mecánica base (carrete y reductor).
- **PETamentor2**, de Tofna1: [Thingiverse 5888962](https://www.thingiverse.com/thing:5888962).
  Referencia.

> Verificar la licencia de cada uno antes de publicar piezas derivadas.
