/*
 * PetFilamento.ino
 * ---------------------------------------------------------------------------
 * Firmware para la máquina que convierte tiras de botellas PET en filamento
 * de 1.75 mm (mecánica PetPull-2 de Sapienz, Thingiverse 4900782).
 *
 * El Arduino Nano hace SOLO dos cosas:
 *   1. Controla la velocidad del motor NEMA 17 (A4988) según un potenciómetro.
 *   2. Actúa como TOPE de seguridad de temperatura: si la boquilla se pasa de
 *      TEMP_TOPE_C, activa el relé y corta la pistola de silicón.
 *
 * El calentamiento normal lo hace la propia pistola con su PTC. Este firmware
 * NUNCA enciende la pistola ni regula su temperatura (no hay PID). El relé va
 * por el contacto NC: relé desactivado = pistola normal; relé activado =
 * pistola cortada.
 *
 * Estado: SIN PROBAR EN HARDWARE.
 *
 * Placa: Arduino Nano (ATmega328P). Librería: AccelStepper.
 * Sin delay() en todo el código.
 * ---------------------------------------------------------------------------
 */

#include <AccelStepper.h>
#include <math.h>

// ===========================================================================
// OPCIONES DE COMPILACIÓN
// ===========================================================================

// Línea de estado por Serial cada 500 ms. Comentar para desactivarla.
// (Los mensajes de FALLA se envían siempre, con o sin esta opción.)
#define DEBUG_SERIAL

// Watchdog de 2 s. Desactivado por defecto: los Nano con el bootloader viejo
// (ATmega328P "Old Bootloader") pueden quedar en un bucle de reinicios tras un
// reset por watchdog. Actívalo solo si sabes que tu bootloader lo soporta.
// #define USAR_WATCHDOG

#ifdef USAR_WATCHDOG
#include <avr/wdt.h>
#endif

// ===========================================================================
// CONSTANTES DE CALIBRACIÓN
// Las marcadas con CALIBRAR necesitan una medición antes de usar la máquina.
// Ver docs/puesta-en-marcha.md.
// ===========================================================================

// --- Motor y mecánica -------------------------------------------------------

// CALIBRAR: vueltas del MOTOR por cada vuelta del CARRETE. Se obtiene contando
// los dientes del reductor: producto de (dientes conducido / dientes motriz)
// de cada etapa. 1.0 es un valor provisional.
const float RELACION_REDUCCION = 1.0;

// CALIBRAR: velocidad del carrete con el potenciómetro justo encima de la
// zona muerta y al máximo, en rpm del CARRETE. Valores conservadores.
const float VELOCIDAD_MIN_RPM_CARRETE = 0.5;
const float VELOCIDAD_MAX_RPM_CARRETE = 4.0;

// CALIBRAR: aceleración de la rampa propia, en pasos/s² (de micropaso).
const float ACELERACION_PASOS_S2 = 100.0;

// CALIBRAR: invierte el sentido de giro si el carrete enrolla al revés.
const bool DIRECCION_INVERTIDA = false;

// Datos fijos del motor y del driver (no requieren calibración).
const int PASOS_POR_VUELTA_MOTOR = 200;  // NEMA 17, 1.8° por paso
const int MICROPASOS = 8;                // MS1=H, MS2=H, MS3=L -> 1/8 de paso

// Límite superior fijo para AccelStepper. Se pasa a setMaxSpeed() UNA sola
// vez en setup(); setSpeed() recorta cualquier valor por encima de este.
const float VELOCIDAD_MAX_PASOS_S = 2000.0;

// Por debajo de este valor del ADC filtrado del potenciómetro, motor parado.
const int ZONA_MUERTA_ADC = 15;

// Filtro EMA del potenciómetro (0 < alfa <= 1; más bajo = más suave).
const float ALFA_EMA_POT = 0.1;

// --- Termistor --------------------------------------------------------------

// CALIBRAR: valor real de la resistencia de 4.7k del divisor (medirla con el
// multímetro y poner aquí lo que marque, en ohmios).
const float R_PULLUP = 4700.0;

