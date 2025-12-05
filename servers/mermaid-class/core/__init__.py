# core/__init__.py
# Re-export the most-used symbols so consumers can do:
#   from core import normalize_path, DiagramItem, process_folder_bulk, ...

from .utils import normalize_path, _strip_generics, logger
from .models import (
    DiagramItem,
    BulkDiagramResponse,
    BatchCreateClassDiagramRequest,
)
from .parser import generate_mermaid_from_csharp
from .processor import process_folder_bulk

__all__ = [
    "normalize_path",
    "_strip_generics",
    "logger",
    "DiagramItem",
    "BulkDiagramResponse",
    "BatchCreateClassDiagramRequest",
    "generate_mermaid_from_csharp",
    "process_folder_bulk",
]

