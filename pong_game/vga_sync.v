`timescale 1ns / 1ps

module vga_sync(
    input clk100MHz,   
    input reset,        
    output videoOn,    
    output hsync,       
    output vsync,       
    output pTick,     
    output [9:0] x,     
    output [9:0] y      
    );
    
    parameter HD = 640;             
    parameter HF = 48;              
    parameter HB = 16;             
    parameter HR = 96;             
    parameter HMAX = HD + HF + HB + HR - 1; 
    parameter VD = 480;             
    parameter VF = 10;              
    parameter VB = 33;             
    parameter VR = 2;               
    parameter VMAX = VD + VF + VB + VR - 1;   

    reg [1:0] r25MHz;
    wire w25MHz;
    
    always @(posedge clk100MHz or posedge reset)
        if (reset)
            r25MHz <= 0;
        else
            r25MHz <= r25MHz + 1;
    
    assign w25MHz = (r25MHz == 0) ? 1 : 0; // assert tick 1/4 of the time
    
    reg [9:0] hCountReg, hCountNext;
    reg [9:0] vCountReg, vCountNext;
    
    reg vSyncReg, hSyncReg;
    wire vSyncNext, hSyncNext;
    
    // Register Control
    always @(posedge clk100MHz or posedge reset)
        if (reset) begin
            vCountReg <= 0;
            hCountReg <= 0;
            vSyncReg  <= 1'b0;
            hSyncReg  <= 1'b0;
        end
        else begin
            vCountReg <= vCountNext;
            hCountReg <= hCountNext;
            vSyncReg  <= vSyncNext;
            hSyncReg  <= hSyncNext;
        end
         
    // Logic for horizontal counter
    always @(posedge w25MHz or posedge reset)      // pixel tick
        if (reset)
            hCountNext = 0;
        else
            if (hCountReg == HMAX)                 // end of horizontal scan
                hCountNext = 0;
            else
                hCountNext = hCountReg + 1;         
  
    // Logic for vertical counter
    always @(posedge w25MHz or posedge reset)
        if (reset)
            vCountNext = 0;
        else
            if (hCountReg == HMAX)                 // end of horizontal scan
                if ((vCountReg == VMAX))           // end of vertical scan
                    vCountNext = 0;
                else
                    vCountNext = vCountReg + 1;
        
    assign hSyncNext = (hCountReg >= (HD + HB) && hCountReg <= (HD + HB + HR - 1));
    assign vSyncNext = (vCountReg >= (VD + VB) && vCountReg <= (VD + VB + VR - 1));
    assign videoOn = (hCountReg < HD) && (vCountReg < VD); // 0-639 and 0-479 
    
    assign hsync = hSyncReg;
    assign vsync = vSyncReg;
    assign x = hCountReg;
    assign y = vCountReg;
    assign pTick = w25MHz;
            
endmodule
