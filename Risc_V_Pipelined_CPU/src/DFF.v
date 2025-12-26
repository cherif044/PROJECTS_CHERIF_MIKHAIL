`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/30/2025 02:09:11 PM
// Design Name: 
// Module Name: DFF
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
module DFF (
    input clk, 
    input rst, 
    input D, 
    output reg Q
);

    always @ (posedge clk or posedge rst)
    if (rst) begin
        Q <= 1'b0;
    end else begin
        Q <= D;
    end 
endmodule