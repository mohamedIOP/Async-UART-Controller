module FIFO_RD (
    input rclk,rrst_n,
    input rinc,
    input [3:0] rq2_wptr,
    output [3:0] rptr,
    output [2:0] raddr,
    output rempty
);
    reg [3:0] raddr_total;
    assign raddr = raddr_total[2:0];
    always @(posedge rclk or negedge rrst_n) begin
        if (!rrst_n) begin
            raddr_total <= 0;
        end
        else if (rinc && !rempty) begin
            raddr_total <= raddr_total + 1;
        end
    end
    assign rptr = raddr_total ^ (raddr_total >> 1);
    assign rempty = (rptr == rq2_wptr);
endmodule //FIFO_RD