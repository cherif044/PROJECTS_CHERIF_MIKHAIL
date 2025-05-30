# FPGA Pong Game

This project implements a classic Pong game in Verilog, designed for an FPGA using the Vivado design suite. The game is controlled and played directly on the FPGA board, utilizing its inputs (e.g., buttons or switches) and outputs (e.g., VGA display).

## Project Overview
The Pong game features two paddles and a ball, with players controlling paddle movement to hit the ball and score points. The implementation leverages FPGA hardware for real-time game logic, VGA output, and input handling.

## Files
- `BCD.v`: Handles Binary-Coded Decimal conversion for displaying scores.
- `debouncer.v`: Ensures clean input signals by debouncing FPGA button/switch inputs.
- `pixels.v`: Manages pixel-level rendering of game objects (ball, paddles).
- `topmodule.v`: Top-level module integrating all components (game logic, VGA, inputs).
- `vga_sync.v`: Generates VGA synchronization signals (HSYNC, VSYNC) for display.

## General Approach
1. **Game Logic**:
   - `topmodule.v` coordinates ball and paddle movement, collision detection, and scoring.
   - `pixels.v` renders game objects to the screen.
2. **VGA Output**:
   - `vga_sync.v` produces timing signals for a 640x480 VGA display.
   - Pixel data is synchronized with game logic for real-time visuals.
3. **Input Handling**:
   - `debouncer.v` processes FPGA inputs to avoid noise.
   - Inputs control paddle movement in `topmodule.v`.
4. **Scoring**:
   - `BCD.v` converts score values to decimal for display.

## Requirements
- **Software**: Vivado Design Suite (tested on version 2023.1 or later).
- **Hardware**: FPGA board with VGA output and input peripherals.
- **Dependencies**: None beyond Vivado and FPGA board libraries.

## Setup Instructions
1. Clone this repository.
2. Open Vivado and create a project for your FPGA board.
3. Add all `.v` files to the project.
4. Include a `constraints.xdc` file with pin assignments for your board.
5. Synthesize and implement the design.
6. Program the FPGA board.
7. Connect a VGA monitor and input devices as per the constraints.
8. Power on to play.

## Controls
- **Player 1**: Use designated buttons/switches (check `constraints.xdc`) for the left paddle.
- **Player 2**: Use designated buttons/switches for the right paddle.

## Notes
- Match the FPGA clock frequency with the code’s timing.
- Adjust `constraints.xdc` for your board’s pinout.
- Game runs at 60 FPS for smooth play.

## License
MIT License. See `LICENSE` for details.