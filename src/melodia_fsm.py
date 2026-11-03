"""Máquina de estados de la melodía automática (Sección V-F, Fig. 2).

Estados: IDLE -> LOAD -> PLAY -> GAP -> (LOAD ... | FIN) -> IDLE
(El estado END de la Fig. 2 se llama FIN porque END es palabra reservada
de VHDL.)

- `inicio`: pulso de un ciclo (BTNU con antirrebote). En IDLE arranca la
  melodía; en LOAD/PLAY/GAP la detiene.
- `tecla_activa`: cualquier tecla manual detiene la melodía (CP-15).
- `sonando`: 1 solo en PLAY.  `nota`: índice 0..7 de la nota actual.
- `estado_dbg`: código del estado (0 IDLE, 1 LOAD, 2 PLAY, 3 GAP, 4 FIN),
  útil para la simulación.
"""
from myhdl import block, always_seq, always_comb, Signal, intbv, enum

t_estado = enum("IDLE", "LOAD", "PLAY", "GAP", "FIN")


@block
def melodia_fsm(clk, rst, inicio, tecla_activa, sonando, nota, estado_dbg,
                NOTAS, DURACIONES, PAUSA):
    """NOTAS: tupla de índices de nota; DURACIONES: tupla de duraciones en
    ciclos de reloj (C = T * fclk); PAUSA: ciclos de silencio entre notas."""
    NOTAS = tuple(int(x) for x in NOTAS)
    DURACIONES = tuple(int(x) for x in DURACIONES)
    PAUSA = int(PAUSA)
    n = len(NOTAS)
    assert n == len(DURACIONES) and n >= 1

    estado = Signal(t_estado.IDLE)
    i = Signal(intbv(0, min=0, max=n))
    LIMITE = max(max(DURACIONES), PAUSA)
    temporizador = Signal(intbv(0, min=0, max=LIMITE + 1))
    duracion = Signal(intbv(0, min=0, max=LIMITE + 1))
    nota_reg = Signal(intbv(0, min=0, max=8))

    @always_comb
    def tabla():
        duracion.next = DURACIONES[i]

    @always_seq(clk.posedge, reset=rst)
    def fsm():
        if estado == t_estado.IDLE:
            temporizador.next = 0
            i.next = 0
            if inicio and not tecla_activa:
                estado.next = t_estado.LOAD

        elif inicio or tecla_activa:
            # Detener: nueva pulsación de BTNU o tecla manual.
            estado.next = t_estado.IDLE
            temporizador.next = 0
            i.next = 0

        elif estado == t_estado.LOAD:
            nota_reg.next = NOTAS[i]
            temporizador.next = 0
            estado.next = t_estado.PLAY      # "listo" un ciclo después

        elif estado == t_estado.PLAY:
            if temporizador >= duracion - 1:
                temporizador.next = 0
                estado.next = t_estado.GAP
            else:
                temporizador.next = temporizador + 1

        elif estado == t_estado.GAP:
            if temporizador >= PAUSA - 1:
                temporizador.next = 0
                if i == n - 1:
                    estado.next = t_estado.FIN
                else:
                    i.next = i + 1
                    estado.next = t_estado.LOAD
            else:
                temporizador.next = temporizador + 1

        else:  # FIN -> IDLE automáticamente ("auto")
            estado.next = t_estado.IDLE
            i.next = 0

    @always_comb
    def salidas():
        sonando.next = estado == t_estado.PLAY
        nota.next = nota_reg
        if estado == t_estado.IDLE:
            estado_dbg.next = 0
        elif estado == t_estado.LOAD:
            estado_dbg.next = 1
        elif estado == t_estado.PLAY:
            estado_dbg.next = 2
        elif estado == t_estado.GAP:
            estado_dbg.next = 3
        else:
            estado_dbg.next = 4

    return tabla, fsm, salidas
