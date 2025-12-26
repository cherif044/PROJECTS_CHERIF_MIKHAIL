`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/09/2025 04:27:02 PM
// Design Name: 
// Module Name: memory_access_unit
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


module Memory_Access_Unit (
    input [31:0] data_in,
    input [2:0] function3,
    output reg [31:0] data_out
);

    always @(*) begin
        case (function3)
            3'b000: data_out = {{24{data_in[7]}}, data_in[7:0]}; // byte
            3'b001: data_out = {{16{data_in[15]}}, data_in[15:0]}; // half-word
            3'b010: data_out = data_in; // word
            3'b100: data_out = {24'b0, data_in[7:0]}; // byte unsigned
            3'b101: data_out = {16'b0, data_in[15:0]}; // half-word unsigned
            default: data_out = 32'b0;
        endcase
    end
    
endmodule