from dataclasses import dataclass
from pathlib import Path


@dataclass
class Directory:
    original: str
    resolved: str
    is_directory: bool
    does_exist: bool
