"""Antirrebote del pulsador BTNU con detección de flanco.

La entrada (ya sincronizada) debe mantenerse estable durante CICLOS ciclos
de reloj para aceptarse. Cada pulsación aceptada genera un único pulso de
un ciclo en `pulso`.
"""
from myhdl import block, always_seq, Signal, intbv


@block
def antirrebote(clk, rst, entrada, pulso, CICLOS=1_000_000):
    cuenta = Signal(intbv(0, min=0, max=CICLOS + 1))
    estable = Signal(bool(0))

    @always_seq(clk.posedge, reset=rst)
    def logica():
        pulso.next = 0
        if entrada == estable:
            cuenta.next = 0
        elif cuenta == CICLOS - 1:
            cuenta.next = 0
            estable.next = entrada
            if entrada:
                pulso.next = 1
        else:
            cuenta.next = cuenta + 1

    return logica
