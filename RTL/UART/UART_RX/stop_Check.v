module stop_Check (
    input stp_chk_en,sampled_bit,
    input CLK,RST,soft_rst,
    output reg stp_err
);
    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            stp_err <= 0;
        end
        else if (soft_rst) begin
            stp_err <= 0;
        end
        else if (stp_chk_en) begin
            stp_err <= !sampled_bit;
        end
    end
endmodule //stop_Check