# Auto-generated RISC-V RV32I test
# Generated: 2025-11-23 20:20:30
# Seed: 0.3137258208175068
# Instructions: 20

.text
.globl _start
_start:
L0:
    blt x23, x12, L1                # 0x00cbc263
L1:
    bne x21, x17, L0                # 0xff1a9ee3
    sh x8, 60(x22)                  # 0x028b1e23
    slti x5, x3, 12                 # 0x00c1a293
    bgeu x4, x8, L1                 # 0xfe827ae3
    bltu x2, x3, L10                # 0x00316a63
    sw x2, 160(x2)                  # 0x0a212023
    bne x15, x20, L9                # 0x01479463
    lw x2, 24(x2)                   # 0x01812103
L9:
    blt x2, x20, L18                # 0x03414263
L10:
    slti x5, x9, -1001              # 0xc174a293
    addi x25, x18, 1150             # 0x47e90c93
    andi x1, x5, -32                # 0xfe02f093
    bltu x18, x14, L19              # 0x00e96c63
    sh x13, 112(x2)                 # 0x06d11823
    bne x28, x3, L17                # 0x003e1463
    sltiu x19, x5, -98              # 0xf9e2b993
L17:
    add x16, x4, x19                # 0x01320833
L18:
    lhu x12, 252(x19)               # 0x0fc9d603
L19:
    slt x12, x12, x29               # 0x01d62633

# End of test
