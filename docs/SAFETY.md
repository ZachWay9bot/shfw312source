# Hardware safety and non-distribution boundaries

**Read-only collection and offline inspection only.** The programs here do not send any commands to the scooter or flash the ESC.

- RDP enabled was observed after SHFW installation. Whether SHFW itself, SHU, or a prior install state set RDP is **not proven**.
- On STM32F103, transitioning out of RDP Level 1 generally triggers chip erase. DO NOT use read-unprotect, change option bytes, or mass erase merely to inspect SHFW.
- Never connect ESP32-C3 TX to the Yellowwire. Only tap with RX on a verified logic-level compatible connection and common ground; take isolation and ground differences into account.
- Do not reflash the scooter merely for another passive capture if you already have one complete and internally verified session.
- The recovered APP lacks a proven full flash map, bootloader, configuration, device-specific state and Option Bytes. It is **not flash ready**.
- A captured encrypted payload is not automatically a safe IAP file. Reflashing can fail or leave the controller unbootable.
- If the user maintains a stock backup, keep it separate and verified before any firmware changes.
- No proprietary SHFW firmware bytes, raw transfer bytes, or verbatim decompilation of third-party proprietary code are published by this repository.
