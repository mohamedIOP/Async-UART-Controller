module ClkDiv (
    input i_ref_clk,i_rst_n,i_clk_en,
    input [7:0] i_div_ratio,
    output reg o_div_clk
);
    wire [7:0] positive_counter = i_div_ratio >> 1;
    wire CLK_DIV_EN = i_clk_en && i_div_ratio != 0 && i_div_ratio != 1;
    reg [7:0] counter;
    always @(posedge i_ref_clk or negedge i_rst_n) begin
        if (!i_rst_n) begin
            counter <= 0;
            o_div_clk <= 0;
        end
        else if (!CLK_DIV_EN) begin
            counter <= 0;
            o_div_clk <= 0;
        end
        else begin
            if (counter < positive_counter) begin
                o_div_clk <= 1;
            end
            else begin
                o_div_clk <= 0;
            end
            if (counter == i_div_ratio - 1) begin
                counter <= 0;
            end else begin
                counter <= counter + 1;
            end
        end
    end
endmodule //ClkDiv