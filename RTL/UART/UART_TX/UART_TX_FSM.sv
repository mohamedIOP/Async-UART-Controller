module UART_TX_FSM (
    input parEn,serDone,dataValid, // inputs needed for FSM Transitions
    input CLK,RST,
    output reg serEn,busy,regData, // control signals of serializer and control unit
    output reg [1:0] muxSel // choose which bit for the TX_OUT
);
    // Define the states 
    typedef enum logic [2:0] {
        idle  = 'b000,
        start = 'b001,
        data  = 'b011,
        parity = 'b010,
        stop = 'b110
} state_t;
    state_t currentState,nextState;
    // Output Control Signals
    always @(*) begin
        serEn = (currentState == data); // to start from first bit and not to be shifted
        busy = (currentState != idle); // if it's not idle so it's working
        regData = dataValid && (currentState == idle || currentState == stop);
        muxSel = 'b0; // default mux selection
        // Set Mux Selection lines for TX_OUT
        case (currentState)
            start: muxSel = 'b00;
            data: muxSel = 'b10;
            parity: muxSel = 'b11;
            stop: muxSel = 'b01;
            default: muxSel = 'b01; // idle -> line idle high
        endcase
    end
    // Change the current state
    always @(posedge CLK or negedge RST) begin
        if(!RST) begin
            currentState <= idle;
        end
        else begin
            currentState <= nextState;
        end
    end
    // nextState Controlling 
    always @(*) begin
        nextState = idle;
        case (currentState)
            idle: nextState = (dataValid)  ? start : idle;
            start: nextState = data;
            data: nextState = (serDone) ? (parEn ? parity : stop) : data;
            parity: nextState = stop;
            stop: nextState = (dataValid) ? start : idle;
            default : nextState = idle;
        endcase
    end
endmodule