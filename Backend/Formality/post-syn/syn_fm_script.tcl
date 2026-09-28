
########################### Define Top Module ############################
                                                   
set top_module SYS_TOP

######################### Formality Setup File ###########################

set synopsys_auto_setup true

set_svf "../../syn/$top_module.svf"




set SSLIB "/home/ICer/IC/Projects/System/std_cells/scmetro_tsmc_cl013g_rvt_ss_1p08v_125c.db"
set TTLIB "/home/ICer/IC/Projects/System/std_cells/scmetro_tsmc_cl013g_rvt_tt_1p2v_25c.db"
set FFLIB "/home/ICer/IC/Projects/System/std_cells/scmetro_tsmc_cl013g_rvt_ff_1p32v_m40c.db"

######################### Reference Container ############################

## Read Reference technology libraries
read_db -container Ref [list $SSLIB $TTLIB $FFLIB]

## Read Reference Design Files
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/ALU/ALU.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/ASYNC_FIFO/ASYNC_FIFO.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/ASYNC_FIFO/DF_SYNC.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/ASYNC_FIFO/FIFO_MEM_CNTRL.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/ASYNC_FIFO/FIFO_RD.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/ASYNC_FIFO/FIFO_WR.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/CLK_Divider/ClkDiv.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/CLKDIV_MUX/CLKDIV_MUX.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/Clock_Gating/CLK_GATE.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/DATA_SYNC/DATA_SYNC.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/PULSE_GEN/PULSE_GEN.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/RegFile/RegFile.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/RST_SYNC/RST_SYNC.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/SYS_CTRL/SYS_CTRL.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/SYS_TOP/SYS_TOP.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_RX/data_sampling.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_RX/deserializer.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_RX/edge_bit_counter.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_RX/parity_Check.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_RX/stop_Check.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_RX/strt_Check.v
read_sverilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_RX/UART_RX_FSM.sv
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_RX/UART_RX_TOP.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_TOP/UART.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_TX/Mux_4X1.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_TX/parity_Calc.v
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_TX/Serializer.v
read_sverilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_TX/UART_TX_FSM.sv
read_verilog -container Ref /home/ICer/IC/Projects/System/rtl/UART/UART_TX/UART_TX_TOP.v

## set the top Reference Design 
set_reference_design SYS_TOP
set_top SYS_TOP

######################## Implementation Container #########################

## Read Implementation technology libraries
read_db -container Imp [list $SSLIB $TTLIB $FFLIB]

## Read Implementation Design Files
read_verilog -container Imp /home/ICer/IC/Projects/System/syn/netlists/SYS_TOP.v
## set the top Implementation Design
set_implementation_design SYS_TOP
set_top SYS_TOP


## matching Compare points
match

## verify
set successful [verify]
if {!$successful} {
diagnose
analyze_points -failing
}

report_passing_points > "reports/passing_points.rpt"
report_failing_points > "reports/failing_points.rpt"
report_aborted_points > "reports/aborted_points.rpt"
report_unverified_points > "reports/unverified_points.rpt"


start_gui
