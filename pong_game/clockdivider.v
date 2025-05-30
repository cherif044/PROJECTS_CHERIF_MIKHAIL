`timescale 1ns / 1ps
module clockdivider #(parameter n = 50000000)
(input clk, rst, output reg clk_out);
wire [31:0] count;
// Big enough to hold the maximum possible value
// Increment count
counter_x_bit #(32,n) counterMod
(.clk(clk), .reset(rst), .count(count),.en(1'b1));
// Handle the output clock
always @ (posedge clk, posedge rst) begin
if (rst) // Asynchronous Reset
clk_out <= 0;
else if (count == n-1)
clk_out <= ~ clk_out;
end
endmodule
