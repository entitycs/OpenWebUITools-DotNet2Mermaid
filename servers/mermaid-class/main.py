from fastapi import FastAPI, Body
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os, pathlib, re

app = FastAPI(
    title="Mermaid Diagram API",
    version="1.0.0",
    description="Provides mermaid diagrams for csharp class source code",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ------------------------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------------------------
def normalize_path(requested_path: str) -> pathlib.Path:
    requested = pathlib.Path(os.path.expand(requested_path)).resolve()
#    for allowed in ALLOWED_DIRECTORIES:
#    if true: #str(requested).lower().startswith(allowed.lower()): # Case-insensitive check
    return requested

def _strip_generics(name: str) -> str:
    """Remove generic type arguments like <T> or <T1, T2> from a C# identifier."""
    return re.sub(r"<([^>]+)>", r"~\g<1>~", name)

def generate_mermaid_from_csharp(
    file_path: str,
    include_interfaces: bool = True,
    include_abstracts: bool = True,
) -> str:
    """
    Parse a C# file and generate a Mermaid diagram.
    :param file_path: path of the file from which chart is to be generated.
    :param include_interfaces: false to skip diagramming of interfaces.
    :param include_abstracts: false to skip diagramming of abstract classes.
    """

    if not os.path.exists(file_path):
        return f"ERROR: File not found at {file_path}"

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    lines = code.split("\n")

    mermaid = [
        "```mermaid",
        "classDiagram",
        f"    %% File: {os.path.basename(file_path)}",
    ]

    class_pattern = re.compile(
        r"^\s*(public|internal|private|protected)?\s*(abstract|sealed)?\s*class\s+(\w+(?:<[^>]+>)?)(?:\s*:\s*([^}{]+))?"
    )
    interface_pattern = re.compile(
        r"^\s*(public|internal)?\s*interface\s+(\w+(?:<[^>]+>)?)"
    )

    for line in lines:
        line = line.strip()

        # Classes
        class_match = class_pattern.search(line)
        if class_match:
            modifiers = class_match.group(2) or ""
            class_name = _strip_generics(class_match.group(3).strip())
            bases = class_match.group(4)

            mermaid.append(f"    class {class_name}")

            if include_abstracts and "abstract" in modifiers:
                mermaid.append(f"    abstract_{class_name}")

            if bases:
                for base in [b.strip() for b in bases.split(",")]:
                    if base and not base.startswith("{"):
                        clean_base = _strip_generics(base.split()[-1])
                        mermaid.append(f"    {clean_base} <|-- {class_name}")

        # Interfaces
        if include_interfaces:
            iface_match = interface_pattern.search(line)
            if iface_match:
                iface_name = _strip_generics(iface_match.group(2).strip())
                mermaid.append(f"    class interface_{iface_name}")

    mermaid.append("```")
    return "\n".join(mermaid)

# ---------------- Responses ----------------
class SuccessResponse(BaseModel):
    message: str = Field(..., description="Success message indicating the operation was completed.")

# ---------------- Requests ----------------
class CreateDiagramRequest(BaseModel):
    file_path: str = Field(default="/workspace/src/main.cs")
    include_interfaces: bool = True
    include_abstracts: bool = True

class BatchCreateClassDiagramRequest(BaseModel):
    folder_path: str = Field(default="/workspace/src")
    max_files: int = 10
    include_interfaces: bool = True
    include_abstracts: bool = True

# ---------------- Endpoints ----------------
@app.post("/bulk_class_diagram", response_model=SuccessResponse)
async def bulk_class_diagram(data: BatchCreateClassDiagramRequest = Body(...)):
    folder_path = data.folder_path
    if not os.path.exists(folder_path):
        return Response(content=f"ERROR: Folder not found at {folder_path}", media_type="text/markdown")

    output_blocks = []
    processed = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".cs") and not file.endswith(".g.cs") and "obj/" not in root:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, folder_path)
                diagram = generate_mermaid_from_csharp(full_path,
                                                      include_interfaces=data.include_interfaces,
                                                      include_abstracts=data.include_abstracts)
                block = f"### {rel_path}\n{diagram}"
                output_blocks.append(block)
                processed += 1
                if processed >= data.max_files:
                    output_blocks.append(f"... stopped at {data.max_files} files")
                    break
        if processed >= data.max_files:
            break

    markdown = "\n\n".join(output_blocks)
    return Response(content=markdown, media_type="text/markdown")

@app.post("/generate_diagram", response_model=SuccessResponse)
async def generate_diagram(data: CreateDiagramRequest = Body(...)):
    file_path = data.file_path
    if not os.path.exists(file_path):
        return Response(content=f"ERROR: File not found at {file_path}", media_type="text/markdown")

    diagram = generate_mermaid_from_csharp(file_path,
                                           include_interfaces=data.include_interfaces,
                                           include_abstracts=data.include_abstracts)
    block = f"### {file_path}\n{diagram}"
    return Response(content=block, media_type="text/markdown")
