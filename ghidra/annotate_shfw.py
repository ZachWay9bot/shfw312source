# Ghidra Jython script: label documented recovery landmarks.
# @category SHFW
# Run AFTER importing as ARM little-endian raw binary at 0x08001000.
# These names are investigative labels, not proven original C symbols.
from ghidra.program.model.symbol import SourceType

base = 0x08001000
symbols = [
    (0x08001000, "VECTOR_TABLE"),
    (0x08001188, "RESET_HANDLER_THUMB"),
    (0x08001400, "STR_SCOOTER_G30_SAT"),
    (0x0800979C, "STR_FLASH_NAME"),
    (0x08009AA4, "STR_SHFWVER"),
    (0x0800C6BC, "STR_SCOOTERHACKING"),
]
for addr, name in symbols:
    address = toAddr(addr)
    if currentProgram.getMemory().contains(address):
        try:
            createLabel(address, name, True)
            print("Label:", name, "at", address)
        except Exception as e:
            print("Skipped", name, str(e))
    else:
        print("Not mapped:", name, address)
print("Only known byte-level landmarks have been labeled. FOC/Hall functions remain unidentified.")
