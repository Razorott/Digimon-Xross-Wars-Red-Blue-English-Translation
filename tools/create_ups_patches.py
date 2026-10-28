"""Create and verify standard UPS patches for the non-wireless release builds."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path


def put_varint(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value == 0:
            out.append(byte | 0x80)
            return bytes(out)
        out.append(byte)
        value -= 1


def get_varint(data: bytes, offset: int) -> tuple[int, int]:
    value = shift = 0
    while True:
        byte = data[offset]
        offset += 1
        value += (byte & 0x7F) << shift
        if byte & 0x80:
            return value, offset
        shift += 7
        value += 1 << shift


def make_patch(source: bytes, target: bytes) -> bytes:
    patch = bytearray(b"UPS1")
    patch += put_varint(len(source))
    patch += put_varint(len(target))
    cursor = last_offset = 0
    shared = min(len(source), len(target))
    while cursor < shared:
        while cursor < shared and source[cursor] == target[cursor]:
            cursor += 1
        if cursor == shared:
            break
        patch += put_varint(cursor - last_offset)
        last_offset = cursor
        while cursor < shared and source[cursor] != target[cursor]:
            patch.append(source[cursor] ^ target[cursor])
            cursor += 1
        # The zero terminator consumes one unchanged byte in the UPS stream.
        patch.append(0)
        if cursor < shared:
            cursor += 1
        last_offset = cursor
    patch += struct.pack("<II", zlib.crc32(source), zlib.crc32(target))
    patch += struct.pack("<I", zlib.crc32(patch))
    return bytes(patch)


def apply_patch(source: bytes, patch: bytes) -> bytes:
    if patch[:4] != b"UPS1" or zlib.crc32(patch[:-4]) != struct.unpack_from("<I", patch, len(patch)-4)[0]:
        raise ValueError("Invalid UPS signature or patch CRC")
    offset = 4
    source_size, offset = get_varint(patch, offset)
    target_size, offset = get_varint(patch, offset)
    if len(source) != source_size or zlib.crc32(source) != struct.unpack_from("<I", patch, len(patch)-12)[0]:
        raise ValueError("Source ROM size or CRC does not match the patch")
    out = bytearray(max(source_size, target_size))
    out[:source_size] = source
    cursor = last_offset = 0
    records_end = len(patch) - 12
    while offset < records_end:
        delta, offset = get_varint(patch, offset)
        cursor = last_offset + delta
        while True:
            value = patch[offset]
            offset += 1
            if value == 0:
                cursor += 1
                break
            if cursor >= len(out):
                raise ValueError("UPS record extends beyond target ROM")
            out[cursor] ^= value
            cursor += 1
        last_offset = cursor
    result = bytes(out[:target_size])
    if zlib.crc32(result) != struct.unpack_from("<I", patch, len(patch)-8)[0]:
        raise ValueError("Target ROM CRC does not match the patch")
    return result


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    release = root / "build" / "release" / "v1.0"
    release.mkdir(parents=True, exist_ok=True)
    manifest = {"version": "1.0", "format": "UPS1", "wireless_battle": False, "patches": {}}
    for version in ("Blue", "Red"):
        original = root / "Original Roms" / f"561{0 if version == 'Blue' else 1}_-_Digimon_Story_Super_Xros_Wars_{version}_JPN_NDS-HR.nds"
        translated = root / "build" / f"Digimon_Super_Xros_Wars_{version}_English_batch126.nds"
        patch_path = release / f"Digimon_Super_Xros_Wars_{version}_English_v1.0.ups"
        source_bytes = original.read_bytes()
        target_bytes = translated.read_bytes()
        patch_bytes = make_patch(source_bytes, target_bytes)
        reconstructed = apply_patch(source_bytes, patch_bytes)
        if reconstructed != target_bytes:
            raise AssertionError(f"{version} patch reconstruction mismatch")
        patch_path.write_bytes(patch_bytes)
        manifest["patches"][version.lower()] = {
            "file": patch_path.name,
            "source_sha256": sha256(original),
            "target_sha256": sha256(translated),
            "patch_sha256": hashlib.sha256(patch_bytes).hexdigest(),
            "patch_bytes": len(patch_bytes),
            "target_bytes": len(target_bytes),
            "round_trip": "passed",
        }
    (release / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
