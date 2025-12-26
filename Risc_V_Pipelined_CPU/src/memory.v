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


module memory(
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
            mem[addr+32'd32] <= mem_access_out;
        end
    end

    always @(*) begin
        if (MemRead) begin
            data_out = mem[addr+32];
        end
        else begin
            data_out = mem[addr];
        end
    end

    initial begin
        // --- U-Type Instruction Tests ---
        mem[0] = 32'habcde337; // lui x6, 703710 (lui t1, 0xABCDE)
        mem[1] = 32'h00001397; // auipc x7, 1


        // --- Store Results ---
        // la s0, result_lui is expanded into auipc and addi
        mem[2] = 32'h00000417; // auipc x8, 0
        mem[3] = 32'hff840413; // addi x8, x8, -8
        // Store the test results to memory
        mem[4] = 32'h00642023; // sw x6, 0(x8)   (sw t1, 0(s0))
        mem[5] = 32'h00742223; // sw x7, 4(x8)   (sw t2, 4(s0))


        // The .bss section starts at the beginning of the data segment in RARS.
        // We assume it maps to the start of our data memory here.
        // The la s0, result_lui will resolve to the address of mem[32].

        // Expected to become 0xABCDE000 after sw t1, 0(s0)
        mem[32] = 32'h00000000;

        // Expected to become 0x00401004 after sw t2, 4(s0)
        mem[33] = 32'h00000000;

        // Initialize the rest of memory to 0
        mem[34] = 32'h0; mem[35] = 32'h0; // and so on...
    end




//    initial begin
//        $readmemh("test1.txt",mem);
//    end
endmodule