// Datos nominales del NTC 100k B3950 (de la hoja de datos).
const float R0_TERMISTOR = 100000.0;  // resistencia a T0, en ohmios
const float T0_TERMISTOR_C = 25.0;    // temperatura de referencia, en °C
const float BETA_TERMISTOR = 3950.0;  // coeficiente Beta, en kelvin

// CALIBRAR: corrección que se suma a la temperatura calculada, en °C.
// Se ajusta comparando con un termómetro de referencia.
const float TEMP_OFFSET_C = 0.0;

// Filtro EMA del termistor.
const float ALFA_EMA_TERMISTOR = 0.1;

// --- Tope de temperatura ----------------------------------------------------

// CALIBRAR: temperatura a la que el relé corta la pistola, en °C. Debe estar
// por encima de la temperatura de trabajo que alcanza la pistola sola.
const float TEMP_TOPE_C = 230.0;

// El relé se suelta cuando T <= TEMP_TOPE_C - TEMP_HISTERESIS_C.
const float TEMP_HISTERESIS_C = 5.0;

// Tiempo mínimo entre un corte y la reactivación de la pistola. Solo aplica
// a REACTIVAR; el corte siempre es inmediato.
const unsigned long TIEMPO_MIN_REACTIVAR_MS = 10000UL;

// Por encima de esta temperatura se asume sensor dañado o falla grave:
// FALLA enclavada.
const float TEMP_FALLA_C = 300.0;

// Límites del ADC filtrado del termistor. Fuera de ellos la lectura no es
// válida: > ADC_ABIERTO = termistor desconectado; < ADC_CORTO = cortocircuito.
const float ADC_ABIERTO = 1015.0;
const float ADC_CORTO = 5.0;

// Evaluaciones seguidas con lectura fuera de rango para entrar en FALLA.
const uint8_t EVALUACIONES_FALLA_SENSOR = 3;

// --- Relé -------------------------------------------------------------------

// CALIBRAR: nivel de la señal que ACTIVA el relé (= corta la pistola).
// La mayoría de módulos de 5 V son activos en bajo, por eso LOW por defecto.
// Comprobarlo con el multímetro (paso 1 de docs/puesta-en-marcha.md).
const uint8_t RELE_NIVEL_ACTIVO = LOW;
const uint8_t RELE_NIVEL_INACTIVO = (RELE_NIVEL_ACTIVO == LOW) ? HIGH : LOW;

// --- Tiempos del lazo -------------------------------------------------------

const unsigned long PERIODO_LECTURA_ADC_MS = 25;    // pot y termistor
const unsigned long PERIODO_RAMPA_MS = 10;          // rampa de velocidad
const unsigned long PERIODO_TEMPERATURA_MS = 250;   // evaluación del tope
const unsigned long PERIODO_SERIAL_MS = 500;        // línea de estado
const unsigned long PERIODO_MENSAJE_FALLA_MS = 2000;

// ===========================================================================
// PINES (fijos por hardware, no cambiar)
// ===========================================================================

const uint8_t PIN_STEP = 2;    // A4988 STEP
const uint8_t PIN_DIR = 3;     // A4988 DIR (lo maneja AccelStepper)
const uint8_t PIN_ENABLE = 4;  // A4988 ENABLE, activo en bajo, pull-up 10k
const uint8_t PIN_RELE = 5;    // señal del módulo de relé
const uint8_t PIN_POT = A0;    // cursor del potenciómetro B50K
const uint8_t PIN_NTC = A1;    // divisor del termistor

// ===========================================================================
// ESTADO
// ===========================================================================

AccelStepper motor(AccelStepper::DRIVER, PIN_STEP, PIN_DIR);

// Lecturas filtradas
float adcPotFiltrado = 0.0;
float adcNtcFiltrado = 0.0;
uint8_t ultimoCanalAdc = 0xFF;  // para descartar la 1.ª lectura al cambiar

// Motor
float rpmCarreteObjetivo = 0.0;
float velocidadObjetivoPasosS = 0.0;
float velocidadActualPasosS = 0.0;
bool driverHabilitado = false;

