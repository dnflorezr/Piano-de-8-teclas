# Piano digital de 8 teclas — Nexys 4 DDR (MyHDL → VHDL → Vivado)

Código del proyecto descrito en el anteproyecto
*Anteproyecto_Piano_Digital_8_Teclas_FPGA_Nexys4DDR_v2.docx* (propuesta 10).
El hardware está descrito en Python con MyHDL, se simula con bancos de prueba
en Python y se convierte a VHDL para sintetizar en Vivado.

## Uso de IA

En este proyecto se usó IA (Claude) para revisar el anteproyecto y generar el
código, las pruebas y la documentación. Qué se hizo, cómo se verificó y qué queda
pendiente está en [docs/VERIFICACION_USO_IA.md](docs/VERIFICACION_USO_IA.md).

## Estructura

```
codigo/
├── src/                        Diseño en MyHDL
│   ├── parametros.py           Notas, ecuaciones (1)-(3), Tabla II, canciones
│   ├── piano_top.py            Entidad de nivel superior (Fig. 1, Tabla I)
│   ├── sincronizador_reset.py  Reinicio síncrono a partir de BTNC
│   ├── sincronizador.py        Dos biestables en cascada (teclas, volumen, botones)
│   ├── antirrebote.py          Antirrebote de BTNU/BTNL/BTNR + pulso de un ciclo
│   ├── codificador_prioridad.py Detector de tecla activa (gana la de menor número)
│   ├── tabla_divisores.py      Índice de nota → divisor N
│   ├── generador_tono.py       Contador de 18 bits, f = fclk / 2N
│   ├── pwm_volumen.py          PWM de 8 bits (~390 kHz), 8 niveles con SW15–SW13
│   ├── melodia_fsm.py          FSM IDLE/LOAD/PLAY/GAP/FIN (Fig. 2), varias canciones
│   ├── selector_cancion.py     BTNL / BTNR eligen la canción (extensión)
│   ├── salida_drenador_abierto.py  AUD_PWM: '0' o 'Z'
│   └── convertir_vhdl.py       Genera el VHDL
├── tests/                      Bancos de prueba MyHDL (pytest), CP-1 a CP-15
├── vhdl/
│   ├── piano_top.vhd           VHDL convertido del diseño completo (100 MHz)
│   ├── pck_myhdl_011.vhd       Paquete de soporte de MyHDL (agregarlo a Vivado)
│   ├── modulos/                Cada bloque convertido por separado (documentación)
│   └── sim/tb_piano_top.vhd    Banco de prueba VHDL para el simulador de Vivado
├── xdc/piano_nexys4ddr.xdc     Restricciones (basadas en Nexys-4-DDR-Master.xdc)
└── crear_proyecto_vivado.tcl   Crea el proyecto de Vivado con todo lo anterior
```

## Uso en la placa

| Control | Función |
|---|---|
| SW0 … SW7 | Teclas C4 D4 E4 F4 G4 A4 B4 C5 |
| SW13 … SW15 | Volumen (000 = 12,5 % … 111 = 100 % de ciclo de trabajo) |
| BTNU | Inicia la canción elegida; otra pulsación la detiene |
| BTNR / BTNL | Canción siguiente / anterior (da la vuelta) |
| LD8 … LD11 | Canción elegida (una encendida) |
| BTNC | Reinicio |
| LD0 … LD7 | Nota que está sonando |
| Conector de audio | Audífonos o parlante amplificado (la placa no trae altavoz) |

## Cómo correr todo

```bash
pip install -r requirements.txt

# 1. Simulación MyHDL (30 pruebas, ~16 s)
cd tests
python -m pytest -v

# 2. Tabla II
cd ../src
python parametros.py

# 3. Conversión a VHDL (sobrescribe la carpeta vhdl/)
python convertir_vhdl.py
```

En Vivado (consola Tcl):

```tcl
cd {C:/Users/diego/Piano de 8 teclas/codigo}
source crear_proyecto_vivado.tcl
```

Luego *Run Simulation* (usa `tb_piano_top`, ~160 ms simulados, tarda unos
minutos), *Run Synthesis*, *Run Implementation* y *Generate Bitstream*.

## Casos de prueba (Tabla III) → pruebas

