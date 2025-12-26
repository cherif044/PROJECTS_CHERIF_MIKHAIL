`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/07/2025 03:46:04 PM
// Design Name: 
// Module Name: ALU
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

//`include "defines.v"
module ALU(
    input [31:0] A, B,
    input [3:0] ALU_select,
    output wire zero_flag, carry_flag, overflow_flag, sign_flag,
    output reg [31 :0] out
);

    wire [31:0] adder_out;

    RCA adder(
        .A(A),
        .B(ALU_select[0] ? ~B : B),
        .cin(ALU_select[0]),
        .Sum(adder_out),
        .Cout(carry_flag)
    );
    assign zero_flag = (adder_out == 32'b0);
    assign sign_flag = adder_out[31];
    assign overflow_flag = (A[31] == ALU_select[0] ? ~B[31] : B[31]) && (adder_out[31] != A[31]);

    wire [31:0] shift_out;

    Shifter shifter_inst (
        .A(A),
        .shamt(B[4:0]),
        .alufn(ALU_select[1:0]),
        .out(shift_out)
    );

    always @(*) begin
        case (ALU_select)
            4'b0000: out = adder_out; // ADD
            4'b0001: out = adder_out; // SUB
            4'b0100: out = A | B;    // OR
            4'b0101: out = A & B;    // AND
            4'b0111: out = A ^ B;    // XOR
            4'b1000: out = shift_out; // SLL
            4'b1001: out = shift_out; // SRL
            4'b1010: out = shift_out; // SRA 
            4'b1101: out = {30'b0, sign_flag != overflow_flag}; // SLT
            4'b1111: out = {30'b0, ~carry_flag}; // SLTU
            default: out = adder_out;
        endcase
    end

endmodule
