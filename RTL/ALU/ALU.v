module ALU(
    input [15:0] A,B,
    input [3:0] ALU_FUN,
    input CLK,RST,
    input EN,
    output reg [15:0] ALU_OUT,
    output reg OUT_VALID
);
    reg [15:0] ALU_OUT_Comb;
    reg OUT_VALID_Comb;
    always @(posedge CLK or negedge RST) begin
        if(!RST) 
            begin
                ALU_OUT <= 'b0;
                OUT_VALID <= 'b0;
            end
        else 
            begin
                ALU_OUT <= ALU_OUT_Comb;
                OUT_VALID <= OUT_VALID_Comb;
            end
    end
    always @(*) begin
        OUT_VALID_Comb = 1'b0 ;
        ALU_OUT_Comb   = 'b0 ;
        if(EN)
            begin
                OUT_VALID_Comb = 1'b1 ;
                case (ALU_FUN)
                    4'b0000: ALU_OUT_Comb = {1'b0, A} + {1'b0, B};
                    4'b0001: ALU_OUT_Comb = {1'b0, A} - {1'b0, B};
                    4'b0010: ALU_OUT_Comb = A * B;
                    4'b0011: ALU_OUT_Comb = A / B;
                    4'b0100: ALU_OUT_Comb = A & B;
                    4'b0101: ALU_OUT_Comb = A | B;
                    4'b0110: ALU_OUT_Comb = ~(A & B);
                    4'b0111: ALU_OUT_Comb = ~(A | B);
                    4'b1000: ALU_OUT_Comb = (A ^ B);
                    4'b1001: ALU_OUT_Comb = (A ~^ B);
                    4'b1010: ALU_OUT_Comb = (A == B) ? 16'd1 : 16'd0;
                    4'b1011: ALU_OUT_Comb = (A > B)  ? 16'd2 : 16'd0;
                    4'b1100: ALU_OUT_Comb = (A < B)  ? 16'd3 : 16'd0;
                    4'b1101: ALU_OUT_Comb = A >> 1;
                    4'b1110: ALU_OUT_Comb = A << 1;
                    default: ALU_OUT_Comb = 0;
                endcase
            end
    end
endmodule
