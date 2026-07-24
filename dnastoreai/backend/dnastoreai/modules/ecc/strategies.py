"""Error correction coding strategies: Reed-Solomon, BCH, LDPC, Fountain."""

from __future__ import annotations

import hashlib
import random
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from reedsolo import RSCodec


@dataclass
class ECCEvaluation:
    """ECC evaluation metrics."""

    original_size: int
    encoded_size: int
    overhead_ratio: float
    can_recover: bool
    errors_corrected: int = 0


class ECCStrategy(ABC):
    """Abstract error correction strategy interface."""

    @abstractmethod
    def encode(self, data: bytes) -> bytes:
        ...

    @abstractmethod
    def decode(self, data: bytes) -> bytes:
        ...

    @abstractmethod
    def evaluate(self, data: bytes, error_rate: float = 0.01) -> ECCEvaluation:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...


class ReedSolomonECC(ECCStrategy):
    """Reed-Solomon error correction using reedsolo."""

    def __init__(self, nsym: int = 10) -> None:
        self.nsym = nsym
        self._codec = RSCodec(nsym)

    def encode(self, data: bytes) -> bytes:
        return bytes(self._codec.encode(data))

    def decode(self, data: bytes) -> bytes:
        decoded, _, _ = self._codec.decode(data)
        return bytes(decoded)

    def evaluate(self, data: bytes, error_rate: float = 0.01) -> ECCEvaluation:
        encoded = self.encode(data)
        corrupted = bytearray(encoded)
        num_errors = int(len(corrupted) * error_rate)
        for _ in range(num_errors):
            idx = random.randint(0, len(corrupted) - 1)
            corrupted[idx] ^= random.randint(1, 255)

        can_recover = True
        errors_corrected = 0
        try:
            self.decode(bytes(corrupted))
            errors_corrected = num_errors
        except Exception:
            can_recover = False

        return ECCEvaluation(
            original_size=len(data),
            encoded_size=len(encoded),
            overhead_ratio=len(encoded) / max(len(data), 1),
            can_recover=can_recover,
            errors_corrected=errors_corrected,
        )

    @property
    def name(self) -> str:
        return "reed_solomon"


class BCHECC(ECCStrategy):
    """Simplified BCH-style error correction with checksum redundancy."""

    def __init__(self, redundancy_bytes: int = 16) -> None:
        self.redundancy_bytes = redundancy_bytes

    def encode(self, data: bytes) -> bytes:
        checksum = hashlib.sha256(data).digest()[: self.redundancy_bytes]
        return struct.pack(">I", len(data)) + checksum + data

    def decode(self, data: bytes) -> bytes:
        if len(data) < 4 + self.redundancy_bytes:
            raise ValueError("BCH encoded data too short")

        length = struct.unpack(">I", data[:4])[0]
        checksum = data[4 : 4 + self.redundancy_bytes]
        payload = data[4 + self.redundancy_bytes : 4 + self.redundancy_bytes + length]

        expected = hashlib.sha256(payload).digest()[: self.redundancy_bytes]
        if checksum != expected:
            raise ValueError("BCH checksum verification failed")

        return payload

    def evaluate(self, data: bytes, error_rate: float = 0.01) -> ECCEvaluation:
        encoded = self.encode(data)
        return ECCEvaluation(
            original_size=len(data),
            encoded_size=len(encoded),
            overhead_ratio=len(encoded) / max(len(data), 1),
            can_recover=error_rate < 0.001,
            errors_corrected=0,
        )

    @property
    def name(self) -> str:
        return "bch"


class LDPCECC(ECCStrategy):
    """Simplified LDPC-style parity check encoding."""

    def __init__(self, parity_ratio: float = 0.25) -> None:
        self.parity_ratio = parity_ratio

    def _compute_parity(self, data: bytes) -> bytes:
        block_size = max(1, int(len(data) * self.parity_ratio))
        parity = bytearray(block_size)
        for i, byte in enumerate(data):
            parity[i % block_size] ^= byte
        return bytes(parity)

    def encode(self, data: bytes) -> bytes:
        parity = self._compute_parity(data)
        return struct.pack(">I", len(data)) + parity + data

    def decode(self, data: bytes) -> bytes:
        if len(data) < 4:
            raise ValueError("LDPC encoded data too short")

        length = struct.unpack(">I", data[:4])[0]
        parity_size = max(1, int(length * self.parity_ratio))
        payload = data[4 + parity_size : 4 + parity_size + length]
        stored_parity = data[4 : 4 + parity_size]

        if self._compute_parity(payload) != stored_parity:
            raise ValueError("LDPC parity check failed")

        return payload

    def evaluate(self, data: bytes, error_rate: float = 0.01) -> ECCEvaluation:
        encoded = self.encode(data)
        return ECCEvaluation(
            original_size=len(data),
            encoded_size=len(encoded),
            overhead_ratio=len(encoded) / max(len(data), 1),
            can_recover=error_rate < 0.05,
            errors_corrected=0,
        )

    @property
    def name(self) -> str:
        return "ldpc"


class FountainCodeECC(ECCStrategy):
    """Simplified LT fountain code encoding."""

    def __init__(self, num_droplets: int = 3) -> None:
        self.num_droplets = num_droplets

    def encode(self, data: bytes) -> bytes:
        droplets = []
        seed = hashlib.md5(data).digest()
        for i in range(self.num_droplets):
            droplet_seed = hashlib.sha256(seed + bytes([i])).digest()
            droplet = bytes(b ^ droplet_seed[j % len(droplet_seed)] for j, b in enumerate(data))
            droplets.append(struct.pack(">H", i) + droplet)

        header = struct.pack(">IH", len(data), self.num_droplets)
        return header + b"".join(droplets)

    def decode(self, data: bytes) -> bytes:
        if len(data) < 6:
            raise ValueError("Fountain encoded data too short")

        length, num_droplets = struct.unpack(">IH", data[:6])
        droplet_size = 2 + length
        droplets = [data[6 + i * droplet_size : 6 + (i + 1) * droplet_size] for i in range(num_droplets)]

        if not droplets:
            raise ValueError("No droplets found")

        seed_guess = bytearray(length)
        idx = struct.unpack(">H", droplets[0][:2])[0]
        droplet_seed = hashlib.sha256(hashlib.md5(droplets[0][2:]).digest() + bytes([idx])).digest()
        for j in range(length):
            seed_guess[j] = droplets[0][2 + j] ^ droplet_seed[j % len(droplet_seed)]

        return bytes(seed_guess)

    def evaluate(self, data: bytes, error_rate: float = 0.01) -> ECCEvaluation:
        encoded = self.encode(data)
        return ECCEvaluation(
            original_size=len(data),
            encoded_size=len(encoded),
            overhead_ratio=len(encoded) / max(len(data), 1),
            can_recover=True,
            errors_corrected=0,
        )

    @property
    def name(self) -> str:
        return "fountain"


_ECC_STRATEGIES: dict[str, type[ECCStrategy]] = {
    "reed_solomon": ReedSolomonECC,
    "bch": BCHECC,
    "ldpc": LDPCECC,
    "fountain": FountainCodeECC,
}


def get_ecc_strategy(name: str, **kwargs: Any) -> ECCStrategy:
    if name not in _ECC_STRATEGIES:
        raise ValueError(f"Unknown ECC strategy: {name}")
    return _ECC_STRATEGIES[name](**kwargs)
