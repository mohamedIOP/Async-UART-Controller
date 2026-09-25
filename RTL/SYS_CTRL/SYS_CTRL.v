/////////////////////////////////////////////////////////////
////////////////////////  SYS_CTRL  ////////////////////////
/////////////////////////////////////////////////////////////
// Decodes command frames arriving from UART_RX (through the
// RX Data_Sync), drives the RegFile / ALU, and forwards the
// result byte to UART_TX (through the ASYNC_FIFO).
//
// Supported commands (first frame = opcode byte):
//   0xAA  RF_Wr_CMD          : Frame0=0xAA, Frame1=Wr_Data, Frame2=Wr_Addr
//   0xBB  RF_Rd_CMD          : Frame0=0xBB, Frame1=Rd_Addr
//   0xCC  ALU_OPER_W_OP_CMD  : Frame0=0xCC, Frame1=OperandA, Frame2=OperandB, Frame3=ALU_FUN
//   0xDD  ALU_OPER_W_NOP_CMD : Frame0=0xDD, Frame1=ALU_FUN  (uses REG0/REG1 already in RegFile)
//
// RF_Wr_CMD writes normal-range addresses (0x4-0x15) as well as
// the reserved config addresses (0x0-0x3). ALU_OPER_W_OP_CMD
// stages its operands through RegFile addresses 0x0 (REG0/A)
// and 0x1 (REG1/B), since the ALU's A/B ports are hard-wired to
// REG0/REG1.
/////////////////////////////////////////////////////////////