// Temperatura y relé
float temperaturaC = NAN;
bool lecturaTermistorValida = false;
bool releActivo = false;           // true = pistola cortada
unsigned long instanteCorteMs = 0;
uint8_t contadorLecturasInvalidas = 0;

// Falla enclavada
bool enFalla = false;
const char *motivoFalla = "";

// Temporizadores
unsigned long ultimoAdcMs = 0;
unsigned long ultimaRampaMs = 0;
unsigned long ultimaTemperaturaMs = 0;
unsigned long ultimoSerialMs = 0;
unsigned long ultimoMensajeFallaMs = 0;

// ===========================================================================
// ADC
// ===========================================================================

// Lee un canal analógico. Si el canal es distinto del anterior, descarta la
// primera conversión: el condensador de muestreo del ADC aún guarda la
// tensión del otro canal y esa lectura sale contaminada.
int leerAdc(uint8_t pin) {
  if (pin != ultimoCanalAdc) {
    analogRead(pin);  // lectura descartada
    ultimoCanalAdc = pin;
  }
  return analogRead(pin);
}

void actualizarLecturas() {
  adcPotFiltrado += ALFA_EMA_POT * ((float)leerAdc(PIN_POT) - adcPotFiltrado);
  adcNtcFiltrado += ALFA_EMA_TERMISTOR * ((float)leerAdc(PIN_NTC) - adcNtcFiltrado);
}

// ===========================================================================
// MOTOR
// ===========================================================================

// Convierte rpm del carrete a pasos (de micropaso) por segundo:
//
//   pasos/s = rpm_carrete x RELACION_REDUCCION x 200 x 8 / 60
//
//   - rpm_carrete x RELACION_REDUCCION = rpm del eje del motor.
//   - x 200: pasos completos por vuelta del NEMA 17.
//   - x 8:   micropasos por paso completo (A4988 en 1/8).
//   - / 60:  de "por minuto" a "por segundo".
//
// Ejemplo: 4 rpm de carrete con reducción 1.0 -> 4 x 1 x 1600 / 60 = 106.7 pasos/s.
float rpmCarreteAPasosS(float rpmCarrete) {
  return rpmCarrete * RELACION_REDUCCION * PASOS_POR_VUELTA_MOTOR * MICROPASOS / 60.0;
}

// Calcula la velocidad objetivo a partir del potenciómetro.
void calcularVelocidadObjetivo() {
  if (enFalla || adcPotFiltrado < ZONA_MUERTA_ADC) {
    rpmCarreteObjetivo = 0.0;
  } else {
    // Mapeo lineal en float desde el borde de la zona muerta hasta 1023.
    float fraccion = (adcPotFiltrado - ZONA_MUERTA_ADC) / (1023.0 - ZONA_MUERTA_ADC);
    if (fraccion > 1.0) fraccion = 1.0;
    rpmCarreteObjetivo = VELOCIDAD_MIN_RPM_CARRETE +
                         fraccion * (VELOCIDAD_MAX_RPM_CARRETE - VELOCIDAD_MIN_RPM_CARRETE);
  }

  velocidadObjetivoPasosS = rpmCarreteAPasosS(rpmCarreteObjetivo);
  if (velocidadObjetivoPasosS > VELOCIDAD_MAX_PASOS_S) {
    velocidadObjetivoPasosS = VELOCIDAD_MAX_PASOS_S;
  }
}

// Rampa propia: acerca la velocidad actual a la objetivo sin pasarla.
void actualizarRampa(unsigned long dtMs) {
  float maxCambio = ACELERACION_PASOS_S2 * (dtMs / 1000.0);
  float diferencia = velocidadObjetivoPasosS - velocidadActualPasosS;

  if (diferencia > maxCambio) {
    velocidadActualPasosS += maxCambio;
  } else if (diferencia < -maxCambio) {
    velocidadActualPasosS -= maxCambio;
  } else {
    velocidadActualPasosS = velocidadObjetivoPasosS;  // llega exacto, sin pasarse
  }

  motor.setSpeed(velocidadActualPasosS);
}

