`timescale 1ns / 1ps

module SYS_TOP_tb;

    // =========================================================================
    // 1. Clock & System Parameters
    // =========================================================================
    // REF_CLK = 50 MHz -> Period = 20 ns
    localparam REF_CLK_PERIOD  = 20; 
    // UART_CLK = 3.6864 MHz -> Period = ~271.267 ns
    localparam UART_CLK_PERIOD = 271.267; 
    
    // UART Configuration Defaults
    // Bit Period at 115200 Baud = 1 / 115200 ≈ 8.68055 us = 8680.55 ns
    localparam real BIT_PERIOD = 8680.55; 

    // Command Opcodes
    localparam [7:0] WR_CMD       = 8'hAA; // Register File Write
    localparam [7:0] RD_CMD       = 8'hBB; // Register File Read
    localparam [7:0] ALU_W_OP_CMD = 8'hCC; // ALU Operation with Operand
    localparam [7:0] ALU_NOP_CMD  = 8'hDD; // ALU Operation with No Operand

    // ALU Operations
    localparam [3:0] ALU_ADD = 4'b0000;
    localparam [3:0] ALU_SUB = 4'b0001;
    localparam [3:0] ALU_MUL = 4'b0010;

    // =========================================================================
    // 2. Interface Signals
    // =========================================================================
    reg  REF_CLK;
    reg  UART_CLK;
    reg  RST;
    reg  RX_IN;
    wire TX_OUT;
    wire RF_PAR_ERR; // Added to fix 7-port warning
    wire RF_STP_ERR; // Added to fix 7-port warning

    // Testbench Control & Synchronization Signals
    event start_test_trigger;
    event test_done;
    
    integer test_case_id = 0;
    string  test_label   = "";
    
    // Test Summary Counters
    integer total_tc  = 0;
    integer passed_tc = 0;
    integer failed_tc = 0;
    integer failed_cases_list[$];

    // Time tracking variables
    time tc_start_time;
    time tc_end_time;

    // Shared communication structure for Checker Initial Block
    integer expected_num_bytes = 0;
    reg [7:0] expected_bytes [0:1];

    // =========================================================================
    // 3. DUT Instantiation (Updated to match all 7 ports of SYS_TOP)
    // =========================================================================
    SYS_TOP DUT (
        .REF_CLK    (REF_CLK),
        .UART_CLK   (UART_CLK),
        .RST        (RST),
        .RX_IN      (RX_IN),
        .TX_OUT     (TX_OUT),
        .RF_PAR_ERR (RF_PAR_ERR),
        .RF_STP_ERR (RF_STP_ERR)
    );

    // =========================================================================
    // 4. Clock Generation
    // =========================================================================
    always #(REF_CLK_PERIOD / 2.0)  REF_CLK  = ~REF_CLK;
    always #(UART_CLK_PERIOD / 2.0) UART_CLK = ~UART_CLK;

    // =========================================================================
    // 5. Helper Tasks (UART Frame Drive)
    // =========================================================================
    task send_uart_frame(input [7:0] data_in);
        integer i;
        reg parity_bit;
        begin
            parity_bit = ^data_in; // Even Parity

            // Start bit
            RX_IN = 1'b0;
            #(BIT_PERIOD);

            // Data bits (LSB First)
            for (i = 0; i < 8; i = i + 1) begin
                RX_IN = data_in[i];
                #(BIT_PERIOD);
            end

            // Parity bit
            RX_IN = parity_bit;
            #(BIT_PERIOD);

            // Stop bit
            RX_IN = 1'b1;
            #(BIT_PERIOD);
        end
    endtask

    // =========================================================================
    // 6. INITIAL BLOCK 1: WRITING THREAD (Stimulus & Test Execution)
    // =========================================================================
    initial begin
        // Initialize Signals
        REF_CLK  = 0;
        UART_CLK = 0;
        RST      = 1;
        RX_IN    = 1;

        // Apply Reset Sequence
        #100;
        RST = 0;
        #200;
        RST = 1;
        #500;

        $display("\n=========================================================");
        $display("          STARTING SYSTEM TESTBENCH EXECUTION            ");
        $display("=========================================================\n");

        // CONFIGURATION PHASE: Address 0x02 and 0x03
        send_uart_frame(WR_CMD);
        send_uart_frame(8'h02);
        send_uart_frame(8'h81);
        #(BIT_PERIOD * 2);

        send_uart_frame(WR_CMD);
        send_uart_frame(8 'h03);
        send_uart_frame(8'h20);
        #(BIT_PERIOD * 2);

        // TEST CASE 1: RegFile Write
        total_tc     = total_tc + 1;
        test_case_id = 1;
        test_label   = "RegFile Write Operation [Write 0x55 to Addr 0x05]";
        expected_num_bytes = 0;

        tc_start_time = $time;
        -> start_test_trigger;

        send_uart_frame(WR_CMD);
        send_uart_frame(8'h05);
        send_uart_frame(8'h55);

        @ (test_done);

        // TEST CASE 2: RegFile Read
        total_tc     = total_tc + 1;
        test_case_id = 2;
        test_label   = "RegFile Read Operation [Read Addr 0x05, Expected: 0x55]";
        expected_num_bytes = 1;
        expected_bytes[0]  = 8'h55;

        tc_start_time = $time;
        -> start_test_trigger;

        send_uart_frame(RD_CMD);
        send_uart_frame(8'h05);

        @ (test_done);

        // TEST CASE 3: ALU Operation with Operand (Addition)
        total_tc     = total_tc + 1;
        test_case_id = 3;
        test_label   = "ALU Op with Operand [ADD: OperA=0x20, OperB=0x05 -> Exp: 0x0025]";
        expected_num_bytes = 2;
        expected_bytes[0]  = 8'h25; // LSB
        expected_bytes[1]  = 8'h00; // MSB

        tc_start_time = $time;
        -> start_test_trigger;

        send_uart_frame(ALU_W_OP_CMD);
        send_uart_frame(8'h20);
        send_uart_frame(8'h05);
        send_uart_frame({4'b0000, ALU_ADD});

        @ (test_done);

        // TEST CASE 4: ALU Operation with No Operand (Subtraction)
        total_tc     = total_tc + 1;
        test_case_id = 4;
        test_label   = "ALU Op w/ No Operand [SUB: 0x20 - 0x05 -> Exp: 0x001B]";
        expected_num_bytes = 2;
        expected_bytes[0]  = 8'h1B; // LSB
        expected_bytes[1]  = 8'h00; // MSB

        tc_start_time = $time;
        -> start_test_trigger;

        send_uart_frame(ALU_NOP_CMD);
        send_uart_frame({4'b0000, ALU_SUB});

        @ (test_done);

        // TEST CASE 5: ALU Operation with Operand (Multiplication)
        total_tc     = total_tc + 1;
        test_case_id = 5;
        test_label   = "ALU Op with Operand [MUL: OperA=0x12, OperB=0x10 -> Exp: 0x0120]";
        expected_num_bytes = 2;
        expected_bytes[0]  = 8'h20; // LSB
        expected_bytes[1]  = 8'h01; // MSB

        tc_start_time = $time;
        -> start_test_trigger;

        send_uart_frame(ALU_W_OP_CMD);
        send_uart_frame(8'h12);
        send_uart_frame(8'h10);
        send_uart_frame({4'b0000, ALU_MUL});

        @ (test_done);

        #(BIT_PERIOD * 10);

        // SUMMARY DISPLAY
        $display("\n=========================================================");
        $display("                   TESTBENCH SUMMARY                     ");
        $display("=========================================================");
        $display(" Total Testcases Executed : %0d", total_tc);
        $display(" Passed Testcases         : %0d", passed_tc);
        $display(" Failed Testcases         : %0d", failed_tc);
        
        if (failed_tc > 0) begin
            $write(" Failed Testcase Numbers  : ");
            foreach (failed_cases_list[i]) begin
                $write("TC#%0d ", failed_cases_list[i]);
            end
            $display("");
        end else begin
            $display(" STATUS                   : ALL TEST CASES PASSED SUCCESSFULLY!");
        end
        $display("=========================================================\n");

        $finish;
    end

    // =========================================================================
    // 7. INITIAL BLOCK 2: READING THREAD (Monitor & Self-Checker)
    // =========================================================================
    initial begin
        reg [7:0] rx_byte;
        integer b, bit_idx;
        reg tc_passed;

        forever begin
            @ (start_test_trigger);
            tc_passed = 1'b1;

            $display("---------------------------------------------------------");
            $display("TC#%0d Start Time: %0t ns | Label: %s", test_case_id, tc_start_time, test_label);

            if (expected_num_bytes > 0) begin
                for (b = 0; b < expected_num_bytes; b = b + 1) begin
                    @ (negedge TX_OUT);
                    #(BIT_PERIOD / 2.0);

                    rx_byte = 8'h00;
                    for (bit_idx = 0; bit_idx < 8; bit_idx = bit_idx + 1) begin
                        #(BIT_PERIOD);
                        rx_byte[bit_idx] = TX_OUT;
                    end

                    #(BIT_PERIOD * 2);

                    if (rx_byte !== expected_bytes[b]) begin
                        $display("  [ERROR] Byte %0d Mismatch! Received: 0x%0h | Expected: 0x%0h", 
                                 b, rx_byte, expected_bytes[b]);
                        tc_passed = 1'b0;
                    end else begin
                        $display("  [MATCH] Byte %0d Received correctly: 0x%0h", b, rx_byte);
                    end
                end
            end else begin
                #(BIT_PERIOD * 5);
            end

            tc_end_time = $time;
            $display("TC#%0d End Time  : %0t ns", test_case_id, tc_end_time);

            // FIX: Corrected internal signals path according to SYS_TOP.v and RegFile.v
            $display("  [INNER SIGNALS] ALU_OUT: 0x%0h | RegFile[0x05]: 0x%0h", 
                     DUT.U_ALU.ALU_OUT, DUT.U_RegFile.regArr[5]);

            if (tc_passed) begin
                $display("TC#%0d VERDICT   : PASSED", test_case_id);
                passed_tc = passed_tc + 1;
            end else begin
                $display("TC#%0d VERDICT   : FAILED", test_case_id);
                failed_tc = failed_tc + 1;
                failed_cases_list.push_back(test_case_id);
            end

            -> test_done;
        end
    end

endmodule