## This file MCP Research Agent Workflow (Configurations, Agent Nodes & Edges and Compiled Workflow)
## Here, it is similar to the Research Agent Workflow only tools are bound using MCP Server Tools

"""Research Agent with MCP Integration.

This module implements a research agent that integrates with Model Context Protocol (MCP)
servers to access tools and resources. The agent demonstrates how to use MCP filesystem
server for local document research and analysis.

Key features:
- MCP server integration for tool access
- Async operations for concurrent tool execution (required by MCP protocol)
- Filesystem operations for local document research
- Secure directory access with permission checking
- Research compression for efficient processing
- Lazy MCP client initialization for LangGraph Platform compatibility
"""

import os, subprocess
from rich.console import Console
from typing_extensions import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, filter_messages
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END

from research_utils import format_messages
import asyncio
from langchain_core.messages import HumanMessage
from rich.markdown import Markdown

from deep_research_prompts.prompts import research_agent_prompt_with_mcp, compress_research_system_prompt, compress_research_human_message
from state_research import ResearcherState, ResearcherOutputState
from research_stage_prompt.prompts import get_today_str, think_tool, get_current_dir

## CONFIGURATION

## MCP server configuration for filesystem access
## The MCP Client Configuration requires Command, Arguments and Transport to be defined
## Command: Server executes locally as a process using the npx command

console = Console()

sample_docs_path = os.path.abspath("./deep_research_files/")
console.print(f"[bold blue]Sample docs path:[/bold blue] {sample_docs_path}")

if not os.path.exists(sample_docs_path):
    console.print("[red]✗ Directory does not exist![/red]")
else:
    console.print(f"[green]✓ Directory exists with files:[/green] {os.listdir(sample_docs_path)}")

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


mcp_config = {
    "filesystem": {
        "command": "npx.cmd",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", sample_docs_path],
        "transport": "stdio"
    }
}

## Global client variable - will be initialized lazily
_client = None

def get_mcp_client():
    """Get or initialize MCP client lazily to avoid issues with LangGraph Platform."""
    global _client
    if _client is None:
        _client = MultiServerMCPClient(mcp_config)
    return _client

## Initialize models
compress_model = init_chat_model(model="ollama:granite3.3:8b", max_tokens=32000)
model = init_chat_model(model="ollama:llama3.1:8b")

## AGENT NODES

async def llm_call(state: ResearcherState):
    """Analyze current state and decide on tool usage with MCP integration.

    This node:
    1. Retrieves available tools from MCP server
    2. Binds tools to the language model
    3. Processes user input and decides on tool usage

    Returns updated state with model response.
    """
    # Get available tools from MCP server
    client = get_mcp_client()
    mcp_tools = await client.get_tools()

    # Use MCP tools for local document access
    tools = mcp_tools + [think_tool]

    # Initialize model with tool binding
    model_with_tools = model.bind_tools(tools)

    # Process user input with system prompt
    return {
        "researcher_messages": [
            model_with_tools.invoke(
                [SystemMessage(content=research_agent_prompt_with_mcp.format(date=get_today_str()))] + state["researcher_messages"]
            )
        ]
    }

