"""Generador de tono: CP-2, CP-4, CP-6, CP-12, CP-13, CP-14.

Se usan divisores reducidos (escala calculada con fclk = 200 kHz) para que
la simulación sea rápida; el período esperado sigue siendo 2N ciclos.
"""
from myhdl import (block, instance, always, Signal, ResetSignal, intbv,
                   StopSimulation)

import parametros as P
from generador_tono import generador_tono
from utilidades import reloj, periodos, simular

TABLA = P.tabla_divisores(200_000)        # (382, 340, ..., 191)
NMAX = max(TABLA) + 1


def armar():
    clk = Signal(bool(0))
    rst = ResetSignal(1, active=1, isasync=False)
    div = Signal(intbv(0, min=0, max=NMAX))
    hab = Signal(bool(0))
    tono = Signal(bool(0))
    return clk, rst, div, hab, tono


@block
def monitor(clk, tono, registro):
    """Guarda el número de ciclo de cada flanco de subida de `tono`."""
    ciclo = [0]
    anterior = [0]

    @always(clk.posedge)
    def mon():
        ciclo[0] += 1
        if tono and not anterior[0]:
            registro.append(ciclo[0])
        anterior[0] = int(tono)
    return mon


def esperar(clk, n):
    for _ in range(n):
        yield clk.posedge


def test_cp2_cada_divisor_y_cp6_sostenido():
    clk, rst, div, hab, tono = armar()
    flancos = []

    @block
    def tb():
        dut = generador_tono(clk, rst, div, hab, tono)
        mon = monitor(clk, tono, flancos)

        @instance
        def estimulo():
            yield esperar(clk, 3)
            rst.next = 0
            for k, n in enumerate(TABLA):
                del flancos[:]
                div.next = n
                hab.next = 1
                vueltas = 20 if k == 0 else 4      # CP-6: C4 sostenido 20 períodos
                yield esperar(clk, 2 * n * vueltas + 5)
                ps = periodos(flancos)
                assert len(ps) >= vueltas - 2
                assert all(p == 2 * n for p in ps), (n, ps)
                hab.next = 0
                yield esperar(clk, 3)
                assert not tono                     # CP-1: inhibido -> 0
            raise StopSimulation

        return dut, mon, reloj(clk), estimulo

    simular(tb())


@block
def monitor_semiperiodos(clk, tono, registro):
    """Guarda el ciclo de cada conmutación (subida o bajada) de `tono`."""
    ciclo = [0]
    anterior = [0]

    @always(clk.posedge)
    def mon():
        ciclo[0] += 1
        if int(tono) != anterior[0]:
            registro.append(ciclo[0])
        anterior[0] = int(tono)
    return mon


def cambio_de_nota(n1, n2, retardo):
    """Suena n1 y `retardo` ciclos después cambia a n2. Comprueba que no haya
    pulsos anómalos: el semiperíodo de transición dura entre n2 y n1 + n2, y
    todos los siguientes duran exactamente n2."""
    clk, rst, div, hab, tono = armar()
    flancos = []
    conmutaciones = []
    res = {}

    @block
    def tb():
        dut = generador_tono(clk, rst, div, hab, tono)
        mon = monitor(clk, tono, flancos)
        mon2 = monitor_semiperiodos(clk, tono, conmutaciones)

        @instance
        def estimulo():
            yield esperar(clk, 3)
            rst.next = 0
            div.next = n1
            hab.next = 1
            yield esperar(clk, retardo)
            del flancos[:]
            div.next = n2
            yield esperar(clk, 2 * n2 * 5 + 5)
            sp = periodos(conmutaciones)
            # Ningún semiperíodo más corto que el de las notas involucradas
            # ni más largo que n1 + n2 (+1 por el registro del divisor).
            assert all(min(n1, n2) <= x <= n1 + n2 + 1 for x in sp), sp
            # Tras la transición, todos los semiperíodos son de la nota nueva.
            assert all(x == n2 for x in sp[-8:]), sp
            res["periodos"] = periodos(flancos[1:])
            raise StopSimulation

        return dut, mon, mon2, reloj(clk), estimulo

    simular(tb())
    return res


def test_cp4_cambio_sin_liberar():
    r = cambio_de_nota(TABLA[2], TABLA[5], 1000)
    assert all(p == 2 * TABLA[5] for p in r["periodos"])


def test_cp13_cambio_cuando_contador_llega_a_n():
    n1 = TABLA[3]
    # Cambio justo en el ciclo en que el contador llega a N-1 (conmutación).
    for retardo in (n1 - 1, n1, n1 + 1, 2 * n1 - 1, 2 * n1, 2 * n1 + 1):
        r = cambio_de_nota(n1, TABLA[6], retardo)
        assert r["periodos"] and all(p == 2 * TABLA[6] for p in r["periodos"]), retardo


def test_cp14_c5_a_c4():
    c4, c5 = TABLA[0], TABLA[7]
    for retardo in (3 * c5 + 7, 2 * c5 - 1, 2 * c5, 2 * c5 + 1):
        r = cambio_de_nota(c5, c4, retardo)
        assert r["periodos"] and all(p == 2 * c4 for p in r["periodos"])
    r = cambio_de_nota(c4, c5, 2 * c4 + 1)       # y en sentido contrario
    assert r["periodos"] and all(p == 2 * c5 for p in r["periodos"])


def test_cp12_reinicio_con_tecla():
    clk, rst, div, hab, tono = armar()
    flancos = []

    @block
    def tb():
        dut = generador_tono(clk, rst, div, hab, tono)
        mon = monitor(clk, tono, flancos)

        @instance
        def estimulo():
            div.next = TABLA[4]
            hab.next = 1
            for _ in range(3 * TABLA[4]):     # reinicio activo con tecla accionada
                yield clk.posedge
                assert not tono
            rst.next = 0
            del flancos[:]
            yield esperar(clk, 2 * TABLA[4] * 4 + 5)
            ps = periodos(flancos)
            assert ps and all(p == 2 * TABLA[4] for p in ps)
            raise StopSimulation

        return dut, mon, reloj(clk), estimulo

    simular(tb())
