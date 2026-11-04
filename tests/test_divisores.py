"""Verificación de la Tabla II (cálculo de los divisores a 100 MHz)."""
import parametros as P

TABLA_II = (191110, 170265, 151685, 143172, 127551, 113636, 101239, 95557)


def test_tabla_ii():
    assert P.tabla_divisores() == TABLA_II


def test_contador_de_18_bits():
    assert max(P.tabla_divisores()) < 2 ** 18
    assert max(P.tabla_divisores()) >= 2 ** 17


def test_error_menor_a_0_001_por_ciento():
    for f in P.FRECUENCIAS:
        assert abs(P.error_relativo(f)) < 0.001


def test_melodia_valida():
    assert all(0 <= n < 8 and d >= 1 for n, d in P.MELODIA)


def test_canciones_validas():
    # Cuatro canciones para SW9..SW8, todas dentro de C4..C5.
    assert len(P.CANCIONES) == len(P.NOMBRES_CANCIONES) == 4
    assert P.CANCIONES[0] == P.MELODIA
    for c in P.CANCIONES:
        assert c and all(0 <= n < 8 and d >= 1 for n, d in c)
