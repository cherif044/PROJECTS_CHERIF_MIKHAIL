`timescale 1ns / 1ps



module debouncer(input clk,in, output out);
reg q1,q2,q3;
always@(posedge clk) begin


 q1 <= in;
 q2 <= q1;
 q3 <= q2;
 
end
assign out = q1&q2&q3;
endmodule