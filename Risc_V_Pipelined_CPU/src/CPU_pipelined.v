`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/16/2025 07:06:30 PM
// Design Name: 
// Module Name: CPU_pipelined
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


module CPU_pipelined(
    input clk, rst
);

    wire [31:0] PC_out;
    reg [31:0] mux1;  
  
  //FORWARD
  reg stall;
  
  always @(*) begin
      if((instruction[6:0] == 7'b0001111 || instruction[6:0] == 7'b1110011))begin
        stall = 1;
      end
      else if ((ID_EX_Ctrl[2] || ID_EX_Ctrl[6])) begin
        stall = 1;
      end
      else begin
        stall = 0;
      end
  end

  wire PCSrc;
  assign PCSrc = (EX_MEM_Ctrl[4] && branchSel) ? 1'b1 : 1'b0;
  
    register #(32) PC(
        .clk(clk),
        .rst(rst),
        .load(~stall), // edited: forward
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

    
    // always @(*) begin
    //     if (stop == 1) begin
    //         stop = 1'b1;
    //     end
    //     else if  begin
    //         stop = 1'b1;
    //     end else begin
    //         stop = 1'b0;
    //     end
    // end

  
  ///added
  // IF/ID
  wire [31:0] IF_ID_PC, IF_ID_Inst, IF_ID_PC_Plus4;
    register #(96) IF_ID_reg (
        .clk(clk),
        .rst(rst),
        .load(1'b1), // ~stall
        .D({PC_out, 
            (PCSrc || stall) ? 32'h00000033 : instruction,  // (PCSrc)
            PC_plus4}),
        .Q({IF_ID_PC, 
            IF_ID_Inst, 
            IF_ID_PC_Plus4})
    );
  //added
  
  
  
  
    wire Branch, MemRead, MemtoReg, MemWrite, ALUSrc, RegWrite;
    wire [1:0] ALUOp;
    Control control_unit(
        .instruction6_2(IF_ID_Inst[6:2]), // instruction[6:0]?
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
        .readReg1(IF_ID_Inst[19:15]),
        .readReg2(IF_ID_Inst[24:20]),
        .writeReg(MEM_WB_Rd),
        .regWriteEnable(MEM_WB_Ctrl[0]),
        .readData1(read_data1),
        .readData2(read_data2),
        .writeData(RB_mux)
    );

    wire [31:0] immediate;
    immediate_generator imm_gen (
        .instruction(IF_ID_Inst),
        .opcode(IF_ID_Inst[6:0]),
        .immediate(immediate)
    );
  
  
   //ID/EX
    wire [31:0] ID_EX_PC, ID_EX_RegR1, ID_EX_RegR2, ID_EX_Imm, ID_EX_PC_Plus4;
    wire [7:0] ID_EX_Ctrl;
    wire [3:0] ID_EX_Func;  // func3 should continue alone to EX/MEM then branch ctrl
    wire [4:0] ID_EX_Rs1, ID_EX_Rs2, ID_EX_Rd;
  	wire ID_EX_Inst5, ID_EX_Inst2;
  	wire ID_EX_Inst3;
  	wire ID_EX_Inst6;
  	
    register #(191) ID_EX_reg (
        .clk(~clk),
        .rst(rst),
        .load(1'b1),
        
        .D({IF_ID_PC, 
            read_data1, 
            read_data2, 
            immediate,
            IF_ID_PC_Plus4,
            (stall || PCSrc) ? 8'd0 : {Branch, MemRead, MemtoReg, ALUOp, MemWrite, ALUSrc, RegWrite}, //!!!!!!!!!!!!!!!!!  FORWARD
            {IF_ID_Inst[30], IF_ID_Inst[14:12]},
            IF_ID_Inst[19:15], 
            IF_ID_Inst[24:20], 
            IF_ID_Inst[11:7],
            IF_ID_Inst[5], 
            IF_ID_Inst[2],
            IF_ID_Inst[3],
            IF_ID_Inst[6]}),
            
        .Q({ID_EX_PC, 
            ID_EX_RegR1, 
            ID_EX_RegR2, 
            ID_EX_Imm, 
            ID_EX_PC_Plus4,
            ID_EX_Ctrl,
            ID_EX_Func,
            ID_EX_Rs1, 
            ID_EX_Rs2, 
            ID_EX_Rd,
            ID_EX_Inst5,
            ID_EX_Inst2,
            ID_EX_Inst3,
            ID_EX_Inst6})
    );
        ////FORWARD

    wire [1:0] forwardA, forwardB;
    forwarding_unit fw_unit (
        .EX_MEM_RegWrite(EX_MEM_Ctrl[0]),
        .MEM_WB_RegWrite(MEM_WB_Ctrl[0]),
        .EX_MEM_RegisterRd(EX_MEM_Rd),
        .ID_EX_RegisterRs1(ID_EX_Rs1),
        .ID_EX_RegisterRs2(ID_EX_Rs2),
        .MEM_WB_RegisterRd(MEM_WB_Rd),
        .forwardA(forwardA),
        .forwardB(forwardB)
    );    
        ////FORWARD

    
    reg [31:0] ALU_input1;     ////FORWARD
    reg [31:0] ALU_input2;
    wire [3:0] ALU_select;
    
    ALU_control alu_control_unit (
        .ALUOp(ID_EX_Ctrl[4:3]),
        .function3(ID_EX_Func[2:0]),
      .opcode(ID_EX_Inst5 & ID_EX_Func[3]),  
        .ALU_select(ALU_select)
    );

    wire [31:0] ALU_result;
    wire zero_flag, carry_flag, overflow_flag, sign_flag;


always @(*) begin
        case (forwardA)
            2'b00: ALU_input1 = ID_EX_RegR1;
            2'b01: ALU_input1 = RB_mux;
            2'b10: ALU_input1 = EX_MEM_ALU_out;
            default: ALU_input1 = ID_EX_RegR1;
        endcase

        case (forwardB)
            2'b00: ALU_input2 = ID_EX_RegR2;
            2'b01: ALU_input2 = RB_mux;
            2'b10: ALU_input2 = EX_MEM_ALU_out;
            default: ALU_input2 = ID_EX_RegR2;
        endcase
    end  

    wire [31:0] mux_ALU_input2_2x1;
    //reg [31:0] ALU_input2;    ////FORWARD
    assign mux_ALU_input2_2x1 = ID_EX_Ctrl[1] ? ID_EX_Imm : ALU_input2;       ////FORWARD
    
    
    
    ALU alu(
        .A(ALU_input1),
        .B(mux_ALU_input2_2x1),
        .ALU_select(ALU_select),
        .zero_flag(zero_flag),
        .carry_flag(carry_flag),
        .overflow_flag(overflow_flag),
        .sign_flag(sign_flag),
        .out(ALU_result)
    );

    // NEEDS CORRECTION
    wire [31:0] PC_plus_imm;
    wire cout2;
    RCA pc_adder (
      .A(ID_EX_PC),
        .B(ID_EX_Imm),
        .cin(1'b0),
        .Sum(PC_plus_imm),
        .Cout(cout2)
    );

    reg [31:0] EX_out;
        always @(*) begin
            if(ID_EX_Inst2)begin
                case({ID_EX_Inst6, ID_EX_Inst5})
                    2'b00: begin //auipc
                        EX_out = PC_plus_imm; //pc + imm
                    end
                    2'b01: begin //lui
                        EX_out = ID_EX_Imm;        // imm
                    end
                    2'b11: begin //jalr & jal
                        EX_out = ID_EX_PC +32'd4;    //pc+4
                    end
                    default: begin
                        EX_out = ALU_result;       //mux output
                    end
                endcase
            end
            else begin
                EX_out = ALU_result;
            end
        end

  
  // EX/MEM
    wire [31:0] EX_MEM_BranchAddOut, EX_MEM_ALU_out, EX_MEM_RegR2, EX_MEM_PC_Plus4;
    wire [4:0]EX_MEM_Ctrl;
    wire [4:0]EX_MEM_Rd;
    wire [2:0] EX_MEM_func3; //added
    wire [3:0] EX_MEM_Flags;
    wire EX_MEM_Inst2;
    wire EX_MEM_Inst3;
    wire [31:0] EX_MEM_PC;
    wire [31:0] EX_MEM_Imm;
    wire EX_MEM_Inst5,EX_MEM_Inst6;
    
    //to be continued
    register #(213) EX_MEM (
        .clk(clk), .rst(rst), .load(1'b1),
        .D({  {PCSrc ? 5'b0 : {ID_EX_Ctrl[7],ID_EX_Ctrl[6],ID_EX_Ctrl[5],ID_EX_Ctrl[2],ID_EX_Ctrl[0]} }, //ctrl
            PC_plus_imm,
            ID_EX_PC_Plus4,
            {zero_flag,carry_flag,overflow_flag,sign_flag},
            EX_out, 
            ALU_input2,
            ID_EX_Rd ,
            ID_EX_Func[2:0],
            ID_EX_Inst2,
            ID_EX_Inst3,
            ID_EX_PC,
            ID_EX_Imm,
            ID_EX_Inst5,
            ID_EX_Inst6
        }),
        .Q({EX_MEM_Ctrl, 
            EX_MEM_BranchAddOut, 
            EX_MEM_PC_Plus4,
            EX_MEM_Flags,
            EX_MEM_ALU_out, 
            EX_MEM_RegR2, 
            EX_MEM_Rd,
            EX_MEM_func3,
            EX_MEM_Inst2,
            EX_MEM_Inst3,
            EX_MEM_PC,
            EX_MEM_Imm,
            EX_MEM_Inst5,
            EX_MEM_Inst6})
    );
    

//`define IR_funct3 14:12

