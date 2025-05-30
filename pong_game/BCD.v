`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/10/2024 04:09:50 PM
// Design Name: 
// Module Name: BCD
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


module BCD(
input [1:0]tog,
input [3:0] num,
output reg [0:6] segments,
output reg [3:0] anode_active
);

always @* begin
        case(tog)
            0: anode_active = 4'b1110;
            1: anode_active = 4'b1101;
            2: anode_active = 4'b1011;
            3: anode_active = 4'b0111;
        endcase 
        case(num)
0: segments = 7'b1000000; // 0
1: segments = 7'b1111001; // 1
2: segments = 7'b0100100; // 2
3: segments = 7'b0110000; // 3
4: segments = 7'b0011001; // 4
5: segments = 7'b0010010; // 5
6: segments = 7'b0000010; // 6
7: segments = 7'b1111000; // 7
8: segments = 7'b0000000; // 8
9: segments = 7'b0010000; // 9
 default: segments = 7'b0000000;

        endcase

end

endmodule
