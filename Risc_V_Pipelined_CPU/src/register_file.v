`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/07/2025 02:19:08 PM
// Design Name: 
// Module Name: register_file
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
module register_file(
    input clk,
    input rst,
    input[4:0] readReg1,
    input[4:0] readReg2,
    input[4:0] writeReg,
    input regWriteEnable,
    output [31:0] readData1,
    output [31:0] readData2,
    input [31:0] writeData
    );

    reg [31:0] regFile [31:0];
    integer i;
    
    always@(negedge clk or posedge rst) begin
        if(rst == 1'b1) begin
            for (i=0;i<32;i=i+1)
                regFile[i] = 0;
        end
        
        else if(regWriteEnable == 1 && writeReg != 0) begin
                    regFile[writeReg] = writeData;
        end
    end   
    
    assign readData1 = regFile[readReg1];
    assign readData2 = regFile[readReg2];

endmodule
