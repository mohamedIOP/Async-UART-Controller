module edge_bit_counter (
    input edge_bit_cnt_enable, soft_rst,
    input [5:0] prescale,
    input CLK, RST,
    output reg [4:0] edge_cnt,
    output reg [3:0] bit_cnt
);
    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            edge_cnt <= 0;
            bit_cnt  <= 0;
        end
        else if (soft_rst) begin
            bit_cnt <= 0;
            // If active in valid state with next frame starting, start incrementing edge_cnt seamlessly
            if (edge_bit_cnt_enable) begin
                edge_cnt <= edge_cnt + 1'b1;
            end
            else begin
                edge_cnt <= 0;
            end
        end
        else if (edge_bit_cnt_enable) begin
            if (edge_cnt == prescale - 1) begin
                edge_cnt <= 0;
                bit_cnt  <= bit_cnt + 1'b1;
            end
            else begin
                edge_cnt <= edge_cnt + 1'b1;
            end
        end
    end
endmodule