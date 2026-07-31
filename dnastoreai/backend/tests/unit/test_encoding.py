"""Unit tests for DNA encoding."""

from dnastoreai.modules.encoding.encoder import (
    BasicEncoder,
    CustomEncoder,
    GCBalancedEncoder,
    RotatingEncoder,
    get_encoder,
)


class TestEncoding:
    def test_basic_roundtrip(self):
        enc = BasicEncoder()
        data = b"DNA encoding test"
        assert enc.decode(enc.encode(data)) == data

    def test_rotating_roundtrip(self):
        enc = RotatingEncoder()
        data = b"rotating code test data"
        assert enc.decode(enc.encode(data)) == data

    def test_gc_balanced_roundtrip(self):
        enc = GCBalancedEncoder()
        data = b"gc balanced encoding test"
        assert enc.decode(enc.encode(data)) == data

    def test_custom_roundtrip(self):
        enc = CustomEncoder()
        data = b"custom encoding"
        assert enc.decode(enc.encode(data)) == data

    def test_encoder_names(self):
        assert BasicEncoder().name == "basic"
        assert RotatingEncoder().name == "rotating"
        assert GCBalancedEncoder().name == "gc_balanced"
        assert CustomEncoder().name == "custom"

    def test_get_encoder(self):
        assert get_encoder("basic").name == "basic"

    def test_empty_data(self):
        enc = BasicEncoder()
        assert enc.decode(enc.encode(b"")) == b""

    def test_basic_mapping(self):
        enc = BasicEncoder()
        seq = enc.encode(b"\x00")
        assert all(c in "ACGT" for c in seq)
