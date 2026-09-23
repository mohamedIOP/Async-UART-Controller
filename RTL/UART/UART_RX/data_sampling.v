module data_sampling (
    input RX_IN,
    input dat_samp_en,soft_rst,
    input CLK,RST,
    output sampled_bit
);
    reg [1:0] inner_counter;
    // Sample three bits
    reg [2:0] majority_reg;
    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            majority_reg  <= 0;
            inner_counter <= 0;
        end
        else if (soft_rst) begin
            majority_reg  <= 0;
            inner_counter <= 0;
        end
        else if (!dat_samp_en) begin
            // Reset counter between sample windows so it's ready for the next bit
            inner_counter <= 2'b0;
        end
        else if (inner_counter < 3 && dat_samp_en) begin
            majority_reg[inner_counter] <= RX_IN;
            inner_counter <= inner_counter + 1;
        end
        // else: dat_samp_en still high but we already have 3 samples — hold, do nothing
    end
    // Calualate the majority bit
    assign sampled_bit = (majority_reg[0] && majority_reg[1]) || (majority_reg[0] && majority_reg[2]) || (majority_reg[1] && majority_reg[2]);
endmodule //data_sampling