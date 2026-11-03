"""Modulador PWM de volumen (Sección V-E).

Contador libre de 8 bits sobre el reloj de 100 MHz: portadora de
100 MHz / 256 ~ 390 kHz. SW15-SW13 eligen uno de ocho niveles de ciclo de
trabajo: D = (volumen + 1) / 8, es decir 12,5 %, 25 %, ..., 100 %.
"""
from myhdl import block, always_seq, always_comb, Signal, intbv, modbv

UMBRALES = tuple((v + 1) * 32 for v in range(8))  # 32, 64, ..., 256


@block
def pwm_volumen(clk, rst, volumen, pwm):
    cuenta = Signal(modbv(0)[8:])
    umbral = Signal(intbv(0, min=0, max=257))

    @always_comb
    def seleccion():
        umbral.next = UMBRALES[volumen]

    @always_seq(clk.posedge, reset=rst)
    def logica():
        cuenta.next = cuenta + 1
        pwm.next = cuenta < umbral

    return seleccion, logica
