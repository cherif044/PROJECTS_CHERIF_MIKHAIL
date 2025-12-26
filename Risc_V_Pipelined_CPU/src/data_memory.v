`include "defines.v"

module DataMem(
    input clk, MemRead, MemWrite,
    input [2:0] function3,
    input [5:0] addr, 
    input [31:0] data_in, 
    output reg [31:0] data_out
);

    wire [31:0] mem_access_out;
    
    Memory_Access_Unit memory_access_unit(
        .data_in(MemWrite ? data_in : mem[addr]),
        .function3(function3),
        .data_out(mem_access_out)
    );

    reg [31:0] mem [0:63];

    always @(posedge clk) begin
        if (MemWrite) begin
            mem[addr] <= mem_access_out;
        end
    end

    always @(*) begin
        if (MemRead) begin
            data_out = mem_access_out;
        end
    end
    initial begin
                // Initialize all memory to zero first
        mem[0]  = 32'h00000000;
        mem[1]  = 32'h00000000;
        mem[2]  = 32'h00000000;
        mem[3]  = 32'h00000000;
        mem[4]  = 32'h00000000;
        mem[5]  = 32'h00000000;
        mem[6]  = 32'h00000000;
        mem[7]  = 32'h00000000;
        mem[8]  = 32'h00000000;
        
        // mem[9] - offset 36: LW access from instr mem[14]
        mem[9]  = 32'h12345678; // Word load test
        
        // mem[10] - offset 40: SH store target from instr mem[5]
        mem[10] = 32'h00000000; // Will be written by store halfword
        
        // mem[11] - offset 44: LBU access from instr mem[13]
        mem[11] = 32'hFF00AA55; // Unsigned byte load test (should load 0x000000FF)
        
        mem[12] = 32'h00000000;
        mem[13] = 32'h00000000;
        mem[14] = 32'h00000000;
        mem[15] = 32'h00000000;
        mem[16] = 32'h00000000;
        mem[17] = 32'h00000000;
        mem[18] = 32'h00000000;
        mem[19] = 32'h00000000;
        
        // mem[20] - offset 80: LW access from instr mem[17]
        mem[20] = 32'hDEADBEEF; // Word load test
        
        mem[21] = 32'h00000000;
        mem[22] = 32'h00000000;
        mem[23] = 32'h00000000;
        mem[24] = 32'h00000000;
        mem[25] = 32'h00000000;
        mem[26] = 32'h00000000;
        mem[27] = 32'h00000000;
        mem[28] = 32'h00000000;
        mem[29] = 32'h00000000;
        mem[30] = 32'h00000000;
        mem[31] = 32'h00000000;
        mem[32] = 32'h00000000;
        mem[33] = 32'h00000000;
        mem[34] = 32'h00000000;
        mem[35] = 32'h00000000;
        mem[36] = 32'h00000000;
        mem[37] = 32'h00000000;
        mem[38] = 32'h00000000;
        
        // mem[39] - offset 156: LW access from instr mem[1], SW store from instr mem[18]
        mem[39] = 32'hCAFEBABE; // Word load test, will be overwritten by store
        
        mem[40] = 32'h00000000;
        mem[41] = 32'h00000000;
        
        // mem[42] - offset 168: LB access from instr mem[4]
        mem[42] = 32'h7FFFFF80; // Signed byte load test (should load 0xFFFFFF80 = -128)
        
        mem[43] = 32'h00000000;
        mem[44] = 32'h00000000;
        mem[45] = 32'h00000000;
        mem[46] = 32'h00000000;
        mem[47] = 32'h00000000;
        mem[48] = 32'h00000000;
        mem[49] = 32'h00000000;
        
        // mem[50] - offset 200: LH access from instr mem[0]
        mem[50] = 32'h1234ABCD; // Halfword load test (should load 0xFFFFABCD = -21555 signed)
        
        mem[51] = 32'h00000000;
        mem[52] = 32'h00000000;
        mem[53] = 32'h00000000;
        mem[54] = 32'h00000000;
        mem[55] = 32'h00000000;
        mem[56] = 32'h00000000;
        mem[57] = 32'h00000000;
        mem[58] = 32'h00000000;
        mem[59] = 32'h00000000;
        mem[60] = 32'h00000000;
        mem[61] = 32'h00000000;
        mem[62] = 32'h00000000;
        mem[63] = 32'h00000000;

    end
    
//    initial begin
//    $readmemh("data_mem_data_.txt", mem);
//    end

endmodule