`timescale 1ns / 1ps

module SYS_TOP_tb;

    localparam REF_CLK_PERIOD  = 20.000;
    localparam UART_CLK_PERIOD = 271.267;
    localparam real BIT_PERIOD = 8680.55;

    localparam [7:0] WR_CMD       = 8'hAA;
    localparam [7:0] RD_CMD       = 8'hBB;
    localparam [7:0] ALU_W_OP_CMD = 8'hCC;
    localparam [7:0] ALU_NOP_CMD  = 8'hDD;

    localparam [3:0] ALU_ADD = 4'b0000;
    localparam [3:0] ALU_SUB = 4'b0001;
    localparam [3:0] ALU_MUL = 4'b0010;

    reg  REF_CLK, UART_CLK, RST, RX_IN;
    wire TX_OUT, RF_PAR_ERR, RF_STP_ERR;

    event start_test_trigger;
    event test_done;
    
    integer test_case_id = 0;
    string  test_label   = "";
    integer total_tc  = 0, passed_tc = 0, failed_tc = 0;
    integer failed_cases_list[$];
    time tc_start_time, tc_end_time;
    integer expected_num_bytes = 0;
    reg [7:0] expected_bytes [0:1];

    SYS_TOP DUT (
        .REF_CLK(REF_CLK), .UART_CLK(UART_CLK), .RST(RST),
        .RX_IN(RX_IN), .TX_OUT(TX_OUT),
        .RF_PAR_ERR(RF_PAR_ERR), .RF_STP_ERR(RF_STP_ERR)
    );

    always #(REF_CLK_PERIOD/2.0)  REF_CLK  = ~REF_CLK;
    always #(UART_CLK_PERIOD/2.0) UART_CLK = ~UART_CLK;

    task send_uart_frame(input [7:0] data_in);
        integer i;
        reg parity_bit;
        begin
            parity_bit = ^data_in;
            RX_IN = 1'b0; #(BIT_PERIOD);
            for (i = 0; i < 8; i++) begin
                RX_IN = data_in[i]; #(BIT_PERIOD);
            end
            RX_IN = parity_bit; #(BIT_PERIOD);
            RX_IN = 1'b1; #(BIT_PERIOD);
        end
    endtask

    initial begin
        REF_CLK = 0; UART_CLK = 0; RST = 1; RX_IN = 1;
        #100; RST = 0; #200; RST = 1;
        #1000;  // FIX: Increased from 500ns for RST_SYNC release (needs 542ns)

        $display("\n=== STARTING TESTBENCH ===\n");

        // CONFIG: REG2 = 0x81 (Prescale=32, Parity En=1, Even=0)
        // Frame order: [CMD, ADDR, DATA]
        send_uart_frame(WR_CMD);
        send_uart_frame(8'h02);  // ADDR
        send_uart_frame(8'h81);  // DATA
        #(BIT_PERIOD * 4);

        // CONFIG: REG3 = 0x20 (Div Ratio = 32)
        send_uart_frame(WR_CMD);
        send_uart_frame(8'h03);  // ADDR
        send_uart_frame(8'h20);  // DATA
        #(BIT_PERIOD * 4);

        // TC1: RegFile Write
        total_tc++; test_case_id = 1;
        test_label = "RegFile Write [0x55 -> Addr 0x05]";
        expected_num_bytes = 0;
        tc_start_time = $time; -> start_test_trigger;
        send_uart_frame(WR_CMD);
        send_uart_frame(8'h05);  // ADDR
        send_uart_frame(8'h55);  // DATA
        @ (test_done);

        // TC2: RegFile Read
        total_tc++; test_case_id = 2;
        test_label = "RegFile Read [Addr 0x05, Exp: 0x55]";
        expected_num_bytes = 1; expected_bytes[0] = 8'h55;
        tc_start_time = $time; -> start_test_trigger;
        send_uart_frame(RD_CMD);
        send_uart_frame(8'h05);
        @ (test_done);

        // TC3: ALU ADD
        total_tc++; test_case_id = 3;
        test_label = "ALU ADD [0x20 + 0x05 -> 0x0025]";
        expected_num_bytes = 2; expected_bytes[0] = 8'h25; expected_bytes[1] = 8'h00;
        tc_start_time = $time; -> start_test_trigger;
        send_uart_frame(ALU_W_OP_CMD);
        send_uart_frame(8'h20); send_uart_frame(8'h05);
        send_uart_frame({4'b0000, ALU_ADD});
        @ (test_done);

        // TC4: ALU SUB (no operand)
        total_tc++; test_case_id = 4;
        test_label = "ALU SUB [0x20 - 0x05 -> 0x001B]";
        expected_num_bytes = 2; expected_bytes[0] = 8'h1B; expected_bytes[1] = 8'h00;
        tc_start_time = $time; -> start_test_trigger;
        send_uart_frame(ALU_NOP_CMD);
        send_uart_frame({4'b0000, ALU_SUB});
        @ (test_done);

        // TC5: ALU MUL
        total_tc++; test_case_id = 5;
        test_label = "ALU MUL [0x12 * 0x10 -> 0x0120]";
        expected_num_bytes = 2; expected_bytes[0] = 8'h20; expected_bytes[1] = 8'h01;
        tc_start_time = $time; -> start_test_trigger;
        send_uart_frame(ALU_W_OP_CMD);
        send_uart_frame(8'h12); send_uart_frame(8'h10);
        send_uart_frame({4'b0000, ALU_MUL});
        @ (test_done);

        #(BIT_PERIOD * 10);

        $display("\n=== TESTBENCH SUMMARY ===");
        $display("Total: %0d | Passed: %0d | Failed: %0d", total_tc, passed_tc, failed_tc);
        if (failed_tc == 0) $display("STATUS: ALL TESTS PASSED!");
        else begin
            $write("Failed: ");
            foreach (failed_cases_list[i]) $write("TC#%0d ", failed_cases_list[i]);
            $display("");
        end
        $finish;
    end

    initial begin
        reg [7:0] rx_byte;
        integer b, bit_idx;
        reg tc_passed, timeout_flag;

        forever begin
            @ (start_test_trigger);
            tc_passed = 1'b1; timeout_flag = 1'b0;
            $display("--- TC#%0d: %s ---", test_case_id, test_label);

            if (expected_num_bytes > 0) begin
                for (b = 0; b < expected_num_bytes && !timeout_flag; b++) begin
                    fork
                        begin @ (negedge TX_OUT); end
                        begin #(BIT_PERIOD * 200); timeout_flag = 1'b1; end
                    join_any
                    disable fork;

                    if (timeout_flag) begin
                        $display("  [ERROR] TIMEOUT waiting for TX byte %0d", b);
                        tc_passed = 1'b0;
                    end else begin
                        #(BIT_PERIOD * 1.5);
                        rx_byte = 8'h00;
                        for (bit_idx = 0; bit_idx < 8; bit_idx++) begin
                            rx_byte[bit_idx] = TX_OUT;
                            #(BIT_PERIOD);
                        end
                        #(BIT_PERIOD * 2.0);

                        if (rx_byte !== expected_bytes[b]) begin
                            $display("  [ERROR] Byte %0d: Got 0x%0h, Exp 0x%0h", b, rx_byte, expected_bytes[b]);
                            tc_passed = 1'b0;
                        end else begin
                            $display("  [MATCH] Byte %0d: 0x%0h", b, rx_byte);
                        end
                    end
                end
            end else begin
                #(BIT_PERIOD * 50);
            end

            $display("  [REGFILE[5]] = 0x%0h", DUT.U_RegFile.regArr[5]);
            if (tc_passed) begin
                $display("TC#%0d: PASSED", test_case_id);
                passed_tc++;
            end else begin
                $display("TC#%0d: FAILED", test_case_id);
                failed_tc++;
                failed_cases_list.push_back(test_case_id);
            end
            -> test_done;
        end
    end

endmodule