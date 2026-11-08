#!/usr/bin/env python3
"""Read-only STM32 Cortex-M3 raw application inspector. No disassembler needed."""
import argparse
from collections import Counter
import hashlib
import math
from pathlib import Path
import struct

KNOWN=(b"Scooter_G30_SAT",b"FLASH_NAME",b"SHFWVER",b"ScooterHacking",b"DRV")

def entropy(data):
    if not data: return 0
    n=len(data)
    return -sum((v/n)*math.log2(v/n) for v in Counter(data).values())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("image",type=Path)
    p.add_argument("--base",type=lambda s:int(s,0),default=0x08001000)
    args=p.parse_args()
    data=args.image.read_bytes()
    print("Size:",len(data),"SHA-256:",hashlib.sha256(data).hexdigest())
    print("Entropy:",round(entropy(data),4),"bits/byte")
    if len(data)<8: raise SystemExit("Image too short for vectors")
    sp,reset=struct.unpack_from("<II",data,0)
    print(f"Initial SP: 0x{sp:08X}  (plausible STM32 SRAM: {0x20000000 <= sp <= 0x20010000})")
    print(f"Reset vector: 0x{reset:08X}; Thumb bit: {reset&1}")
    limit=args.base+len(data)
    print(f"Image range: 0x{args.base:08X}..0x{limit-1:08X}")
    print("Reset within image:",args.base<=(reset&~1)<limit)
    print("First 16 vector table entries:")
    for i in range(0,min(64,len(data)-3),4):
        value=struct.unpack_from("<I",data,i)[0]
        print(f"  0x{args.base+i:08X}: 0x{value:08X}")
    for token in KNOWN:
        hits=[]
        start=0
        while True:
            at=data.find(token,start)
            if at<0: break
            hits.append(args.base+at)
            start=at+1
        print(token.decode(),":",", ".join(f"0x{a:08X}" for a in hits) if hits else "not found")
    if not (0x20000000 <= sp <= 0x20010000 and reset&1 and args.base<=(reset&~1)<limit):
        print("WARNING: vectors do not match expected STM32F103 app layout.")
if __name__=="__main__":
    main()
