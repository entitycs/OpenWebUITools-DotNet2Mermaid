"""
name: Grep Search
title: Grep Search 
author: EntityCS
description: Search the given folder path for a given pattern, or textual term with grep (shows file, line numbers and context).Use this tool whenever the user wants to find where something is defined or used. Use this tool whenever the user wants more context around the usage of a term or pattern.
required_open_webui_version: 0.4.0
requirements: fastapi, starlette, pydantic
icon: https://img.icons8.com/search
version: 0.0.2
licence: MIT
"""
import os
import subprocess
from pydantic import BaseModel, Field
from typing import Annotated, List
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import StreamingResponse
import logging

logger = logging.getLogger("uvicorn")

app = FastAPI(
    title="Grep Search API",
    version="1.0.0",
    description="Searches for a regular expression (grep) pattern within a codebase; taking lines of context and case sensitivity as params.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    logger.info(f"→ {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Body: {body.decode('utf-8', errors='replace') or ''}")
    print("log request called")
    response = await call_next(request)

    async def stream():
        async for chunk in response.body_iterator:
            yield chunk
        logger.info(f"← {response.status_code}")

    return StreamingResponse(
        stream(),
        status_code=response.status_code,
        headers=response.headers,
        media_type=response.media_type,
    )
class GrepResponse(BaseModel):
    """ Format of a search response """
    content: List[str] = Field(..., description="List of processed matches of pattern in codebase")
    processed: int = Field(..., description="Number of files processed")
    truncated: bool = Field(False, description="True if stopped early due to max_files")
    total_scanned: int = Field(0, description="Total .cs files found before limit")

class GrepRequest(BaseModel):
    """ Format of a search request """
    pattern: str = Field(..., description="Search term")
    folder_path: str | None = Field("/workspace/src", description="Path to folder containing .cs files")
    context_lines: int | None = Field(10, ge=1, le=1000)
    case_sensitive: bool | None = True

@app.post("/grep_request", response_model=GrepResponse, summary="Perform a grep search")
async def grep_request(data: GrepRequest = Body(...)):
    """
    Search the given folder path for a given pattern, or textual term.
    Use this tool when the user asks to 'use grep'.
    Use this tool whenever the user wants to find where something is defined or used.
    Use this tool whenever the user wants more context around the usage of a term or pattern.
    Use higher number of context lines in attempts to increase contextual knowledge.
    """
    folder = data.folder_path or "./"
    context = data.context_lines
    flags = ["-r", "-n"]
    pattern = "".join(ch for ch in data.pattern if ch.isprintable())

    if not data.case_sensitive:
        flags.append("-i")
    if data.context_lines > 0:
        flags.append("-C")
        flags.append(str(context))
    results = []
    logger.info(f"Calling grep_request with pattern: {pattern} in folder {folder}")
    # Ensure we search inside the correct folder
    if not os.path.isdir(folder):
        raise HTTPException(status_code=500, detail=f"Error: Directory not found: {folder}")

    try:
        cmd = ["egrep"] + flags + [pattern, "--", "."]
        result = subprocess.run(
            cmd, cwd=folder, capture_output=True, text=True, timeout=45
        )
        if result.returncode == 0 and result.stdout.strip():
            entirety = result.stdout.strip()
            for match in entirety.rsplit("--"):
                results.append(match.strip())
            return GrepResponse(
                content=results,
                processed=1,
                truncated=False,
                total_scanned=1
            )
        
        #result.stdout.strip()
        elif result.returncode == 1:
            raise HTTPException(status_code=501, detail=f"No matches found for '{pattern}'")
        else:
           raise HTTPException(status_code=502, detail=f"grep error ({result.returncode}):\n{result.stderr.strip()}")

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=503, detail=f"grep command timed out (45s limit)")
    except Exception as e:
        raise HTTPException(status_code=504, message=f"Unexpected error: {str(e)}")
    # return process_folder_bulk(
    #     folder_path=normalize_path(data.folder_path),
    #     context_lines=data.context_lines,
    #     case_sensitive=data.case_sensitive
    # )


# """
# name: Grep Code Search
# description: Search the entire project folder recursively with grep (shows file, line numbers and context)
# icon: https://img.icons8.com/search
# """

# class Tools:
#     def __init__(self):
#         self.valves = self.Valves()

#     class Valves(BaseModel):
#         folder_path: str = Field(
#             "/workspace/src",
#             description="Default path to the folder containing C# files",
#         )
#         pass

#     class UserValves(BaseModel):
#         # folder_path: str = Field(
#         #     default="/workspace/src",
#         #     description="Root directory to search (absolute path recommended)",
#         # )
#         context_lines: int = Field(
#             default=3,
#             description="Number of context lines shown before/after each match (-C flag)",
#         )
#         case_sensitive: bool = Field(
#             default=True, description="If False, adds -i flag (case-insensitive search)"
#         )
#         pass

#     def grep_search(
#         self, search_term: str, __user__: Dict[str, Any] | None = None
#     ) -> str:
#         """
#         Search the codebase using grep.
#         Use this tool whenever the user wants to find where something is defined or used.
#         """
#         user_valves = __user__["valves"]
#         folder = self.valves.folder_path.strip() or "."
#         context = user_valves.context_lines
#         flags = ["-r", "-n", "-C", str(context)]

#         if not user_valves.case_sensitive:
#             flags.append("-i")

#         # Ensure we search inside the correct folder
#         if not os.path.isdir(folder):
#             return f"Error: Directory not found: {folder}"

#         try:
#             cmd = ["grep"] + flags + [search_term, "."]
#             result = subprocess.run(
#                 cmd, cwd=folder, capture_output=True, text=True, timeout=45
#             )

#             if result.returncode == 0 and result.stdout.strip():
#                 return result.stdout.strip()
#             elif result.returncode == 1:
#                 return f"No matches found for '{search_term}'"
#             else:
#                 return f"grep error ({result.returncode}):\n{result.stderr.strip()}"

#         except subprocess.TimeoutExpired:
#             return "grep command timed out (45s limit)"
#         except Exception as e:
#             return f"Unexpected error: {str(e)}"
