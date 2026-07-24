"""Unit tests for ECC strategies."""

import pytest

from dnastoreai.modules.ecc.strategies import (
    BCHECC,
    FountainCodeECC,
    LDPCECC,
    ReedSolomonECC,
    get_ecc_strategy,
)


class TestECC:
    def test_reed_solomon_roundtrip(self):
        ecc = ReedSolomonECC(nsym=10)
        data = b"ECC test data for Reed-Solomon encoding"
        encoded = ecc.encode(data)
        assert len(encoded) > len(data)
        decoded = ecc.decode(encoded)
        assert decoded == data

    def test_reed_solomon_evaluate(self):
        ecc = ReedSolomonECC()
        result = ecc.evaluate(b"test data")
        assert result.overhead_ratio > 1.0

    def test_bch_roundtrip(self):
        ecc = BCHECC()
        data = b"BCH test data"
        assert ecc.decode(ecc.encode(data)) == data

    def test_bch_invalid_checksum(self):
        ecc = BCHECC()
        encoded = ecc.encode(b"test")
        corrupted = bytearray(encoded)
        corrupted[4] ^= 0xFF
        with pytest.raises(ValueError):
            ecc.decode(bytes(corrupted))

    def test_ldpc_roundtrip(self):
        ecc = LDPCECC()
        data = b"LDPC test data"
        assert ecc.decode(ecc.encode(data)) == data

    def test_fountain_roundtrip(self):
        ecc = FountainCodeECC()
        data = b"Fountain code test"
        decoded = ecc.decode(ecc.encode(data))
        assert len(decoded) == len(data)

    def test_get_ecc_invalid(self):
        with pytest.raises(ValueError):
            get_ecc_strategy("invalid")

    def test_ecc_names(self):
        assert ReedSolomonECC().name == "reed_solomon"
        assert BCHECC().name == "bch"
        assert LDPCECC().name == "ldpc"
        assert FountainCodeECC().name == "fountain"

    def test_bch_too_short(self):
        with pytest.raises(ValueError):
            BCHECC().decode(b"short")

    def test_ldpc_too_short(self):
        with pytest.raises(ValueError):
            LDPCECC().decode(b"x")

    def test_fountain_too_short(self):
        with pytest.raises(ValueError):
            FountainCodeECC().decode(b"x")
