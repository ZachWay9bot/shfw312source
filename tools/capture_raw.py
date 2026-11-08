#!/usr/bin/env python3
"""Host-only passive ESP32-C3 USB raw capture, no serial writes."""
import argparse
import hashlib
import pathlib
import sys
import time

def main():
    ap=argparse.ArgumentParser(description="Receive raw Yellowwire bytes from ESP32-C3")
    ap.add_argument("--port",default="COM3")
    ap.add_argument("--out",default="yellowwire_raw.bin")
    ap.add_argument("--baud",type=int,default=115200)
    args=ap.parse_args()
    try:
        import serial
    except ImportError:
        print("Install pyserial: py -3 -m pip install pyserial")
        return 2
    path=pathlib.Path(args.out)
    if path.exists():
        print("Refusing to overwrite:",path)
        return 2
    h=hashlib.sha256()
    n=0
    print("PASSIVE RX-ONLY:",args.port,"->",path)
    try:
        with serial.Serial(args.port,baudrate=args.baud,timeout=.2) as port, path.open("xb") as dest:
            last=time.monotonic()
            start=last
            while True:
                buf=port.read(16384)
                if buf:
                    dest.write(buf)
                    h.update(buf)
                    n+=len(buf)
                now=time.monotonic()
                if now-last>=2:
                    dest.flush()
                    print(f"{n} bytes in {now-start:.1f}s",flush=True)
                    last=now
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print("Capture failure:",exc)
        return 1
    print("Saved",n,"bytes; SHA256",h.hexdigest())
    return 0

if __name__=="__main__":
    sys.exit(main())
