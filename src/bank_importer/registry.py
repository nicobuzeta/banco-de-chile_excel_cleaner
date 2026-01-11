from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Importer


class ImporterRegistry:
    """Registry for transaction importers."""

    _importers: dict[str, type["Importer"]] = {}

    @classmethod
    def register(cls, importer_class: type["Importer"]) -> type["Importer"]:
        """Decorator to register an importer class."""
        cls._importers[importer_class.name] = importer_class
        return importer_class

    @classmethod
    def get(cls, name: str) -> type["Importer"]:
        """Get an importer class by name."""
        if name not in cls._importers:
            available = ", ".join(sorted(cls._importers.keys()))
            raise KeyError(f"Unknown importer: {name}. Available: {available}")
        return cls._importers[name]

    @classmethod
    def list_all(cls) -> list[type["Importer"]]:
        """List all registered importers."""
        return list(cls._importers.values())
