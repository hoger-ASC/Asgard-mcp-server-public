import fnmatch
import os

import bs4
import requests
from langchain_core.documents import Document
from sentence_transformers import sentence_transformer
from PIL import Image

import httpx
from mcp.server.fastmcp import FastMCP
import ollama

mcp = FastMCP("ollama-server", host="127.0.0.1", port="8765")

@mcp.tool()
def search_files(pattern: str, root_dir: str = ".", max_results: int = 50) -> list[str]:
    """Search for files under root_dir whose name matches a glob pattern
    (e.g. '.py', 'config.json'). Returns matching file paths."""
    matches = []
    for dirpath, _, filenames in os.walk(root_dir):
        for name in filenames:
            if fnmatch.fnmatch(name, pattern):
                matches.append(os.path.join(dirpath, name))
                if len(matches) >= max_results:
                    return matches
    return matches


@mcp.tool()
def fetch_url(url: str, method: str = "GET", timeout: int = 10) -> str:
    """Fetch a URL (like curl) and return the response body as text.
    Only GET/HEAD are allowed for safety."""
    if method.upper() not in ("GET", "HEAD"):
        return "Error: only GET and HEAD are permitted."
    try:
        resp = httpx.request(method.upper(), url, timeout=timeout, follow_redirects=True)
        return f"Status: {resp.status_code}\n\n{resp.text[:5000]}"
    except httpx.RequestError as e:
        return f"Request failed: {e}"

@mcp.tool()
def read_text_file(file: str):
  """Read a text file in any format after finding it with search_files;
  Parameter file is the requested file"""
  with open(file, 'r') as data:
    contents = data.read()

@mcp.tool()
def search_knowledge_base(query):
    """nomic-embed based query function."""
    ollama.embeddings(model="nomic-embed-text", prompt=query)

@mcp.tool()
def embedImage(image_path: str) -> list[float]:
    """Convert an image into an embedding vector using CLIP"""
    img = image.open(image_path)
    embedding = clip_model.encode(img)
    return embedding.tolist()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
