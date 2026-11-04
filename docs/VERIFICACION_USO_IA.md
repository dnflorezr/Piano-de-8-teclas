# Verificación de uso de IA

**Proyecto:** Piano digital de 8 teclas con generación de tonos (propuesta 10)
**Curso:** Electrónica Digital
**Placa / herramienta:** Nexys 4 DDR (Artix-7 XC7A100T) / Vivado
**Lenguaje:** MyHDL (Python) convertido a VHDL
**Autores:** Diego Florez Rojas, Andres Moreno Plazas
**Fecha de esta declaración:** 3 de noviembre de 2026 (actualizada el 4 de noviembre de 2026)

Este documento declara de forma transparente qué partes del proyecto se hicieron
con ayuda de inteligencia artificial, qué herramienta se usó, cómo se verificó
lo que produjo y qué queda bajo responsabilidad del equipo.

---

## 1. Herramienta utilizada

| Campo | Valor |
|---|---|
| Herramienta | Claude (Anthropic), usado a través de Claude Code en la web (claude.ai) |
| Modalidad | Conversación con el asistente, que además ejecutó código (Python, pytest, GHDL) en un entorno en la nube |
| Período de uso | 2 al 4 de noviembre de 2026 |
| Quién la usó | Diego Florez Rojas |

## 2. Para qué se usó la IA

| # | Actividad | Qué hizo la IA | Qué hizo el equipo | Evidencia |
|---|---|---|---|---|
| 1 | Revisión del anteproyecto | Comparó el anteproyecto original con la propuesta 10 y con los "Criterios para todas las propuestas" de `project_proposal_list.md`, y señaló brechas: faltaba el contador PWM de volumen, las teclas estaban en interruptores y no en botones, faltaban pruebas exhaustivas y de frontera, y había inconsistencias entre figuras y texto. | Definió las restricciones (no añadir ni quitar funciones de la propuesta; Nexys 4 DDR y Vivado; MyHDL como lenguaje) y decidió qué brechas corregir. | Conversación del proyecto |
| 2 | Prompt de ajuste del anteproyecto | Redactó un prompt con la lista de cambios obligatorios y restricciones. | Revisó el prompt y lo usó para producir la versión ajustada. | `prompt_ajuste_anteproyecto.md`, `Anteproyecto_..._v2.docx` (se conserva la versión original) |
| 3 | Código MyHDL | Escribió los 12 módulos de `src/` siguiendo la arquitectura de la Fig. 1, las ecuaciones (1)–(3) y la Tabla II del anteproyecto. | Fijó la arquitectura, las ecuaciones y los valores de la Tabla II (hechos antes en el anteproyecto). Debe revisar y validar las decisiones de la sección 4. | `src/` |
| 4 | Bancos de prueba | Escribió 23 pruebas en pytest que cubren los casos CP-1 a CP-15 de la Tabla III, más el antirrebote y la Tabla II. | Definió los casos de prueba en la Tabla III del anteproyecto. | `tests/`, tabla "Casos de prueba" del `README.md` |
| 5 | Conversión a VHDL | Escribió `convertir_vhdl.py`, generó `vhdl/piano_top.vhd` y los módulos por separado, y escribió el banco de prueba VHDL `vhdl/sim/tb_piano_top.vhd`. | — | `vhdl/` |
| 6 | Restricciones y proyecto de Vivado | Escribió `xdc/piano_nexys4ddr.xdc` a partir del archivo maestro Nexys-4-DDR-Master.xdc y el script `crear_proyecto_vivado.tcl`. | Debe confirmar los pines contra el archivo maestro oficial de Digilent al sintetizar. | `xdc/`, `crear_proyecto_vivado.tcl` |
| 7 | Documentación | Escribió el `README.md` y este documento. | Revisa y firma esta declaración (sección 7). | `README.md`, `docs/VERIFICACION_USO_IA.md` |
| 8 | **Extensión: varias canciones** (4/11/2026) | Propuso y escribió tres canciones más de dominio público dentro de C4–C5, la selección con BTNL/BTNR y LD8–LD11 (`selector_cancion.py`), el cambio de la FSM para guardar varias canciones, 7 pruebas nuevas y la actualización del XDC y del banco VHDL. | Pidió agregar canciones y eligió el control con BTNL/BTNR. Debe validar las decisiones 7 y 9 de la sección 4. | `src/parametros.py`, `src/selector_cancion.py`, `src/melodia_fsm.py`, `tests/test_selector_cancion.py` |

**Nota sobre el alcance:** la propuesta 10 pide una melodía automática. Tener
varias canciones y elegirlas con BTNL/BTNR es una **extensión** que el equipo
decidió agregar después de probar el diseño base en la placa; no está en el
anteproyecto.

**No se usó IA** para definir el tema del proyecto (lo fija la propuesta 10 del
curso) ni para elegir la placa y la herramienta.

## 3. Cómo se verificó lo que produjo la IA

Ningún resultado de la IA se tomó como correcto sin una prueba que lo respalde.

