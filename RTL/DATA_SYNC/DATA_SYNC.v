module DATA_SYNC #(
    parameter NUM_STAGES = 2,
    parameter BUS_WIDTH = 8
)(
    input [BUS_WIDTH - 1:0] unsync_bus,
    input bus_enable,
    input CLK,RST,
    output reg [BUS_WIDTH - 1:0] sync_bus,
    output reg enable_pulse
);
    reg [NUM_STAGES - 1:0] Multi_Flip_Flop_Synchronizer;
    reg Pulse_Gen_Flop;
    wire Pulse_Gen_Output = (Multi_Flip_Flop_Synchronizer[0]) && (!Pulse_Gen_Flop);
    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            sync_bus <= 0;
            enable_pulse <= 0;
            Multi_Flip_Flop_Synchronizer <= 0;
            Pulse_Gen_Flop <= 0;
        end
        else begin
            Multi_Flip_Flop_Synchronizer <= {bus_enable, Multi_Flip_Flop_Synchronizer[NUM_STAGES - 1:1]};
            Pulse_Gen_Flop <= Multi_Flip_Flop_Synchronizer[0];
            enable_pulse <= Pulse_Gen_Output;
            if (Pulse_Gen_Output) begin
                sync_bus <= unsync_bus;
            end
            else begin
                sync_bus <= sync_bus;
            end
        end
    end
endmodule //DATA_SYNC