| Caso | Prueba |
|---|---|
| CP-1 | `test_piano_top::test_cp1_sin_teclas_y_cp2_cada_tecla`, `test_generador_tono::test_cp2_...` |
| CP-2 | `test_piano_top::test_cp1_sin_teclas_y_cp2_cada_tecla` (8 teclas), `test_generador_tono::test_cp2_cada_divisor_y_cp6_sostenido` |
| CP-3 | `test_codificador_prioridad::test_256_combinaciones` (exhaustivo), `test_piano_top::test_cp3_varias_teclas` |
| CP-4 | `test_generador_tono::test_cp4_cambio_sin_liberar` |
| CP-5 | `test_piano_top::test_cp5_accionamiento_breve` |
| CP-6 | `test_generador_tono::test_cp2_cada_divisor_y_cp6_sostenido` |
| CP-7 | `test_melodia_fsm::test_cp7_reinicio_durante_reproduccion`, `test_piano_top::test_cp12_reinicio_con_tecla_y_cp7` |
| CP-8, CP-9, CP-10 | `test_melodia_fsm::test_cp8_cp9_cp10_melodia_completa`, `test_piano_top::test_cp8_cp9_cp10_melodia_y_cp15` |
| CP-11 | `test_pwm_volumen::test_cp11_ocho_niveles`, `test_piano_top::test_cp11_volumen_en_la_salida` |
| CP-12 | `test_generador_tono::test_cp12_reinicio_con_tecla`, `test_piano_top::test_cp12_...` |
| CP-13 | `test_generador_tono::test_cp13_cambio_cuando_contador_llega_a_n` |
| CP-14 | `test_generador_tono::test_cp14_c5_a_c4` |
| CP-15 | `test_melodia_fsm::test_cp15_tecla_detiene_melodia`, `test_piano_top::test_cp8_cp9_cp10_melodia_y_cp15` |
| Antirrebote | `test_antirrebote::test_rebotes_y_pulso_unico` |
| Varias canciones (extensión) | `test_selector_cancion`, `test_melodia_fsm::test_seleccion_*`, `test_melodia_fsm::test_cambiar_seleccion_durante_cancion_no_afecta`, `test_piano_top::test_seleccion_de_cancion_con_btnl_btnr`, `test_divisores::test_canciones_validas` |
| Tabla II | `test_divisores` |

Las pruebas MyHDL usan un reloj reducido (200 kHz) para que corran en
segundos; como todo se calcula con `C = T · fclk` y `N = redondeo(fclk / 2f)`,
el comportamiento es el mismo que a 100 MHz. El banco `vhdl/sim/tb_piano_top.vhd`
sí usa los 100 MHz reales sobre el VHDL convertido.

## Decisiones de diseño tomadas al escribir el código

Estas son concreciones de lo que el anteproyecto deja abierto; si el equipo
prefiere otra, se cambia en un solo lugar.

1. **Prioridad**: con varias teclas suena la de menor número (SW0 = C4).
2. **Niveles de volumen**: ciclo de trabajo = (SW15–SW13 + 1) / 8, de 12,5 % a
   100 % (`pwm_volumen.py`). No hay nivel de silencio.
3. **Cambio de nota**: el divisor se registra y el contador se reinicia en el
   mismo flanco, pero la salida conserva su nivel. Así el semiperíodo de
   transición dura entre N_nuevo y N_anterior + N_nuevo y nunca aparece un
   pulso corto (forzar la salida a 0 dejaba un pulso de 1 ciclo cuando el
   cambio coincidía con una conmutación; lo detectó la prueba CP-13).
4. **AUD_PWM de drenador abierto**: el manual de la Nexys 4 DDR pide llevar
   AUD_PWM a '0' o dejarlo en alta impedancia, así que un '1' sale como 'Z'.
   MyHDL 0.11 no conecta el driver triestado al puerto al convertir, por lo
   que `convertir_vhdl.py` corrige esa línea del VHDL automáticamente.
5. **AUD_SD** vale 0 durante el reinicio y 1 el resto del tiempo.
6. **BTNU**: antirrebote de 10 ms y detección de flanco; la melodía no arranca
   si hay una tecla accionada.
7. **Canciones**: la propuesta pide una melodía; como extensión hay cuatro,
   todas de dominio público y dentro de C4–C5: 0 "Himno a la alegría",
   1 "Estrellita, ¿dónde estás?", 2 "Los pollitos dicen" y 3 "María tenía un
   corderito". Unidad de 125 ms y pausa (GAP) de 30 ms. Se cambian en
   `parametros.py` (`CANCIONES`, `T_TIEMPO`, `T_PAUSA`); caben hasta 4.
9. **Selección de canción**: BTNR pasa a la siguiente y BTNL a la anterior
   (con antirrebote de 10 ms y dando la vuelta); LD8–LD11 muestran cuál está
   elegida. La FSM la lee al pulsar BTNU, así que cambiarla mientras suena no
   corta la canción. El reinicio (BTNC) vuelve a la canción 0.
8. El estado END de la Fig. 2 se llama `FIN` porque `END` es palabra reservada
   de VHDL.
