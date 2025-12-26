# RISC-V RV32I Random Test Generator

A configurable random instruction sequence generator for RISC-V RV32I base integer instruction set.

## Features

- **42 RV32I Instructions**: Complete coverage of base integer ISA
- **Configurable Weights**: Instruction mix matches typical compiled code
- **Hazard Injection**: RAW, WAW, and load-use hazards with configurable probabilities
- **Loop Support**: Forward and backward branches with depth control
- **Deterministic**: Auto-generated seeds stored in manifest for reproducibility
- **Multiple Outputs**: Assembly (.S), hex (.hex), and JSON manifest

## Files

- `test_generator.py` - Main generator script
- `rv32i_metadata.json` - Instruction encoding metadata (42 instructions)
- `config_defaults.json` - Default configuration (weights, hazard probabilities, etc.)

## Usage

### Basic Generation

Generate 100 random instructions:

```powershell
python test_generator.py
```

### Custom Length

Generate specific number of instructions:

```powershell
python test_generator.py -n 500
```

### Custom Output Prefix

Specify output file names:

```powershell
python test_generator.py -n 200 -o my_test
```

This creates:

- `my_test.S` - Assembly file
- `my_test.hex` - Hex dump (one 32-bit word per line)
- `my_test_manifest.json` - Generation metadata

## Output Format

### Assembly File (.S)

```assembly
# Auto-generated RISC-V RV32I test
# Generated: 2025-11-23 14:30:00
# Seed: 0.123456789

.text
.globl _start
_start:
    addi x5, x6, 42                  # 0x02a30293
    lw x7, 16(x2)                    # 0x01012383
L5:
    beq x7, x5, L10                  # 0x00538263
    ...
```

### Hex File (.hex)

```
02a30293
01012383
00538263
...
```

### Manifest File (.json)

```json
{
  "generator": "RV32I Random Test Generator",
  "version": "1.0",
  "timestamp": "2025-11-23 14:30:00",
  "seed": 0.123456789,
  "length": 100,
  "weights": {...},
  "backward_branches": 3
}
```

## Configuration

Edit `config_defaults.json` to customize:

### Instruction Mix (weights)

```json
"weights": {
  "alu_logic": 0.38,    // ALU and logic operations
  "load": 0.22,         // Load instructions
  "store": 0.12,        // Store instructions
  "branch": 0.16,       // Conditional branches
  "jump": 0.02,         // JAL/JALR
  "upper": 0.03,        // LUI/AUIPC
  ...
}
```

### Hazard Probabilities

```json
"hazards": {
  "raw_dependency_prob": 0.40,  // Read-after-write
  "waw_repeat_prob": 0.15,      // Write-after-write
  "load_use_prob": 0.30         // Load-use hazard
}
```

### Register Usage

- Uniform distribution x0..x31
- x2 (sp) used as base in 55% of memory operations
- x1 (ra) used as destination in 80% of JAL instructions

### Immediate Values

- Small (-1, 0, 1): 25%
- Boundary (±2047): 5%
- Medium (|v|≤32): 20%
- Random full range: 40%
- Special patterns (0xFF, 0xF0, etc.): 10%

### Branch/Jump Offsets

- Near (±8 bytes): 40%
- Mid (±64 bytes): 45%
- Far (±256 bytes): 15%
- Backward branches allowed (loops enabled)

## Instruction Coverage

### Arithmetic & Logic (19 instructions)

ADD, SUB, SLL, SLT, SLTU, XOR, SRL, SRA, OR, AND, ADDI, SLTI, SLTIU, XORI, ORI, ANDI, SLLI, SRLI, SRAI

### Memory (8 instructions)

LB, LH, LW, LBU, LHU, SB, SH, SW

### Control Flow (8 instructions)

BEQ, BNE, BLT, BGE, BLTU, BGEU, JAL, JALR

### Upper Immediate (2 instructions)

LUI, AUIPC

### System (4 instructions)

FENCE, FENCE.I, ECALL, EBREAK

### Pseudo (1)

NOP (encoded as ADDI x0, x0, 0)

## Examples

### Generate a small test

```powershell
python test_generator.py -n 50 -o small_test
```

### Generate a large stress test

```powershell
python test_generator.py -n 10000 -o stress_test
```

## Notes

- All generated tests are self-contained (no external dependencies)
- Seeds are auto-generated from time + PID (stored in manifest for replay)
- Branch targets are validated and clamped to valid ranges
- Loop depth limited to prevent excessive dynamic execution
- Hazards can be disabled by setting probabilities to 0 in config

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## License

Educational/Academic use.
