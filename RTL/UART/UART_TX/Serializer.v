module Serializer (
    input [7:0] pData,
    input serEn,regData,
    input CLK,RST,
    output reg serData,serDone
);
    reg [7:0] pDataReg;
    reg [3:0] counter;
    wire counterMax = (counter == 7);
    always @(posedge CLK or negedge RST) begin
        if (!RST)        pDataReg <= 0;
        else if (regData) pDataReg <= pData;
    end
    always @(*) begin
        serDone = counterMax;
        serData = pDataReg[counter];
    end
    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            counter <= 0;
        end
        else if (regData) begin
            counter <= 0;
        end
        else if (serEn) begin
            counter <= counter + 1;
        end
    end
endmodule //Serializer