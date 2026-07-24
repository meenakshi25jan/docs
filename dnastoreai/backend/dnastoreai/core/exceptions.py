"""Custom exceptions for DNAStoreAI platform."""


class DNAStoreAIError(Exception):
    """Base exception for all platform errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class CompressionError(DNAStoreAIError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "COMPRESSION_ERROR")


class SegmentationError(DNAStoreAIError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "SEGMENTATION_ERROR")


class ECCEncodingError(DNAStoreAIError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "ECC_ENCODING_ERROR")


class ECCDecodingError(DNAStoreAIError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "ECC_DECODING_ERROR")


class DNAEncodingError(DNAStoreAIError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "DNA_ENCODING_ERROR")


class ReconstructionError(DNAStoreAIError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "RECONSTRUCTION_ERROR")


class ArchiveNotFoundError(DNAStoreAIError):
    def __init__(self, archive_id: str) -> None:
        super().__init__(f"Archive not found: {archive_id}", "ARCHIVE_NOT_FOUND")


class FileNotFoundError(DNAStoreAIError):
    def __init__(self, file_id: str) -> None:
        super().__init__(f"File not found: {file_id}", "FILE_NOT_FOUND")
