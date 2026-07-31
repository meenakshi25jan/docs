"""Binary to DNA encoding with multiple coding schemes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

EncodingMethod = Literal["basic", "rotating", "gc_balanced", "custom"]

BASE_MAP = {"00": "A", "01": "C", "10": "G", "11": "T"}
REVERSE_MAP = {v: k for k, v in BASE_MAP.items()}


class DNAEncoder(ABC):
    """Abstract DNA encoder interface."""

    @abstractmethod
    def encode(self, data: bytes) -> str:
        ...

    @abstractmethod
    def decode(self, sequence: str) -> bytes:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


class BasicEncoder(DNAEncoder):
    """Basic 2-bit to nucleotide mapping: 00->A, 01->C, 10->G, 11->T."""

    def encode(self, data: bytes) -> str:
        bits = "".join(f"{b:08b}" for b in data)
        padded = bits + "0" * ((4 - len(bits) % 4) % 4)
        return "".join(BASE_MAP[padded[i : i + 2]] for i in range(0, len(padded), 2))

    def decode(self, sequence: str) -> bytes:
        sequence = sequence.upper()
        bits = "".join(REVERSE_MAP.get(base, "00") for base in sequence)
        byte_count = len(bits) // 8
        return bytes(int(bits[i : i + 8], 2) for i in range(0, byte_count * 8, 8))

    @property
    def name(self) -> str:
        return "basic"


class RotatingEncoder(DNAEncoder):
    """Rotating code that shifts mapping based on position."""

    ROTATIONS = [
        {"00": "A", "01": "C", "10": "G", "11": "T"},
        {"00": "C", "01": "G", "10": "T", "11": "A"},
        {"00": "G", "01": "T", "10": "A", "11": "C"},
        {"00": "T", "01": "A", "10": "C", "11": "G"},
    ]

    def encode(self, data: bytes) -> str:
        bits = "".join(f"{b:08b}" for b in data)
        padded = bits + "0" * ((4 - len(bits) % 4) % 4)
        result = []
        for i in range(0, len(padded), 2):
            mapping = self.ROTATIONS[(i // 2) % len(self.ROTATIONS)]
            result.append(mapping[padded[i : i + 2]])
        return "".join(result)

    def decode(self, sequence: str) -> bytes:
        sequence = sequence.upper()
        bits = []
        for i, base in enumerate(sequence):
            mapping = self.ROTATIONS[i % len(self.ROTATIONS)]
            reverse = {v: k for k, v in mapping.items()}
            bits.append(reverse.get(base, "00"))
        bit_string = "".join(bits)
        byte_count = len(bit_string) // 8
        return bytes(int(bit_string[j : j + 8], 2) for j in range(0, byte_count * 8, 8))

    @property
    def name(self) -> str:
        return "rotating"


class GCBalancedEncoder(DNAEncoder):
    """GC-balanced encoding that alternates GC-rich and AT-rich codons."""

    GC_CODONS = {"00": "G", "01": "C", "10": "T", "11": "A"}
    AT_CODONS = {"00": "A", "01": "T", "10": "G", "11": "C"}

    def encode(self, data: bytes) -> str:
        bits = "".join(f"{b:08b}" for b in data)
        padded = bits + "0" * ((4 - len(bits) % 4) % 4)
        result = []
        for i in range(0, len(padded), 2):
            codon = padded[i : i + 2]
            mapping = self.GC_CODONS if (i // 2) % 2 == 0 else self.AT_CODONS
            result.append(mapping[codon])
        return "".join(result)

    def decode(self, sequence: str) -> bytes:
        sequence = sequence.upper()
        bits = []
        for i, base in enumerate(sequence):
            mapping = self.GC_CODONS if i % 2 == 0 else self.AT_CODONS
            reverse = {v: k for k, v in mapping.items()}
            bits.append(reverse.get(base, "00"))
        bit_string = "".join(bits)
        byte_count = len(bit_string) // 8
        return bytes(int(bit_string[j : j + 8], 2) for j in range(0, byte_count * 8, 8))

    @property
    def name(self) -> str:
        return "gc_balanced"


class CustomEncoder(DNAEncoder):
    """Research custom code with user-defined mapping."""

    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self.mapping = mapping or BASE_MAP.copy()
        self._reverse = {v: k for k, v in self.mapping.items()}

    def encode(self, data: bytes) -> str:
        bits = "".join(f"{b:08b}" for b in data)
        padded = bits + "0" * ((4 - len(bits) % 4) % 4)
        return "".join(self.mapping[padded[i : i + 2]] for i in range(0, len(padded), 2))

    def decode(self, sequence: str) -> bytes:
        sequence = sequence.upper()
        bits = "".join(self._reverse.get(base, "00") for base in sequence)
        byte_count = len(bits) // 8
        return bytes(int(bits[i : i + 8], 2) for i in range(0, byte_count * 8, 8))

    @property
    def name(self) -> str:
        return "custom"


_ENCODERS: dict[str, DNAEncoder] = {
    "basic": BasicEncoder(),
    "rotating": RotatingEncoder(),
    "gc_balanced": GCBalancedEncoder(),
    "custom": CustomEncoder(),
}


def get_encoder(method: EncodingMethod) -> DNAEncoder:
    if method not in _ENCODERS:
        raise ValueError(f"Unknown encoding method: {method}")
    return _ENCODERS[method]
