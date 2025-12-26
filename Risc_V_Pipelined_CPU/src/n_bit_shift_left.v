`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/30/2025 02:12:53 PM
// Design Name: 
// Module Name: n_bit_shift_left
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

`include "defines.v"
module n_bit_shift_left (
    input [31:0] in,
    output [31:0] out
);

    assign out = {in[30:0], 1'b0};

endmodule