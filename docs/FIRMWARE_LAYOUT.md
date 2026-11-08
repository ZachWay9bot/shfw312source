# Decoded SHFW application: proven layout facts

All observations below are byte-level observations from the validated decrypted application, **not symbolized C source**. The analysis applies to this particular user capture only, with SHA-256 `7a82f65d5032b8bcc96ebd165bb6724134618772b95669f5c5f5e8a21faff2d0`.

| Field | Value |
|---|---|
| Decrypted application length | 46,796 bytes |
| Candidate base address | 0x08001000 |
| Last image byte (if at base) | 0x0800C6CB |
| First word, initial stack pointer | 0x20002988 |
| Second word, reset vector | 0x08001189 (Thumb entry) |
| Function code address of reset vector | 0x08001188 |
| Internal plaintext checksum | 0x76756A9D, verified |
| Encrypt-roundtrip vs captured wire | byte-exact |

## Literal string locations

- 0x08001400: Scooter_G30_SAT
- 0x0800979C: FLASH_NAME
- 0x08009AA4: SHFWVER
- 0x08009AB5: DRV (literal occurrence)
- 0x0800C6BC: ScooterHacking

Literal strings alone **do not prove their semantic interpretation**; in particular, the repository name SHFW312 does not prove the captured version number.

## Gaps and open analysis

- No annotated original function names, original C source, or symbol table
- No proven FOC PI gains, PWM/deadtime, Hall sector logic, phase current sampling, watchdog logic or sensorless observer constants
- No validated exact app/bootloader boundary beyond the tentative 0x08001000 app load address
- No verified 128-KiB stock/SHFW physical flash diff, because SWD RDP was active
- No verified flash-ready package or live reflashing test performed from the recovered file

## Next reverse-engineering targets

1. Ghidra import / align vectors and startup code; identify interrupt handlers.
2. Build STM32F103 peripheral cross-references (TIM1 PWM, ADC1/2, DMA, USARTs).
3. Resolve motor control call graph, phase-current regulation and Hall reads.
4. Validate inferred subsystem behaviors using **read-only** telemetry before changing hardware.
5. Record evidence and counterexamples for each function hypothesis.

Use tools/inspect_app.py before running Ghidra.
