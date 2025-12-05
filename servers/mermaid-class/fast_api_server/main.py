from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import StreamingResponse

from core import (
    BulkDiagramResponse,
    BatchCreateClassDiagramRequest,
    process_folder_bulk,
    normalize_path,
    logger
)

app = FastAPI(
    title="Mermaid Diagram API",
    version="1.0.0",
    description="Provides mermaid diagrams for C# class source code",
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

@app.post("/bulk_class_diagram", response_model=BulkDiagramResponse)
async def bulk_class_diagram(data: BatchCreateClassDiagramRequest = Body(...)):
    return process_folder_bulk(
        folder_path=normalize_path(data.folder_path),
        max_files=data.max_files,
        include_interfaces=data.include_interfaces,
        include_abstracts=data.include_abstracts,
    )

