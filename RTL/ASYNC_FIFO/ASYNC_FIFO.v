module ASYNC_FIFO #(
    parameter DATA_WIDTH = 8
)(
    input W_CLK,W_RST,W_INC,
    input R_CLK,R_RST,R_INC,
    input [DATA_WIDTH - 1:0] WR_DATA,
    output FULL,EMPTY,
    output [DATA_WIDTH - 1:0] RD_DATA
);
    wire [2:0] waddr_inner,raddr_inner;
    wire [3:0] wptr_inner,rptr_inner;
    wire [3:0] wq2_rptr_inner,rq2_wptr_inner;
    FIFO_WR FIFO_WR_Block (
        .wclk(W_CLK),.wrst_n(W_RST),
        .winc(W_INC),
        .wq2_rptr(wq2_rptr_inner),
        .waddr(waddr_inner),
        .wptr(wptr_inner),
        .wfull(FULL)
    );
    DF_SYNC #(.WIDTH(4)) sync_w2r (
    .CLK(R_CLK),
    .RST(R_RST),
    .Data_In(wptr_inner),
    .Data_Out(rq2_wptr_inner)
    );
    FIFO_RD FIFO_RD_Block (
        .rclk(R_CLK),.rrst_n(R_RST),
        .rinc(R_INC),
        .rq2_wptr(rq2_wptr_inner),
        .rptr(rptr_inner),
        .raddr(raddr_inner),
        .rempty(EMPTY)
    );
    DF_SYNC #(.WIDTH(4)) sync_r2w (
    .CLK(W_CLK),
    .RST(W_RST),
    .Data_In(rptr_inner),
    .Data_Out(wq2_rptr_inner)
    );
    FIFO_MEM_CNTRL #(.DATA_WIDTH(DATA_WIDTH)) FIFO_Memory_Block (
        .wdata(WR_DATA),
        .wclken(W_INC && !FULL),.wclk(W_CLK),
        .waddr(waddr_inner),.raddr(raddr_inner),
        .rdata(RD_DATA)
    );
endmodule //ASYNC_FIFO