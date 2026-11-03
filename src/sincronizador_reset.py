"""Sincronizador del reinicio (BTNC).

Produce el reinicio síncrono que usan todos los demás bloques. No tiene
entrada de reinicio propia: es el único bloque que la genera.
"""
from myhdl import block, always, Signal


@block
def sincronizador_reset(clk, rst_btn, rst_sync):
    etapa1 = Signal(bool(1))

    @always(clk.posedge)
    def logica():
        etapa1.next = rst_btn
        rst_sync.next = etapa1

    return logica
