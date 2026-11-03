"""CP-11: ciclo de trabajo de cada nivel de volumen = (volumen + 1) / 8."""
from myhdl import block, instance, Signal, ResetSignal, intbv, StopSimulation

from pwm_volumen import pwm_volumen
from utilidades import reloj, simular


def test_cp11_ocho_niveles():
    clk = Signal(bool(0))
    rst = ResetSignal(1, active=1, isasync=False)
    vol = Signal(intbv(0)[3:])
    pwm = Signal(bool(0))

    @block
    def tb():
        dut = pwm_volumen(clk, rst, vol, pwm)

        @instance
        def estimulo():
            yield clk.posedge
            rst.next = 0
            for v in range(8):
                vol.next = v
                for _ in range(300):          # deja asentar el nuevo nivel
                    yield clk.posedge
                altos = 0
                for _ in range(256 * 4):
                    yield clk.posedge
                    altos += int(pwm)
                assert altos == (v + 1) * 32 * 4, (v, altos)
            raise StopSimulation

        return dut, reloj(clk), estimulo

    simular(tb())
