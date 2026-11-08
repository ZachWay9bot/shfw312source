#!/usr/bin/env python3
"""Offline test with synthetic data, no scooter connected."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from extract_iap import parse_frames,extract
from ninebot_tea_verify import cipher,checksum,decrypt_verified,encrypt_verified

def f(src,dst,cmd,arg,data):
    head=bytes([0x5a,0xa5,len(data),src,dst,cmd,arg])+data
    return head+(0xffff ^ (sum(head[2:])&0xffff)).to_bytes(2,"little")
plain=bytes(range(256))*2
stream=f(0x3e,0x20,7,0,len(plain).to_bytes(4,"little"))
for i in range(4):
    payload=plain[i*128:(i+1)*128]
    stream+=f(0x3e,0x20,8,i,payload)
    if i==1: stream+=f(0x3e,0x20,8,i,payload)
    stream+=f(0x20,0x3e,11,0,b"\0")
stream+=f(0x3e,0x20,9,0,(0xffffffff ^ sum(plain)).to_bytes(4,"little"))
frames,bad,other,incomplete=parse_frames(stream)
sessions=extract(frames)
assert len(sessions)==1 and not bad and not other and not incomplete
s=sessions[0]
assert s.expected==len(plain) and bytes(s.data)==plain and s.duplicates==1
assert len(s.acks)==4 and s.missing==0 and s.conflicts==0
assert s.verify==(0xffffffff ^ sum(plain))
wire=encrypt_verified(plain)
restored,check=decrypt_verified(wire)
assert restored==plain and check==checksum(plain)
assert wire==encrypt_verified(restored)
print("PASS: synthetic IAP framing, duplicate handling, checksum, TEA roundtrip")
