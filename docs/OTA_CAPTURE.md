# OTA acquisition and integrity trail

The target was a Ninebot G30D Gen1 3-Cap controller with STM32F103 (128 KiB as reported by STM32CubeProgrammer). The controller was accessible via ST-Link, but its option bytes reported RDP ENABLED after installing SHFW. No option bytes were changed in the experiment.

## Passive setup

ESP32-C3, GPIO20 as receive only, common ground, verified 3.3-V compatible signal level. The C3 forwarded raw 115200 8N1 bytes over USB. TX was **not** connected to the scooter. Windows capture process persisted unfiltered bytes. The C3 USB COM port is distinct from the ESC IoT/COM9 port; do not confuse them.

## Original capture, 2026-11-07

- Raw byte count: **89314**
- Raw SHA-256: **e78f4f66692178b8cb4d086138b0106884fe0a729c3a15dda114a4909ebd49a3**
- Valid Ninebot frames: **3196**
- CRC errors / false headers: **2**
- Other bytes not parsed: **66**
- Unfinished candidates: **0**
- IAP BEGIN first raw offset: **17045**
- IAP BEGIN declared length: **46800**
- CMD08 transfer frames: **366**
- Wire payload total before declared-length trimming: **46848**
- Stored bytes after length trim: **46800**
- Counter gaps: **0**
- Conflicting frames: **0**
- Retransmits: **0**
- CMD09 reported checksum: **0xFFA4D460**
- Byte-sum complement check: **0xFFA4D460**, match
- CMD0B acknowledgments: **368**
- Wire SHA-256: **afe890b6214ea74b2380e5e62bc46a168f2a23e6120e9b4ba469843f75cfbc72**

The errors/unparsed bytes elsewhere in the raw stream cannot simply be labeled harmless; they do not appear to defeat the reconstructed IAP data checks, but the capture tool itself cannot prove that an overrun never occurred.

## Wire format and observed commands

Frame header: 5A A5; payload size byte; source; destination; command; argument; payload; 16-bit little-endian complement-of-byte-sum checksum.

Observed transfer path: source 0x3E to destination 0x20 (ESC).

| Command | Interpreted purpose | Observed count for transfer direction |
|---|---|---|
| 0x07 | IAP BEGIN | 1 |
| 0x08 | IAP TRANSFER | 366 |
| 0x09 | IAP VERIFY | 1 |
| 0x0B | IAP ACK, reverse path | 368 |
| 0x0A | reset/control | 4 (full raw stream) |

The total frame counts and direction totals are separately in reports/REPORT_ORIGINAL.txt. Both normal dashboard frames and BLE/ESC messages were present during capture.

## Limits

This establishes the completeness of the captured **transferred payload under the checksum**. It does not establish that the decrypted app is byte-for-byte identical to all bytes actually programmed into MCU flash, nor does it recover the bootloader, options, runtime configuration, or RAM state.

See docs/SAFETY.md before attempting any hardware experiments.
