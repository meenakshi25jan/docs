"""Unit tests for dataset generators."""

from dnastoreai.modules.datasets.generators import (
    BinaryDatasetGenerator,
    ImageDatasetGenerator,
    MixedDatasetGenerator,
    TextDatasetGenerator,
    get_dataset_generator,
)


class TestDatasets:
    def test_text_generator(self):
        files = TextDatasetGenerator().generate(3, min_size=50, max_size=200)
        assert len(files) == 3
        assert files[0].file_type == "txt"

    def test_image_generator(self):
        files = ImageDatasetGenerator().generate(2)
        assert len(files) == 2
        assert files[0].file_type == "png"

    def test_binary_generator(self):
        files = BinaryDatasetGenerator().generate(2, min_size=100, max_size=500)
        assert len(files) == 2

    def test_mixed_generator(self):
        files = MixedDatasetGenerator().generate(8)
        assert len(files) == 8
        types = {f.file_type for f in files}
        assert len(types) > 1

    def test_mixed_zip(self):
        gen = MixedDatasetGenerator()
        zf = gen.generate_zip(3)
        assert zf.file_type == "zip"

    def test_get_generator(self):
        gen = get_dataset_generator("text")
        assert gen.generate(1)

    def test_invalid_generator(self):
        import pytest
        with pytest.raises(ValueError):
            get_dataset_generator("invalid")
