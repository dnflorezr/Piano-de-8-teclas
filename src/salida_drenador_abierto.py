"""Salida de drenador abierto para AUD_PWM.

El manual de referencia de la Nexys 4 DDR indica que AUD_PWM debe llevarse
a '0' o dejarse en alta impedancia (la placa tiene resistencia de pull-up
hacia el filtro). Un '1' lógico de `entrada` se entrega como 'Z'.
"""
from myhdl import block, always_comb


@block
def salida_drenador_abierto(entrada, salida):
    """salida: TristateSignal(bool)."""
    drv = salida.driver()

    @always_comb
    def logica():
        drv.next = None if entrada else 0

    return logica
