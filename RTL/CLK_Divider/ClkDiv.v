module ClkDiv (
    input  wire       i_ref_clk,
    input  wire       i_rst_n,
    input  wire       i_clk_en,
    input  wire [7:0] i_div_ratio,
    output wire       o_div_clk
);

    wire [7:0] positive_counter = i_div_ratio >> 1;
    wire       CLK_DIV_EN       = i_clk_en && (i_div_ratio != 8'd0);
    
    reg [7:0] counter;
    reg       div_clk_reg;

    // 1. Sequential Division Logic (Used only when i_div_ratio > 1)
    always @(posedge i_ref_clk or negedge i_rst_n) begin
        if (!i_rst_n) begin
            counter     <= 8'd0;
            div_clk_reg <= 1'b0;
        end
        else if (!CLK_DIV_EN) begin
            counter     <= 8'd0;
            div_clk_reg <= 1'b0;
        end
        else begin
            if (i_div_ratio > 8'd1) begin
                // Duty cycle control
                if (counter < positive_counter) begin
                    div_clk_reg <= 1'b1;
                end else begin
                    div_clk_reg <= 1'b0;
                end

                // Counter reset / increment
                if (counter == i_div_ratio - 1'b1) begin
                    counter <= 8'd0;
                end else begin
                    counter <= counter + 1'b1;
                end
            end else begin
                counter     <= 8'd0;
                div_clk_reg <= 1'b0;
            end
        end
    end

    // 2. Clock Output Muxing Logic
    // If ratio == 1: Bypass divider and output i_ref_clk directly.
    // If ratio > 1 : Output divided clock from flip-flop.
    // If disabled : Output 0.
    assign o_div_clk = (!CLK_DIV_EN)          ? 1'b0 :
                       (i_div_ratio == 8'd1) ? i_ref_clk :
                                               div_clk_reg;

endmodule