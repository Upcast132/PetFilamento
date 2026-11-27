# Puesta en marcha

Hay dos partes:

- **Versión base (pasos 1 a 3):** solo el motor. La pistola se enchufa directo
  a la pared con su propio cable, sin modificar nada de 110 V.
- **Mejora opcional (pasos O1 a O3):** el tope de temperatura con termistor y
  relé. Solo hace falta si se monta esa mejora.

Anota cada valor medido y cópialo en las constantes del inicio de
`firmware/PetFilamento/PetFilamento.ino`. **Antes de la homologación de la
feria**, el firmware tiene que quedar calibrado y grabado: después no se
permiten cambios en el prototipo.

> **USB con el adaptador enchufado:** el Uno original conmuta solo entre USB
> y fuente externa, así que puedes ver el Serial con los 12 V conectados. En
> un clon, apaga la máquina antes de conectar el USB.

Material: multímetro, destornillador pequeño de cerámica o plástico, pinzas,
calibrador (pie de rey), balanza de cocina y cronómetro. Para la mejora
opcional, además, un termómetro de referencia.

---

## Versión base

### Paso 1 — Ajustar el Vref del A4988 (motor DESCONECTADO)

> **No conectes ni desconectes el motor con el driver alimentado.**

1. Con el motor desconectado, alimenta el A4988 (12 V en VMOT y 5 V en VDD).
2. Busca la **corriente nominal** del motor en su etiqueta o en su hoja de
   datos (por ejemplo, 1.5 A por fase). La meta es el **70 %** de esa
   corriente.
3. Lee la **resistencia de sensado (Rs)** del módulo: son las dos resistencias
   pequeñas junto al chip. Los códigos más comunes son `R100` = 0.1 Ω,
   `R068` = 0.068 Ω y `R050` = 0.05 Ω.
4. Calcula:

   ```
   Vref = corriente × 8 × Rs
   ```

   Ejemplo: motor de 1.5 A → 70 % = 1.05 A. Con Rs = 0.1 Ω:
   Vref = 1.05 × 8 × 0.1 = **0.84 V**. (Con Rs = 0.068 Ω serían 0.57 V.)
5. Mide con el multímetro entre el **potenciómetro del A4988** (o el pin Vref)
   y **GND**. Gíralo poco a poco con el destornillador de plástico hasta llegar
   al valor calculado.
6. Si el A4988 no lleva disipador, no pases de unos 1 A, aunque el motor admita
   más.
7. Apaga todo y entonces conecta el motor.

### Paso 2 — Motor en vacío y relación de reducción

1. Une el tambor a la rueda de 55 dientes con **8 tornillos M3
   autorroscantes**: pasan por los agujeros de Ø 4.56 de la rueda (`G54`) y
   muerden en el piloto de Ø 2.55 del tambor (`G55`). No hace falta repasar
   nada. Fija los rodamientos 608 en su soporte (`G46`, alojamiento de
   Ø 22.96); si quedan flojos, pégalos.
2. Con el reductor montado pero **sin tira ni pistola**, enciende con 12 V.
   Al arrancar, el Serial debe decir `Modo: solo motor (version base).` Con el
   potenciómetro al mínimo (zona muerta) debe salir `driver=OFF`, y el eje del
   motor debe quedar libre. Con el reductor 60:1 el tambor cuesta mucho de
   mover a mano: no lo fuerces.
3. Sube el potenciómetro poco a poco. Debe salir `driver=ON` y el motor debe
   acelerar suavemente. Al bajarlo de nuevo a la zona muerta, el motor frena
   con rampa y luego vuelve a `driver=OFF`.
4. Si gira al revés, cambia `DIRECCION_INVERTIDA`.
5. Si vibra, zumba sin girar o pierde pasos: revisa el par de cada bobina,
   sube un poco Vref o baja `ACELERACION_PASOS_S2`.
6. **Revisa que el piñón no patine ni baile en el eje de 5 mm del NEMA 17.**
   El agujero del piñón (`G51`) es en D, de Ø 5.96 mm con el plano a 5.39 mm:
   casi 1 mm más grande que el eje (Ø 5 mm, plano a 4.5 mm). Marca con un
   rotulador una línea que cruce el eje y el piñón, y haz girar el motor con el
   tambor frenado suavemente con la mano. Si la línea se desfasa, o el piñón
   tiene juego, **reimprímelo con el agujero en D de Ø 5.2 mm y el plano a
   4.7 mm**. Si queda demasiado justo, ajústalo con una broca de 5 mm.
