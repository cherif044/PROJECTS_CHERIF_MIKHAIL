`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/16/2025 07:08:27 PM
// Design Name: 
// Module Name: common_memory
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


module common_memory(
    input clk, MemRead, MemWrite,
    input [2:0] function3,
    input [5:0] addr, 
    input [31:0] data_in, 
    output reg [31:0] data_out
);
    reg [31:0] mem [0:63];
    
    wire [31:0] mem_access_out;
    
    Memory_Access_Unit memory_access_unit(
        .data_in(MemWrite ? data_in : mem[addr]),
        .function3(function3),
        .data_out(mem_access_out)
    );

    always @(posedge clk) begin
        if (MemWrite) begin
            mem[addr] <= mem_access_out;
        end
    end

    always @(*) begin
        data_out = mem[addr];
    end
//    always @(*) begin
//        if (MemRead) begin
//            data_out = mem_access_out;
//        end
//    end
endmodule

