########################### Define Top Module ############################
set top_module SYS_TOP

##################### Define Working Library Directory ######################
define_design_lib work -path ./work

############################# Formality Setup File ##########################
set_svf $top_module.svf

################## Design Compiler Library Setup ######################
puts "###########################################"
puts "#       Setting Design Libraries          #"
puts "###########################################"

lappend search_path /home/IC/tsmc_fb_cl013g_sc/aci/sc-m/synopsys
lappend search_path /home/ICer/IC/Projects/System/std_cells
lappend search_path /home/ICer/IC/Projects/System/rtl

set SSLIB "scmetro_tsmc_cl013g_rvt_ss_1p08v_125c.db"
set TTLIB "scmetro_tsmc_cl013g_rvt_tt_1p2v_25c.db"
set FFLIB "scmetro_tsmc_cl013g_rvt_ff_1p32v_m40c.db"

set target_library [list $SSLIB $TTLIB $FFLIB]
set link_library   [list * $SSLIB $TTLIB $FFLIB]  

######################## Reading RTL Files #################################
puts "###########################################"
puts "#             Reading RTL Files           #"
puts "###########################################"

set fh [open system.lst r+]
set rtl [read $fh]
close $fh

set designs ""
regsub -all "\n" $rtl " " designs

analyze -format sverilog [split $designs]
elaborate $top_module

current_design $top_module

puts "###############################################"
puts "######## Linking & Design Checks ##############"
puts "###############################################"
link 
check_design

#################### Define Design Constraints #########################
puts "###############################################"
puts "############ Design Constraints ###############"
puts "###############################################"
source ./cons.tcl

########################## Define DFT Signals ##########################
puts "###############################################"
puts "############ Setup DFT Signals ################"
puts "###############################################"

set_dft_signal -port [get_ports scan_clk]  -type ScanClock   -view existing_dft -timing {20 40}
set_dft_signal -port [get_ports scan_rst]  -type Reset       -view existing_dft -active_state 0
set_dft_signal -port [get_ports test_mode] -type Constant    -view existing_dft -active_state 1
set_dft_signal -port [get_ports test_mode] -type TestMode    -view spec         -active_state 1
set_dft_signal -port [get_ports SE]        -type ScanEnable  -view spec         -active_state 1 -usage scan
set_dft_signal -port [get_ports SI]        -type ScanDataIn  -view spec 
set_dft_signal -port [get_ports SO]        -type ScanDataOut -view spec 

#################### Configure Scan Chains #########################
puts "###############################################"
puts "############ Configure Scan Chains ############"
puts "###############################################"

set_scan_configuration -chain_count 3 \
                       -clock_mixing no_mix \
                       -style multiplexed_flip_flop \
                       -replace true \
                       -max_length 100

###################### Mapping and Optimization ########################
puts "###############################################"
puts "########## Mapping & Optimization #############"
puts "###############################################"

compile_ultra -scan

############################# Create Test Protocol #######################
create_test_protocol

###################### Pre-DFT Design Rule Checking #######################
dft_drc -verbose

############################# Preview & Insert DFT ##############################
preview_dft -show scan_summary
insert_dft

######################## Optimize Logic Post-DFT #######################
compile_ultra -scan -incremental

###################### Post-DFT Design Rule Checking #######################
dft_drc -verbose -coverage_estimate

##################### Close Formality Setup File ###########################
set_svf -off

#############################################################################
# Write Out Design Files
#############################################################################
write_file -format verilog -hierarchy -output netlists/$top_module.v
write_file -format ddc     -hierarchy -output netlists/$top_module.ddc
write_sdf  sdf/$top_module.sdf
write_sdc  -nosplit sdc/$top_module.sdc

####################### Reporting ##########################################
report_area -hierarchy      > reports/area.rpt
report_power -hierarchy     > reports/power.rpt
report_timing -delay_type min > reports/hold.rpt
report_timing -delay_type max > reports/setup.rpt
report_clock -attributes    > reports/clocks.rpt

exit