module parity_Check (
    input par_chk_en,PAR_TYP,sampled_bit,soft_rst,
    input CLK,RST,
    input [7:0] P_DATA,
    output reg par_err
);
    wire calc_par_bit = (PAR_TYP) ? ~^P_DATA : ^P_DATA;
    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            par_err <= 0;
        end
        else if (soft_rst) begin
            par_err <= 0;
        end
        else if (par_chk_en) begin
            par_err <= (calc_par_bit ^ sampled_bit);
        end
    end
endmodule //parity_Check