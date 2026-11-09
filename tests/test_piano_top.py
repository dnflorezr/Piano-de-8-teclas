"""Pruebas del sistema completo (piano_top) con reloj reducido.

FCLK = 200 kHz en simulación: los divisores son 382..191 ciclos y los
tiempos de melodía y antirrebote se escalan con C = T * fclk.
Casos: CP-1, CP-2, CP-3, CP-5, CP-7, CP-8..CP-10, CP-11, CP-12, CP-15 y
selección de canción con BTNL / BTNR.
"""
from myhdl import (block, instance, always, Signal, TristateSignal, intbv,
                   StopSimulation)

import parametros as P
from piano_top import piano_top
from utilidades import reloj, nivel, periodos, simular

FCLK = 200_000
TABLA = P.tabla_divisores(FCLK)
MELODIA = ((2, 2), (0, 1), (7, 1))          # E4, C4, C5
MELODIA_B = ((4, 1), (6, 2))                # G4, B4
CANCIONES = (MELODIA, MELODIA_B)
T_TIEMPO = 0.02                             # 4000 ciclos por unidad
T_PAUSA = 0.002                             # 400 ciclos
T_AR = 0.0001                               # 20 ciclos de antirrebote
LAT = 8                                     # latencia entrada -> salida (ciclos)


class Banco:
    def __init__(self):
        self.clk = Signal(bool(0))
        self.rst = Signal(bool(1))
        self.teclas = Signal(intbv(0)[8:])
        self.volumen = Signal(intbv(7)[3:])
        self.melodia = Signal(bool(0))
        self.anterior = Signal(bool(0))
        self.siguiente = Signal(bool(0))
        self.led_cancion = Signal(intbv(0)[4:])
        self.tono = TristateSignal(bool(0))
        self.aud_en = Signal(bool(0))
        self.leds = Signal(intbv(0)[8:])
        self.ciclo = 0
        self.flancos = []
        self.historial_leds = []
        self.altos = 0

    def ciclos(self, n):
        for _ in range(n):
            yield self.clk.posedge

    def soltar_reset(self):
        yield self.ciclos(4)
        self.rst.next = 0
        yield self.ciclos(4)

    def presionar(self, boton):
        boton.next = 1
        yield self.ciclos(int(T_AR * FCLK) + 10)
        boton.next = 0
        yield self.ciclos(int(T_AR * FCLK) + 10)

    def presionar_btnu(self):
        yield self.presionar(self.melodia)


@block
def entorno(b, cuerpo):
    anterior = [0]

    @always(b.clk.posedge)
    def monitor():
        b.ciclo += 1
        v = nivel(b.tono)
        if v and not anterior[0]:
            b.flancos.append(b.ciclo)
        anterior[0] = v
        b.altos += v
        if not b.historial_leds or b.historial_leds[-1] != int(b.leds):
            b.historial_leds.append(int(b.leds))

    dut = piano_top(b.clk, b.rst, b.teclas, b.volumen, b.melodia, b.anterior,
                    b.siguiente, b.tono, b.aud_en, b.leds, b.led_cancion, FCLK=FCLK, T_TIEMPO=T_TIEMPO,
                    T_PAUSA=T_PAUSA, T_ANTIRREBOTE=T_AR, CANCIONES=CANCIONES)

    @instance
    def estimulo():
        yield cuerpo(b)
        raise StopSimulation

    return dut, reloj(b.clk), monitor, estimulo


def correr(cuerpo):
    b = Banco()
    simular(entorno(b, cuerpo))
    return b


def test_cp1_sin_teclas_y_cp2_cada_tecla():
    def cuerpo(b):
        yield b.soltar_reset()
        assert b.aud_en == 1
        yield b.ciclos(2000)                       # CP-1
        assert b.flancos == [] and b.leds == 0 and nivel(b.tono) == 0
        for k, n in enumerate(TABLA):             # CP-2
            b.teclas.next = 1 << k
            yield b.ciclos(LAT)
            del b.flancos[:]
            yield b.ciclos(2 * n * 5)
            ps = periodos(b.flancos)
            assert len(ps) >= 3 and all(p == 2 * n for p in ps), (k, ps)
            assert b.leds == (1 << k)
            b.teclas.next = 0
            yield b.ciclos(LAT + n)
            assert b.leds == 0 and nivel(b.tono) == 0
    correr(cuerpo)


def test_cp3_varias_teclas():
    def cuerpo(b):
        yield b.soltar_reset()
        for comb in (0b11111111, 0b10100000, 0b00011000, 0b10000001, 0b01000100):
            b.teclas.next = comb
            menor = (comb & -comb).bit_length() - 1
            yield b.ciclos(LAT)
            del b.flancos[:]
            yield b.ciclos(2 * TABLA[menor] * 4)
            assert b.leds == (1 << menor)          # una sola nota activa
            ps = periodos(b.flancos)
            assert ps and all(p == 2 * TABLA[menor] for p in ps)
    correr(cuerpo)


