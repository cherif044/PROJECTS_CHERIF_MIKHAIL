`include "defines.v"

module branch_control (
    input Branch,
    input [1:0] inst3_2,
    input [2:0] function3,
    input zero_flag, carry_flag, overflow_flag, sign_flag,
    output reg [1:0] branch_sel
);

    always@(*)begin
        if(Branch == 1'b1)begin
            if(inst3_2 == 2'b11)begin
                branch_sel = 2'b01;
            end
            else if(inst3_2 == 2'b01)begin
                branch_sel = 2'b11;
            end
            else begin
                case (function3)
                    3'b000: branch_sel = {1'b0, zero_flag};               // BEQ
                    3'b001: branch_sel = {1'b0, ~zero_flag};              // BNE
                    3'b100: branch_sel = {1'b0, sign_flag != overflow_flag}; // BLT
                    3'b101: branch_sel = {1'b0, (sign_flag == overflow_flag)}; // BGE
                    3'b110: branch_sel = {1'b0, ~carry_flag};            // BLTU
                    3'b111: branch_sel = {1'b0, carry_flag};             // BGEU
                    default: branch_sel = 2'b00;
                endcase
            end
        end
        else begin
            branch_sel = 2'b00;
        end
    end

endmodule