# core/processor.py
import os
import pathlib
from typing import List

from .models import DiagramItem, BulkDiagramResponse
from .parser import generate_mermaid_from_csharp
from .utils import normalize_path, logger

def process_folder_bulk(
    folder_path: str,
    max_files: int,
    include_interfaces: bool,
    include_abstracts: bool,
) -> BulkDiagramResponse:
    """
    Shared bulk processing logic.
    Used by both FastAPI and MCP servers.
    """
    folder_path = normalize_path(folder_path)

    if not folder_path.exists():
        raise ValueError(f"Folder not found: {folder_path}")
    if not folder_path.is_dir():
        raise ValueError(f"Not a directory: {folder_path}")

    diagrams: List[DiagramItem] = []
    processed = 0
    total_scanned = 0

    for root, _, files in os.walk(folder_path):
        for file in sorted(files):
            if file.endswith(".cs") and not file.endswith(".g.cs") and "obj" not in root.split(os.sep):
                total_scanned += 1
                full_path = pathlib.Path(root) / file
                rel_path = full_path.relative_to(folder_path).as_posix()
                try:
                    raw_diagram = generate_mermaid_from_csharp(
                        str(full_path),
                        include_interfaces=include_interfaces,
                        include_abstracts=include_abstracts,
                    )
                    diagrams.append(DiagramItem(file=rel_path, mermaid=raw_diagram))
                    processed += 1
                except (ValueError, RuntimeError) as exc:
                    logger.warning(f"Skipping {rel_path}: {exc}")
                    continue

                if processed >= max_files:
                    break
        if processed >= max_files:
            break

    return BulkDiagramResponse(
        content=diagrams,
        processed=processed,
        truncated=processed >= max_files,
        total_scanned=total_scanned,
    )