wire [1:0] branchSel;

branch_control branch_cntrl(
    .Branch(EX_MEM_Ctrl[4]),
    .inst3_2({EX_MEM_Inst3 ,EX_MEM_Inst2}),
    .function3(EX_MEM_func3),
    .zero_flag(EX_MEM_Flags[3]), .carry_flag(EX_MEM_Flags[2]), .overflow_flag(EX_MEM_Flags[1]), .sign_flag(EX_MEM_Flags[0]),
    .branch_sel(branchSel));


  
    wire [31:0] read_data_memory;
    wire [31:0] memory_output;
    
    memory mem(
        .clk(clk),
        .MemRead(EX_MEM_Ctrl[3]),
        .MemWrite(EX_MEM_Ctrl[1]),
        .function3(EX_MEM_func3),
        .addr(EX_MEM_Ctrl[3] || EX_MEM_Ctrl[1] ? EX_MEM_ALU_out[7:2] : PC_out[7:2]),
        .data_in(EX_MEM_RegR2),
        .data_out(memory_output)
    );
    
    // Route memory output to correct destination based on operation
    assign instruction = (EX_MEM_Ctrl[3] || EX_MEM_Ctrl[1]) ? instruction : memory_output;
    assign read_data_memory = (EX_MEM_Ctrl[3] || EX_MEM_Ctrl[1]) ? memory_output : 32'b0;



  //MEM/RB
  wire [31:0] MEM_WB_Mem_out, MEM_WB_ALU_out;
  wire  [1:0]MEM_WB_Ctrl;
  wire [4:0] MEM_WB_Rd;
  wire MEM_WB_Inst3;
  wire [1:0] MEM_WB_branchSel;
  wire [31:0] MEM_WB_BranchAddOut;
  wire [31:0] MEM_WB_PC, MEM_WB_PC_Plus4;
  wire MEM_WB_Inst2,MEM_WB_Inst5,MEM_WB_Inst6;
  wire [31:0] MEM_WB_Imm;
  
  register #(205) MEM_WB (
    .clk(~clk), .rst(rst), .load(1'b1),
    .D({{EX_MEM_Ctrl[2],EX_MEM_Ctrl[0]},
        read_data_memory, 
        EX_MEM_ALU_out,
        EX_MEM_Rd,EX_MEM_Inst3,
        branchSel,
        EX_MEM_BranchAddOut,
        EX_MEM_PC,
        EX_MEM_PC_Plus4,
        EX_MEM_Inst2,
        EX_MEM_Inst5,
        EX_MEM_Inst6,
        EX_MEM_Imm}),
    .Q({MEM_WB_Ctrl,
        MEM_WB_Mem_out, 
        MEM_WB_ALU_out,
        MEM_WB_Rd,
        MEM_WB_Inst3,
        MEM_WB_branchSel,
        MEM_WB_BranchAddOut,
        MEM_WB_PC, 
        MEM_WB_PC_Plus4,
        MEM_WB_Inst2,
        MEM_WB_Inst5,
        MEM_WB_Inst6,
        MEM_WB_Imm})
  );

    //Fixed branch selection
    always @(*) begin
        case(branchSel) //removed MEM_WB_branchSel
            2'b00: mux1 = PC_plus4; // changed 
            2'b01: mux1 = EX_MEM_BranchAddOut; //changed
            2'b11: mux1 = MEM_WB_ALU_out;
        endcase
    end  
  
  wire [31:0] RB_mux;
    assign RB_mux = MEM_WB_Ctrl[1] ? MEM_WB_Mem_out : MEM_WB_ALU_out;

    // always @(*) begin
    //     if(MEM_WB_Inst2)begin
    //         case({MEM_WB_Inst6, MEM_WB_Inst5})
    //             2'b00: begin //auipc
    //                 write_data = MEM_WB_BranchAddOut; //pc + imm
    //             end
    //             2'b01: begin //lui
    //                 write_data = MEM_WB_Imm;        // imm
    //             end
    //             2'b11: begin //jalr & jal
    //                 write_data = MEM_WB_PC +32'd4;    //pc+4
    //             end
    //             default: begin
    //                 write_data = RB_mux;       //mux output
    //             end
    //         endcase
    //     end
    //     else begin
    //         write_data = RB_mux;
    //     end
    // end
  
endmodule