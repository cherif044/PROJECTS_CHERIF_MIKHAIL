`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 12/04/2024 12:02:11 PM
// Design Name: 
// Module Name: score
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module score(
    input clk, reset,
    input [3:0] score1units, score1tens,score2units,score2tens,
    output [6:0] seg,
    output [3:0] an
    );
    
    integer i;
    reg [1:0] tog; 
    reg [3:0] numselect;
    BCD bcd(tog, numselect, seg, an);
    always @(posedge clk or posedge reset) begin
    if (reset) begin i<=0; tog = 2'b00; numselect = 4'b0000; end
    else
    if(i ==4) i<=0;
    else begin
    case (i) 
    0:begin tog =  2'b00; numselect = score1units; end
    1:begin tog =  2'b01; numselect = score1tens; end
    2:begin tog =  2'b10; numselect = score2units; end
    3:begin tog =  2'b11; numselect = score2tens; end
    endcase
    i = i+1;
    end
    end

endmodule