module SYS_CTRL (
    input  wire        CLK,
    input  wire        RST,          // active-low async reset (REF_CLK domain)

    // ALU interface
    input  wire [15:0] ALU_OUT,
    input  wire        OUT_Valid,
    output reg  [3:0]  ALU_FUN,
    output reg         EN,

    // Clock gate for the ALU
    output reg         CLK_EN,

    // RegFile interface
    output reg  [3:0]  Address,
    output reg         WrEn,
    output reg         RdEn,
    output reg  [7:0]  WrData,
    input  wire [7:0]  RdData,
    input  wire        RdData_Valid,

    // UART_RX side (arrives via Data_Synchronizer, already in this clock domain)
    input  wire [7:0]  RX_P_DATA,
    input  wire        RX_D_VLD,

    // UART_TX side (departs via ASYNC_FIFO into the UART_CLK domain)
    output reg  [7:0]  TX_P_DATA,
    output reg         TX_D_VLD,
    input  wire        FIFO_FULL,

    // Clock divider enable (config bookkeeping - dividers are tied on at top level)
    output wire        clk_div_en
);

    // divider is free-running per spec.
    assign clk_div_en = 1'b1;

    // Opcodes
    localparam [7:0] CMD_RF_WR       = 8'hAA;
    localparam [7:0] CMD_RF_RD       = 8'hBB;
    localparam [7:0] CMD_ALU_OP      = 8'hCC;
    localparam [7:0] CMD_ALU_NOP     = 8'hDD;

    // States
    localparam [3:0] S_IDLE          = 4'd0,
                      S_FRAME1        = 4'd1,
                      S_FRAME2        = 4'd2,
                      S_FRAME3        = 4'd3,
                      S_RF_WRITE      = 4'd4,
                      S_RF_READ_REQ   = 4'd5,
                      S_RF_READ_WAIT  = 4'd6,
                      S_RF_READ_SEND  = 4'd7,
                      S_ALU_WR_A      = 4'd8,
                      S_ALU_WR_B      = 4'd9,
                      S_ALU_EXEC      = 4'd10,
                      S_ALU_WAIT      = 4'd11,
                      S_ALU_SEND      = 4'd12,
                      S_TX_PULSE      = 4'd13;

    reg [3:0] state, next_state;
    reg [7:0] cmd_reg;
    reg [7:0] frame1_reg, frame2_reg, frame3_reg;
    always @(posedge CLK or negedge RST) begin
        if (!RST)
            state <= S_IDLE;
        else
            state <= next_state;
    end

    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            cmd_reg    <= 8'b0;
            frame1_reg <= 8'b0;
            frame2_reg <= 8'b0;
            frame3_reg <= 8'b0;
        end
        else begin
            case (state)
                S_IDLE:   if (RX_D_VLD) cmd_reg    <= RX_P_DATA;
                S_FRAME1: if (RX_D_VLD) frame1_reg <= RX_P_DATA;
                S_FRAME2: if (RX_D_VLD) frame2_reg <= RX_P_DATA;
                S_FRAME3: if (RX_D_VLD) frame3_reg <= RX_P_DATA;
                default: ; // hold
            endcase
        end
    end

    always @(*) begin
        // Defaults every cycle - pulses are one-cycle wide.
        next_state = state;
        WrEn       = 1'b0;
        RdEn       = 1'b0;
        Address    = 4'b0;
        WrData     = 8'b0;
        ALU_FUN    = 4'b0;
        EN         = 1'b0;
        TX_D_VLD   = 1'b0;
        TX_P_DATA  = 8'b0;
        CLK_EN     = 'b0;
        case (state)
            S_IDLE: begin
                if (RX_D_VLD)
                    next_state = S_FRAME1;
            end

            S_FRAME1: begin
                if (RX_D_VLD) begin
                    case (cmd_reg)
                        CMD_RF_WR:   next_state = S_FRAME2;   // need Wr_Addr next
                        CMD_RF_RD:   next_state = S_RF_READ_REQ;
                        CMD_ALU_OP:  next_state = S_FRAME2;   // need Operand B next
                        CMD_ALU_NOP: next_state = S_ALU_EXEC;
                        default:     next_state = S_IDLE;     // unknown opcode, drop
                    endcase
                end
            end

            S_FRAME2: begin
                if (RX_D_VLD) begin
                    case (cmd_reg)
                        CMD_RF_WR:  next_state = S_RF_WRITE;
                        CMD_ALU_OP: next_state = S_FRAME3;    // need ALU_FUN next
                        default:    next_state = S_IDLE;
                    endcase
                end
            end

            S_FRAME3: begin
                if (RX_D_VLD)
                    next_state = S_ALU_WR_A;                  // stage operand A into RegFile first
            end

            // ---- RF_Wr_CMD: frame2 = data, frame1 = addr ----
            S_RF_WRITE: begin
                WrEn    = 1'b1;
                Address = frame1_reg[3:0];
                WrData  = frame2_reg;
                next_state = S_IDLE;
            end

            // ---- RF_Rd_CMD: frame1 = addr ----
            S_RF_READ_REQ: begin
                RdEn    = 1'b1;
                Address = frame1_reg[3:0];
                next_state = S_RF_READ_WAIT;
            end
            S_RF_READ_WAIT: begin
                if (RdData_Valid)
                    next_state = S_RF_READ_SEND;
            end
            S_RF_READ_SEND: begin
                if (!FIFO_FULL) begin
                    TX_P_DATA = RdData;
                    TX_D_VLD  = 1'b1;
                    next_state = S_IDLE;
                end
            end

            // ---- ALU_OPER_W_OP_CMD: frame1=A, frame2=B, frame3=FUN ----
            // (ALU_OPER_W_NOP_CMD skips straight to S_ALU_EXEC using
            //  whatever operands are already loaded in REG0/REG1.)
            S_ALU_WR_A: begin
                WrEn    = 1'b1;
                Address = 4'h0;          // REG0 = Operand A
                WrData  = frame1_reg;
                next_state = S_ALU_WR_B;
            end
            S_ALU_WR_B: begin
                WrEn    = 1'b1;
                Address = 4'h1;          // REG1 = Operand B
                WrData  = frame2_reg;
                CLK_EN = 1;
                next_state = S_ALU_EXEC;
            end

            S_ALU_EXEC: begin
                EN = 1'b1;
                CLK_EN = 1;
                // frame3 holds ALU_FUN for the WITH-operand command;
                // frame1 holds it for the NO-operand command.
                ALU_FUN = (cmd_reg == CMD_ALU_OP) ? frame3_reg[3:0] : frame1_reg[3:0];
                next_state = S_ALU_WAIT;
            end
            S_ALU_WAIT: begin
                if (OUT_Valid) begin
                    next_state = S_ALU_SEND;
                    CLK_EN = 0;
                end
            end
            S_ALU_SEND: begin
                if (!FIFO_FULL) begin
                    TX_P_DATA = ALU_OUT[7:0];
                    TX_D_VLD  = 1'b1;
                    next_state = S_IDLE;
                end
            end

            default: next_state = S_IDLE;
        endcase
    end

endmodule //SYS_CTRL