async def tool_node(state: ResearcherState):
    """Execute tool calls using MCP tools.

    This node:
    1. Retrieves current tool calls from the last message
    2. Executes all tool calls using async operations (required for MCP)
    3. Returns formatted tool results

    Note: MCP requires async operations due to inter-process communication
    with the MCP server subprocess. This is unavoidable.
    """
    tool_calls = state["researcher_messages"][-1].tool_calls

    async def execute_tools():
        """Execute all tool calls. MCP tools require async execution."""
        # Get fresh tool references from MCP server
        client = get_mcp_client()
        mcp_tools = await client.get_tools()
        tools = mcp_tools + [think_tool]
        tools_by_name = {tool.name: tool for tool in tools}

        # Execute tool calls (sequentially for reliability)
        observations = []
        for tool_call in tool_calls:
            tool = tools_by_name[tool_call["name"]]
            if tool_call["name"] == "think_tool":
                # think_tool is sync, use regular invoke
                observation = tool.invoke(tool_call["args"])
            else:
                # MCP tools are async, use ainvoke
                observation = await tool.ainvoke(tool_call["args"])
            observations.append(observation)

        # Format results as tool messages
        tool_outputs = [
            ToolMessage(
                content=observation,
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
            for observation, tool_call in zip(observations, tool_calls)
        ]

        return tool_outputs

    messages = await execute_tools()

    return {"researcher_messages": messages}

def compress_research(state: ResearcherState) -> dict:
    """Compress research findings into a concise summary.

    Takes all the research messages and tool outputs and creates
    a compressed summary suitable for further processing or reporting.

    This function filters out think_tool calls and focuses on substantive
    file-based research content from MCP tools.
    """
    
    system_message = compress_research_system_prompt.format(date=get_today_str())
    messages = [SystemMessage(content=system_message)] + state.get("researcher_messages", []) + [HumanMessage(content=compress_research_human_message)]

    response = compress_model.invoke(messages)

    # Extract raw notes from tool and AI messages
    raw_notes = [
        str(m.content) for m in filter_messages(
            state["researcher_messages"], 
            include_types=["tool", "ai"]
        )
    ]

    return {
        "compressed_research": str(response.content),
        "raw_notes": ["\n".join(raw_notes)]
    }

## ROUTING LOGIC

def should_continue(state: ResearcherState) -> Literal["tool_node", "compress_research"]:
    """Determine whether to continue with tool execution or compress research.

    Determines whether to continue with tool execution or compress research
    based on whether the LLM made tool calls.
    """
    messages = state["researcher_messages"]
    last_message = messages[-1]

    # Continue to tool execution if tools were called
    if last_message.tool_calls:
        return "tool_node"
    # Otherwise, compress research findings
    return "compress_research"

## GRAPH CONSTRUCTION: Agent Workflow

## Build the agent workflow
agent_builder_mcp = StateGraph(ResearcherState, output_schema=ResearcherOutputState)

## Add nodes to the graph
agent_builder_mcp.add_node("llm_call", llm_call)
agent_builder_mcp.add_node("tool_node", tool_node)
agent_builder_mcp.add_node("compress_research", compress_research)

## Add edges to connect nodes
agent_builder_mcp.add_edge(START, "llm_call")
agent_builder_mcp.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "tool_node": "tool_node",        # Continue to tool execution
        "compress_research": "compress_research",  # Compress research findings
    },
)
agent_builder_mcp.add_edge("tool_node", "llm_call")  # Loop back for more processing
agent_builder_mcp.add_edge("compress_research", END)

## Compile the agent
mcp_agent = agent_builder_mcp.compile()

## Invoke the agent

research_brief = """I want to identify and evaluate the coffee shops in Toronto that are considered the best based specifically  
on coffee quality. My research should focus on analyzing and comparing coffee shops within the Toronto area, 
using coffee quality as the primary criterion. I am open regarding methods of assessing coffee quality (e.g.,      
expert reviews, customer ratings, specialty coffee certifications), and there are no constraints on ambiance,      
location, wifi, or food options unless they directly impact perceived coffee quality. Please prioritize primary    
sources such as the official websites of coffee shops, reputable third-party coffee review organizations (like     
Coffee Review or Specialty Coffee Association), and prominent review aggregators like Google or Yelp where direct  
customer feedback about coffee quality can be found. The study should result in a well-supported list or ranking of
the top coffee shops in Toronto, emphasizing their coffee quality according to the latest available data as  
of July 2025."""

async def mcp_agent_output():
    result = await mcp_agent.ainvoke({"researcher_messages": [HumanMessage(content=f"{research_brief}.")]})
    format_messages(result['researcher_messages'])
    comp_markdn = Markdown(result["compressed_research"])
    console.print("[green]✓ Conpressed MarkDown:[/green]")
    console.print(comp_markdn)

if __name__ == "__main__":
    asyncio.run(mcp_agent_output())
