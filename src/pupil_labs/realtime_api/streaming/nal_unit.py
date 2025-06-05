import struct
from collections.abc import ByteString


def extract_payload_from_nal_unit(unit: ByteString) -> ByteString:
    """Extract and process payload from a Network Abstraction Layer (NAL) unit.

    This function extracts the payload from a NAL unit, handling various formats:
    - Prepends NAL unit start code to payload if necessary
    - Handles fragmented units (of type FU-A)

    The implementation follows RFC 3984 specifications for H.264 NAL units.

    Args:
        unit: The NAL unit as a ByteString.

    Returns:
        ByteString: The processed payload, potentially with start code prepended.

    Raises:
        ValueError: If the first bit is not zero (forbidden_zero_bit).

    References:
        Inspired by https://github.com/runtheops/rtsp-rtp/blob/master/transport/primitives/nal_unit.py
        Rewritten due to license incompatibility.
        See RFC 3984 (https://www.ietf.org/rfc/rfc3984.txt) for detailed NAL unit
        specifications.

    """
    start_code = b"\x00\x00\x00\x01"
    offset = 0
    # slice to keep ByteString type; indexing would return int in native byte order
    first_byte_raw = unit[:1]
    # ensure network order for conversion to uint8
    first_byte = struct.unpack("!B", first_byte_raw)[0]
    is_first_bit_one = (first_byte & 0b10000000) != 0
    if is_first_bit_one:
        # See section 1.3 of https://www.ietf.org/rfc/rfc3984.txt
        raise ValueError("First bit must be zero (forbidden_zero_bit)")

    nal_type = first_byte & 0b00011111
    if nal_type == 28:
        # Fragmentation unit FU-A
        # https://www.ietf.org/rfc/rfc3984.txt
        # Section 5.8.
        fu_header_raw = unit[1:2]  # get second byte while retaining ByteString type
        fu_header = struct.unpack("!B", fu_header_raw)[0]
        offset = 2  # skip first two bytes

        is_fu_start_bit_one = (fu_header & 0b10000000) != 0
        if is_fu_start_bit_one:
            # reconstruct header of a non-fragmented NAL unit
            first_byte_bits_1_to_3 = first_byte & 0b11100000
            # NAL type of non-fragmented NAL unit:
            fu_header_bits_4_to_8 = fu_header & 0b00011111
            reconstructed_header = first_byte_bits_1_to_3 + fu_header_bits_4_to_8
            start_code += bytes((reconstructed_header,))  # convert int to ByteString
        else:
            # do not prepend start code to payload since we are in the middle of a
            # fragmented unit
            start_code = b""

    return start_code + unit[offset:]
