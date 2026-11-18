"""Pruebas unitarias de los sincronizadores (Sección V-D).

- sincronizador: la salida reproduce la entrada exactamente dos ciclos
  después (dos biestables en cascada), para buses y para señales de 1 bit.
- sincronizador_reset: el reinicio síncrono sigue al pulsador BTNC con dos
  ciclos de retardo y arranca activo al encender.
"""
from myhdl import (block, instance, always, Signal, ResetSignal, intbv,
                   StopSimulation)

from sincronizador import sincronizador
from sincronizador_reset import sincronizador_reset
from utilidades import reloj, simular

SECUENCIA = [0, 0x5A, 0xFF, 0x01, 0x80, 0x3C, 0x00, 0xA5, 0xA5, 0x7E]


def test_sincronizador_bus_retardo_de_dos_ciclos():
    clk = Signal(bool(0))
    rst = ResetSignal(1, active=1, isasync=False)
    ent = Signal(intbv(0)[8:])
    sal = Signal(intbv(0)[8:])
    salidas = []

    @block
    def tb():
        dut = sincronizador(clk, rst, ent, sal)

        @always(clk.posedge)
        def mon():
            salidas.append(int(sal))

        @instance
        def estimulo():
            yield clk.posedge
            rst.next = 0
            yield clk.posedge
            del salidas[:]
            for v in SECUENCIA:
                ent.next = v
                yield clk.posedge
            for _ in range(3):
                yield clk.posedge
            raise StopSimulation

        return dut, reloj(clk), mon, estimulo

    simular(tb())
    # El monitor lee `sal` justo antes de que se actualice en cada flanco.
    # Un valor aplicado antes del flanco k entra al primer biestable en k,
    # llega a la salida en k + 1 y el monitor lo lee en k + 2; como la
    # secuencia empieza a aplicarse antes del flanco 1, aparece desde la
    # muestra 3: dos ciclos de retardo, sin pérdidas ni reordenamientos.
    assert salidas[3:3 + len(SECUENCIA)] == SECUENCIA, salidas


def test_sincronizador_un_bit_y_reinicio():
    clk = Signal(bool(0))
    rst = ResetSignal(1, active=1, isasync=False)
    ent = Signal(bool(1))
    sal = Signal(bool(0))

    @block
    def tb():
        dut = sincronizador(clk, rst, ent, sal)

        @instance
        def estimulo():
            for _ in range(5):                 # durante el reinicio: 0
                yield clk.posedge
                yield clk.negedge
                assert sal == 0
            rst.next = 0
            yield clk.posedge
            yield clk.negedge
            assert sal == 0                    # primer biestable aún cargando
            yield clk.posedge
            yield clk.negedge
            assert sal == 1                    # segundo ciclo: llega la entrada
            raise StopSimulation

        return dut, reloj(clk), estimulo

    simular(tb())


def test_sincronizador_reset():
    clk = Signal(bool(0))
    btn = Signal(bool(0))
    rst_s = Signal(bool(0))
    valores = []

    @block
    def tb():
        dut = sincronizador_reset(clk, btn, rst_s)

        @always(clk.posedge)
        def mon():
            valores.append(int(rst_s))

        @instance
        def estimulo():
            for _ in range(4):
                yield clk.posedge
            btn.next = 1
            for _ in range(4):
                yield clk.posedge
            btn.next = 0
            for _ in range(4):
                yield clk.posedge
            raise StopSimulation

        return dut, reloj(clk), mon, estimulo

    simular(tb())
    # Al encender la primera etapa vale 1: el sistema arranca en reinicio y
    # sale de él dos flancos después; luego sigue a BTNC con 2 ciclos.
    # Misma convención de muestreo que arriba (el monitor lee el valor previo
    # al flanco). Al encender la primera etapa vale 1, así que el sistema
    # arranca en reinicio y sale de él solo; después rst_s sigue a BTNC con
    # dos ciclos de retardo: BTNC sube antes del flanco 4 -> se lee en 6;
    # baja antes del flanco 8 -> se lee en 10.
    assert valores[1] == 1, valores
    assert valores[2:6] == [0, 0, 0, 0], valores
    assert valores[6:10] == [1, 1, 1, 1], valores
    assert valores[10] == 0, valores
