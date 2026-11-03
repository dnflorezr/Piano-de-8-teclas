"""CP-1 y CP-3: codificador con prioridad, 256 combinaciones exhaustivas."""
from myhdl import block, instance, delay, Signal, intbv

from codificador_prioridad import codificador_prioridad
from utilidades import simular


def esperado(v):
    for i in range(8):
        if (v >> i) & 1:
            return i, 1
    return 0, 0


@block
def tb():
    teclas = Signal(intbv(0)[8:])
    indice = Signal(intbv(0, min=0, max=8))
    activa = Signal(bool(0))
    dut = codificador_prioridad(teclas, indice, activa)

    @instance
    def estimulo():
        for v in range(256):
            teclas.next = v
            yield delay(1)
            idx, act = esperado(v)
            assert int(activa) == act, "combinación %d" % v
            if act:
                assert int(indice) == idx, "combinación %d: %d != %d" % (v, indice, idx)

    return dut, estimulo


def test_256_combinaciones():
    simular(tb())
