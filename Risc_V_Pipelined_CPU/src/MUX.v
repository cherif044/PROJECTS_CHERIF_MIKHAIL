`include "defines.v"
module MUX (
    input A, B, sel,
    output Y
);

    assign Y = sel ? B : A;
    
endmodule