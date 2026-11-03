-- Banco de prueba en VHDL para simular en Vivado el piano_top.vhd convertido
-- desde MyHDL, con el reloj real de 100 MHz (sin parámetros reducidos).
--
-- Comprueba sobre el VHDL generado:
--   CP-1  sin teclas: salida en '0' y LED apagados
--   CP-2  cada tecla: período medido = 2N/fclk (Tabla II) y LED correcto
--   CP-3  dos teclas: suena la de menor número
--   CP-11 volumen: con SW15-SW13 = "000" la salida pasa 1/8 del tiempo en alto
--         mientras el tono está en alto
--   CP-8 / CP-15  BTNU inicia la melodía (LED de la primera nota) y una
--         tecla manual la detiene
-- Tiempo simulado aproximado: 70 ms (en Vivado: "run all"; tarda unos minutos).
-- AUD_PWM es de drenador abierto: la placa tiene pull-up, por eso aquí se
-- conecta una resistencia de pull-up ('H') y 'Z' se lee como '1'.

library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity tb_piano_top is
end entity tb_piano_top;

architecture sim of tb_piano_top is
    constant T_CLK : time := 10 ns;
    type t_tabla is array (0 to 7) of integer;
    constant TABLA : t_tabla := (191110, 170265, 151685, 143172,
                                 127551, 113636, 101239, 95557);

    signal clk     : std_logic := '0';
    signal rst     : std_logic := '1';
    signal teclas  : unsigned(7 downto 0) := (others => '0');
    signal volumen : unsigned(2 downto 0) := "111";
    signal melodia : std_logic := '0';
    signal tono    : std_logic;
    signal aud_en  : std_logic;
    signal leds    : unsigned(7 downto 0);
    signal fin     : boolean := false;

    function alto(s : std_logic) return boolean is
    begin
        return to_X01(s) = '1';
    end function;
begin
    tono <= 'H';                          -- pull-up de la placa

    dut : entity work.piano_top
        port map (clk => clk, rst => rst, teclas => teclas,
                  volumen => volumen, melodia => melodia, tono => tono,
                  aud_en => aud_en, leds => leds);

    clk <= not clk after T_CLK / 2 when not fin else '0';

    estimulo : process
        variable t1, t2 : time;
        variable altos, total : integer;
        variable errores : integer := 0;

        -- Mide el período entre dos flancos de subida de la salida.
        procedure medir_periodo(variable p : out time) is
            variable ta : time;
        begin
            wait until rising_edge(clk) and alto(tono);
            wait until rising_edge(clk) and not alto(tono);
            wait until rising_edge(clk) and alto(tono);
            ta := now;
            wait until rising_edge(clk) and not alto(tono);
            wait until rising_edge(clk) and alto(tono);
            p := now - ta;
        end procedure;

        variable periodo : time;
    begin
        wait for 20 * T_CLK;
        rst <= '0';
        wait for 20 * T_CLK;
        assert aud_en = '1' report "AUD_SD no habilitado" severity error;

        -- CP-1
        wait for 100 us;
        assert to_X01(tono) = '0' and leds = 0
            report "CP-1: salida o LED activos sin teclas" severity error;

        -- CP-2: cada tecla
        for k in 0 to 7 loop
            teclas <= (others => '0');
            teclas(k) <= '1';
            wait for 1 us;
            medir_periodo(periodo);
            if periodo /= 2 * TABLA(k) * T_CLK then
                report "CP-2: tecla " & integer'image(k) & " periodo incorrecto"
                    severity error;
                errores := errores + 1;
            else
                report "CP-2: SW" & integer'image(k) & " periodo = "
                    & integer'image(periodo / 1 ns) & " ns OK";
            end if;
            assert leds = shift_left(to_unsigned(1, 8), k)
                report "CP-2: LED incorrecto" severity error;
        end loop;

        -- CP-3: SW7 y SW2 a la vez -> suena SW2 (menor número)
        teclas <= "10000100";
        wait for 1 us;
        medir_periodo(periodo);
        assert periodo = 2 * TABLA(2) * T_CLK and leds = "00000100"
            report "CP-3: prioridad incorrecta" severity error;

        -- CP-11: volumen mínimo, se cuenta el tiempo en alto durante un
        -- semiperíodo alto del tono (debe ser ~1/8)
        teclas <= "00000001";
        volumen <= "000";
        wait for 1 us;
        wait until rising_edge(clk) and alto(tono);
        altos := 0;
        total := 0;
        for c in 1 to TABLA(0) loop
            wait until rising_edge(clk);
            total := total + 1;
            if alto(tono) then
                altos := altos + 1;
            end if;
        end loop;
        report "CP-11: volumen 000 -> " & integer'image(altos) & " de "
            & integer'image(total) & " ciclos en alto";
        assert altos > TABLA(0) / 8 - 300 and altos < TABLA(0) / 8 + 300
            report "CP-11: ciclo de trabajo incorrecto" severity error;
        volumen <= "111";
        teclas <= (others => '0');
        wait for 1 ms;

        -- CP-8: BTNU (más de 10 ms por el antirrebote) inicia la melodía
        melodia <= '1';
        wait for 12 ms;
        melodia <= '0';
        wait for 1 ms;
        assert leds = "00000100"
            report "CP-8: la melodia no inicio en E4" severity error;
        report "CP-8: melodia iniciada, LED = E4";

        -- CP-15: una tecla manual detiene la melodía
        teclas <= "00100000";
        wait for 1 ms;
        assert leds = "00100000" report "CP-15: no suena la tecla" severity error;
        teclas <= (others => '0');
        wait for 1 ms;
        assert leds = 0 report "CP-15: la melodia no se detuvo" severity error;
        report "CP-15: OK";

        report "Fin de la simulacion. Errores CP-2: " & integer'image(errores);
        fin <= true;
        wait;
    end process;
end architecture sim;
