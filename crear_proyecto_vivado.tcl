# Crea el proyecto de Vivado del piano digital (Nexys 4 DDR, XC7A100T).
# Uso, desde la carpeta del proyecto, en la consola Tcl de Vivado:
#     cd {C:/Users/diego/Piano de 8 teclas/codigo}
#     source crear_proyecto_vivado.tcl
# Antes, generar el VHDL con:  python src/convertir_vhdl.py

set raiz [file normalize [file dirname [info script]]]
create_project piano_8_teclas [file join $raiz vivado] -part xc7a100tcsg324-1 -force
set_property target_language VHDL [current_project]

add_files -norecurse [list \
    [file join $raiz vhdl pck_myhdl_011.vhd] \
    [file join $raiz vhdl piano_top.vhd]]
add_files -fileset constrs_1 -norecurse [file join $raiz xdc piano_nexys4ddr.xdc]
add_files -fileset sim_1 -norecurse [file join $raiz vhdl sim tb_piano_top.vhd]

set_property top piano_top [current_fileset]
set_property top tb_piano_top [get_filesets sim_1]
set_property -name {xsim.simulate.runtime} -value {all} -objects [get_filesets sim_1]
update_compile_order -fileset sources_1

puts "Proyecto creado. Siguiente paso: Run Synthesis / Run Implementation / Generate Bitstream."