| Verificación | Resultado | Estado | Quién la ejecutó |
|---|---|---|---|
| Pruebas MyHDL: `cd tests && python -m pytest -v` | **30 de 30 pasan** (≈16 s) con la extensión de canciones (4/11/2026). La versión base tenía 23. | Hecho | IA (entorno en la nube); el equipo debe repetirlo en su PC |
| Codificador con prioridad, 256 combinaciones (CP-3) | Las 256 entradas dan la tecla de menor número | Hecho | IA |
| Tabla II: `python src/parametros.py` | Divisores N y frecuencias iguales a la Tabla II; error máximo 0,0004 % | Hecho | IA, contra la tabla calculada por el equipo |
| Simulación del VHDL convertido a 100 MHz (`tb_piano_top.vhd`) | Pasó en GHDL, también con la selección de canción (4/11/2026) | Hecho | IA (GHDL en la nube) |
| Simulación del VHDL en el simulador de Vivado | — | **Pendiente** | Equipo |
| Síntesis, implementación y bitstream en Vivado | Versión base: bitstream generado en Vivado 2026.1. Con la extensión: pendiente | Base hecha; extensión **pendiente** | Equipo |
| Prueba en la placa (sonido con audífonos, 8 notas, 8 niveles de volumen, melodía) | Versión base: suena y funciona. Con la extensión (BTNL/BTNR, LD8–LD11, 4 canciones): pendiente | Base hecha; extensión **pendiente** | Equipo |

### Errores de la IA detectados por las pruebas

Las pruebas encontraron fallas en el código generado, que se corrigieron antes
de entregarlo:

1. **Pulso corto al cambiar de nota (CP-13).** La primera versión forzaba la
   salida a 0 al cambiar de nota; si el cambio coincidía con una conmutación,
   aparecía un pulso de un ciclo. Se cambió para que el contador se reinicie
   pero la salida conserve su nivel (decisión 3 de la sección 4).
2. **Salida triestado no conectada.** MyHDL 0.11 no conecta el driver triestado
   de AUD_PWM al puerto al convertir a VHDL. `convertir_vhdl.py` corrige esa
   línea automáticamente (`tono <= 'Z'` / `'0'`).
3. **Rutas con espacios en el script de Vivado.** `crear_proyecto_vivado.tcl`
   pasaba las rutas del XDC y del banco de prueba sin `[list ...]`, y Vivado
   las partía en la carpeta `Piano de 8 teclas`. Lo detectó el equipo al crear
   el proyecto; se corrigió el 4/11/2026.

## 4. Decisiones de diseño que tomó la IA y que el equipo debe validar

El anteproyecto deja estos puntos abiertos; la IA eligió una opción para poder
escribir el código. Están explicadas en el `README.md` y cada una se cambia en
un solo lugar.

| # | Decisión | ¿Validada por el equipo? |
|---|---|---|
| 1 | Con varias teclas suena la de menor número (SW0 = C4) | ☐ |
| 2 | Volumen: ciclo de trabajo = (SW15–SW13 + 1) / 8, de 12,5 % a 100 %, sin nivel de silencio | ☐ |
| 3 | Al cambiar de nota el contador se reinicia y la salida conserva su nivel | ☐ |
| 4 | AUD_PWM como drenador abierto ('0' o 'Z'), como pide el manual de la Nexys 4 DDR | ☐ |
| 5 | AUD_SD = 0 durante el reinicio y 1 el resto del tiempo | ☐ |
| 6 | BTNU con antirrebote de 10 ms; la melodía no arranca si hay una tecla accionada | ☐ |
| 7 | Canciones (dominio público, solo C4–C5): 0 "Himno a la alegría", 1 "Estrellita, ¿dónde estás?", 2 "Los pollitos dicen", 3 "María tenía un corderito"; unidad de 125 ms, pausa de 30 ms | ☐ |
| 8 | El estado END de la Fig. 2 se llama `FIN` (END es palabra reservada en VHDL) | ☐ |
| 9 | Selección: BTNR siguiente, BTNL anterior, da la vuelta; LD8–LD11 muestran la canción; se lee al pulsar BTNU (cambiarla mientras suena no afecta); el reinicio vuelve a la canción 0 | ☐ |

## 5. Comprensión del código por parte del equipo

Para poder sustentar el proyecto, cada integrante debe poder explicar sin ayuda:

- [ ] Cómo se obtiene N = redondeo(fclk / 2f) y por qué el contador es de 18 bits.
- [ ] Por qué hay dos biestables en cascada en las entradas (metaestabilidad).
- [ ] Cómo el filtro pasabajos de la etapa de audio convierte el ciclo de trabajo del PWM en amplitud.
- [ ] Los estados y transiciones de la FSM de la melodía (IDLE, LOAD, PLAY, GAP, FIN) y qué pasa al accionar una tecla durante la melodía.
- [ ] Cómo se guardan las cuatro canciones en una sola ROM y cómo la FSM usa la posición inicial y final de la canción elegida.
- [ ] Qué verifica cada caso de prueba de la Tabla III y qué prueba de `tests/` lo cubre.
- [ ] Cómo se pasa de MyHDL a VHDL y qué corrige `convertir_vhdl.py`.

## 6. Límites y responsabilidad

- La IA puede equivocarse. Las pruebas reducen ese riesgo, pero no reemplazan
  la síntesis en Vivado ni la prueba en la placa, que siguen pendientes.
- Las pruebas MyHDL usan un reloj reducido (200 kHz) para correr en segundos;
  la equivalencia con 100 MHz se sostiene porque todos los tiempos se calculan
  con `C = T · fclk` y `N = redondeo(fclk / 2f)`. El banco VHDL sí usa 100 MHz.
- El equipo es responsable del contenido entregado, de su corrección y de poder
  explicarlo.

## 7. Firma

Declaramos que la información anterior describe con exactitud el uso de IA en
este proyecto.

| Integrante | Firma | Fecha |
|---|---|---|
| Diego Florez Rojas | | |
| Andres Moreno Plazas | | |
