module FIFO_RD (
    input               rclk,
    input               rrst_n,
    input               rinc,
    input       [3:0]   rq2_wptr,
    output reg  [3:0]   rptr,        // Registered output
    output      [2:0]   raddr,
    output              rempty
);
    reg  [3:0] raddr_total;
    wire [3:0] raddr_next;
    wire [3:0] rptr_next;

    assign raddr = raddr_total[2:0];

    // Compute next binary address and next Gray pointer
    assign raddr_next = (rinc && !rempty) ? (raddr_total + 1'b1) : raddr_total;
    assign rptr_next  = raddr_next ^ (raddr_next >> 1);

    always @(posedge rclk or negedge rrst_n) begin
        if (!rrst_n) begin
            raddr_total <= 4'b0000;
            rptr        <= 4'b0000; // Registered to isolate domain crossing
        end else begin
            raddr_total <= raddr_next;
            rptr        <= rptr_next;
        end
    end

    assign rempty = (rptr == rq2_wptr);

endmodule // FIFO_RD