def test_cp5_accionamiento_breve():
    def cuerpo(b):
        yield b.soltar_reset()
        n = TABLA[7]
        b.teclas.next = 1 << 7
        yield b.ciclos(int(1.5 * n))               # menos de un período
        b.teclas.next = 0
        yield b.ciclos(LAT)
        assert len(b.flancos) == 1                 # sonó mientras estuvo activa
        assert 1 << 7 in b.historial_leds
        yield b.ciclos(3 * n)
        assert len(b.flancos) == 1 and nivel(b.tono) == 0 and b.leds == 0
    correr(cuerpo)


def test_cp11_volumen_en_la_salida():
    def cuerpo(b):
        yield b.soltar_reset()
        n = TABLA[0]
        b.teclas.next = 1
        for v in range(8):
            b.volumen.next = v
            yield b.ciclos(2 * n)
            b.altos = 0
            # 64 períodos: la fase entre el tono (764 ciclos) y la portadora
            # PWM (256 ciclos) se desplaza 4 ciclos por período y recorre
            # toda la portadora, así el promedio no queda sesgado.
            yield b.ciclos(2 * n * 64)
            fraccion = b.altos / (2 * n * 64)
            esperado = 0.5 * (v + 1) / 8           # 50 % del tono x D
            assert abs(fraccion - esperado) < 0.01, (v, fraccion)
    correr(cuerpo)


def test_cp12_reinicio_con_tecla_y_cp7():
    def cuerpo(b):
        b.teclas.next = 1 << 4
        yield b.ciclos(3 * TABLA[4])               # reinicio activo
        assert b.flancos == [] and b.aud_en == 0 and b.leds == 0
        b.rst.next = 0
        yield b.ciclos(LAT)
        del b.flancos[:]
        yield b.ciclos(2 * TABLA[4] * 4)
        ps = periodos(b.flancos)
        assert ps and all(p == 2 * TABLA[4] for p in ps)
        # CP-7: reinicio en plena reproducción
        b.rst.next = 1
        yield b.ciclos(LAT)
        assert b.leds == 0 and b.aud_en == 0 and nivel(b.tono) == 0
    correr(cuerpo)


def test_cp8_cp9_cp10_melodia_y_cp15():
    def cuerpo(b):
        yield b.soltar_reset()
        del b.historial_leds[:]
        yield b.presionar_btnu()
        total = sum(P.ciclos(d * T_TIEMPO, FCLK) for _, d in MELODIA)
        total += len(MELODIA) * (P.ciclos(T_PAUSA, FCLK) + 1) + 200
        yield b.ciclos(total)
        notas = [l for l in b.historial_leds if l]
        assert notas == [1 << n for n, _ in MELODIA], b.historial_leds
        assert b.leds == 0                         # volvió a IDLE (CP-10)
        # CP-15: una tecla durante la melodía la detiene
        yield b.presionar_btnu()
        yield b.ciclos(500)
        assert b.leds == (1 << MELODIA[0][0])
        b.teclas.next = 1 << 5
        yield b.ciclos(LAT)
        assert b.leds == (1 << 5)
        b.teclas.next = 0
        yield b.ciclos(total)
        assert b.leds == 0                         # la melodía no se reanuda
        # Segunda pulsación de BTNU detiene la melodía
        yield b.presionar_btnu()
        yield b.ciclos(500)
        assert b.leds != 0
        yield b.presionar_btnu()
        yield b.ciclos(LAT)
        assert b.leds == 0
    correr(cuerpo)


def duracion_total(melodia):
    total = sum(P.ciclos(d * T_TIEMPO, FCLK) for _, d in melodia)
    return total + len(melodia) * (P.ciclos(T_PAUSA, FCLK) + 1) + 200


def test_seleccion_de_cancion_con_btnl_btnr():
    def cuerpo(b):
        yield b.soltar_reset()
        assert b.led_cancion == 0b0001             # tras el reinicio: canción 0
        # (botón, canción esperada): BTNR avanza, BTNL retrocede, da la vuelta
        pasos = ((b.siguiente, 1), (b.siguiente, 0), (b.anterior, 1),
                 (b.anterior, 0))
        for boton, esperada in pasos:
            yield b.presionar(boton)
            assert b.led_cancion == 1 << esperada, (esperada, int(b.led_cancion))
            melodia = CANCIONES[esperada]
            del b.historial_leds[:]
            yield b.presionar_btnu()
            yield b.ciclos(duracion_total(melodia))
            notas = [l for l in b.historial_leds if l]
            assert notas == [1 << n for n, _ in melodia], (esperada, b.historial_leds)
            assert b.leds == 0
        # Cambiar de canción mientras suena no altera la que está sonando
        yield b.presionar(b.siguiente)              # elegida: canción 1
        del b.historial_leds[:]
        yield b.presionar_btnu()
        yield b.presionar(b.anterior)               # elegida: canción 0
        assert b.led_cancion == 0b0001
        yield b.ciclos(duracion_total(MELODIA_B))
        notas = [l for l in b.historial_leds if l]
        assert notas == [1 << n for n, _ in MELODIA_B], b.historial_leds
        # BTNC reinicia la selección
        yield b.presionar(b.siguiente)
        assert b.led_cancion == 0b0010
        b.rst.next = 1
        yield b.ciclos(LAT)
        b.rst.next = 0
        yield b.ciclos(LAT)
        assert b.led_cancion == 0b0001
    correr(cuerpo)
