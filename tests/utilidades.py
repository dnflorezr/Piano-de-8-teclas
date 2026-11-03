"""Utilidades comunes de los bancos de prueba."""
from myhdl import block, always, delay, instance, Signal, StopSimulation


@block
def reloj(clk, semiperiodo=5):
    @always(delay(semiperiodo))
    def gen():
        clk.next = not clk
    return gen


def nivel(sig):
    """Lee una salida de drenador abierto: 'Z' (None) equivale a '1'
    por la resistencia de pull-up de la placa."""
    v = sig.val
    return 1 if v is None else int(v)


def periodos(flancos):
    """Diferencias entre flancos de subida consecutivos (en ciclos)."""
    return [b - a for a, b in zip(flancos, flancos[1:])]


def simular(tb, vcd=False):
    tb.config_sim(trace=vcd)
    tb.run_sim(quiet=1)
