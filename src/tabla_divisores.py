"""Selector de nota: índice de nota -> valor del divisor N (Tabla II)."""
from myhdl import block, always_comb


@block
def tabla_divisores(indice, divisor, TABLA):
    TABLA = tuple(int(n) for n in TABLA)

    @always_comb
    def logica():
        divisor.next = TABLA[indice]

    return logica
