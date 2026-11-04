"""Selector de canción con BTNL (anterior) y BTNR (siguiente).

Extensión del proyecto: la propuesta pide una melodía automática; aquí se
puede elegir entre N canciones. `anterior` y `siguiente` son pulsos de un
ciclo (pulsadores ya sincronizados y con antirrebote). La selección da la
vuelta (de la última pasa a la primera y al revés) y se muestra en
`leds_cancion` con un LED encendido (LD8 = canción 0, LD9 = canción 1, ...).
Al encender o reiniciar queda elegida la canción 0.
"""
from myhdl import block, always_seq, always_comb, Signal, intbv


@block
def selector_cancion(clk, rst, anterior, siguiente, seleccion, leds_cancion,
                     N=4):
    """seleccion: Signal(intbv) con 2**len(seleccion) >= N.
    leds_cancion: Signal(intbv) de al menos N bits."""
    N = int(N)
    assert 1 <= N <= 2 ** len(seleccion) and N <= len(leds_cancion)
    ULTIMA = N - 1
    UNO_CALIENTE = tuple(1 << k for k in range(2 ** len(seleccion)))
    sel = Signal(intbv(0, min=0, max=2 ** len(seleccion)))

    @always_seq(clk.posedge, reset=rst)
    def logica():
        if siguiente and not anterior:
            if sel == ULTIMA:
                sel.next = 0
            else:
                sel.next = sel + 1
        elif anterior and not siguiente:
            if sel == 0:
                sel.next = ULTIMA
            else:
                sel.next = sel - 1

    @always_comb
    def salidas():
        seleccion.next = sel
        leds_cancion.next = UNO_CALIENTE[sel]

    return logica, salidas
