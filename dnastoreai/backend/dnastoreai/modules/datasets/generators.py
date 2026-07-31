"""Synthetic dataset generators for research experiments."""

from __future__ import annotations

import io
import json
import os
import random
import struct
import uuid
import zipfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image


@dataclass
class GeneratedFile:
    """A generated test file."""

    file_id: str
    filename: str
    data: bytes
    file_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


class DatasetGenerator(ABC):
    """Abstract dataset generator."""

    @abstractmethod
    def generate(self, count: int = 10, **kwargs: Any) -> list[GeneratedFile]:
        ...


class TextDatasetGenerator(DatasetGenerator):
    """Generate synthetic text files."""

    def generate(self, count: int = 10, min_size: int = 100, max_size: int = 10000, **kwargs: Any) -> list[GeneratedFile]:
        files = []
        words = ["dna", "storage", "encoding", "sequence", "research", "data", "archive", "biology"]
        for i in range(count):
            size = random.randint(min_size, max_size)
            text = " ".join(random.choice(words) for _ in range(size // 5))
            data = text.encode("utf-8")
            files.append(
                GeneratedFile(
                    file_id=str(uuid.uuid4()),
                    filename=f"text_{i:04d}.txt",
                    data=data,
                    file_type="txt",
                    metadata={"size": len(data), "generator": "text"},
                )
            )
        return files


class ImageDatasetGenerator(DatasetGenerator):
    """Generate synthetic PNG images."""

    def generate(self, count: int = 10, width: int = 64, height: int = 64, **kwargs: Any) -> list[GeneratedFile]:
        files = []
        for i in range(count):
            img = Image.new("RGB", (width, height), color=(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            data = buf.getvalue()
            files.append(
                GeneratedFile(
                    file_id=str(uuid.uuid4()),
                    filename=f"image_{i:04d}.png",
                    data=data,
                    file_type="png",
                    metadata={"width": width, "height": height, "generator": "image"},
                )
            )
        return files


class BinaryDatasetGenerator(DatasetGenerator):
    """Generate random binary files."""

    def generate(self, count: int = 10, min_size: int = 1024, max_size: int = 65536, **kwargs: Any) -> list[GeneratedFile]:
        files = []
        for i in range(count):
            size = random.randint(min_size, max_size)
            data = os.urandom(size)
            files.append(
                GeneratedFile(
                    file_id=str(uuid.uuid4()),
                    filename=f"binary_{i:04d}.bin",
                    data=data,
                    file_type="bin",
                    metadata={"size": size, "generator": "binary"},
                )
            )
        return files


class MixedDatasetGenerator(DatasetGenerator):
    """Generate a mixed dataset of text, JSON, CSV, and binary files."""

    def __init__(self) -> None:
        self._text_gen = TextDatasetGenerator()
        self._image_gen = ImageDatasetGenerator()
        self._binary_gen = BinaryDatasetGenerator()

    def generate(self, count: int = 10, **kwargs: Any) -> list[GeneratedFile]:
        files: list[GeneratedFile] = []
        per_type = max(1, count // 4)

        files.extend(self._text_gen.generate(per_type))

        for i in range(per_type):
            data = json.dumps({"id": i, "value": random.random(), "tags": ["dna", "storage"]}).encode()
            files.append(GeneratedFile(
                file_id=str(uuid.uuid4()), filename=f"data_{i:04d}.json", data=data, file_type="json",
                metadata={"generator": "mixed"},
            ))

        for i in range(per_type):
            rows = [f"id,value\n"] + [f"{j},{random.random()}\n" for j in range(50)]
            data = "".join(rows).encode()
            files.append(GeneratedFile(
                file_id=str(uuid.uuid4()), filename=f"table_{i:04d}.csv", data=data, file_type="csv",
                metadata={"generator": "mixed"},
            ))

        files.extend(self._binary_gen.generate(per_type))
        files.extend(self._image_gen.generate(max(1, count - len(files))))

        return files[:count]

    def generate_zip(self, count: int = 5, output_dir: Path | None = None) -> GeneratedFile:
        """Generate a zip archive of mixed files."""
        files = self.generate(count)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for f in files:
                zf.writestr(f.filename, f.data)
        data = buf.getvalue()
        return GeneratedFile(
            file_id=str(uuid.uuid4()),
            filename="mixed_dataset.zip",
            data=data,
            file_type="zip",
            metadata={"file_count": len(files), "generator": "mixed"},
        )


_GENERATORS: dict[str, type[DatasetGenerator]] = {
    "text": TextDatasetGenerator,
    "image": ImageDatasetGenerator,
    "binary": BinaryDatasetGenerator,
    "mixed": MixedDatasetGenerator,
}


def get_dataset_generator(name: str) -> DatasetGenerator:
    if name not in _GENERATORS:
        raise ValueError(f"Unknown generator: {name}")
    return _GENERATORS[name]()
