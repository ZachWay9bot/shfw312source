#!/usr/bin/env python3
"""Offline Ninebot 5A A5 parser and conservative classical ESC IAP extractor.
Does not transmit any scooter commands, and does not alter the raw input.
"""
import argparse
from collections import Counter
import csv
import hashlib
from pathlib import Path
import sys

def parse_frames(raw):
    i=0
    frames=[]
    crc_fail=other=incomplete=0
    while i+9<=len(raw):
        j=raw.find(b"\x5a\xa5",i)
        if j<0:
            other+=len(raw)-i
            i=len(raw)
            break
        other+=j-i
        if j+9>len(raw):
            incomplete+=1
            break
        size=raw[j+2]+9
        if j+size>len(raw):
            incomplete+=1
            i=j+1
            continue
        f=raw[j:j+size]
        expected=0xFFFF ^ (sum(f[2:-2]) & 0xFFFF)
        received=int.from_bytes(f[-2:],"little")
        if expected!=received:
            crc_fail+=1
            i=j+1
            continue
        frames.append(dict(offset=j,src=f[3],dst=f[4],cmd=f[5],arg=f[6],data=f[7:-2],size=size))
        i=j+size
    other+=len(raw)-i
    return frames,crc_fail,other,incomplete

class Session:
    def __init__(self,number,start):
        self.number=number
        self.start=start
        self.expected=None
        self.frames=[]
        self.data=bytearray()
        self.prev_idx=None
        self.prev_payload=None
        self.missing=self.conflicts=self.duplicates=0
        self.verify=None
        self.acks=[]
    def transfer(self,f):
        idx=f["arg"]
        payload=f["data"]
        if idx==self.prev_idx and payload==self.prev_payload:
            self.duplicates+=1
            return
        if idx==self.prev_idx and payload!=self.prev_payload:
            self.conflicts+=1
        elif self.prev_idx is not None and idx!=((self.prev_idx+1)%256):
            self.missing+=(idx-self.prev_idx-1)%256 or 256
        self.data.extend(payload)
        self.prev_idx=idx
        self.prev_payload=payload
        self.frames.append(f)

def extract(frames):
    sessions=[]
    active=None
    for f in frames:
        if f["src"]==0x20 and f["cmd"]==0x0B:
            if active:
                active.acks.append(f)
            continue
        if f["dst"]!=0x20:
            continue
        if f["cmd"]==0x07 and len(f["data"])>=4:
            active=Session(len(sessions)+1,f["offset"])
            active.expected=int.from_bytes(f["data"][:4],"little")
            sessions.append(active)
        elif f["cmd"]==0x08:
            if active is None:
                active=Session(len(sessions)+1,f["offset"])
                sessions.append(active)
            active.transfer(f)
        elif f["cmd"]==0x09 and active is not None:
            active.verify=int.from_bytes(f["data"][:4],"little") if len(f["data"])>=4 else None
        elif f["cmd"]==0x0A:
            active=None
    return sessions

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--raw",default="yellowwire_raw.bin")
    ap.add_argument("--outdir",default="extracted")
    args=ap.parse_args()
    p=Path(args.raw)
    if not p.is_file():
        print("Missing raw:",p)
        return 2
    raw=p.read_bytes()
    out=Path(args.outdir)
    out.mkdir(parents=True,exist_ok=True)
    frames,bad,other,partial=parse_frames(raw)
    counts=Counter(f["cmd"] for f in frames)
    dirs=Counter((f["src"],f["dst"],f["cmd"]) for f in frames)
    sessions=extract(frames)
    with (out/"frames.csv").open("w",newline="",encoding="utf-8") as fo:
        w=csv.writer(fo)
        w.writerow(["offset","src","dst","cmd","arg","payload_bytes","wire_bytes"])
        for f in frames:
            w.writerow([f["offset"],f"0x{f['src']:02X}",f"0x{f['dst']:02X}",f"0x{f['cmd']:02X}",f["arg"],len(f["data"]),f["size"]])
    lines=[
        f"RAW: {p}, {len(raw)} bytes SHA256={hashlib.sha256(raw).hexdigest()}",
        f"Valid frames: {len(frames)}; CRC/header errors: {bad}; outside bytes: {other}; incomplete: {partial}",
        f"CMD frequency: {dict(sorted(counts.items()))}",
        "Caution: pure byte-stream capture cannot rule out UART overruns.",
        "Protocol: 5A A5, checksum ~SUM16; CMD07 begin, 08 transfer, 09 verify, 0B ack.",""
    ]
    for s in sessions:
        content=bytes(s.data)
        full=len(content)
        length_ok=s.expected is not None and full>=s.expected
        if length_ok:
            content=content[:s.expected]
        calculated=0xFFFFFFFF ^ (sum(content) & 0xFFFFFFFF)
        checksum_ok=s.verify is not None and calculated==s.verify
        consistent=length_ok and s.missing==0 and s.conflicts==0 and checksum_ok
        name=f"session_{s.number:02d}_wire_candidate.bin"
        (out/name).write_bytes(content)
        lines+= [
            f"Session {s.number}, initial raw offset {s.start}",
            f"  Begin length: {s.expected}",
            f"  CMD08 frames: {len(s.frames)}, payload bytes {full}, saved {len(content)}",
            f"  Missing: {s.missing}, conflicting: {s.conflicts}, retransmits: {s.duplicates}",
            f"  Verify: {s.verify:#010x}" if s.verify is not None else "  Verify: ABSENT",
            f"  calculated checksum: {calculated:#010x}, matches: {checksum_ok}",
            f"  ACKs: {len(s.acks)}; transfer consistent: {consistent}; global CRC errors: {bad}",
            f"  Output: {name}, SHA256={hashlib.sha256(content).hexdigest()}",""
        ]
    if not sessions:
        lines.append("No classical CMD08 transfer detected.")
    lines.append("Top directions/commands:")
    for (src,dst,cmd),n in dirs.most_common(25):
        lines.append(f"  {src:02X}->{dst:02X} CMD{cmd:02X}: {n}")
    (out/"REPORT.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("\n".join(lines))
    return 0

if __name__=="__main__":
    sys.exit(main())
