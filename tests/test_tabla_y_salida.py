"""Pruebas unitarias de la tabla de divisores y de la salida de drenador
abierto.

- tabla_divisores: cada índice 0..7 entrega el divisor N de la Tabla II
  (con el reloj de 100 MHz de la placa).
- salida_drenador_abierto: un '0' lógico se entrega como '0' y un '1' como
  alta impedancia ('Z'), como pide el manual de la Nexys 4 DDR para AUD_PWM.
"""
from myhdl import (block, instance, delay, Signal, TristateSignal, intbv,
                   StopSimulation)

import parametros as P
from tabla_divisores import tabla_divisores
from salida_drenador_abierto import salida_drenador_abierto
from utilidades import simular

TABLA_II = (191110, 170265, 151685, 143172, 127551, 113636, 101239, 95557)


def test_tabla_divisores_ocho_indices():
    tabla = P.tabla_divisores()
    assert tabla == TABLA_II
    idx = Signal(intbv(0, min=0, max=8))
    div = Signal(intbv(0, min=0, max=max(tabla) + 1))

    @block
    def tb():
        dut = tabla_divisores(idx, div, TABLA=tabla)

        @instance
        def estimulo():
            for i in list(range(8)) + [7, 0, 3]:
                idx.next = i
                yield delay(1)
                assert div == TABLA_II[i], (i, int(div))
            raise StopSimulation

        return dut, estimulo

    simular(tb())


def test_salida_drenador_abierto():
    ent = Signal(bool(0))
    sal = TristateSignal(bool(0))

    @block
    def tb():
        dut = salida_drenador_abierto(ent, sal)

        @instance
        def estimulo():
            for v in (0, 1, 0, 1, 1, 0):
                ent.next = v
                yield delay(1)
                if v:
                    assert sal.val is None          # alta impedancia
                else:
                    assert sal.val is not None and int(sal.val) == 0
            raise StopSimulation

        return dut, estimulo

    simular(tb())
