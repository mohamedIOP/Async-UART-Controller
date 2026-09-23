
module UART # ( parameter DATA_WIDTH = 8)

(
 input   wire                          RST,
 input   wire                          TX_CLK,
 input   wire                          RX_CLK,
 input   wire                          RX_IN_S,
 output  wire   [DATA_WIDTH-1:0]       RX_OUT_P, 
 output  wire                          RX_OUT_V,
 input   wire   [DATA_WIDTH-1:0]       TX_IN_P, 
 input   wire                          TX_IN_V, 
 output  wire                          TX_OUT_S,
 output  wire                          TX_OUT_V,  
 input   wire   [5:0]                  Prescale, 
 input   wire                          parity_enable,
 input   wire                          parity_type,
 output  wire                          parity_error,
 output  wire                          framing_error
);


UART_TX  #(.DATA_WIDTH(DATA_WIDTH)) U0_UART_TX (
.CLK(TX_CLK),
.RST(RST),
.pData(TX_IN_P),
.dataValid(TX_IN_V),
.parEn(parity_enable),
.parTyp(parity_type), 
.txOut(TX_OUT_S),
.busy(TX_OUT_V)
);
 
 
UART_RX U0_UART_RX (
.CLK(RX_CLK),
.RST(RST),
.RX_IN(RX_IN_S),
.Prescale(Prescale),
.PAR_EN(parity_enable),
.PAR_TYP(parity_type),
.P_DATA(RX_OUT_P), 
.data_valid(RX_OUT_V),
.parity_Error(parity_error),
.Stop_Error(framing_error)
);
 



endmodule
 
