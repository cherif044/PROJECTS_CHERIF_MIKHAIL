`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/07/2025 03:49:13 PM
// Design Name: 
// Module Name: n_bit_MUX_16
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
module n_bit_MUX_16 #(parameter WIDTH = 8) (
    input [WIDTH-1:0] A,
    input [WIDTH-1:0] B,
    input [WIDTH-1:0] C,
    input [WIDTH-1:0] D,
    input [WIDTH-1:0] E,
    input [WIDTH-1:0] F,
    input [WIDTH-1:0] G,
    input [WIDTH-1:0] H,
    input [WIDTH-1:0] I,
    input [WIDTH-1:0] J,
    input [WIDTH-1:0] K,
    input [WIDTH-1:0] L,
    input [WIDTH-1:0] M,
    input [WIDTH-1:0] N,
    input [WIDTH-1:0] O,
    input [WIDTH-1:0] P,
    input [3:0] sel,
    output [WIDTH-1:0] Y
);
    genvar i;
    generate
        for (i = 0; i < WIDTH; i = i + 1) begin
            MUX_16 mux_inst (
                .A(A[i]),
                .B(B[i]),
                .C(C[i]),
                .D(D[i]),
                .E(E[i]),
                .F(F[i]),
                .G(G[i]),
                .H(H[i]),
                .I(I[i]),
                .J(J[i]),
                .K(K[i]),
                .L(L[i]),
                .M(M[i]),
                .N(N[i]),
                .O(O[i]),
                .P(P[i]),
                .sel(sel),
                .Y(Y[i])
            );
        end
    endgenerate
endmodule
