import os
import pathlib
import re
import logging

logger = logging.getLogger("mermaid-csharp")

def normalize_path(requested_path: str) -> pathlib.Path:
    return pathlib.Path(os.path.expanduser(requested_path)).resolve()

def _strip_generics(name: str) -> str:
    return re.sub(r"<([^>]+)>", r"~\g<1>~", name.strip() if name else "")

def _strip_comments(token: str) -> str:
    return re.sub(r"(?:\/\/[^\n]*|[/][*]([^*/]+|[^*][/]|[*])*[*][/])","", token) if token else token