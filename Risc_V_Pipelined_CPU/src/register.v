`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/30/2025 02:10:45 PM
// Design Name: 
// Module Name: register
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
module register #(parameter WIDTH = 8) (
    input clk,
    input rst,
    input load,
    input [WIDTH-1:0] D,
    output [WIDTH-1:0] Q
);

    wire [WIDTH-1:0] mux_out;
    genvar i;
    
    generate
        for (i = 0; i < WIDTH; i = i + 1) begin
            MUX mux_inst (
                .A(Q[i]),
                .B(D[i]),
                .sel(load),
                .Y(mux_out[i])
            );

            DFF dff_inst (
                .clk(clk),
                .rst(rst),
                .D(mux_out[i]),
                .Q(Q[i])
            );
        end
    endgenerate

endmodule