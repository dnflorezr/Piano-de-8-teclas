"""Entidad de nivel superior del piano digital de 8 teclas (Fig. 1, Tabla I).

Puertos:
  clk      100 MHz (CLK100MHZ)
  rst      BTNC, activo en alto
  teclas   SW7..SW0  (SW0 = C4 ... SW7 = C5)
  volumen  SW15..SW13 (8 niveles de ciclo de trabajo)
  melodia  BTNU: inicia / detiene la melodía automática
  tono     AUD_PWM (drenador abierto: '0' o 'Z', ver manual de la placa)
  aud_en   AUD_SD  (habilita el amplificador de audio)
  leds     LD7..LD0 (nota que suena)
"""
from myhdl import (block, always_seq, always_comb, Signal, ResetSignal,
                   intbv)

import parametros as P
from sincronizador import sincronizador
from sincronizador_reset import sincronizador_reset
from antirrebote import antirrebote
from codificador_prioridad import codificador_prioridad
from tabla_divisores import tabla_divisores
from generador_tono import generador_tono
from pwm_volumen import pwm_volumen
from salida_drenador_abierto import salida_drenador_abierto
from melodia_fsm import melodia_fsm

UNO_CALIENTE = tuple(1 << k for k in range(8))


@block
def piano_top(clk, rst, teclas, volumen, melodia, tono, aud_en, leds,
              FCLK=P.FCLK_PLACA, CON_MELODIA=True,
              T_TIEMPO=P.T_TIEMPO, T_PAUSA=P.T_PAUSA,
              T_ANTIRREBOTE=P.T_ANTIRREBOTE, MELODIA=P.MELODIA):
    TABLA = P.tabla_divisores(FCLK)
    NMAX = max(TABLA) + 1

    # ---- reinicio sincronizado ----
    rst_s = ResetSignal(1, active=1, isasync=False)
    u_rst = sincronizador_reset(clk, rst, rst_s)

    # ---- sincronización de entradas (2 biestables) ----
    teclas_s = Signal(intbv(0)[8:])
    volumen_s = Signal(intbv(0)[3:])
    melodia_s = Signal(bool(0))
    u_sync_t = sincronizador(clk, rst_s, teclas, teclas_s)
    u_sync_v = sincronizador(clk, rst_s, volumen, volumen_s)
    u_sync_m = sincronizador(clk, rst_s, melodia, melodia_s)

    # ---- detección de tecla activa ----
    idx_tecla = Signal(intbv(0, min=0, max=8))
    hay_tecla = Signal(bool(0))
    u_cod = codificador_prioridad(teclas_s, idx_tecla, hay_tecla)

    # ---- melodía automática (opcional) ----
    m_sonando = Signal(bool(0))
    m_nota = Signal(intbv(0, min=0, max=8))
    m_estado = Signal(intbv(0, min=0, max=8))
    inicio = Signal(bool(0))
    bloques_melodia = []
    if CON_MELODIA:
        notas = tuple(n for n, _ in MELODIA)
        dur = tuple(P.ciclos(d * T_TIEMPO, FCLK) for _, d in MELODIA)
        u_ar = antirrebote(clk, rst_s, melodia_s, inicio,
                           CICLOS=P.ciclos(T_ANTIRREBOTE, FCLK))
        u_fsm = melodia_fsm(clk, rst_s, inicio, hay_tecla, m_sonando, m_nota,
                            m_estado, NOTAS=notas, DURACIONES=dur,
                            PAUSA=P.ciclos(T_PAUSA, FCLK))
        bloques_melodia = [u_ar, u_fsm]

    # ---- multiplexor: el teclado manual tiene prioridad ----
    idx_sel = Signal(intbv(0, min=0, max=8))
    sonar = Signal(bool(0))

    @always_comb
    def multiplexor():
        if hay_tecla:
            idx_sel.next = idx_tecla
            sonar.next = 1
        elif m_sonando:
            idx_sel.next = m_nota
            sonar.next = 1
        else:
            idx_sel.next = 0
            sonar.next = 0

    # ---- selector de divisor y generador de tono ----
    divisor = Signal(intbv(0, min=0, max=NMAX))
    onda = Signal(bool(0))
    u_tab = tabla_divisores(idx_sel, divisor, TABLA=TABLA)
    u_gen = generador_tono(clk, rst_s, divisor, sonar, onda)

    # ---- volumen PWM ----
    pwm = Signal(bool(0))
    u_pwm = pwm_volumen(clk, rst_s, volumen_s, pwm)

    # ---- salidas registradas ----
    audio = Signal(bool(0))
    leds_r = Signal(intbv(0)[8:])
    aud_en_r = Signal(bool(0))

    @always_seq(clk.posedge, reset=rst_s)
    def registro_salidas():
        audio.next = onda and pwm            # tono AND pwm
        aud_en_r.next = 1                    # 0 durante el reinicio
        if sonar:
            leds_r.next = UNO_CALIENTE[idx_sel]
        else:
            leds_r.next = 0

    # AUD_PWM es de drenador abierto: '1' lógico = alta impedancia (Z).
    salida_audio = salida_drenador_abierto(audio, tono)

    @always_comb
    def salidas():
        leds.next = leds_r
        aud_en.next = aud_en_r

    return (u_rst, u_sync_t, u_sync_v, u_sync_m, u_cod, bloques_melodia,
            multiplexor, u_tab, u_gen, u_pwm, registro_salidas,
            salida_audio, salidas)