7. Toca el disipador o el chip del A4988 tras unos minutos de uso. Debe estar
   tibio, no quemar.
8. **Comprueba la relación de reducción.** El firmware ya usa
   `RELACION_REDUCCION = 60` (8→32, 12→36 y 11→55: 4 × 3 × 5 = 60). Cuenta los
   dientes impresos para confirmarlo. Después marca el tambor con un
   rotulador: con el potenciómetro al máximo, el tambor debe dar
   `VELOCIDAD_MAX_RPM_CARRETE` vueltas en un minuto (4 con el valor por
   defecto). Si da otra cantidad, revisa la reducción o el puente MS1/MS2/MS3
   (medio paso: MS1 a 5 V, MS2 y MS3 a GND).
9. Con 60:1 y medio paso, el límite de 2000 pasos/s equivale a 5 rpm de
   tambor. Si pones `VELOCIDAD_MAX_RPM_CARRETE` por encima de 5, el firmware
   recorta la velocidad.

### Paso 3 — Prueba de la tira

Valida lo más incierto: si la pistola calienta lo suficiente para formar el
filamento.

1. **Con la pistola desenchufada y fría**, saca los restos de pegamento de la
   boquilla y del canal.
2. Comprueba que la boquilla esté perforada a **1.6 mm**. Si no lo está,
   perfórala con la broca de 1.6 mm, también con la pistola fría y
   desenchufada, y limpia la viruta. Después monta la pistola en su soporte
   impreso y revisa que quede firme.
3. Prepara una tira de botella de ancho parejo y córtale la punta en forma de
   **pico** para que entre por el agujero.
4. Enchufa la pistola directo a la pared, espera a que caliente y mete la
   punta por la boquilla.
5. Con **pinzas**, jala la punta lentamente con la mano (sin motor) y mira el
   resultado:
   - **Sale redondo, liso y del grosor esperado** → la temperatura sirve.
     Pasa la punta al tambor y prueba con el motor, empezando por la velocidad
     más baja.
   - **Sale plano, o la tira no pasa y se rompe** → falta temperatura. La
     pistola puede no ser suficiente (ver Limitaciones en el README).
   - **Sale oscuro, con burbujas o echa humo** → hay demasiada temperatura.
     Desenchufa y revisa.
6. Con el motor en marcha, busca la velocidad a la que el filamento sale
   uniforme y anótala para `VELOCIDAD_MIN_RPM_CARRETE` y
   `VELOCIDAD_MAX_RPM_CARRETE`. La línea de Serial muestra la velocidad
   lineal en m/min (con el tambor vacío).
7. Recuerda: al llenarse el tambor la velocidad lineal sube. Ve bajando el
   potenciómetro.
8. Cada botella da un tramo corto. Para formar un rollo hay que empalmar los
   tramos de varias botellas.

**Datos para el informe técnico.** Anótalos durante esta prueba; son la
evidencia de la sección de resultados:

| Dato | Cómo medirlo |
|---|---|
| Diámetro del filamento | Calibrador en 10 puntos de un tramo: promedio, mínimo y máximo |
| Ancho y grosor de la tira | Calibrador, antes de pasarla por la boquilla |
| Metros de filamento por botella | Medir el tramo que sale de una botella (anotar si es de 500 ml, 1.5 L o 2 L) |
| Gramos de filamento por botella | Pesar el tramo en la balanza |
| Velocidad óptima | rpm y m/min del Serial con los que sale mejor |
| Tiempo por botella | Cronómetro, desde que entra la punta hasta que se acaba la tira |

Ventila el lugar y no dejes la máquina sin supervisión en ningún momento.

---

## Mejora opcional: tope de temperatura

Solo si se monta el termistor y el relé. Antes de grabar el firmware,
descomenta `#define USAR_TOPE_TEMPERATURA` en el `.ino`. Al arrancar, el
Serial debe decir `Modo: motor + tope de temperatura (mejora opcional).`

> Si activas la opción sin el termistor conectado, el firmware entra en FALLA
> y no deja arrancar el motor. Es el comportamiento esperado.

Los pasos O1 y O2 se hacen **sin 110 V**: basta con alimentar el Uno por USB.

### Paso O1 — ¿El relé es activo en alto o en bajo?

Se hace con el módulo suelto, sin la pistola conectada a sus bornes.

