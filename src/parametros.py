"""Parámetros de diseño del piano digital de 8 teclas (Nexys 4 DDR).

Todos los valores dependen de la frecuencia de reloj FCLK, de modo que el
mismo código se puede simular con un reloj reducido y sintetizar con 100 MHz.
"""

FCLK_PLACA = 100_000_000  # oscilador de 100 MHz de la Nexys 4 DDR

# Escala de Do mayor C4..C5 (temperamento igual, La4 = 440 Hz). Tabla II.
NOMBRES = ("C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5")
FRECUENCIAS = (261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25)

# Melodía de ejemplo para el modo automático (la define el equipo):
# "Himno a la alegría" (Beethoven, dominio público), solo con notas C4..C5.
# Cada elemento es (índice de nota 0..7, duración en tiempos de negra).
C4, D4, E4, F4, G4, A4, B4, C5 = range(8)
MELODIA = (
    (E4, 2), (E4, 2), (F4, 2), (G4, 2),
    (G4, 2), (F4, 2), (E4, 2), (D4, 2),
    (C4, 2), (C4, 2), (D4, 2), (E4, 2),
    (E4, 3), (D4, 1), (D4, 4),
)
T_TIEMPO = 0.125      # s por unidad de duración (2 unidades = negra de 0,25 s)
T_PAUSA = 0.030       # s de silencio entre notas (estado GAP)
T_ANTIRREBOTE = 0.010 # s que BTNU debe permanecer estable


def divisor(f_nota, fclk=FCLK_PLACA):
    """Ecuación (2): N = redondeo(fclk / (2 f))."""
    return int(round(fclk / (2.0 * f_nota)))


def tabla_divisores(fclk=FCLK_PLACA):
    return tuple(divisor(f, fclk) for f in FRECUENCIAS)


def frecuencia_obtenida(n, fclk=FCLK_PLACA):
    """Ecuación (1): f_sal = fclk / (2N)."""
    return fclk / (2.0 * n)


def error_relativo(f_nota, fclk=FCLK_PLACA):
    """Ecuación (3), en porcentaje."""
    n = divisor(f_nota, fclk)
    return (frecuencia_obtenida(n, fclk) - f_nota) / f_nota * 100.0


def ciclos(t_segundos, fclk=FCLK_PLACA):
    """Relación C = T * fclk (mínimo 1 ciclo)."""
    return max(1, int(round(t_segundos * fclk)))


if __name__ == "__main__":
    print("Tecla Nota  f_obj(Hz)    N        f_obt(Hz)   e(%)")
    for i, (nom, f) in enumerate(zip(NOMBRES, FRECUENCIAS)):
        n = divisor(f)
        print(f"SW{i}   {nom}   {f:9.2f}  {n:7d}  {frecuencia_obtenida(n):10.3f}  {error_relativo(f):+.4f}")
