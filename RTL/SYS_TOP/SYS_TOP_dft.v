/////////////////////////////////////////////////////////////
////////////////////////  SYS_TOP  /////////////////////////
/////////////////////////////////////////////////////////////
// Top-level integration, wired exactly per Final_System.pdf:
//   Clock Domain 1 (REF_CLK) : RegFile, ALU, Clock Gating, SYS_CTRL
//   Clock Domain 2 (UART_CLK): UART_TX, UART_RX, PULSE_GEN, 2x Clock Divider
//   Crossings                : RST_SYNC x2, Data_Synchronizer x2, ASYNC_FIFO
/////////////////////////////////////////////////////////////

module SYS_TOP #(
    parameter RF_WIDTH   = 8,
    parameter RF_DEPTH   = 16,
    parameter RF_ADDR    = 4,
    parameter FIFO_WIDTH = 8,
    parameter NUM_OF_CHAINS = 3
)(
    input  wire        scan_clk, 
    input  wire        scan_rst, 
    input  wire        test_mode, 
    input  wire        SE, 
    input  wire  [NUM_OF_CHAINS-1:0]      SI, 
    input  wire  [NUM_OF_CHAINS-1:0]      SO, 
    input  wire        REF_CLK,     // 50 MHz
    input  wire        UART_CLK,    // 3.6864 MHz
    input  wire        RST,         // active-low async top reset
    input  wire        RX_IN,
    output wire        TX_OUT,
    output wire        RF_PAR_ERR,
    output wire        RF_STP_ERR
);
    //=========================================================
    // MUXED Scan Chain
    //=========================================================
    wire REF_CLK_MUXED;
    wire UART_CLK_MUXED;
    wire RST_MUXED;
    wire SYNC_RST_1_MUXED;
    wire SYNC_RST_2_MUXED;

    mux2X1 REF_CLK_MUX_CLK (
        .IN_0(REF_CLK),
        .IN_1(scan_clk),
        .SEL(test_mode),
        .OUT(REF_CLK_MUXED)
    );

    mux2X1 UART_CLK_MUX_CLK (
        .IN_0(UART_CLK),
        .IN_1(scan_clk),
        .SEL(test_mode),
        .OUT(UART_CLK_MUXED)
    );

    mux2X1 RST_MUX (
        .IN_0(RST),
        .IN_1(scan_rst),
        .SEL(test_mode),
        .OUT(RST_MUXED)
    );

    mux2X1 SYNC_RST_1_MUX (
        .IN_0(SYNC_RST_1),
        .IN_1(scan_rst),
        .SEL(test_mode),
        .OUT(SYNC_RST_1_MUXED)
    );

    mux2X1 SYNC_RST_2_MUX (
        .IN_0(SYNC_RST_2),
        .IN_1(scan_rst),
        .SEL(test_mode),
        .OUT(SYNC_RST_2_MUXED)
    );
    //=========================================================
    // Reset synchronizers - one per clock domain
    //=========================================================
    wire SYNC_RST_1; // REF_CLK domain
    wire SYNC_RST_2; // UART_CLK domain

    RST_SYNC RST_SYNC_1 (
        .CLK (REF_CLK_MUXED),
        .RST (RST_MUXED),
        .SYNC_RST (SYNC_RST_1)
    );

    RST_SYNC RST_SYNC_2 (
        .CLK (UART_CLK_MUXED),
        .RST (RST_MUXED),
        .SYNC_RST (SYNC_RST_2)
    );

    //=========================================================
    // Clock Domain 1 (REF_CLK): RegFile, ALU, Clock Gating, SYS_CTRL
    //=========================================================
    wire [RF_WIDTH-1:0] REG0, REG1, REG2, REG3;
    wire [RF_ADDR-1:0]  RF_Address;
    wire                RF_WrEn, RF_RdEn;
    wire [RF_WIDTH-1:0] RF_WrData, RF_RdData;
    wire                RF_RdData_Valid;

    RegFile #(.WIDTH(RF_WIDTH), .DEPTH(RF_DEPTH), .ADDR(RF_ADDR)) U_RegFile (
        .CLK        (REF_CLK_MUXED),
        .RST        (SYNC_RST_1_MUXED),
        .WrEn       (RF_WrEn),
        .RdEn       (RF_RdEn),
        .Address    (RF_Address),
        .WrData     (RF_WrData),
        .RdData     (RF_RdData),
        .RdData_VLD (RF_RdData_Valid),
        .REG0       (REG0),
        .REG1       (REG1),
        .REG2       (REG2),
        .REG3       (REG3)
    );

    wire ALU_CLK_EN, ALU_GATED_CLK;

    CLK_GATE U_CLK_GATE (
        .CLK_EN     (ALU_CLK_EN | test_mode),
        .CLK        (REF_CLK_MUXED),
        .GATED_CLK  (ALU_GATED_CLK)
    );

    wire [15:0] ALU_OUT;
    wire        ALU_OUT_VALID;
    wire [3:0]  ALU_FUN;
    wire        ALU_EN;

    ALU U_ALU (
        .A          ({{8{1'b0}}, REG0}),
        .B          ({{8{1'b0}}, REG1}),
        .ALU_FUN    (ALU_FUN),
        .CLK        (ALU_GATED_CLK),
        .RST        (SYNC_RST_1_MUXED),
        .EN         (ALU_EN),
        .ALU_OUT    (ALU_OUT),
        .OUT_VALID  (ALU_OUT_VALID)
    );

    // ---- RX path into SYS_CTRL (Data_Sync crosses UART_CLK -> REF_CLK) ----
    wire [7:0] RX_P_DATA_sync;
    wire       RX_D_VLD_sync;

    // ---- TX path out of SYS_CTRL, into ASYNC_FIFO (REF_CLK -> UART_CLK) ----
    wire [7:0] SYS_TX_P_DATA;
    wire       SYS_TX_D_VLD;
    wire       FIFO_FULL, FIFO_EMPTY;

    wire       clk_div_en_inner;

    SYS_CTRL U_SYS_CTRL (
        .CLK          (REF_CLK_MUXED),
        .RST          (SYNC_RST_1_MUXED),
        .ALU_OUT      (ALU_OUT),
        .OUT_Valid    (ALU_OUT_VALID),
        .ALU_FUN      (ALU_FUN),
        .EN           (ALU_EN),
        .CLK_EN       (ALU_CLK_EN),
        .Address      (RF_Address),
        .WrEn         (RF_WrEn),
        .RdEn         (RF_RdEn),
        .WrData       (RF_WrData),
        .RdData       (RF_RdData),
        .RdData_Valid (RF_RdData_Valid),
        .RX_P_DATA    (RX_P_DATA_sync),
        .RX_D_VLD     (RX_D_VLD_sync),
        .TX_P_DATA    (SYS_TX_P_DATA),
        .TX_D_VLD     (SYS_TX_D_VLD),
        .FIFO_FULL    (FIFO_FULL),
        .clk_div_en   (clk_div_en_inner)
    );

    //=========================================================
    // Clock Domain 2 (UART_CLK): Clock Dividers, UART, PULSE_GEN
    //=========================================================
    wire RX_CLK, TX_CLK;

    // Decode the 6-bit Prescale field (REG2[7:2], synced into this domain
    // as UART_Prescale below) into the RX divider's ratio. Keeps
    // prescale_raw * RX_div_ratio constant (=32) across all four legal
    // one-hot settings, so RX always ends up baud-matched to TX.
    wire [7:0] RX_div_ratio;

    //=========================================================
    // REG2 (UART config: parity enable/type + Prescale) is written
    // once during initial configuration, before any UART traffic
    // starts, and held static afterward - so it's connected directly
    // into the UART_CLK domain, same as REG3/Div_Ratio already is.
    // No Data_Sync needed for a signal that isn't toggling.
    //=========================================================
    wire        UART_PAR_EN  = REG2[0];
    wire        UART_PAR_TYP = REG2[1];
    wire [5:0]  UART_Prescale = REG2[7:2];


    CLKDIV_MUX #(.WIDTH(8)) U_CLKDIV_MUX (
        .IN  (UART_Prescale),
        .OUT (RX_div_ratio)
    );

    ClkDiv U_ClkDiv_RX (
        .i_ref_clk   (UART_CLK_MUXED),
        .i_rst_n     (SYNC_RST_2_MUXED),
        .i_clk_en    (clk_div_en_inner),          // divider is always on, per spec
        .i_div_ratio (RX_div_ratio),
        .o_div_clk   (RX_CLK)
    );

    ClkDiv U_ClkDiv_TX (
        .i_ref_clk   (UART_CLK_MUXED),
        .i_rst_n     (SYNC_RST_2_MUXED),
        .i_clk_en    (clk_div_en_inner),
        .i_div_ratio (REG3),
        .o_div_clk   (TX_CLK)
    );

    wire [7:0] UART_RX_P_DATA;
    wire       UART_RX_D_VLD;
    wire       UART_TX_BUSY;
    wire [7:0] FIFO_RD_DATA; //FIFO Intermediate Signal


    UART U_UART (
        .RST            (SYNC_RST_2_MUXED),
        .TX_CLK         (TX_CLK),
        .RX_CLK         (RX_CLK),
        .RX_IN_S        (RX_IN),
        .RX_OUT_P       (UART_RX_P_DATA),
        .RX_OUT_V       (UART_RX_D_VLD),
        .TX_IN_P        (FIFO_RD_DATA),
        .TX_IN_V        (~FIFO_EMPTY),
        .TX_OUT_S       (TX_OUT),
        .TX_OUT_V       (UART_TX_BUSY),
        .Prescale       (UART_Prescale),
        .parity_enable  (UART_PAR_EN),
        .parity_type    (UART_PAR_TYP),
        .parity_error   (RF_PAR_ERR),
        .framing_error  (RF_STP_ERR)
    );

    wire FIFO_R_INC;

    PULSE_GEN U_PULSE_GEN (
        .clk       (TX_CLK),
        .rst       (SYNC_RST_2_MUXED),
        .lvl_sig   (UART_TX_BUSY),
        .pulse_sig (FIFO_R_INC)
    );



    //=========================================================
    // Crossing: UART_RX data -> Data_Sync -> REF_CLK domain -> SYS_CTRL
    //=========================================================
    DATA_SYNC U_Data_Sync_RX (
        .unsync_bus   (UART_RX_P_DATA),
        .bus_enable   (UART_RX_D_VLD),
        .CLK          (REF_CLK_MUXED),
        .RST          (SYNC_RST_1_MUXED),
        .sync_bus     (RX_P_DATA_sync),
        .enable_pulse (RX_D_VLD_sync)
    );

    //=========================================================
    // Crossing: SYS_CTRL result byte -> ASYNC_FIFO -> UART_TX
    //=========================================================


    ASYNC_FIFO #(.DATA_WIDTH(FIFO_WIDTH)) U_ASYNC_FIFO (
        .W_CLK   (REF_CLK_MUXED),
        .W_RST   (SYNC_RST_1_MUXED),
        .W_INC   (SYS_TX_D_VLD),
        .R_CLK   (TX_CLK),
        .R_RST   (SYNC_RST_2_MUXED),
        .R_INC   (FIFO_R_INC),
        .WR_DATA (SYS_TX_P_DATA),
        .FULL    (FIFO_FULL),
        .EMPTY   (FIFO_EMPTY),
        .RD_DATA (FIFO_RD_DATA)
    );

endmodule //SYS_TOP