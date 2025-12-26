# Auto-generated RISC-V RV32I test
# Generated: 2025-11-24 21:30:46
# Seed: 0.5643982401955745
# Instructions: 42

.text
.globl _start
_start:
    jal x1, L2                      # 0x008000ef
    and x1, x1, x3                  # 0x0030f0b3
L2:
    jalr x17, x30, 421              # 0x1a5f08e7
    slti x13, x17, 1423             # 0x58f8a693
    bne x24, x10, L19               # 0x02ac1e63
    slt x8, x26, x10                # 0x00ad2433
    sb x12, 36(x2)                  # 0x02c10223
    sltu x24, x5, x0                # 0x0002bc33
    lb x16, 0(x26)                  # 0x000d0803
    auipc x8, 0x1                   # 0x00001417
    sltu x8, x8, x7                 # 0x00743433
    slti x7, x8, 1886               # 0x75e42393
    bltu x12, x0, L19               # 0x00066e63
    sh x13, 100(x2)                 # 0x06d11223
    slt x0, x27, x11                # 0x00bda033
    sltu x31, x22, x22              # 0x016b3fb3
    xor x31, x30, x6                # 0x006f4fb3
    bltu x5, x5, L31                # 0x0252ec63
    and x11, x3, x9                 # 0x0091f5b3
L19:
    lb x29, 820(x31)                # 0x334f8e83
    lui x25, 0x1                    # 0x00001cb7
    slti x24, x25, 1                # 0x001cac13
    xori x6, x24, -1                # 0xfffc4313
L23:
    sb x14, 24(x6)                  # 0x00e30c23
    lbu x7, 24(x2)                  # 0x01814383
    bltu x7, x23, L23               # 0xff73ece3
L26:
    andi x13, x9, 1008              # 0x3f04f693
    sb x14, 20(x5)                  # 0x00e28a23
    lb x18, 44(x2)                  # 0x02c10903
    bltu x18, x19, L36              # 0x01396e63
    sltiu x25, x3, 11               # 0x00b1bc93
L31:
    or x31, x16, x30                # 0x01e86fb3
    nop x20, x31, -1462             # 0xa4af8a13
    lbu x1, 0(x20)                  # 0x000a4083
    sh x20, 152(x1)                 # 0x09409c23
    bne x29, x1, L36                # 0x001e9263
L36:
    slt x31, x10, x12               # 0x00c52fb3
    or x1, x31, x30                 # 0x01efe0b3
    addi x1, x1, -1                 # 0xfff08093
    bne x1, x6, L26                 # 0xfc6096e3
    lbu x31, 16(x11)                # 0x0105cf83
L41:
    bge x31, x9, L41                # 0x009fd063

# End of test
