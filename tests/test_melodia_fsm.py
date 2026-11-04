"""Máquina de estados de la melodía: CP-7, CP-8, CP-9, CP-10, CP-15,
detención con una segunda pulsación de BTNU y selección de canción."""
from myhdl import (block, instance, always, Signal, ResetSignal, intbv,
                   StopSimulation)

from melodia_fsm import melodia_fsm
from utilidades import reloj, simular

IDLE, LOAD, PLAY, GAP, FIN = range(5)
NOTAS = (2, 0, 7, 7)            # E4, C4, C5, C5 (repetición: la separa GAP)
DUR = (10, 5, 8, 6)
PAUSA = 3
NOTAS_B = (5, 6, 1)             # segunda canción: A4, B4, D4
DUR_B = (4, 7, 2)
CANCIONES = ((NOTAS, DUR), (NOTAS_B, DUR_B))   # SEL 2 y 3 -> canción 0


def armar():
    s = dict(
        clk=Signal(bool(0)),
        rst=ResetSignal(1, active=1, isasync=False),
        inicio=Signal(bool(0)),
        tecla=Signal(bool(0)),
        sel=Signal(intbv(0)[2:]),
        sonando=Signal(bool(0)),
        nota=Signal(intbv(0, min=0, max=8)),
        estado=Signal(intbv(0, min=0, max=8)),
    )
    return s


@block
def dut(s):
    return melodia_fsm(s["clk"], s["rst"], s["inicio"], s["tecla"], s["sel"],
                       s["sonando"], s["nota"], s["estado"],
                       CANCIONES=CANCIONES, PAUSA=PAUSA)


@block
def traza(s, registro):
    @always(s["clk"].posedge)
    def mon():
        registro.append((int(s["estado"]), int(s["sonando"]), int(s["nota"])))
    return mon


def pulso(s):
    s["inicio"].next = 1
    yield s["clk"].posedge
    s["inicio"].next = 0


def comprimir(tr):
    """Lista de (estado, nota, duración) agrupando ciclos consecutivos."""
    res = []
    for e, _, n in tr:
        clave = (e, n if e == PLAY else None)
        if res and res[-1][0] == clave:
            res[-1][1] += 1
        else:
            res.append([clave, 1])
    return [(c[0], c[1], d) for c, d in res]


def tocar_completa(sel, notas, dur, cambiar_sel_a=None):
    """Toca la canción `sel` de principio a fin y compara la secuencia de
    estados con (notas, dur). Si cambiar_sel_a no es None, mueve los
    interruptores en plena canción (no debe afectar)."""
    s = armar()
    s["sel"] = Signal(intbv(sel)[2:])
    tr = []

    @block
    def tb():
        @instance
        def estimulo():
            yield s["clk"].posedge
            s["rst"].next = 0
            yield s["clk"].posedge
            del tr[:]
            yield pulso(s)
            if cambiar_sel_a is not None:
                for _ in range(dur[0] // 2):
                    yield s["clk"].posedge
                s["sel"].next = cambiar_sel_a
            for _ in range(sum(dur) + len(dur) * (PAUSA + 1) + 10):
                yield s["clk"].posedge
            raise StopSimulation
        return dut(s), traza(s, tr), reloj(s["clk"]), estimulo

    simular(tb())
    seq = comprimir(tr)
    # quitar el IDLE inicial y final
    assert seq[0][0] == IDLE and seq[-1][0] == IDLE
    cuerpo = seq[1:-1]
    esperado = []
    for n, d in zip(notas, dur):
        esperado += [(LOAD, None, 1), (PLAY, n, d), (GAP, None, PAUSA)]
    esperado += [(FIN, None, 1)]
    assert cuerpo == esperado, cuerpo
    # 'sonando' solo en PLAY
    assert all(son == (e == PLAY) for e, son, _ in tr)


def test_cp8_cp9_cp10_melodia_completa():
    tocar_completa(0, NOTAS, DUR)


def test_seleccion_segunda_cancion():
    tocar_completa(1, NOTAS_B, DUR_B)


def test_seleccion_sin_cancion_toca_la_primera():
    tocar_completa(3, NOTAS, DUR)


def test_cambiar_seleccion_durante_cancion_no_afecta():
    tocar_completa(1, NOTAS_B, DUR_B, cambiar_sel_a=0)
    tocar_completa(0, NOTAS, DUR, cambiar_sel_a=1)


def detener(accion):
    s = armar()
    tr = []

    @block
    def tb():
        @instance
        def estimulo():
            yield s["clk"].posedge
            s["rst"].next = 0
            yield pulso(s)
            for _ in range(DUR[0] + PAUSA + 4):   # ya en la segunda nota
                yield s["clk"].posedge
            assert int(s["estado"]) in (LOAD, PLAY, GAP)
            if accion == "boton":
                yield pulso(s)
            elif accion == "tecla":
                s["tecla"].next = 1
                yield s["clk"].posedge
            else:
                s["rst"].next = 1
                yield s["clk"].posedge
            yield s["clk"].posedge
            assert int(s["estado"]) == IDLE and not s["sonando"]
            s["tecla"].next = 0
            s["rst"].next = 0
            for _ in range(50):                     # permanece en reposo
                yield s["clk"].posedge
                assert int(s["estado"]) == IDLE
            raise StopSimulation
        return dut(s), traza(s, tr), reloj(s["clk"]), estimulo

    simular(tb())


def test_detener_con_btnu():
    detener("boton")


def test_cp15_tecla_detiene_melodia():
    detener("tecla")


def test_cp7_reinicio_durante_reproduccion():
    detener("reinicio")


def test_inicio_ignorado_con_tecla_accionada():
    s = armar()

    @block
    def tb():
        @instance
        def estimulo():
            yield s["clk"].posedge
            s["rst"].next = 0
            s["tecla"].next = 1
            yield pulso(s)
            for _ in range(5):
                yield s["clk"].posedge
                assert int(s["estado"]) == IDLE
            raise StopSimulation
        return dut(s), reloj(s["clk"]), estimulo

    simular(tb())