// ENABLE del A4988 (activo en bajo):
//   - LOW solo cuando hay velocidad objetivo mayor que cero.
//   - HIGH de nuevo cuando la rampa terminó de bajar a cero.
void actualizarEnable() {
  if (velocidadObjetivoPasosS > 0.0) {
    if (!driverHabilitado) {
      digitalWrite(PIN_ENABLE, LOW);
      driverHabilitado = true;
    }
  } else if (velocidadActualPasosS <= 0.0) {
    if (driverHabilitado) {
      digitalWrite(PIN_ENABLE, HIGH);
      driverHabilitado = false;
    }
  }
}

// ===========================================================================
// TEMPERATURA Y RELÉ
// ===========================================================================

// Ecuación Beta:
//   R_termistor = R_PULLUP x ADC / (1023 - ADC)
//   1/T = 1/T0 + ln(R/R0) / B       (T y T0 en kelvin)
// Solo se llama con el ADC dentro de [ADC_CORTO, ADC_ABIERTO].
float adcATemperaturaC(float adc) {
  float rTermistor = R_PULLUP * adc / (1023.0 - adc);
  float t0K = T0_TERMISTOR_C + 273.15;
  float invT = 1.0 / t0K + log(rTermistor / R0_TERMISTOR) / BETA_TERMISTOR;
  return (1.0 / invT) - 273.15 + TEMP_OFFSET_C;
}

void activarRele() {
  digitalWrite(PIN_RELE, RELE_NIVEL_ACTIVO);
  if (!releActivo) {
    releActivo = true;
    instanteCorteMs = millis();
  }
}

void desactivarRele() {
  digitalWrite(PIN_RELE, RELE_NIVEL_INACTIVO);
  releActivo = false;
}

void entrarEnFalla(const char *motivo) {
  if (enFalla) return;
  enFalla = true;
  motivoFalla = motivo;
  activarRele();
  ultimoMensajeFallaMs = millis() - PERIODO_MENSAJE_FALLA_MS;  // avisa ya
}

void evaluarTemperatura() {
  if (enFalla) {
    activarRele();  // la falla es enclavada: solo sale reiniciando el Nano
    return;
  }

  lecturaTermistorValida = (adcNtcFiltrado >= ADC_CORTO && adcNtcFiltrado <= ADC_ABIERTO);

  if (!lecturaTermistorValida) {
    temperaturaC = NAN;
    // Sin lectura fiable se corta la pistola de inmediato, por precaución,
    // aunque la falla enclavada solo se declara tras varias evaluaciones.
    activarRele();
    if (contadorLecturasInvalidas < 255) contadorLecturasInvalidas++;
    if (contadorLecturasInvalidas >= EVALUACIONES_FALLA_SENSOR) {
      entrarEnFalla(adcNtcFiltrado > ADC_ABIERTO ? "termistor abierto o desconectado"
                                                 : "termistor en cortocircuito");
    }
    return;
  }

  contadorLecturasInvalidas = 0;
  temperaturaC = adcATemperaturaC(adcNtcFiltrado);

  if (temperaturaC > TEMP_FALLA_C) {
    entrarEnFalla("temperatura por encima de TEMP_FALLA_C");
    return;
  }

  if (temperaturaC >= TEMP_TOPE_C) {
    activarRele();  // corte inmediato, sin esperas
  } else if (releActivo &&
             temperaturaC <= TEMP_TOPE_C - TEMP_HISTERESIS_C &&
             millis() - instanteCorteMs >= TIEMPO_MIN_REACTIVAR_MS) {
    desactivarRele();  // la pistola vuelve a funcionar con su PTC
  }
}

// ===========================================================================
// SERIAL
// ===========================================================================

