"""Generador de tono: contador que conmuta la salida al llegar a N.

f_sal = fclk / (2N)  (ecuación 1).

- Con `habilitar` = 0 el generador está inhibido: contador en 0 y salida en 0.
- El divisor se carga en un registro sincronizado con el reloj. Si el valor
  de entrada cambia, el contador se reinicia en ese mismo flanco y la salida
  CONSERVA su nivel: el semiperíodo de transición dura entre N_nuevo y
  N_anterior + N_nuevo ciclos, así que nunca aparece un pulso más corto que
  un semiperíodo de la nota nueva (CP-4, CP-13, CP-14). Si en cambio se
  forzara la salida a 0, un cambio justo después de una conmutación dejaría
  un pulso de un solo ciclo.
"""
from myhdl import block, always_seq, always_comb, Signal, intbv


@block
def generador_tono(clk, rst, divisor, habilitar, tono):
    MAX = divisor.max
    div_reg = Signal(intbv(0, min=0, max=MAX))
    cuenta = Signal(intbv(0, min=0, max=MAX))
    salida = Signal(bool(0))

    @always_seq(clk.posedge, reset=rst)
    def logica():
        if not habilitar:
            cuenta.next = 0
            salida.next = 0
            div_reg.next = divisor
        elif divisor != div_reg:
            div_reg.next = divisor
            cuenta.next = 0
        elif cuenta >= div_reg - 1:
            # >= en lugar de == : si por cualquier motivo la cuenta supera
            # al divisor, no hay desbordamiento (CP-6, CP-14).
            cuenta.next = 0
            salida.next = not salida
        else:
            cuenta.next = cuenta + 1

    @always_comb
    def conexion():
        tono.next = salida

    return logica, conexion
