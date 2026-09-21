module FIFO_WR (
    input wclk,wrst_n,
    input winc,
    input [3:0] wq2_rptr,
    output [2:0] waddr,
    output [3:0] wptr,
    output wfull
);
    reg [3:0] waddr_total;
    assign waddr = waddr_total[2:0];
    always @(posedge wclk or negedge wrst_n) begin
        if (!wrst_n) begin
            waddr_total <= 0;
        end
        else if (winc && !wfull) begin
            waddr_total <= waddr_total + 1;
        end
    end
    assign wptr = waddr_total ^ (waddr_total >> 1);
    assign wfull = (wptr[3] != wq2_rptr[3]) && (wptr[2] != wq2_rptr[2]) && (wptr[1:0] == wq2_rptr[1:0]);
endmodule //FIFO_WR