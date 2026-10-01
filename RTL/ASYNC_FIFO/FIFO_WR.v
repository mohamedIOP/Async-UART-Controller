module FIFO_WR (
    input               wclk,
    input               wrst_n,
    input               winc,
    input       [3:0]   wq2_rptr,
    output      [2:0]   waddr,
    output reg  [3:0]   wptr,        // Registered output
    output              wfull
);
    reg  [3:0] waddr_total;
    wire [3:0] waddr_next;
    wire [3:0] wptr_next;

    assign waddr = waddr_total[2:0];

    // Compute next binary address and next Gray pointer
    assign waddr_next = (winc && !wfull) ? (waddr_total + 1'b1) : waddr_total;
    assign wptr_next  = waddr_next ^ (waddr_next >> 1);

    always @(posedge wclk or negedge wrst_n) begin
        if (!wrst_n) begin
            waddr_total <= 4'b0000;
            wptr        <= 4'b0000; // Registered to isolate domain crossing
        end else begin
            waddr_total <= waddr_next;
            wptr        <= wptr_next;
        end
    end

    assign wfull = (wptr == {~wq2_rptr[3:2], wq2_rptr[1:0]});

endmodule // FIFO_WR