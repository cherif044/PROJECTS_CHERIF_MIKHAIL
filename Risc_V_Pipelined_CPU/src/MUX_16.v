`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/07/2025 03:44:24 PM
// Design Name: 
// Module Name: MUX_16
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
module MUX_16 (
    input A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, 
    input [3:0] sel,
    output reg Y
);
    always @(*) begin
        case (sel)
            4'b0000:   Y = A;
            4'b0001:   Y = B;
            4'b0010:   Y = C;
            4'b0011:   Y = D;
            4'b0100:   Y = E;
            4'b0101:   Y = F;
            4'b0110:   Y = G;
            4'b0111:   Y = H;
            4'b1000:   Y = I;
            4'b1001:   Y = J;
            4'b1010:   Y = K;
            4'b1011:   Y = L;
            4'b1100:   Y = M;
            4'b1101:   Y = N;
            4'b1110:   Y = O;
            4'b1111:   Y = P;
        endcase
    end
endmodule