1. Alimenta el módulo: VCC a 5 V y GND a GND (del Uno conectado por USB).
2. Pon el multímetro en **continuidad** entre los bornes **COM** y **NC**.
   Con el relé en reposo debe pitar (NC cerrado).
3. Con un cable, conecta **IN a GND**.
   - Si el relé hace "clic", se enciende su LED y COM–NC **deja de pitar**:
     el módulo es **activo en bajo** → `RELE_NIVEL_ACTIVO = LOW`.
4. Si no pasó nada, conecta **IN a 5 V**.
   - Si ahora hace "clic" y COM–NC deja de pitar: es **activo en alto** →
     `RELE_NIVEL_ACTIVO = HIGH`.
5. Comprueba también qué pasa con **IN al aire** (desconectado). Así está el
   pin mientras el Uno arranca. Lo normal en un módulo activo en bajo es que
   el relé quede en reposo, y con eso la pistola funciona normal.
6. Graba el firmware y verifica por Serial: al arrancar debe decir
   `rele=normal` y COM–NC debe seguir pitando. Si dice `normal` pero COM–NC
   está abierto, el nivel está al revés: corrige la constante.

> Si el módulo tiene un puente H/L, déjalo fijo y anota en qué posición quedó.

### Paso O2 — Comprobar el termistor

1. Conecta el divisor (4.7k + NTC + 100 nF) a A1 como indica
   [cableado.md](cableado.md#5-mejora-opcional-tope-de-temperatura).
2. Antes de soldarla, mide la resistencia de 4.7k con el multímetro y pon el
   valor real en `R_PULLUP`.
3. Abre el Monitor Serie a 115200. A temperatura ambiente, `T=` debe marcar
   algo cercano a la del cuarto.
   - Si aparece `T=--` y luego `FALLA: termistor abierto`, el termistor está
     desconectado o mal soldado.
   - Si aparece `FALLA: termistor en cortocircuito`, revisa que las patas no se
     toquen entre sí ni toquen la boquilla.
   - Para salir de una falla hay que reiniciar el Uno.
4. Compara con el termómetro de referencia en al menos dos puntos:
   - Temperatura ambiente.
   - Agua caliente o hirviendo, con el termistor y el termómetro juntos (mete
     el termistor en una funda o bolsita para que no se moje). Ojo: el agua
     hierve a menos de 100 °C en altura (por ejemplo, unos 90 °C a 2800 m), así
     que fíate del termómetro y no del "100 °C".
5. Si la diferencia es parecida en los dos puntos, ajusta `TEMP_OFFSET_C`
   (positivo si el Arduino marca menos que el termómetro). Si la diferencia
   crece mucho con la temperatura, revisa `R_PULLUP` y `BETA_TERMISTOR` antes
   de tocar el offset.

> La lectura pierde exactitud cerca de 200 °C (ver la mejora opcional en el
> README). Para el tope, deja margen.

### Paso O3 — Conectar los 110 V por el relé (solo después de la revisión)

> ⚠️ **No sigas sin que un profesor o un electricista haya revisado el
> cableado de 110 V y la caja cerrada.**

Lista para la revisión:

- [ ] El relé interrumpe la **fase**, por **COM y NC**. NO queda libre y aislado.
- [ ] Ningún borne ni empalme de 110 V queda expuesto; la caja está cerrada.
- [ ] Los cables tienen alivio de tensión: un tirón no los arranca.
- [ ] La pistola conserva su PTC y su termostato originales.
- [ ] El paso O1 confirmó `RELE_NIVEL_ACTIVO`.

Prueba del tope (con supervisión):

1. Cambia temporalmente `TEMP_TOPE_C` a un valor bajo, por ejemplo 80 °C, y
   graba el firmware.
2. Enchufa la pistola y mira el Serial. Al llegar a 80 °C debe salir
   `rele=CORTA` y la pistola debe dejar de calentar.
3. Al bajar de 75 °C, pasados al menos 10 s desde el corte, debe volver a
   `rele=normal`.
4. Desconecta el termistor con la pistola funcionando. El relé debe cortar al
   instante, y en menos de 1 s debe salir el mensaje de FALLA cada 2 s. Para
   salir, reinicia el Uno.
5. **Vuelve a poner `TEMP_TOPE_C` en su valor definitivo** y graba de nuevo.
6. Deja la pistola calentar sola unos 10 minutos y anota la temperatura máxima
   que alcanza. `TEMP_TOPE_C` debe quedar algo por encima de ese valor: si
   queda por debajo, el relé cortará en cada ciclo de trabajo normal.
