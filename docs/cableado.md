# Cableado

Pines fijos. Si cambias alguno, también hay que cambiar el firmware.

**Regla general:** todas las tierras (GND del adaptador de 12 V, del Nano, del
A4988, del potenciómetro, del termistor y del relé) van unidas en un solo punto
común.

## 1. Alimentación

| Desde | Hacia | Notas |
|---|---|---|
| Adaptador +12 V | Nano VIN | El regulador del Nano genera los 5 V |
| Adaptador +12 V | A4988 VMOT | Potencia del motor |
| Adaptador GND | Nano GND y A4988 GND (de motor) | GND común |
| Condensador de 100 µF | Entre VMOT (+) y GND (−) | **Lo más cerca posible del A4988.** Respeta la polaridad. Protege el driver de picos de tensión |
| Nano 5V | A4988 VDD, potenciómetro, divisor del termistor, relé VCC | Lógica |

> El pin 5V del Nano, alimentado desde VIN, da poca corriente (el regulador se
> calienta con 12 V de entrada). La bobina del relé consume unos 70–80 mA, y
> eso entra dentro de lo razonable. No le cuelgues más cargas.

> **Nunca conectes ni desconectes el motor con el A4988 alimentado.** El driver
> se puede quemar.

## 2. Driver A4988 y motor

| Pin del A4988 | Conectar a |
|---|---|
| STEP | Nano D2 |
| DIR | Nano D3 |
| ENABLE | Nano D4 **y** resistencia de 10k a 5 V (pull-up) |
| MS1 | 5 V |
| MS2 | 5 V |
| MS3 | GND |
| RESET | Puenteado con SLEEP |
| SLEEP | Puenteado con RESET |
| VDD | 5 V del Nano |
| GND (lógica) | GND común |
| VMOT | +12 V, con 100 µF a GND |
| GND (motor) | GND común |
| 1A, 1B | Bobina A del NEMA 17 |
| 2A, 2B | Bobina B del NEMA 17 |

Con MS1 = H, MS2 = H y MS3 = L el A4988 trabaja en **1/8 de paso**: 200 × 8 =
1600 micropasos por vuelta del motor.

**Cómo identificar las bobinas:** con el multímetro en continuidad, los dos
cables que marcan continuidad entre sí son una bobina. Una bobina va a 1A/1B y
la otra a 2A/2B. Si el motor gira al revés, cambia `DIRECCION_INVERTIDA` en el
firmware. No hace falta recablear.

**ENABLE:** es activo en bajo. El pull-up de 10k lo mantiene deshabilitado
(HIGH) mientras el Nano arranca o se está programando, así que el motor no
recibe corriente hasta que el firmware lo habilita.

## 3. Potenciómetro B50K

```
5 V ──── extremo 1
          cursor ──── A0
GND ──── extremo 2
```

Si el giro del potenciómetro va "al revés" de lo que esperas, intercambia los
extremos.

## 4. Termistor NTC 100k (B 3950)

```
5 V ──[ 4.7 kΩ ]──┬──────────► A1
                  │
                  ├── NTC 100k ──┐
                  │              │
                  └── 100 nF ────┴──► GND
```

- El NTC va del nodo A1 a GND. La resistencia de 4.7k va del nodo A1 a 5 V.
- El condensador de 100 nF va en paralelo al termistor, lo más cerca posible
  del Nano, para filtrar ruido.
- **Montaje:** pega el termistor al metal de la boquilla con cinta Kapton (no
  con cinta común, que se derrite). Aísla sus patas con funda de alta
  temperatura (fibra de vidrio o teflón) para que no hagan corto con la
  boquilla metálica.
- Usa cable trenzado para el termistor y aléjalo de los cables del motor y de
  110 V.

Con estos valores, a temperatura ambiente el ADC lee cerca de 975–990, y a
unos 230 °C lee alrededor de 90. Por encima de 1015 el firmware lo toma como
termistor desconectado. Por debajo de 5, como cortocircuito.

## 5. Módulo de relé de 5 V (un canal)

### Lado de baja tensión

| Pin del módulo | Conectar a |
|---|---|
| VCC | 5 V del Nano |
| GND | GND común |
| IN | Nano D5 |

Si el módulo tiene un puente para elegir disparo en alto o en bajo (H/L),
anota en qué posición está y comprueba el nivel en el paso 1 de
[puesta-en-marcha.md](puesta-en-marcha.md).

### Lado de 110 V

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

## Diagrama general

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
```
