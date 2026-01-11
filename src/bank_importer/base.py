from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path
from typing import ClassVar

from .models import Transaction


class Importer(ABC):
    """Base class for all transaction importers."""

    name: ClassVar[str]
    description: ClassVar[str]
    supported_extensions: ClassVar[tuple[str, ...]]

    @abstractmethod
    def parse(self, file_path: Path) -> Sequence[Transaction]:
        """Parse the file and return a sequence of transactions."""
        ...
