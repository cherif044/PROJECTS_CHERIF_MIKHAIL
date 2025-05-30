`timescale 1ns / 1ps

module minuteur(
    input clk,
    input reset,
    input timer_start, timer_tick,
    output timer_up
    );
    
    // signal declaration
    reg [8:0] timer_reg, timer_next;
    
    // register control
    always @(posedge clk or posedge reset)
        if(reset)
            timer_reg <= 9'b111111111;
        else
            timer_reg <= timer_next;
    
    // next state logic
    always @*
        if(timer_start)
            timer_next = 9'b111111111;
        else if((timer_tick) && (timer_reg != 0))
            timer_next = timer_reg - 1;
        else
            timer_next = timer_reg;
            
    // output
    assign timer_up = (timer_reg == 0);
    
endmodule
