"""ZBP brush file thumbnail extractor.

Extracts the embedded 96×96 RGBA thumbnail from ZBrush ``.ZBP`` files.
The algorithm is a Python port of the Pixologic C routine
``ReadZBrushFileThumbnail`` by Ofer Alon.

The thumbnail data is stored in a block-compressed, planar-channel format
deep inside the file header.  This module handles both v4 and v5+
compression variants.
"""

from __future__ import annotations

import struct
from typing import Optional

# ZBrush thumbnails are always 96×96 RGBA.
ICON_WIDTH: int = 96
ICON_HEIGHT: int = 96
ICON_PIXEL_COUNT: int = ICON_WIDTH * ICON_HEIGHT
ICON_BYTE_COUNT: int = ICON_PIXEL_COUNT * 4  # 36 864 bytes

# Number of header bytes to read from the file (per Pixologic's spec).
_HEADER_READ_SIZE: int = 37_000

# Magic pattern that marks the start of the thumbnail block.
_MAGIC = bytes([0x00, 0x90, 0x00, 0x00, 0x04, 0x00, 0x80, 0x01])


def extract_zbp_thumbnail(
    file_path: str,
    scale_alpha: bool = True,
) -> Optional[bytes]:
    """Extract the 96×96 RGBA thumbnail from a ZBP file.

    Args:
        file_path: Path to a ``.ZBP`` brush file.
        scale_alpha: When True, alpha is boosted so dark-background icons
            become fully opaque.  Pass False for material/light presets.

    Returns:
        A ``bytes`` object of length 36 864 (96×96×4, RGBA interleaved,
        left-to-right top-to-bottom) on success, or ``None`` if the
        thumbnail cannot be located or decoded.
    """
    try:
        with open(file_path, "rb") as f:
            raw = f.read(_HEADER_READ_SIZE)
    except OSError:
        return None

    return _read_thumbnail(raw, scale_alpha)


def _read_thumbnail(data: bytes, scale_alpha: bool) -> Optional[bytes]:
    """Core decoder — port of Pixologic's ``ReadZBrushFileThumbnail``.

    Args:
        data: The first ~37 000 bytes of the ZBP file.
        scale_alpha: Whether to boost the alpha channel.

    Returns:
        RGBA pixel data or None.
    """
    result = bytearray(ICON_BYTE_COUNT)
    temp = bytearray(ICON_BYTE_COUNT + 256)

    # Skip the 200-byte file header, then scan for the magic pattern.
    pos = 200
    scan_limit = min(len(data) - 8, pos + 40)

    while pos < scan_limit:
        if data[pos : pos + 8] == _MAGIC:
            break
        pos += 1
    else:
        return None  # Magic not found.

    # Compression version is 6 bytes before the magic pattern.
    compression_version = data[pos - 6]
    pos += 8  # Advance past the magic.

    if compression_version < 4:
        return None  # Old unsupported format.

    # Read block byte counts (compressed sizes per block).
    block_counts = [0, 0, 0, 0]

    if compression_version > 4:
        # v5+: skip 12 bytes, then two 4-byte block sizes.
        pos += 12
        block_counts[0] = struct.unpack_from("<i", data, pos)[0]; pos += 4
        block_counts[1] = struct.unpack_from("<i", data, pos)[0]; pos += 4
    else:
        # v4: four 2-byte block sizes.
        for i in range(4):
            block_counts[i] = struct.unpack_from("<h", data, pos)[0]; pos += 2

    # Each block contains RLE-compressed data for ALL 4 channels
    # stored sequentially.  After decompression the data in tempBuffer
    # is split into 4 interleaved sub-channels in the result buffer.
    result_offset = 0

    for blocks_index in range(4):
        if block_counts[blocks_index] == 0:
            break

        block_start = pos
        write_count = 0

        # v6+ has an extra 4-byte skip per block.
        if compression_version >= 6:
            pos += 4

        # RLE decompression into temp buffer.
        while pos < len(data):
            sub_count_raw = data[pos]
            pos += 1

            # Signed byte: 0 = end sentinel.
            if sub_count_raw == 0:
                break

            if sub_count_raw <= 127:
                # Positive: repeat next byte ``sub_count_raw`` times.
                sub_count = sub_count_raw
                if pos >= len(data):
                    break
                val = data[pos]
                pos += 1
                for _ in range(sub_count):
                    if write_count < len(temp):
                        temp[write_count] = val
                        write_count += 1
            else:
                # Negative (>127): literal run of ``256 - sub_count_raw`` bytes.
                literal_len = 256 - sub_count_raw
                for _ in range(literal_len):
                    if pos >= len(data) or write_count >= len(temp):
                        break
                    temp[write_count] = data[pos]
                    write_count += 1
                    pos += 1

        # Distribute decompressed data into 4 interleaved sub-channels.
        # sub_ch 0 → byte offsets 0, 4, 8, …  (channel R after swap)
        # sub_ch 1 → byte offsets 1, 5, 9, …  (channel G)
        # sub_ch 2 → byte offsets 2, 6, 10, … (channel B after swap)
        # sub_ch 3 → byte offsets 3, 7, 11, … (channel A)
        read_count = 0
        pixels_per_sub = write_count >> 2

        for sub_ch in range(4):
            p_dest = result_offset + sub_ch
            for _ in range(pixels_per_sub):
                if p_dest < ICON_BYTE_COUNT and read_count < write_count:
                    result[p_dest] = temp[read_count]
                    read_count += 1

                    if sub_ch == 3:
                        # Alpha channel processing + R↔B swap.
                        if scale_alpha and result[p_dest - 1] != 0:
                            prev = int(result[p_dest - 1])
                            squared = prev * prev
                            result[p_dest] = 255 if squared > 255 else int(squared * 0.5)
                        # Swap R (sub_ch 0) and B (sub_ch 2) — same as C++.
                        r_pos = p_dest - 3
                        b_pos = p_dest - 1
                        result[r_pos], result[b_pos] = result[b_pos], result[r_pos]
                p_dest += 4

        result_offset += write_count
        pos = block_start + block_counts[blocks_index]

    return bytes(result)
