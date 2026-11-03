## Piano digital de 8 teclas - Nexys 4 DDR (XC7A100T-1CSG324C)
## Basado en Nexys-4-DDR-Master.xdc (Digilent). Los nombres de puerto son los
## de la entidad piano_top generada por MyHDL. Antes de implementar, comparar
## los pines con el archivo maestro de Digilent.

## Reloj de 100 MHz
set_property -dict { PACKAGE_PIN E3    IOSTANDARD LVCMOS33 } [get_ports { clk }]; #IO_L12P_T1_MRCC_35 Sch=clk100mhz
create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports { clk }];

## Teclas: SW0..SW7 -> teclas[0..7]  (C4 D4 E4 F4 G4 A4 B4 C5)
set_property -dict { PACKAGE_PIN J15   IOSTANDARD LVCMOS33 } [get_ports { teclas[0] }]; #Sch=sw[0]
set_property -dict { PACKAGE_PIN L16   IOSTANDARD LVCMOS33 } [get_ports { teclas[1] }]; #Sch=sw[1]
set_property -dict { PACKAGE_PIN M13   IOSTANDARD LVCMOS33 } [get_ports { teclas[2] }]; #Sch=sw[2]
set_property -dict { PACKAGE_PIN R15   IOSTANDARD LVCMOS33 } [get_ports { teclas[3] }]; #Sch=sw[3]
set_property -dict { PACKAGE_PIN R17   IOSTANDARD LVCMOS33 } [get_ports { teclas[4] }]; #Sch=sw[4]
set_property -dict { PACKAGE_PIN T18   IOSTANDARD LVCMOS33 } [get_ports { teclas[5] }]; #Sch=sw[5]
set_property -dict { PACKAGE_PIN U18   IOSTANDARD LVCMOS33 } [get_ports { teclas[6] }]; #Sch=sw[6]
set_property -dict { PACKAGE_PIN R13   IOSTANDARD LVCMOS33 } [get_ports { teclas[7] }]; #Sch=sw[7]

## Volumen: SW13..SW15 -> volumen[0..2]
set_property -dict { PACKAGE_PIN U12   IOSTANDARD LVCMOS33 } [get_ports { volumen[0] }]; #Sch=sw[13]
set_property -dict { PACKAGE_PIN U11   IOSTANDARD LVCMOS33 } [get_ports { volumen[1] }]; #Sch=sw[14]
set_property -dict { PACKAGE_PIN V10   IOSTANDARD LVCMOS33 } [get_ports { volumen[2] }]; #Sch=sw[15]

## LED LD0..LD7 -> leds[0..7]
set_property -dict { PACKAGE_PIN H17   IOSTANDARD LVCMOS33 } [get_ports { leds[0] }]; #Sch=led[0]
set_property -dict { PACKAGE_PIN K15   IOSTANDARD LVCMOS33 } [get_ports { leds[1] }]; #Sch=led[1]
set_property -dict { PACKAGE_PIN J13   IOSTANDARD LVCMOS33 } [get_ports { leds[2] }]; #Sch=led[2]
set_property -dict { PACKAGE_PIN N14   IOSTANDARD LVCMOS33 } [get_ports { leds[3] }]; #Sch=led[3]
set_property -dict { PACKAGE_PIN R18   IOSTANDARD LVCMOS33 } [get_ports { leds[4] }]; #Sch=led[4]
set_property -dict { PACKAGE_PIN V17   IOSTANDARD LVCMOS33 } [get_ports { leds[5] }]; #Sch=led[5]
set_property -dict { PACKAGE_PIN U17   IOSTANDARD LVCMOS33 } [get_ports { leds[6] }]; #Sch=led[6]
set_property -dict { PACKAGE_PIN U16   IOSTANDARD LVCMOS33 } [get_ports { leds[7] }]; #Sch=led[7]

## Pulsadores: BTNC = reinicio, BTNU = melodía
set_property -dict { PACKAGE_PIN N17   IOSTANDARD LVCMOS33 } [get_ports { rst }];     #Sch=btnc
set_property -dict { PACKAGE_PIN M18   IOSTANDARD LVCMOS33 } [get_ports { melodia }]; #Sch=btnu

## Audio (alternativa A): AUD_PWM (drenador abierto) y AUD_SD
set_property -dict { PACKAGE_PIN A11   IOSTANDARD LVCMOS33 } [get_ports { tono }];   #IO_L4N_T0_15 Sch=aud_pwm
set_property -dict { PACKAGE_PIN D12   IOSTANDARD LVCMOS33 } [get_ports { aud_en }]; #IO_L6P_T0_15 Sch=aud_sd

## Las entradas son asíncronas (interruptores y pulsadores) y pasan por
## sincronizadores de dos biestables: no tienen requisitos de temporización.
set_false_path -from [get_ports { teclas[*] volumen[*] rst melodia }]

## Configuración del dispositivo
set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
