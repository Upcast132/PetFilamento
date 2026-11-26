# Puesta en marcha

Sigue los pasos en orden. **Del paso 1 al 4 se trabaja SIN 110 V**: la pistola
queda desenchufada todo ese tiempo. Para los pasos 1 y 2 basta con alimentar
el Uno por USB. El adaptador de 12 V hace falta desde el paso 3.

> **USB con el adaptador enchufado:** el Uno original conmuta solo entre USB
> y fuente externa, así que puedes ver el Serial con los 12 V conectados. En
> un clon, apaga la máquina antes de conectar el USB.

Anota cada valor medido y cópialo en las constantes del inicio de
`firmware/PetFilamento/PetFilamento.ino`.

Material: multímetro, termómetro de referencia (de cocina o un multímetro con
termopar), destornillador pequeño de cerámica o plástico y pinzas.

---

## Paso 1 — ¿El relé es activo en alto o en bajo?

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

## Paso 2 — Comprobar el termistor

1. Conecta el divisor (4.7k + NTC + 100 nF) a A1 como indica
   [cableado.md](cableado.md).
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

> La lectura pierde exactitud cerca de 200 °C (ver Limitaciones en el README).
> Para el tope, deja margen.

## Paso 3 — Ajustar el Vref del A4988 (motor DESCONECTADO)

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

## Paso 4 — Motor en vacío y relación de reducción

1. Con el reductor montado pero **sin tira ni pistola**, enciende con 12 V.
   Con el potenciómetro al mínimo (zona muerta), por Serial debe salir
   `driver=OFF`, y el motor debe quedar libre: se puede girar a mano.
2. Sube el potenciómetro poco a poco. Debe salir `driver=ON` y el motor debe
   acelerar suavemente. Al bajarlo de nuevo a la zona muerta, el motor frena
   con rampa y luego vuelve a `driver=OFF`.
3. Si gira al revés, cambia `DIRECCION_INVERTIDA`.
4. Si vibra, zumba sin girar o pierde pasos: revisa el par de cada bobina,
   sube un poco Vref o baja `ACELERACION_PASOS_S2`.
5. Toca el disipador o el chip del A4988 tras unos minutos de uso. Debe estar
   tibio, no quemar.
6. **Relación de reducción:** cuenta los dientes de cada engranaje.
   - Para cada etapa: dientes del engranaje conducido ÷ dientes del motriz.
   - `RELACION_REDUCCION` = producto de todas las etapas.
   - Ejemplo: piñón de 10 dientes → rueda de 40 (×4), y en el mismo eje piñón
     de 12 → rueda de 36 (×3). Relación = 4 × 3 = **12**.
   - Compruébalo marcando el carrete con un rotulador: con el potenciómetro al
     máximo, el carrete debe dar `VELOCIDAD_MAX_RPM_CARRETE` vueltas en un
     minuto.
7. Si con la relación real el motor llega al límite de 2000 pasos/s, el
   firmware recorta la velocidad. Baja `VELOCIDAD_MAX_RPM_CARRETE`.

## Paso 5 — Conectar los 110 V (solo después de la revisión)

> ⚠️ **No sigas sin que un profesor o un electricista haya revisado el
> cableado de 110 V y la caja cerrada.**

Lista para la revisión:

- [ ] El relé interrumpe la **fase**, por **COM y NC**. NO queda libre y aislado.
- [ ] Ningún borne ni empalme de 110 V queda expuesto; la caja está cerrada.
- [ ] Los cables tienen alivio de tensión: un tirón no los arranca.
- [ ] La pistola conserva su PTC y su termostato originales.
- [ ] El paso 1 confirmó `RELE_NIVEL_ACTIVO`.

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

## Paso 6 — Prueba de la tira

Valida lo más incierto: si la pistola calienta lo suficiente para formar el
filamento.

1. **Con la pistola desenchufada y fría**, saca los restos de pegamento de la
   boquilla y del canal.
2. Perfora la boquilla a **1.6 mm** con una broca, también con la pistola fría
   y desenchufada. Limpia la viruta.
3. Prepara una tira de botella de ancho parejo y córtale la punta en forma de
   **pico** para que entre por el agujero.
4. Enchufa la pistola, espera a que caliente y mete la punta por la boquilla.
5. Con **pinzas**, jala la punta lentamente con la mano (sin motor) y mira el
   resultado:
   - **Sale redondo, liso y del grosor esperado** → la temperatura sirve.
     Pasa la punta al carrete y prueba con el motor, empezando por la velocidad
     más baja.
   - **Sale plano, o la tira no pasa y se rompe** → falta temperatura. La
     pistola puede no ser suficiente (ver Limitaciones en el README).
   - **Sale oscuro, con burbujas o echa humo** → hay demasiada temperatura.
     Desenchufa y revisa.
6. Con el motor en marcha, busca la velocidad a la que el filamento sale
   uniforme y anótala para `VELOCIDAD_MIN_RPM_CARRETE` y
   `VELOCIDAD_MAX_RPM_CARRETE`. Mide el diámetro con un calibrador en varios
   puntos.
7. Recuerda: al llenarse el carrete la velocidad lineal sube. Ve bajando el
   potenciómetro.

Ventila el lugar y no dejes la máquina sin supervisión en ningún momento.
