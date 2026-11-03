"""Detector de tecla activa: codificador con prioridad (Sección V-D).

Entrega el índice de la tecla accionada de MENOR número (SW0 = C4 tiene la
mayor prioridad) y la señal `activa` que indica si hay alguna tecla.
"""
from myhdl import block, always_comb, downrange


@block
def codificador_prioridad(teclas, indice, activa):
    N = len(teclas)

    @always_comb
    def logica():
        indice.next = 0
        activa.next = 0
        # Se recorre de la tecla mayor a la menor: la última asignación gana,
        # así que la tecla de menor número accionada fija el índice.
        for i in downrange(N):
            if teclas[i]:
                indice.next = i
                activa.next = 1

    return logica
