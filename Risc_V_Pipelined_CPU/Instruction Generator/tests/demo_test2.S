# Auto-generated RISC-V RV32I test
# Generated: 2025-11-23 20:06:19
# Seed: 0.70163681668475
# Instructions: 20

.text
.globl _start
_start:
    lh x30, 52(x2)                  # 0x03411f03
    lhu x13, 60(x30)                # 0x03cf5683
    sw x23, 184(x6)                 # 0x0b732c23
    slti x3, x3, -1                 # 0xfff1a193
    slti x3, x27, -1397             # 0xa8bda193
    lbu x15, 140(x2)                # 0x08c14783
    lw x4, 508(x15)                 # 0x1fc7a203
    lbu x28, 56(x4)                 # 0x03824e03
    lw x6, 0(x28)                   # 0x000e2303
    addi x30, x5, -2019             # 0x81d28f13
    add x30, x16, x9                # 0x00980f33
    addi x30, x3, 0                 # 0x00018f13
    sub x10, x5, x26                # 0x41a28533
    lhu x9, 164(x2)                 # 0x0a415483
    or x9, x30, x17                 # 0x011f64b3
    blt x9, x0, L16                 # 0x0004c263
L16:
    sb x4, 40(x2)                   # 0x02410423
    blt x2, x4, L18                 # 0x00414263
L18:
    sw x19, 0(x2)                   # 0x01312023
    auipc x1, 0x10                  # 0x00010097

# End of test
