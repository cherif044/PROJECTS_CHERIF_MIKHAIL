`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/29/2024 06:42:22 PM
// Design Name: 
// Module Name: counter_x_bit
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


module counter_x_bit #(parameter x = 3, n = 6)
(input clk, reset, en, output reg [x-1:0] count);
always @(posedge clk, posedge reset) begin
 if (reset == 1)
 count <= 0; // non-blocking assignment
 // initialize flip flop here
  else if (en == 1'b1)
         if (count == n-1)
         count <= 0; // non-blocking assignment
         // reach count end and get back to zero
         else 
         count <= count + 1; // non-blocking clk 
 // normal operation
 
 
end


endmodule
