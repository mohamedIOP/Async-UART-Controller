####################################################################################
# Section 0 : DC Variables
#################################################################################### 
set_fix_multiple_port_nets -all -buffer_constants -feedthroughs

####################################################################################
# Section 1 : Clock Definition
#################################################################################### 
set REF_CLK_Period  20.0
set UART_CLK_Period 271.296799

# 1. Master Clocks
create_clock -period $REF_CLK_Period  -name "REF_CLK"  [get_ports REF_CLK]
create_clock -period $UART_CLK_Period -name "UART_CLK" [get_ports UART_CLK]
create_clock -period $REF_CLK_Period  -name "SCAN_CLK" [get_ports scan_clk]

# 2. Generated Clocks (Using get_pins for internal block pins)
create_generated_clock -master_clock "REF_CLK"  -source [get_ports REF_CLK]  -name "ALU_CLK" -divide_by 1  [get_pins U_CLK_GATE/GATED_CLK]
create_generated_clock -master_clock "UART_CLK" -source [get_ports UART_CLK] -name "RX_CLK"  -divide_by 1  [get_pins U_ClkDiv_RX/o_div_clk]
create_generated_clock -master_clock "UART_CLK" -source [get_ports UART_CLK] -name "TX_CLK"  -divide_by 32 [get_pins U_ClkDiv_TX/o_div_clk]

set_clock_uncertainty -setup 0.2 [get_clocks {REF_CLK UART_CLK ALU_CLK RX_CLK TX_CLK SCAN_CLK}]
set_clock_uncertainty -hold  0.1 [get_clocks {REF_CLK UART_CLK ALU_CLK RX_CLK TX_CLK SCAN_CLK}]
set_clock_transition 0.05        [get_clocks {REF_CLK UART_CLK SCAN_CLK}]

set_dont_touch_network [get_clocks {REF_CLK UART_CLK ALU_CLK RX_CLK TX_CLK SCAN_CLK}]

####################################################################################
# Section 2 : Clock Relationships
####################################################################################
set_clock_groups -asynchronous \
                 -group {REF_CLK ALU_CLK} \
                 -group {UART_CLK RX_CLK TX_CLK} \
                 -group {SCAN_CLK}

####################################################################################
# Section 3 : Input / Output Delays
####################################################################################
set_input_delay  [expr 0.2*$UART_CLK_Period]     -clock RX_CLK   [get_ports RX_IN]
set_input_delay  [expr 0.2*$REF_CLK_Period]      -clock SCAN_CLK [get_ports SI]
set_input_delay  [expr 0.2*$REF_CLK_Period]      -clock SCAN_CLK [get_ports SE]
set_output_delay [expr 0.2*$REF_CLK_Period]      -clock SCAN_CLK [get_ports SO]
set_output_delay [expr 0.2*$UART_CLK_Period*32] -clock TX_CLK   [get_ports TX_OUT]
set_output_delay [expr 0.2*$UART_CLK_Period]    -clock RX_CLK   [get_ports RF_PAR_ERR]
set_output_delay [expr 0.2*$UART_CLK_Period]    -clock RX_CLK   [get_ports RF_STP_ERR]

####################################################################################
# Section 4 : Driving Cells & Output Load
####################################################################################
set_driving_cell -library "scmetro_tsmc_cl013g_rvt_ss_1p08v_125c" -lib_cell BUFX2M -pin Y [get_ports {RX_IN SI SE}]
set_load 0.1 [get_ports {TX_OUT RF_PAR_ERR RF_STP_ERR SO}]

####################################################################################
# Section 5 : Operating Conditions & Modes
####################################################################################
set_operating_conditions -min_library "scmetro_tsmc_cl013g_rvt_ff_1p32v_m40c" -min "scmetro_tsmc_cl013g_rvt_ff_1p32v_m40c" \
                         -max_library "scmetro_tsmc_cl013g_rvt_ss_1p08v_125c" -max "scmetro_tsmc_cl013g_rvt_ss_1p08v_125c"

# Force functional mode during initial synthesis
set_case_analysis 1 [get_ports test_mode]