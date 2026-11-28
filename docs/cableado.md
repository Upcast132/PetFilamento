# Cableado

Pines fijos. Si cambias alguno, también hay que cambiar el firmware.

- **Versión base:** secciones 1 a 4 (alimentación, driver y motor,
  potenciómetro y pistola). Es lo que usa el firmware por defecto.
- **Mejora opcional:** sección 5 (termistor y relé del tope de temperatura).
  Solo si se activa `USAR_TOPE_TEMPERATURA` en el firmware.

**Regla general:** todas las tierras (GND de la salida del buck, del Uno, del
A4988, del potenciómetro y, con la mejora, del termistor y del relé) van unidas
en un solo punto común.

## 1. Alimentación

La máquina se alimenta con un **cargador de laptop** (≈ 19 V, ~3 A) y un
**módulo buck LM2596** que baja esa tensión a **12.0 V**. Los dos van en la
sección B de la caja, y el cable sobrante del cargador se enrolla en su carrete.
El buck **no está aislado**: IN− y OUT− son el mismo punto.

### 1.1 Del cargador al buck

| Desde | Hacia | Notas |
|---|---|---|
| Cargador + | Fusible de 3 A en línea → buck IN+ | El fusible va en el positivo, cerca del cargador |
| Cargador − | Buck IN− | |

- Corta el conector del cable y pela los hilos. **Identifica + y − con el
  multímetro antes de empalmar** y marca cada hilo. Aísla los empalmes con
  termorretráctil.
- Si el cargador es de un equipo que sigues usando, no lo cortes: usa uno
  dedicado a la máquina.

### 1.2 Del buck a la electrónica

| Desde | Hacia | Notas |
|---|---|---|
| Buck OUT+ (12.0 V) | Pin VIN del Uno | El Uno acepta de 7 a 12 V; su regulador genera los 5 V. No uses el jack: queda dentro de la caja |
| Buck OUT+ (12.0 V) | A4988 VMOT | Potencia del motor |
| Buck OUT− | Uno GND y A4988 GND (de motor) | GND común |
| Condensador de 100 µF | Entre VMOT (+) y GND (−) | **Lo más cerca posible del A4988.** Respeta la polaridad. Protege el driver de picos de tensión |
| Uno 5V | A4988 VDD y potenciómetro (con la mejora: divisor del termistor y relé VCC) | Lógica |

> **Ajusta el buck a 12.0 V ANTES de conectar el Uno y el A4988** (paso 0 de
> [puesta-en-marcha.md](puesta-en-marcha.md)). Con la salida sin conectar, mide
> con el multímetro y gira el trimmer del módulo hasta leer 12.0 V.

> **VMOT se toma directo de la salida del buck**, con un cable en Y o una
> bornera. No lo saques del pin VIN del Uno: las pistas y el regulador de la
> placa no están pensados para la corriente del motor. Además, por VIN no pasa
> el diodo de protección del jack: **comprueba la polaridad** antes de conectar.

> **Si el buck falla en corto**, su salida puede subir a la tensión del cargador
> (≈ 19 V). Eso queda en el límite del Uno por VIN (máximo 20 V; se recomiendan
> 7 a 12 V) y por debajo del máximo de VMOT del A4988 (35 V). El fusible
> protege contra cortocircuitos, no contra esta falla. Mide la salida con el
> multímetro al armar y después de cualquier cambio en el cableado.

> Con 12 V de entrada, el regulador del Uno se calienta si se le pide mucha
> corriente por el pin 5V. En la versión base solo alimenta la lógica. Con la
> mejora, la bobina del relé suma unos 70–80 mA, y eso entra dentro de lo
> razonable. No le cuelgues más cargas.

> **Programación por USB:** el Uno original conmuta solo entre USB y fuente
> externa. En un clon, apaga la máquina antes de conectar el USB.

> **Nunca conectes ni desconectes el motor con el A4988 alimentado.** El driver
> se puede quemar.

## 2. Driver A4988 y motor

| Pin del A4988 | Conectar a |
|---|---|
| STEP | Uno D2 |
| DIR | Uno D3 |
| ENABLE | Uno D4 **y** resistencia de 10k a 5 V (pull-up) |
| MS1 | 5 V |
| MS2 | GND |
| MS3 | GND |
| RESET | Puenteado con SLEEP |
| SLEEP | Puenteado con RESET |
| VDD | 5 V del Uno |
| GND (lógica) | GND común |
| VMOT | +12 V, con 100 µF a GND |
| GND (motor) | GND común |
| 1A, 1B | Bobina A del NEMA 17 |
| 2A, 2B | Bobina B del NEMA 17 |

