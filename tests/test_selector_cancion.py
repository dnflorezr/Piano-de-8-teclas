"""Selector de canción (extensión): BTNR avanza, BTNL retrocede, la
selección da la vuelta y se muestra con un LED encendido."""
from myhdl import block, instance, Signal, ResetSignal, intbv, StopSimulation

from selector_cancion import selector_cancion
from utilidades import reloj, simular


def probar(n):
    clk = Signal(bool(0))
    rst = ResetSignal(1, active=1, isasync=False)
    ant, sig = Signal(bool(0)), Signal(bool(0))
    sel = Signal(intbv(0)[2:])
    leds = Signal(intbv(0)[4:])

    def pulso(boton):
        boton.next = 1
        yield clk.posedge
        boton.next = 0
        yield clk.posedge
        yield clk.negedge

    @block
    def tb():
        @instance
        def estimulo():
            yield clk.posedge
            rst.next = 0
            yield clk.negedge
            assert sel == 0 and leds == 1
            esperado = 0
            for _ in range(2 * n + 1):              # adelante, con vuelta
                yield pulso(sig)
                esperado = (esperado + 1) % n
                assert sel == esperado and leds == 1 << esperado
            for _ in range(2 * n + 1):              # atrás, con vuelta
                yield pulso(ant)
                esperado = (esperado - 1) % n
                assert sel == esperado and leds == 1 << esperado
            ant.next = 1                            # ambos a la vez: no cambia
            sig.next = 1
            yield clk.posedge
            ant.next = 0
            sig.next = 0
            yield clk.posedge
            yield clk.negedge
            assert sel == esperado
            for _ in range(10):                     # sin pulsos: se mantiene
                yield clk.posedge
            assert sel == esperado
            raise StopSimulation
        return (selector_cancion(clk, rst, ant, sig, sel, leds, N=n),
                reloj(clk), estimulo)

    simular(tb())


def test_cuatro_canciones():
    probar(4)


def test_tres_canciones():
    probar(3)
