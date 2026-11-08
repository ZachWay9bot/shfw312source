#!/usr/bin/env python3
"""Read-only classic Ninebot TEA CBC verifier.
Reference: https://github.com/scooterhacking/NinebotTEA (MIT).
No flashing functions. Python standard library only.
"""
import argparse
import hashlib
import struct
from pathlib import Path
MASK=0xffffffff
DELTA=0x9e3779b9
KEY=bytes.fromhex("FE801CB2D1EF41A6A41731F5A06824F0")

def checksum(data):
    if len(data)%4:
        raise ValueError("Checksum requires length multiple of four")
    total=sum(struct.unpack_from("<I",data,i)[0] for i in range(0,len(data),4))
    swapped=((total>>16)&0xffff)|((total&0xffff)<<16)
    return swapped ^ MASK

def round_key(k):
    blob=b"".join(w.to_bytes(4,"little") for w in k)
    updated=bytes((v+i)&0xff for i,v in enumerate(blob))
    return list(struct.unpack("<4I",updated))

def tea_encrypt(y,z,k):
    s=0
    for _ in range(32):
        s=(s+DELTA)&MASK
        y=(y+(((z<<4)+k[0])^(z+s)^((z>>5)+k[1])))&MASK
        z=(z+(((y<<4)+k[2])^(y+s)^((y>>5)+k[3])))&MASK
    return y,z

def tea_decrypt(y,z,k):
    s=(DELTA*32)&MASK
    for _ in range(32):
        z=(z-(((y<<4)+k[2])^(y+s)^((y>>5)+k[3])))&MASK
        y=(y-(((z<<4)+k[0])^(z+s)^((z>>5)+k[1])))&MASK
        s=(s-DELTA)&MASK
    return y,z

def cipher(data,encode=False):
    if len(data)%8:
        raise ValueError("Ciphertext length must be divisible by eight")
    k=list(struct.unpack("<4I",KEY))
    iv=0
    result=bytearray()
    for i in range(0,len(data),8):
        if i and i%1024==0:
            k=round_key(k)
        left,right=struct.unpack_from("<2I",data,i)
        if encode:
            v=((right<<32)|left)^iv
            y,z=tea_encrypt(v&MASK,v>>32,k)
            cur=(z<<32)|y
            result+=cur.to_bytes(8,"little")
            iv=cur
        else:
            cur=(right<<32)|left
            y,z=tea_decrypt(left,right,k)
            value=((z<<32)|y)^iv
            result+=value.to_bytes(8,"little")
            iv=cur
    return bytes(result)

def decrypt_verified(wire):
    plain=cipher(wire,False)
    found=struct.unpack_from("<I",plain,len(plain)-4)[0]
    expected=checksum(plain[:-4])
    if found!=expected:
        raise ValueError(f"Internal checksum invalid: {found:08X} != {expected:08X}")
    return plain[:-4],found

def encrypt_verified(plain):
    padded=plain+bytes((-len(plain))%4)
    if len(padded)%8==0:
        padded+=bytes(4)
    return cipher(padded+struct.pack("<I",checksum(padded)),True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("encrypted",type=Path)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    wire=args.encrypted.read_bytes()
    plain,internal=decrypt_verified(wire)
    roundtrip=encrypt_verified(plain)==wire
    print("Wire bytes:",len(wire),"SHA256",hashlib.sha256(wire).hexdigest())
    print("Plain bytes:",len(plain),"SHA256",hashlib.sha256(plain).hexdigest())
    print(f"Internal checksum 0x{internal:08X}: VALID")
    print("Byte-perfect re-encryption:",roundtrip)
    sp,reset=struct.unpack_from("<II",plain,0)
    print(f"Vector SP=0x{sp:08X}; reset=0x{reset:08X}")
    if not roundtrip:
        raise SystemExit("Roundtrip failed")
    if args.out:
        args.out.write_bytes(plain)
        print("Saved:",args.out)

if __name__=="__main__":
    main()