Con MS1 = H, MS2 = L y MS3 = L el A4988 trabaja en **medio paso**: 200 × 2 =
400 micropasos por vuelta del motor. Con el reductor 60:1, una vuelta del
tambor son 400 × 60 = 24 000 pasos.

**Cómo identificar las bobinas:** con el multímetro en continuidad, los dos
cables que marcan continuidad entre sí son una bobina. Una bobina va a 1A/1B y
la otra a 2A/2B. Si el motor gira al revés, cambia `DIRECCION_INVERTIDA` en el
firmware. No hace falta recablear.

**ENABLE:** es activo en bajo. El pull-up de 10k lo mantiene deshabilitado
(HIGH) mientras el Uno arranca o se está programando, así que el motor no
recibe corriente hasta que el firmware lo habilita.

## 3. Potenciómetro B50K

```
5 V ──── extremo 1
          cursor ──── A0
GND ──── extremo 2
```

Si el giro del potenciómetro va "al revés" de lo que esperas, intercambia los
extremos.

## 4. Pistola de silicón (versión base)

La pistola se enchufa **directo a la pared con su propio cable**. No se corta
ni se modifica nada de 110 V. Se calienta sola con su PTC, como cualquier
pistola de silicón, y va fija en su soporte impreso.

## 5. Mejora opcional: tope de temperatura

Solo con `#define USAR_TOPE_TEMPERATURA` activado en el firmware. Si activas
la opción sin conectar el termistor, el firmware entra en FALLA y no deja
arrancar el motor.

### 5.1 Termistor NTC 100k (B 3950)

```
5 V ──[ 4.7 kΩ ]──┬──────────► A1
                  │
                  ├── NTC 100k ──┐
                  │              │
                  └── 100 nF ────┴──► GND
```

- El NTC va del nodo A1 a GND. La resistencia de 4.7k va del nodo A1 a 5 V.
- El condensador de 100 nF va en paralelo al termistor, lo más cerca posible
  del Uno, para filtrar ruido.
- **Montaje:** pega el termistor al metal de la boquilla con cinta Kapton (no
  con cinta común, que se derrite). Aísla sus patas con funda de alta
  temperatura (fibra de vidrio o teflón) para que no hagan corto con la
  boquilla metálica.
- Usa cable trenzado para el termistor y aléjalo de los cables del motor y de
  110 V.

Con estos valores, a temperatura ambiente el ADC lee cerca de 975–990, y a
unos 230 °C lee alrededor de 90. Por encima de 1015 el firmware lo toma como
termistor desconectado. Por debajo de 5, como cortocircuito.

### 5.2 Módulo de relé de 5 V (un canal): lado de baja tensión

| Pin del módulo | Conectar a |
|---|---|
| VCC | 5 V del Uno |
| GND | GND común |
| IN | Uno D5 |

Si el módulo tiene un puente para elegir disparo en alto o en bajo (H/L),
anota en qué posición está y comprueba el nivel en el paso O1 de
[puesta-en-marcha.md](puesta-en-marcha.md).

### 5.3 Módulo de relé: lado de 110 V

> ⚠️ **Esta parte la monta o la revisa un profesor o un electricista.** Todo
> va dentro de una caja cerrada, con prensaestopas o alivio de tensión en los
> cables.

```
Enchufe (pared)                                   Pistola de silicón
─────────────────                                 ──────────────────
FASE ───────────► COM ┐                ┌ NC ───────► FASE
                      └──── RELÉ ──────┘
                      (NO queda SIN conectar)
NEUTRO ──────────────────────────────────────────► NEUTRO
TIERRA (si hay) ─────────────────────────────────► TIERRA (si hay)
```

- El relé interrumpe solo la **fase** (el vivo). El neutro pasa directo.
- Se usan **COM y NC**. El terminal **NO** queda libre y aislado.
- Relé en reposo → NC cerrado → la pistola funciona normal con su PTC.
- Relé activado → NC abierto → pistola cortada.
- Revisa que los contactos del relé estén especificados para 110–125 V AC y al
  menos 10 A. Una pistola grande consume poca corriente (≈ 1 A o menos), así
  que con eso sobra margen.
- Para identificar la fase usa un probador de tensión. Si el enchufe no está
  polarizado y no se puede asegurar cuál es la fase, coméntalo con quien
  revise la instalación.

## Diagrama completo (con la mejora opcional)

El diagrama de la versión base, sin termistor ni relé, está en el README.

```
                 +12 V (buck) ──────────────┬──────────────────────┐
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
```
