`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 09/30/2025 02:13:35 PM
// Design Name: 
// Module Name: immediate_generator
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
module immediate_generator (
    input [31:0] instruction,
    input [6:0] opcode,
    output reg [31:0] immediate
);

    always@(*)begin
        case(opcode)
            7'b0010011: immediate = {{21{instruction[31]}},instruction[30:20]}; // I-type
            7'b0100011: immediate = {{21{instruction[31]}},instruction[30:25], instruction[11:7]}; // S-type
            7'b1100011: immediate = {{21{instruction[31]}}, instruction[7], instruction[30:25], instruction[11:8], 1'b0}; // B-type
            7'b0010111: immediate = {instruction[31:12], 12'b0}; // U-type (AUIPC)
            7'b0110111: immediate = {instruction[31:12], 12'b0}; // U-type (LUI)
            7'b1101111: immediate = {{12{instruction[31]}}, instruction[19:12], instruction[20], instruction[30:21]}; // J-type - double check for lsb 0
            7'b1100111: immediate = {{21{instruction[31]}},instruction[30:20]}; // I-type (JALR)
            default: immediate = {{21{instruction[31]}},instruction[30:20]};
        endcase
        
    end
    
endmodule