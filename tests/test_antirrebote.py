"""Antirrebote de BTNU: los rebotes no generan pulsos; cada pulsación
estable genera exactamente un pulso de un ciclo."""
from myhdl import block, instance, always, Signal, ResetSignal, StopSimulation

from antirrebote import antirrebote
from utilidades import reloj, simular

CICLOS = 20


def test_rebotes_y_pulso_unico():
    clk = Signal(bool(0))
    rst = ResetSignal(1, active=1, isasync=False)
    ent = Signal(bool(0))
    pulso = Signal(bool(0))
    pulsos = []
    ciclo = [0]

    @block
    def tb():
        dut = antirrebote(clk, rst, ent, pulso, CICLOS=CICLOS)

        @always(clk.posedge)
        def mon():
            ciclo[0] += 1
            if pulso:
                pulsos.append(ciclo[0])

        @instance
        def estimulo():
            yield clk.posedge
            rst.next = 0
            # Rebotes al presionar (más cortos que CICLOS)
            for ancho in (3, 5, 2, 8, 4, 11):
                ent.next = 1
                for _ in range(ancho):
                    yield clk.posedge
                ent.next = 0
                for _ in range(ancho):
                    yield clk.posedge
            assert pulsos == []
            ent.next = 1                         # pulsación estable
            for _ in range(3 * CICLOS):
                yield clk.posedge
            assert len(pulsos) == 1
            for ancho in (2, 4, 3):              # rebotes al soltar
                ent.next = 0
                for _ in range(ancho):
                    yield clk.posedge
                ent.next = 1
                for _ in range(ancho):
                    yield clk.posedge
            ent.next = 0
            for _ in range(3 * CICLOS):
                yield clk.posedge
            assert len(pulsos) == 1              # soltar no genera pulso
            ent.next = 1                         # segunda pulsación
            for _ in range(3 * CICLOS):
                yield clk.posedge
            assert len(pulsos) == 2
            raise StopSimulation

        return dut, mon, reloj(clk), estimulo

    simular(tb())
