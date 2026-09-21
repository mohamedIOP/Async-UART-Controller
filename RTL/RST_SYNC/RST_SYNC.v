module RST_SYNC #(
    parameter NUM_STAGES = 2
)(
    input CLK,RST,
    output SYNC_RST
);
    reg [NUM_STAGES - 1:0] Synchronizer;
    always @(posedge CLK or negedge RST) begin
        if(!RST) begin
            Synchronizer <= 0;
        end
        else begin
            Synchronizer <= {1'b1,Synchronizer[NUM_STAGES - 1:1]};
        end
    end
    assign SYNC_RST = Synchronizer[0];
endmodule //RST_SYNC