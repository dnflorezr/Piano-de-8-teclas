"""Convierte el diseño MyHDL a VHDL para Vivado.

Uso:  python convertir_vhdl.py
Genera ../vhdl/piano_top.vhd (diseño completo, 100 MHz) y los módulos
individuales en ../vhdl/modulos/.
"""
import os
from myhdl import Signal, ResetSignal, TristateSignal, intbv

import parametros as P
from piano_top import piano_top
from sincronizador import sincronizador
from antirrebote import antirrebote
from codificador_prioridad import codificador_prioridad
from tabla_divisores import tabla_divisores
from generador_tono import generador_tono
from pwm_volumen import pwm_volumen
from melodia_fsm import melodia_fsm
from selector_cancion import selector_cancion

AQUI = os.path.dirname(os.path.abspath(__file__))
DIR_VHDL = os.path.join(AQUI, "..", "vhdl")
DIR_MOD = os.path.join(DIR_VHDL, "modulos")


def top():
    clk, rst, melodia, anterior, siguiente, aud_en = (
        Signal(bool(0)) for _ in range(6))
    teclas = Signal(intbv(0)[8:])
    volumen = Signal(intbv(0)[3:])
    leds = Signal(intbv(0)[8:])
    led_cancion = Signal(intbv(0)[4:])
    tono = TristateSignal(bool(0))
    inst = piano_top(clk, rst, teclas, volumen, melodia, anterior, siguiente,
                     tono, aud_en, leds, led_cancion)
    inst.convert(hdl="VHDL", path=DIR_VHDL, name="piano_top")
    conectar_drenador_abierto(os.path.join(DIR_VHDL, "piano_top.vhd"), "tono")


def conectar_drenador_abierto(archivo, puerto):
    """MyHDL 0.11 declara el driver del TristateSignal como una señal interna
    (salida_drenador_abierto0_drv) y no lo conecta al puerto. Aquí se
    sustituye esa señal por el puerto, de modo que en el VHDL quede
    `tono <= 'Z' / '0'`, que es lo que exige AUD_PWM."""
    drv = "salida_drenador_abierto0_drv"
    with open(archivo) as f:
        lineas = f.readlines()
    salida = []
    for linea in lineas:
        if linea.strip().startswith("signal %s:" % drv):
            continue
        salida.append(linea.replace(drv, puerto))
    texto = "".join(salida)
    assert ("%s <= tern_op" % puerto) in texto, "no se encontró el driver de tono"
    with open(archivo, "w") as f:
        f.write(texto)


def modulos():
    clk = Signal(bool(0))
    rst = ResetSignal(0, active=1, isasync=False)
    tabla = P.tabla_divisores()
    nmax = max(tabla) + 1

    def conv(inst, nombre):
        inst.convert(hdl="VHDL", path=DIR_MOD, name=nombre)

    conv(sincronizador(clk, rst, Signal(intbv(0)[8:]), Signal(intbv(0)[8:])),
         "sincronizador")
    conv(antirrebote(clk, rst, Signal(bool(0)), Signal(bool(0)),
                     CICLOS=P.ciclos(P.T_ANTIRREBOTE)), "antirrebote")
    conv(codificador_prioridad(Signal(intbv(0)[8:]),
                               Signal(intbv(0, min=0, max=8)), Signal(bool(0))),
         "codificador_prioridad")
    conv(tabla_divisores(Signal(intbv(0, min=0, max=8)),
                         Signal(intbv(0, min=0, max=nmax)), TABLA=tabla),
         "tabla_divisores")
    conv(generador_tono(clk, rst, Signal(intbv(0, min=0, max=nmax)),
                        Signal(bool(0)), Signal(bool(0))), "generador_tono")
    conv(pwm_volumen(clk, rst, Signal(intbv(0)[3:]), Signal(bool(0))),
         "pwm_volumen")
    canciones = [([n for n, _ in c], [P.ciclos(d * P.T_TIEMPO) for _, d in c])
                 for c in P.CANCIONES]
    conv(melodia_fsm(clk, rst, Signal(bool(0)), Signal(bool(0)),
                     Signal(intbv(0)[2:]), Signal(bool(0)),
                     Signal(intbv(0, min=0, max=8)), Signal(intbv(0, min=0, max=8)),
                     CANCIONES=canciones, PAUSA=P.ciclos(P.T_PAUSA)),
         "melodia_fsm")
    conv(selector_cancion(clk, rst, Signal(bool(0)), Signal(bool(0)),
                          Signal(intbv(0)[2:]), Signal(intbv(0)[4:]),
                          N=len(P.CANCIONES)), "selector_cancion")


def limpiar_encabezados():
    """Quita la ruta absoluta del encabezado '-- File:' que escribe MyHDL."""
    for carpeta in (DIR_VHDL, DIR_MOD):
        for nombre in os.listdir(carpeta):
            if not nombre.endswith(".vhd"):
                continue
            ruta = os.path.join(carpeta, nombre)
            with open(ruta) as f:
                lineas = f.readlines()
            if lineas and lineas[0].startswith("-- File:"):
                lineas[0] = "-- File: %s\n" % nombre
                with open(ruta, "w") as f:
                    f.writelines(lineas)


if __name__ == "__main__":
    os.makedirs(DIR_MOD, exist_ok=True)
    top()
    modulos()
    limpiar_encabezados()
    print("VHDL generado en", os.path.normpath(DIR_VHDL))
