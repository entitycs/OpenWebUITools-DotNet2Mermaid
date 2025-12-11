import re
import os
from .utils import _strip_generics, _strip_comments, logger

def generate_mermaid_from_csharp(
    file_path: str,
    include_interfaces: bool = True,
    include_abstracts: bool = True,
) -> str:
    logger.info(f"attempting read of {file_path}")
    if not os.path.isfile(file_path):
        raise ValueError(f"Not a file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        raise RuntimeError(f"Cannot read file: {e}")

    mermaid = [
        "classDiagram",
        f"%% File: {os.path.basename(file_path)}",
    ]

    full_pattern = re.compile(
        r'^\s*((?:\[[^\]]+\]\s*(?:\n\s*)?)*)'
        r'(?:public|internal|private|protected|protected\s+internal|private\s+protected)?\s*'
        r'(?:new\s+)?((?:abstract|sealed|partial|static|unsafe|readonly|ref|file)\s*)*'
        r'(class|interface|struct|record)\s+'
        r'(\w+(?:<[^>]+>)?)'
        r'(?:\s*:\s*([^}{\n]+(?:\n\s*[^}{\n]+)*))?',
        re.MULTILINE
    )
    attribute_pattern = re.compile(r"^\s*\[([^\]]+)\]\s*")

    for m in full_pattern.finditer(code):
        modifiers = _strip_comments(m.group(2)) or ""
        class_name = _strip_generics(m.group(4))
        bases = _strip_comments(m.group(5))
        raw_attribs = _strip_comments(m.group(1))

        mermaid.append(f"class {class_name}")
        if include_abstracts and "abstract" in modifiers:
            mermaid.append(f"class {class_name} {{ <<abstract>> }}")

        if bases:
            for base in [b.strip() for b in bases.split(",")]:
                if base and not base.startswith("{"):
                    clean_base = _strip_generics(base.split()[-1])
                    mermaid.append(f"{clean_base} <|-- {class_name}")

        for attr in attribute_pattern.findall(raw_attribs):
            # clean = attr.strip().replace('"', "'")
            mermaid.append(f'  note for {class_name} "{attr}"')

    return "\n".join(mermaid)
