import httpx
from fastmcp import FastMCP

# ----------------------------------------------------------------------
# Server definition
# ----------------------------------------------------------------------
# Use the service name from docker-compose as hostname
client = httpx.AsyncClient(base_url="http://mermaid-openapi:8000")

# Load the OpenAPI spec synchronously once
openapi_spec = httpx.get("http://mermaid-openapi:8000/openapi.json").json()

# Create the MCP server
server = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="My API Server"
)

if __name__ == "__main__":
    server.run(transport="http", host="0.0.0.0", port=8000)
