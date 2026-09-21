module FIFO_MEM_CNTRL #(
    parameter DATA_WIDTH = 8
)(
    input [DATA_WIDTH - 1:0] wdata,
    input wclken,wclk,
    input [2:0] waddr,raddr,
    output [DATA_WIDTH - 1:0] rdata
);
    reg [DATA_WIDTH - 1:0] RAM [0:7];
    always @(posedge wclk) begin
        if (wclken) begin
            RAM[waddr] <= wdata;
        end
    end
    assign rdata = RAM[raddr];
endmodule //FIFO_MEM_CNTRL