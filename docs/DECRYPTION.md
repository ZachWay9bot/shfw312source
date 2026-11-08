# Decryption and provenance

The transfer's byte distribution did not resemble unencrypted Cortex-M firmware. Applying the classic Ninebot TEA/CBC algorithm with publicly documented default key, zero IV, 32 rounds and rolling key updates every 1024 bytes yielded a plausible Cortex-M vector table and a valid internal checksum.

The decrypted data length is 46,800 bytes **including the 4-byte plaintext integrity word**. The 46,796-byte application image excludes that word.

Checks:
1. Wire payload SHA-256: afe890b6214ea74b2380e5e62bc46a168f2a23e6120e9b4ba469843f75cfbc72.
2. CBC/TEA decrypt; verify the final internal checksum equals 0x76756A9D.
3. Drop the trailing 4-byte checksum from the plaintext.
4. Encrypt with the same TEA procedure and compare all 46,800 output bytes to the original ciphertext.
5. Application SHA-256: 7a82f65d5032b8bcc96ebd165bb6724134618772b95669f5c5f5e8a21faff2d0.

Implementations: tools/ninebot_tea_verify.py. No network access, SWD access, or flashing needed.

Upstream protocol references:
- https://github.com/scooterhacking/NinebotTEA
- https://wiki.scooterhacking.org/doku.php?id=zip3

This repository does not redistribute SHFW or claim source ownership of the proprietary firmware.
