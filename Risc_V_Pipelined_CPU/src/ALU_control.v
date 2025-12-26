`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/07/2025 04:52:25 PM
// Design Name: 
// Module Name: ALU_control
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
module ALU_control (
    input [1:0] ALUOp,
    input [2:0] function3,
    input opcode, // opcode[5]
    output reg [3:0] ALU_select
);

    always @(*) begin
        if(ALUOp == 2'b00) begin
            ALU_select = 4'b0000; // ADD
        end
        else if (ALUOp == 2'b01) begin
            ALU_select = 4'b0001; // SUB
        end
        else case ({opcode, function3})
            4'b0000: ALU_select = 4'b0000; // ADD
            4'b1000: ALU_select = 4'b0001; // SUB
            4'b0110: ALU_select = 4'b0100; // OR
            //4'b0011: ALU_select = 4'b0011; // B
            4'b0111: ALU_select = 4'b0101; // AND
            4'b0100: ALU_select = 4'b0111; // XOR 
            4'b0001: ALU_select = 4'b1000; // SLL
            4'b0101: ALU_select = 4'b1001; // SRL
            4'b1101: ALU_select = 4'b1010; // SRA
            4'b0010: ALU_select = 4'b1101; // SLT
            4'b0011: ALU_select = 4'b1111; // SLTU
            default: ALU_select = 4'b0000; // Default to ADD
        endcase
    end
    
endmodule


