# Auto-generated RISC-V RV32I test
# Generated: 2025-11-23 19:53:48
# Seed: 0.08329358696496147
# Instructions: 20

.text
.globl _start
_start:
    lh x25, 200(x3)                 # 0x0c819c83
    lw x25, 156(x22)                # 0x09cb2c83
    and x31, x25, x6                # 0x006cffb3
    ori x21, x31, 734               # 0x2defea93
    lb x21, 168(x21)                # 0x0a8a8a83
    sh x11, 40(x21)                 # 0x02ba9423
    and x8, x20, x16                # 0x010a7433
    slt x13, x8, x5                 # 0x005426b3
    addi x17, x13, -777             # 0xcf768893
    addi x30, x25, -1               # 0xfffc8f13
    bne x30, x27, L19               # 0x03bf1263
    bgeu x5, x23, L12               # 0x0172f263
L12:
    lui x25, 0x26cc                 # 0x026cccb7
    lbu x31, 44(x2)                 # 0x02c14f83
    lw x6, 36(x31)                  # 0x024fa303
L15:
    bgeu x6, x25, L18               # 0x01937663
    bne x5, x17, L15                # 0xff129ee3
    lw x27, 80(x2)                  # 0x05012d83
L18:
    sw x30, 156(x27)                # 0x09edae23
L19:
    bne x5, x5, L19                 # 0x00529063

# End of test
