`timescale 1ns / 1ps

module topmodule(
    input clk100MHz,  
    input speedup,      // 100 MHz clock from Basys 3
    input reset,            // btnR
    input up,               // btnU
    input down,             // btnD
    input up2,              // btnU2
    input down2,            // btnD2
    output hsync,           // VGA hsync signal
    output vsync,           // VGA vsync signal
    output [11:0] rgb,      // RGB output to VGA DAC
    output [6:0] seg,       // 7-segment display segments
    output [3:0] an,
    output sound         // 7-segment display anodes
);
    
    // Debounced buttons
    wire wReset, wUp, wDown, wUp2, wDown2;
    // VGA-related signals
    wire wVidOn, wPTick;
    wire [9:0] wX, wY;

    // RGB signals
    reg [11:0] rgbReg, rgbNext;
    reg still;
    // Score signals (units and tens for both players)
    wire [3:0] score1, score2, score1Ten, score2Ten;

    // FSM-related signals
    reg dInc, dClr, timerStart, dInc2;
    reg [1:0] stateReg, stateNext;
    reg [1:0] ballReg, ballNext;
    wire timerUp;

    // Graphics and text signals
    wire [3:0] textOn;
    wire [11:0] graphRgb, textRgb;

    // Clock divider for slower clock (used for score updates)
    wire clkDiv;
    wire hit1, hit2;
    // State machine states
    localparam [1:0] 
        newGame = 2'b00, 
        play    = 2'b01, 
        newBall = 2'b10, 
        over    = 2'b11;

    // Instantiate VGA sync module
    vga_sync vga(
        .clk100MHz(clk100MHz),
        .reset(wReset),
        .videoOn(wVidOn),
        .hsync(hsync),
        .vsync(vsync),
        .pTick(wPTick),
        .x(wX),
        .y(wY)
    );

    // Instantiate pixel generator (game graphics)
    pixels pg(
        .clk(clk100MHz),
        .reset(wReset),
        .up(wUp),
        .down(wDown),
        .speedup(speedup),
        .videoOn(wVidOn),
        .xCoordinate(wX),
        .yCoordinate(wY),
        .rgbColor(graphRgb),
        .up2(wUp2),
        .down2(wDown2),
        .hit1(hit1),
        .hit2(hit2),
        .screenon(screenOn),
        .still(still),
        .sound(sound)
    );

     //Score counters for player 1 and player 2
    modulus100 counter_unit(
        .clk(clk100MHz),
        .reset(wReset),
        .d_inc(dInc),
        .d_clr(dClr),
        .dig0(score1),
        .dig1(score1Ten)
    );
    modulus100 counter_unit2(
        .clk(clk100MHz),
        .reset(wReset),
        .d_inc(dInc2),
        .d_clr(dClr),
        .dig0(score2),
        .dig1(score2Ten)
    );


////////////////////////

//scorenew temp2323(clk100MHz,reset,dInc,dInc2,score1,score2);
    // Text generator for score display
    text txt(
        .clk(clk100MHz),
        .dig0(score1),
        .dig1(score1Ten),
        .dig2(score2),
        .dig3(score2Ten),
        .x(wX),
        .y(wY),
        .text_on(textOn),
        .text_rgb(textRgb)
    );

    // Clock divider for slowing down the clock
    clockdivider #(250000) clk_div(
        .clk(clk100MHz),
        .rst(wReset),
        .clk_out(clkDiv)
    );

    // 7-segment display for score output
    score scoreModule(
        .clk(clkDiv),
        .reset(wReset),
        .score1units(score1),
        .score1tens(score1Ten),
        .score2units(score2),
        .score2tens(score2Ten),
        .seg(seg),
        .an(an)
    );
 // 60 Hz tick when screen is refreshed
wire timerTick;
assign timerTick = (wX == 0) && (wY == 0);
    // Timer module for delays
    minuteur sec(
        .clk(clk100MHz),
        .reset(wReset),
        .timer_start(timerStart),
        .timer_tick(timerTick),
        .timer_up(timerUp)
    );

    // Debouncer modules for buttons
    debouncer dbR(.clk(clk100MHz), .in(reset), .out(wReset));
    debouncer dbU(.clk(clk100MHz), .in(up), .out(wUp));
    debouncer dbD(.clk(clk100MHz), .in(down), .out(wDown));
    debouncer dbU2(.clk(clk100MHz), .in(up2), .out(wUp2));
    debouncer dbD2(.clk(clk100MHz), .in(down2), .out(wDown2));

    // Assign RGB output
    assign rgb = rgbReg;

    // FSM - Sequential logic
    always @(posedge clk100MHz or posedge wReset) begin
        if (wReset) begin
            stateReg <= newGame;
            ballReg <= 2'b00;
            rgbReg <= 12'h000; // Black screen on reset
        end else begin
            stateReg <= stateNext;
            ballReg <= ballNext;
            if (wPTick)
                rgbReg <= rgbNext;
        end
    end
reg winPlayer1, winPlayer2; 
reg  win1, win2;
// FSM - Combinational logic
always @* begin
    // Default values
    still = 1'b1;
    timerStart = 1'b0;
    dInc = 1'b0;
    dInc2 = 1'b0;
    dClr = 1'b0;
    stateNext = stateReg;
    ballNext = ballReg;
    
    // Check if either score reaches 14
    if ((score1 == 4 && score1Ten == 1) || (score2 == 4 && score2Ten == 1)) begin
        // Reset game if either score is 14
        stateNext = newGame;
        dClr = 1'b1; // Clear the scores
        ballNext = 2'b00; // Reset ball
    end else begin
        case (stateReg)
            newGame: begin
                dClr = 1'b1; // Clear scores
                if (wUp || wDown || wUp2 || wDown2) begin // Start on button press
                    stateNext = play;
                    ballNext = ballReg + 1;
                end
            end

            play: begin
                still = 1'b0;
                if (hit1) begin
                    dInc = 1'b1; // Player 1 scores
                    stateNext = newBall;
                    timerStart = 1'b1;
                end else if (hit2) begin
                    dInc2 = 1'b1; // Player 2 scores
                    stateNext = newBall;
                    timerStart = 1'b1;
                end
            end

            newBall: begin
                if (timerUp)
                    stateNext = play;
            end

            over: begin
                if (timerUp)
                    stateNext = newGame;
            end
        endcase
    end
end

// RGB combinational logic for display
always @* begin
    if (~wVidOn)
        rgbNext = 12'h000; // Blank screen when video is off
    else if (textOn[3] || ((stateReg == newGame) && textOn[1]) || ((stateReg == over) && textOn[0]))
        rgbNext = textRgb; // Text colors for states
    else if (screenOn)
        rgbNext = graphRgb; // Game graphics colors
    else if (textOn[2]) begin
        if (stateReg == winPlayer1)
            rgbNext = 12'hF00; // Red color for Player 1 wins
        else if (stateReg == winPlayer2)
            rgbNext = 12'h00F; // Blue color for Player 2 wins
        else
            rgbNext = textRgb; // Additional text
    end
    else
        rgbNext = 12'h0FF; // Default aqua background
end

endmodule