#ifdef DEBUG_SERIAL
void imprimirEstado() {
  Serial.print(F("rpm_obj="));
  Serial.print(rpmCarreteObjetivo, 2);
  Serial.print(F(" pot="));
  Serial.print((int)adcPotFiltrado);
  Serial.print(F(" T="));
  if (lecturaTermistorValida) {
    Serial.print(temperaturaC, 1);
    Serial.print(F("C"));
  } else {
    Serial.print(F("--"));
  }
  Serial.print(F(" rele="));
  Serial.print(releActivo ? F("CORTA") : F("normal"));
  Serial.print(F(" driver="));
  Serial.print(driverHabilitado ? F("ON") : F("OFF"));
  Serial.print(F(" falla="));
  Serial.println(enFalla ? F("SI") : F("NO"));
}
#endif

void imprimirFalla() {
  Serial.print(F("!!! FALLA: "));
  Serial.print(motivoFalla);
  Serial.print(F(" (ADC termistor="));
  Serial.print((int)adcNtcFiltrado);
  Serial.println(F("). Pistola cortada, motor detenido. Reinicia el Nano."));
}

// ===========================================================================
// SETUP Y LOOP
// ===========================================================================

void setup() {
#ifdef USAR_WATCHDOG
  MCUSR = 0;
  wdt_disable();
#endif

  // Relé: primero el nivel inactivo y después la salida, para que nunca haya
  // un pulso de activación al arrancar.
  digitalWrite(PIN_RELE, RELE_NIVEL_INACTIVO);
  pinMode(PIN_RELE, OUTPUT);
  releActivo = false;

  // ENABLE: primero HIGH (deshabilitado) y después la salida. El pull-up de
  // 10k ya lo mantiene deshabilitado mientras el pin es entrada.
  digitalWrite(PIN_ENABLE, HIGH);
  pinMode(PIN_ENABLE, OUTPUT);
  driverHabilitado = false;

  // AccelStepper: velocidad máxima fija, UNA sola vez. Nunca setMaxSpeed(0).
  motor.setPinsInverted(DIRECCION_INVERTIDA, false, false);
  motor.setMaxSpeed(VELOCIDAD_MAX_PASOS_S);
  motor.setSpeed(0.0);

  Serial.begin(115200);
  Serial.println(F("PetFilamento iniciado (firmware sin probar en hardware)."));

  // Siembra los filtros con una lectura real para no arrancar desde 0
  // (un termistor en 0 parecería un cortocircuito).
  adcPotFiltrado = leerAdc(PIN_POT);
  adcNtcFiltrado = leerAdc(PIN_NTC);

  unsigned long ahora = millis();
  ultimoAdcMs = ahora;
  ultimaRampaMs = ahora;
  ultimaTemperaturaMs = ahora;
  ultimoSerialMs = ahora;

#ifdef USAR_WATCHDOG
  wdt_enable(WDTO_2S);
#endif
}

void loop() {
  // Genera los pasos lo más seguido posible.
  motor.runSpeed();

  unsigned long ahora = millis();

  if (ahora - ultimoAdcMs >= PERIODO_LECTURA_ADC_MS) {
    ultimoAdcMs = ahora;
    actualizarLecturas();
  }

  if (ahora - ultimaTemperaturaMs >= PERIODO_TEMPERATURA_MS) {
    ultimaTemperaturaMs = ahora;
    evaluarTemperatura();
  }

  if (ahora - ultimaRampaMs >= PERIODO_RAMPA_MS) {
    unsigned long dt = ahora - ultimaRampaMs;
    ultimaRampaMs = ahora;
    calcularVelocidadObjetivo();
    actualizarEnable();   // habilita antes de empezar a dar pasos
    actualizarRampa(dt);
    actualizarEnable();   // deshabilita en cuanto la rampa llega a cero
  }

  if (enFalla && ahora - ultimoMensajeFallaMs >= PERIODO_MENSAJE_FALLA_MS) {
    ultimoMensajeFallaMs = ahora;
    imprimirFalla();
  }

#ifdef DEBUG_SERIAL
  if (ahora - ultimoSerialMs >= PERIODO_SERIAL_MS) {
    ultimoSerialMs = ahora;
    imprimirEstado();
  }
#endif

#ifdef USAR_WATCHDOG
  wdt_reset();
#endif
}
