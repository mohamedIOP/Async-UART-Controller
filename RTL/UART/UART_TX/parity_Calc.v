module Parity_Calc(
    input [7:0] pData,
    input parTyp,regData,
    input CLK,RST,
    output reg parBit
);
    always @(posedge CLK or negedge RST) begin
        if (!RST) parBit <= 0;
        else if (regData) begin
            parBit <= parTyp ? !(^pData) : (^pData);
        end
    end
endmodule