module UART_RX_TOP (
    input RX_IN,
    input [5:0] Prescale,
    input PAR_EN,PAR_TYP,
    input CLK,RST,
    output [7:0] P_DATA,
    output parity_Error,Stop_Error,data_valid
);
    // control signals
    wire dat_samp_en_inner,edge_bit_cnt_enable_inner,
         deser_en_inner,stp_chk_en_inner,strt_chk_en_inner,
         par_chk_en_inner,soft_rst_inner;
    // status signals
    wire par_err_inner,strt_glitch_inner,stp_err_inner;
    wire [4:0] edge_cnt_inner;
    wire [3:0] bit_cnt_inner;
    wire sampled_bit_inner;
    // instantiation of blocks
    UART_RX_FSM UART_RX_FSM_Block (
        .RX_IN(RX_IN),
        .PAR_EN(PAR_EN),.par_err(par_err_inner),
        .prescale(Prescale),
        .edge_cnt(edge_cnt_inner),
        .bit_cnt(bit_cnt_inner),
        .strt_glitch(strt_glitch_inner),.stp_err(stp_err_inner),
        .CLK(CLK),.RST(RST),
        .par_chk_en(par_chk_en_inner),.strt_chk_en(strt_chk_en_inner),.stp_chk_en(stp_chk_en_inner),
        .deser_en(deser_en_inner),
        .edge_bit_cnt_enable(edge_bit_cnt_enable_inner),
        .dat_samp_en(dat_samp_en_inner),
        .data_valid(data_valid),
        .soft_rst(soft_rst_inner)
    );
    edge_bit_counter edge_bit_counter_BLock (
        .edge_bit_cnt_enable(edge_bit_cnt_enable_inner),
        .prescale(Prescale),
        .CLK(CLK),.RST(RST),
        .soft_rst(soft_rst_inner),
        .edge_cnt(edge_cnt_inner),
        .bit_cnt(bit_cnt_inner)
    );
    data_sampling data_sampling_Block (
        .RX_IN(RX_IN),
        .dat_samp_en(dat_samp_en_inner),
        .CLK(CLK),.RST(RST),
        .soft_rst(soft_rst_inner),
        .sampled_bit(sampled_bit_inner)
    );
    parity_Check parity_Check_Block (
        .par_chk_en(par_chk_en_inner),.PAR_TYP(PAR_TYP),.sampled_bit(sampled_bit_inner),.soft_rst(soft_rst_inner),
        .CLK(CLK),.RST(RST),
        .P_DATA(P_DATA),
        .par_err(par_err_inner)
    );
    strt_Check strt_Check_Block (
        .strt_chk_en(strt_chk_en_inner),.sampled_bit(sampled_bit_inner),
        .CLK(CLK),.RST(RST),
        .soft_rst(soft_rst_inner),
        .strt_glitch(strt_glitch_inner)
    );
    stop_Check stop_Check_BLock (
        .stp_chk_en(stp_chk_en_inner),.sampled_bit(sampled_bit_inner),
        .CLK(CLK),.RST(RST),.soft_rst(soft_rst_inner),
        .stp_err(stp_err_inner)
    );
    deserializer deserializer_Block (
        .deser_en(deser_en_inner),.sampled_bit(sampled_bit_inner),
        .CLK(CLK),.RST(RST),
        .P_DATA(P_DATA)
    );
    assign parity_Error = par_err_inner;
    assign Stop_Error   = stp_err_inner;
endmodule //UART_RX_TOP