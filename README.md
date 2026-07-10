# **"Asgard" MCP server - public FOSS version**


### <u>Overview</u>
A modular web-http based  <b>*MCP + webapp(uvicorn/fastAPI) + ollama agent*</b> stack written in python; Frontend/ Javascript written by Claude™5[*]

## Usage
After install activate a python virtual environment in the repository root, then open two terminals and run in one line for each in order:
```bash
python server.py
python chat_server.py
```
Afterwards, open localhost:8000 in browser to access the interface.

## <u>Tooling and General Capabilities</u>
The base tooling content of is bulky and still in development and testing; If using this app, you may simply exclude the
unnecesarry libraries and remove the tool's code; It includes:
- search_files
- fetch_url
- read_text_file
- search_knowledge_base
- embedImage

### <p align="center">Footnotes</p>
[*] - Provisional code;

<p>For now, this tool is designed as localhost only; Do not expose it to the world-wide-web.</p>
If you wish to contribute to this Open-Source project, or if you have bug reports or questions please contact me.
