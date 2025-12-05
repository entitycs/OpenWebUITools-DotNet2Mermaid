from pydantic import BaseModel, Field
from typing import List

class DiagramItem(BaseModel):
    file: str = Field(..., description="Relative path or filename")
    mermaid: str = Field(..., description="Pure Mermaid classDiagram code")

class BulkDiagramResponse(BaseModel):
    content: List[DiagramItem] = Field(..., description="List of processed mermaid diagrams")
    processed: int = Field(..., description="Number of files processed")
    truncated: bool = Field(False, description="True if stopped early due to max_files")
    total_scanned: int = Field(0, description="Total .cs files found before limit")

class BatchCreateClassDiagramRequest(BaseModel):
    folder_path: str = Field("/workspace/src", description="Path to folder containing .cs files")
    max_files: int = Field(10, ge=1, le=1000)
    include_interfaces: bool = True
    include_abstracts: bool = True

