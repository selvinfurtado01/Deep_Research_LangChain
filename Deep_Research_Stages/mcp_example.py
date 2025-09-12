## MCP Example
## Install Langchain adapters module: ! pip install langchain_mcp_adapters

import subprocess, os
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

## Path to your local docs
sample_docs_path = os.path.abspath("./deep_research_files/")
console.print(f"[bold blue]Sample docs path:[/bold blue] {sample_docs_path}")

if not os.path.exists(sample_docs_path):
    console.print("[red]✗ Directory does not exist![/red]")
else:
    console.print(f"[green]✓ Directory exists with files:[/green] {os.listdir(sample_docs_path)}")

## Start MCP server as a subprocess
console.print(Panel("[bold yellow]Starting MCP server...[/bold yellow]", expand=False))

server_proc = subprocess.Popen([
    "npx.cmd", "-y", "@modelcontextprotocol/server-filesystem",
    sample_docs_path,
], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


print("Line-Error Debugging")
## Print logs for debugging
for i in range(1):
    print(f"Line: {i}")
    line = server_proc.stderr.readline()
    print(f"Line: {line}")
    if not line:
        break
    print("[MCP Server]", line.decode().strip())

print("Debugging Completed")


## Configure MCP client to connect over WebSocket
mcp_config = {
    "filesystem": {
        "command": "npx.cmd",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", sample_docs_path],
        "transport": "stdio"
    }
}

client = MultiServerMCPClient(mcp_config)
console.print("[green]✓ MCP server process started![/green]")

## Wrap async code for Notebook
async def run_client():
    console.print(Panel("[bold yellow]Getting tools...[/bold yellow]", expand=False))
    tools = await client.get_tools()

    ## Create table of tools
    table = Table(title="Available MCP Tools", show_header=True, header_style="bold magenta")
    table.add_column("Tool Name", style="cyan", width=25)
    table.add_column("Description", style="white", width=80)

    for tool in tools:
        desc = tool.description[:77] + "..." if len(tool.description) > 80 else tool.description
        table.add_row(tool.name, desc)

    console.print(table)
    console.print(f"[bold green]✓ Retrieved {len(tools)} tools from MCP server[/bold green]")

## Run inside Jupyter event loop
if __name__ == "__main__":
    asyncio.run(run_client())