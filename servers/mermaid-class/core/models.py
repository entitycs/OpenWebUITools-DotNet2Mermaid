from pydantic import BaseModel, Field
from typing import List

class DiagramItem(BaseModel):
    """
    Format of response to retrieve a single mermaid diagrams from a file given its file path or filename.
    """
    file: str = Field(..., description="Relative path or filename of the source file")
    mermaid: str = Field(..., description="Pure Mermaid classDiagram code")

class DiagramItemRequest(BaseModel):
    """
    Format of request to retrieve a mermaid diagram from source code given a path (file path or filename).
    """
    path: str = Field(..., description="Filename or file path")

class BulkDiagramResponse(BaseModel):
    """
    Format of response to retrieve one or more mermaid diagrams from source code given a path (file path or filename), or from the current workspace.
    """
    content: List[DiagramItem] = Field(..., description="List of processed mermaid diagrams")
    processed: int = Field(..., description="Number of files processed")
    truncated: bool = Field(False, description="True if stopped early due to max_files")
    total_scanned: int = Field(0, description="Total .cs files found before limit")

class BatchCreateClassDiagramRequest(BaseModel):
    """
    Format of request to retrieve one or more mermaid diagrams from source code given a path (file path or filename), or from the current workspace 
    """
    folder_path: str | None = Field("/workspace/src", description="Path to folder containing .cs files")
    max_files: int | None = Field(10, ge=1, le=1000)
    include_interfaces: bool | None = True # note - likely to deprecate
    include_abstracts: bool | None = True

