
####################################################################################
# Constraints
# ----------------------------------------------------------------------------
#
# 0. Design Compiler variables
#
# 1. Master Clock Definitions
#
# 2. Generated Clock Definitions
#
# 3. Clock Uncertainties
#
# 4. Clock Latencies 
#
# 5. Clock Relationships
#
# 6. #set input/output delay on ports
#
# 7. Driving cells
#
# 8. Output load

####################################################################################
           #########################################################
                  #### Section 0 : DC Variables ####
           #########################################################
#################################################################################### 

# Prevent assign statements in the generated netlist (must be applied before compile command)
set_fix_multiple_port_nets -all -buffer_constants -feedthroughs

####################################################################################
           #########################################################
                  #### Section 1 : Clock Definition ####
           #########################################################
#################################################################################### 
# 1. Master Clock Definitions 
# 2. Generated Clock Definitions
# 3. Clock Latencies
# 4. Clock Uncertainties
# 4. Clock Transitions
####################################################################################
set REF_CLK_Period 20
set UART_CLK_Period 271.296799
#1. Master Clocks
create_clock -period $REF_CLK_Period -name REF_CLK [get_ports REF_CLK]
create_clock -period $UART_CLK_Period -name UART_CLK [get_ports UART_CLK]

#2. Generated clocks
create_generated_clock -master_clock "REF_CLK" -source [get_ports REF_CLK] -name "ALU_CLK" -divide_by 1 [get_port U_CLK_GATE/GATED_CLK]
create_generated_clock -master_clock "UART_CLK" -source [get_ports UART_CLK] -name "RX_CLK" -divide_by 1 [get_port U_ClkDiv_RX/o_div_clk]
create_generated_clock -master_clock "UART_CLK" -source [get_ports UART_CLK] -name "TX_CLK" -divide_by 32 [get_port U_ClkDiv_TX/o_div_clk]

set_clock_uncertainty -setup 0.2 [get_clocks {REF_CLK UART_CLK ALU_CLK RX_CLK TX_CLK}]
set_clock_uncertainty -hold 0.1 [get_clocks {REF_CLK UART_CLK ALU_CLK RX_CLK TX_CLK}]
set_clock_transition 0.05 [get_clocks {REF_CLK UART_CLK}]

set_dont_touch_network {REF_CLK UART_CLK ALU_CLK RX_CLK TX_CLK}

####################################################################################
           #########################################################
             #### Section 2 : Clocks Relationship ####
           #########################################################
####################################################################################
set_clock_groups -asynchronous -group {REF_CLK ALU_CLK} -group {UART_CLK RX_CLK TX_CLK}


####################################################################################
           #########################################################
             #### Section 3 : set input/output delay on ports ####
           #########################################################
####################################################################################
set_input_delay [expr 0.2*$UART_CLK_Period] -clock RX_CLK [get_ports RX_IN]
set_output_delay [expr 0.2*$UART_CLK_Period*32.0] -clock TX_CLK [get_ports TX_OUT]
set_output_delay [expr 0.2*$UART_CLK_Period] -clock RX_CLK [get_ports RF_PAR_ERR]
set_output_delay [expr 0.2*$UART_CLK_Period] -clock RX_CLK [get_ports RF_STP_ERR]
####################################################################################
           #########################################################
                  #### Section 4 : Driving cells ####
           #########################################################
####################################################################################
set_driving_cell -library "scmetro_tsmc_cl013g_rvt_ss_1p08v_125c" -lib_cell BUFX2M -pin Y [get_ports RX_IN]

####################################################################################
           #########################################################
                  #### Section 5 : Output load ####
           #########################################################
####################################################################################
set_load 0.1 [get_ports TX_OUT]
set_load 0.1 [get_ports RF_PAR_ERR]
set_load 0.1 [get_ports RF_STP_ERR]
####################################################################################
           #########################################################
                 #### Section 6 : Operating Condition ####
           #########################################################
####################################################################################

# Define the Worst Library for Max(#setup) analysis
# Define the Best Library for Min(hold) analysis

set_operating_conditions -min_library "scmetro_tsmc_cl013g_rvt_ff_1p32v_m40c" -min "scmetro_tsmc_cl013g_rvt_ff_1p32v_m40c" -max_library "scmetro_tsmc_cl013g_rvt_ss_1p08v_125c" -max "scmetro_tsmc_cl013g_rvt_ss_1p08v_125c"

####################################################################################
           #########################################################
                  #### Section 7 : wireload Model ####
           #########################################################
####################################################################################


####################################################################################
           #########################################################
                  #### Section 8 : premapped cells ####
           #########################################################
####################################################################################


####################################################################################

