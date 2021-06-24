import hashlib
from typing import Any, Final, List

from pydicom import Dataset
from pydicom.dataset import PrivateBlock

fields_to_be_hashed: Final[List[str]] = [
    "SOPInstanceUID",
    "StudyInstanceUID",
    "SeriesInstanceUID",
    "PatientName",
    "PatientID",
    "PixelData",
]

other_byte_string_VR: Final[str] = "OB"
medcog_addr: Final[int] = int("0x" + "".join(f"{ord(v):2x}" for v in "MC"), 16)
medcog_name: Final[str] = "MedCognetics"


def hash_bytes(x: bytes) -> bytes:
    sha256 = hashlib.sha256()
    sha256.update(x)
    return sha256.digest()


def hash_any(value: Any, encoding: str = "utf-8") -> bytes:
    value = str(value).encode(encoding)
    return hash_bytes(value)


def get_value_hashes(ds: Dataset) -> List[bytes]:
    return [hash_any(ds.get(field)) for field in fields_to_be_hashed]


def get_medcog_block(ds: Dataset, create: bool = False) -> PrivateBlock:
    return ds.private_block(medcog_addr, medcog_name, create=create)


def store_value_hashes(ds: Dataset, hash_values: List[bytes]) -> None:
    block = get_medcog_block(ds, create=True)
    for i, value in enumerate(hash_values):
        block.add_new(i, other_byte_string_VR, value)
