`include "defines.v"

module Shifter (
    input signed [31:0] A,
    input [4:0] shamt, // shift amount
    input [1:0] alufn, // {function7[5], function3[2]}
    output reg [31:0] out
);


    always @(*) begin
        if (alufn[1]) begin
            out = $signed(A) >>> shamt; // Arithmetic right shift
        end
        else begin
            if (alufn[0]) begin
                out = A >> shamt; // Logical right shift
            end
            else begin
                out = A << shamt; // Logical left shift
            end
        end
    end
    
endmodule