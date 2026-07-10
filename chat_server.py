import asyncio
from contextlib import asynccontextmanager

import ollama
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_SERVER_URL = "http://127.0.0.1:8765/mcp"
DEFAULT_MODEL = "PASTE-OLLAMA-MODEL-HERE"
MAX_TOOL_ITERATIONS = 7


mcp_session: ClientSession | None = None
mcp_tools_ollama_format: list[dict] = []


def mcp_tool_to_ollama_schema(tool) -> dict:
    """Convert an MCP tool definition into the JSON schema Ollama expects."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mcp_session, mcp_tools_ollama_format
    async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            mcp_tools_ollama_format = [mcp_tool_to_ollama_schema(t) for t in tools_result.tools]
            mcp_session = session
            print(f"Connected to MCP server. Tools available: {[t.name for t in tools_result.tools]}")
            yield
    mcp_session = None


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["self"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    model: str = DEFAULT_MODEL


class ChatResponse(BaseModel):
    reply: str
    history: list[dict] = []
    tool_calls: list[str] = []


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if mcp_session is None:
        return ChatResponse(reply="Error: not connected to MCP server.")
# Continue client's history
    messages = list(req.history) + [{"role": "user", "content": req.message}]
    tool_call_log: list[str] = []

    for _ in range(MAX_TOOL_ITERATIONS):
        response = ollama.chat(
            model=req.model,
            messages=messages,
            tools=mcp_tools_ollama_format,
            options={"num_predict": 2048}
        )
        msg = response["message"]
        messages.append(msg.model_dump() if hasattr(msg, "model_dump") else msg)

        tool_calls = msg.get("tool_calls")
        if not tool_calls:
            clean_history = [m for m in messages if m.get("role") in ("user", "assistant") and not m.get("tool_calls")]
            return ChatResponse(reply=msg["content"], tool_calls=tool_call_log, history=clean_history)

        for call in tool_calls:
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            tool_call_log.append(f"{name}({args})")

            result = await mcp_session.call_tool(name, args)
            result_text = "\n".join(
                block.text for block in result.content if hasattr(block, "text")
            )

            messages.append({
                "role": "tool",
                "content": result_text,
                "name": name,
            })
    clean_history = [m for m in messages if m.get("role") in ("user", "assistant") and not m.get("tool_calls")]
    return ChatResponse(
        reply="Tool-call limit reached without a final answer.",
        tool_calls=tool_call_log,
        history=clean_history
    )


app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
