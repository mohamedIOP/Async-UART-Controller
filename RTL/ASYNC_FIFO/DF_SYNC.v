module DF_SYNC #(
    parameter WIDTH = 1
) (
    input                   CLK,
    input                   RST,
    input      [WIDTH-1:0]  Data_In,
    output     [WIDTH-1:0]  Data_Out
);

    reg [WIDTH-1:0] Synchronizer [1:0];  

    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            Synchronizer[0] <= {WIDTH{1'b0}};
            Synchronizer[1] <= {WIDTH{1'b0}};
        end
        else begin
            Synchronizer[0] <= Data_In;
            Synchronizer[1] <= Synchronizer[0];
        end
    end

    assign Data_Out = Synchronizer[1];

endmodule