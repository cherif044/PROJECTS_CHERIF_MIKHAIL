`include "defines.v"
module CPU (
    input clk, rst
);

    wire [31:0] PC_out;
    reg [31:0] mux1;
//    assign mux1 = Branch & zero_flag ? PC_plus_imm : PC_plus4;
    register PC(
        .clk(clk),
        .rst(rst),
        .load(1'b1),
        .D(mux1),
        .Q(PC_out)
    );
    
    wire cout1;
    wire [31:0] PC_plus4;
    RCA pc_incrementer (
        .A(PC_out),
        .B(32'd4),
        .cin(1'b0),
        .Sum(PC_plus4),
        .Cout(cout1)
    );

    wire [31:0] instruction;
    InstrMem instruction_memory (
        .address(PC_out[7:2]),
        .data_out(instruction)
    );

    wire Branch, MemRead, MemtoReg, MemWrite, ALUSrc, RegWrite;
    wire [1:0] ALUOp;
    Control control_unit(
        .instruction6_2(instruction[6:2]), // instruction[6:0]?
        .Branch(Branch),
        .MemRead(MemRead),
        .MemtoReg(MemtoReg),
        .ALUOp(ALUOp),
        .MemWrite(MemWrite),
        .ALUSrc(ALUSrc),
        .RegWrite(RegWrite)
    );

    wire [31:0] read_data1, read_data2;
    reg [31:0] write_data;
    
    register_file reg_file (
        .clk(clk),
        .rst(rst),
        .readReg1(instruction[19:15]),
        .readReg2(instruction[24:20]),
        .writeReg(instruction[11:7]),
        .regWriteEnable(RegWrite),
        .readData1(read_data1),
        .readData2(read_data2),
        .writeData(write_data)
    );

    wire [31:0] immediate;
    immediate_generator imm_gen (
        .instruction(instruction),
        .opcode(instruction[6:0]),
        .immediate(immediate)
    );


    
//    wire [31:0] ALU_input1;
//    assign ALU_input1 = ALUSrc ? immediate : read_data2;

    wire [31:0] ALU_input2;
    assign ALU_input2 = ALUSrc ? immediate : read_data2;

    wire [3:0] ALU_select;
    ALU_control alu_control_unit (
        .ALUOp(ALUOp),
        .function3(instruction[14:12]),
        .opcode(instruction[5] & instruction[30]),
        .ALU_select(ALU_select)
    );

    wire [31:0] ALU_result;
    wire zero_flag, carry_flag, overflow_flag, sign_flag;

    ALU alu(
        .A(read_data1),
        .B(ALU_input2),
        .ALU_select(ALU_select),
        .zero_flag(zero_flag),
        .carry_flag(carry_flag),
        .overflow_flag(overflow_flag),
        .sign_flag(sign_flag),
        .out(ALU_result)
    );


//`define IR_funct3 14:12

wire [1:0] branchSel;

branch_control branch_cntrl(
    .Branch(Branch),
    .inst3_2(instruction[3:2]),
    .function3(instruction[14:12]),
    .zero_flag(zero_flag), .carry_flag(carry_flag), .overflow_flag(overflow_flag), .sign_flag(sign_flag),
    .branch_sel(branchSel));



/*wire is_jalr;
assign is_jalr = (instruction[6:0] == 7'b1100111);

always @(*) begin
    if (is_jalr) begin
        // only JALR case
        mux1 = {ALU_result[31:1], 1'b0}; // clear LSB
    end
    else begin
        case({instruction[3],branchSel})
            2'b01: begin //PC + imm
                mux1 = PC_plus_imm;
            end
            default: begin //PC + 4
                mux1 = PC_plus4;
            end
        endcase
    end
end*/

//    // TO FIX: no B-type instructions handling
//    always @(*) begin
//        case({instruction[3],branchSel})
////            2'b01: begin //PC + imm // jal (needs to check)
////                mux1 = PC_plus_imm;
////            end
////            2'b10: begin //JALR //first bit should be 0 (jalr opcode)
////                mux1 = ALU_result;    // jalr needs correction,potential solution commented above
////            end

//            2'b11: begin //PC + imm // jal (needs to check)
//                mux1 = PC_plus_imm;
//            end
//            2'b01: begin //JALR //first bit should be 0 (jalr opcode)
//                mux1 = ALU_result;    // jalr needs correction,potential solution commented above
//            end

//            default: begin //PC + 4
//                mux1 = PC_plus4;
//            end
//        endcase
//    end

    //Fixed branch selection
    always @(*) begin
        case(branchSel)
            2'b00: mux1 = PC_plus4;
            2'b01: mux1 = PC_plus_imm;
            2'b11: mux1 = ALU_result;
        endcase
    end


    wire [31:0] PC_plus_imm;
    wire cout2;
    RCA pc_adder (
        .A(PC_out),
        .B(immediate),
        .cin(1'b0),
        .Sum(PC_plus_imm),
        .Cout(cout2)
    );

    wire [31:0] read_data_memory;
    DataMem data_memory(
        .clk(clk),
        .MemRead(MemRead),
        .MemWrite(MemWrite),
        .function3(instruction[14:12]),
        .addr(ALU_result[7:2]), // ALU_result?
        .data_in(read_data2),
        .data_out(read_data_memory)
    );

    wire [31:0] RB_mux;
    assign RB_mux = MemtoReg ? read_data_memory : ALU_result;

    always @(*) begin
        if(instruction[2])begin
            case(instruction[6:5])
                2'b00: begin //auipc
                    write_data = PC_plus_imm;
                end
                2'b01: begin //lui
                    write_data = immediate;
                end
                2'b11: begin //jalr & jal
                    write_data = PC_plus4;
                end
                default: begin
                    write_data = RB_mux;
                end
            endcase
        end
        else begin
            write_data = RB_mux;
        end
    end

endmodule