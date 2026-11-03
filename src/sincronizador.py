"""Sincronizador de dos biestables en cascada (Sección V-D).

Evita la metaestabilidad de las entradas asíncronas (interruptores y
pulsadores) respecto al reloj de 100 MHz.
"""
from myhdl import block, always_seq, Signal, intbv, modbv


@block
def sincronizador(clk, rst, entrada, salida):
    """entrada/salida: Signal(intbv) de cualquier ancho, o Signal(bool)."""
    if isinstance(entrada.val, intbv):
        ancho = len(entrada)
        etapa1 = Signal(intbv(0)[ancho:])
    else:
        etapa1 = Signal(bool(0))

    @always_seq(clk.posedge, reset=rst)
    def logica():
        etapa1.next = entrada
        salida.next = etapa1

    return logica
