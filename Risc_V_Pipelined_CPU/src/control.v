`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/07/2025 03:45:10 PM
// Design Name: 
// Module Name: control
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
module Control (
    input [4:0] instruction6_2,
    output reg Branch,
    output reg MemRead,
    output reg MemtoReg,
    output reg [1:0] ALUOp,
    output reg MemWrite,
    output reg ALUSrc,
    output reg RegWrite
);

`define     OPCODE_Branch   5'b11_000  //beq, bne, blt, bge, bltu, bgeu [DONE]
`define     OPCODE_Load     5'b00_000  //lb, lh, lw, lbu, lhu [DONE]
`define     OPCODE_Store    5'b01_000  //sb,sh,sw [DONE]
`define     OPCODE_JALR     5'b11_001  //jalr
`define     OPCODE_JAL      5'b11_011  //JAL
`define     OPCODE_Arith_I  5'b00_100  //addi, slti, sltiu, xori, ori, andi
`define     OPCODE_Arith_R  5'b01_100  //add, sub,sll,slt,sltu,xor, srl,sra,or,and [DONE]
`define     OPCODE_AUIPC    5'b00_101  // AUIPC
`define     OPCODE_LUI      5'b01_101  // LUI
`define     OPCODE_SYSTEM   5'b11_100 
`define     OPCODE_Custom   5'b10_001

    always @(*) begin
        case(instruction6_2)
            `OPCODE_Arith_R: begin //add, sub,sll,slt,sltu,xor, srl,sra,or,and
                Branch = 0;
                MemRead = 0;
                MemtoReg = 0;
                ALUOp = 2'b10;
                MemWrite = 0;
                ALUSrc = 0;
                RegWrite = 1;
                end
            
            `OPCODE_Arith_I: begin //addi, slti, sltiu, xori, ori, andi
                Branch = 0;
                MemRead = 0;
                MemtoReg = 0;
                ALUOp = 2'b10;
                MemWrite = 0;
                ALUSrc = 1;
                RegWrite = 1;
                end
            
            `OPCODE_Branch: begin //beq, bne, blt, bge, bltu, bgeu
                 Branch = 1;
                 MemRead = 0;
                 MemtoReg = 1'bx;
                 ALUOp = 2'b01;
                 MemWrite = 0;
                 ALUSrc = 0;
                 RegWrite = 0;
                end
                
            `OPCODE_Load: begin //lb, lh, lw, lbu, lhu
                 Branch = 0;
                 MemRead = 1;
                 MemtoReg = 1;
                 ALUOp = 2'b00;
                 MemWrite = 0;
                 ALUSrc = 1;
                 RegWrite = 1;
                 end
            
            `OPCODE_Store: begin //sb,sh,sw
                 Branch = 0;
                 MemRead = 0;
                 MemtoReg = 1'bx;
                 ALUOp = 2'b00;
                 MemWrite = 1;
                 ALUSrc = 1;
                 RegWrite = 0;
                 end
                 
            `OPCODE_JALR: begin
		         Branch   = 1'b1;
		         MemRead  = 1'bx;
		         MemtoReg = 1'b0;
		         ALUOp    = 2'b00;
		         MemWrite = 1'bx;
		         ALUSrc   = 1'b1;
		         RegWrite = 1'b1;
                 end
            
            `OPCODE_JAL: begin
		         Branch = 1;
		         MemRead = 1'bx;
		         MemtoReg = 0;
		         ALUOp = 2'b00;
		         MemWrite = 1'bx;
		         ALUSrc = 1;
		         RegWrite = 1;
                 end
            
            `OPCODE_AUIPC: begin
		         Branch = 0;
		         MemRead = 0;
		         MemtoReg = 0;
		         ALUOp = 2'b00;
		         MemWrite = 0;
		         ALUSrc = 1;
		         RegWrite = 1;
                 end
            
            `OPCODE_LUI: begin
		         Branch = 0;
		         MemRead = 0;
		         MemtoReg = 0;
		         ALUOp = 2'b10;
		         MemWrite = 0;
		         ALUSrc = 1;
		         RegWrite = 1;
                 end
        endcase
    end    

//    always @(*) begin
//        if (instruction6_2 == 5'b01100) begin // R-type
//             Branch = 0;
//             MemRead = 0;
//             MemtoReg = 0;
//             ALUOp = 2'b10;
//             MemWrite = 0;
//             ALUSrc = 0;
//             RegWrite = 1;
//        end
//        else if (instruction6_2 == 5'b00000) begin // LW
//             Branch = 0;
//             MemRead = 1;
//             MemtoReg = 1;
//             ALUOp = 2'b00;
//             MemWrite = 0;
//             ALUSrc = 1;
//             RegWrite = 1;
//        end
//        else if (instruction6_2 == 5'b01000) begin // SW
//             Branch = 0;
//             MemRead = 0;
//             MemtoReg = 1'bx;
//             ALUOp = 2'b00;
//             MemWrite = 1;
//             ALUSrc = 1;
//             RegWrite = 0;
//        end
//        else if (instruction6_2 == 5'b11000) begin // BEQ
//             Branch = 1;
//             MemRead = 0;
//             MemtoReg = 1'bx;
//             ALUOp = 2'b01;
//             MemWrite = 0;
//             ALUSrc = 0;
//             RegWrite = 0;
//        end
//        else begin
//             Branch = 0;
//             MemRead = 0;
//             MemtoReg = 0;
//             ALUOp = 2'b00;
//             MemWrite = 0;
//             ALUSrc = 0;
//             RegWrite = 0;
//        end 
//    end
    
endmodule
