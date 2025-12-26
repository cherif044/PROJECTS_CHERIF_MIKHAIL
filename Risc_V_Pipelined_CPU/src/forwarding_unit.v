`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 18.11.2025 13:50:11
// Design Name: 
// Module Name: forwarding_unit
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


module forwarding_unit(
    input EX_MEM_RegWrite, MEM_WB_RegWrite,
    input [4:0] EX_MEM_RegisterRd, ID_EX_RegisterRs1, ID_EX_RegisterRs2, MEM_WB_RegisterRd,
    output reg [1:0] forwardA, forwardB
    );

    always @(*) begin
        if((EX_MEM_RegWrite == 1 && (EX_MEM_RegisterRd != 0) && (EX_MEM_RegisterRd == ID_EX_RegisterRs1)))begin
            forwardA = 2'b10;
        end
        else if((MEM_WB_RegWrite == 1 && MEM_WB_RegisterRd != 0 && MEM_WB_RegisterRd == ID_EX_RegisterRs1))begin
            forwardA = 2'b01;
        end
        else begin
            forwardA = 2'b00;
        end
    end

    always @(*) begin
        if((EX_MEM_RegWrite == 1 && (EX_MEM_RegisterRd != 0) && (EX_MEM_RegisterRd == ID_EX_RegisterRs2)))begin
            forwardB = 2'b10;
        end
        else if((MEM_WB_RegWrite == 1 && MEM_WB_RegisterRd != 0 && MEM_WB_RegisterRd == ID_EX_RegisterRs2))begin
            forwardB = 2'b01;
        end
        else begin
            forwardB = 2'b00;
        end
    end
    
endmodule