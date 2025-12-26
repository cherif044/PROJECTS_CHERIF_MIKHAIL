`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/07/2025 03:43:04 PM
// Design Name: 
// Module Name: RCA
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

module RCA(
    input [31:0] A, B,
    input cin,
    output unsigned [31:0] Sum,
    output unsigned Cout
);

    wire [32:0] carry;
    assign carry[0] = cin; // Initial carry-in is 0

    generate
        genvar i;
        for (i = 0; i < 32; i = i + 1) begin
                fullAdder FA (
                    .A(A[i]),
                    .B(B[i]),
                    .Cin(carry[i]),
                    .Out(Sum[i]),
                    .Cout(carry[i+1])
                );
        end
    endgenerate

    assign Cout = carry[32];

endmodule