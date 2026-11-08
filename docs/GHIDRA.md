# Ghidra reverse-engineering setup

1. Use your own locally recovered **decrypted APP**, SHA-256 7a82f65d5032b8bcc96ebd165bb6724134618772b95669f5c5f5e8a21faff2d0.
2. Import as **Raw Binary**; choose ARM little-endian / Cortex-M3/Thumb (the exact architecture descriptor depends on your Ghidra version).
3. Map the binary to **0x08001000**, rather than Ghidra's default zero.
4. Check the first two words at 0x08001000 / 0x08001004: 0x20002988 and 0x08001189.
5. The reset handler's instruction address is 0x08001188; note that 0x08001189 has the Thumb state bit set.
6. Run ghidra/annotate_shfw.py as a Ghidra script to label confirmed landmarks.
7. Begin with startup/ISR vectors and STM32F103 peripheral accesses. Do not label a routine FOC/observer/Hall until the control flow and accesses support it.

An imported binary is **not** the firmware author's C source. Ghidra decompiler output is pseudocode and should be versioned as interpretation with supporting address evidence, not presented as original source.

A standalone preliminary check: python tools/inspect_app.py YOUR_LOCAL_APP.bin.
