# Deep_Research_LangChain
This is a GitHub Repository dedicated to create a Deep Research Agent using LangChain and Evaluating observability, Monitoring  and Tracking AI agent using LangSmith

Deep Research Agent Structure:

User >> [Request] >> Scope >> [Generates Brief] >> Research >> [Findings] >> Write >> [Report]
User << [Clarification] >> Scope >> [Generates Brief] >> Research >> [Findings] >> Write >> [Report]

- User & Scope entails a 2-way communication based on whether it's a request/clarification

Deep Research AI Agent is bifurcated into 5 stages:

Stage 1: User Clarification and Brief Generation

Concepts:
a. User Clarification: Identifies if any additional context is required from the user
b. Brief Generation: Detailed reserach questions generated from user conversations
c. LangGraph Commands: For flow control and state updates
d. Structured Output: Reliable and structured schemas for detailed reasoning

Stage 2: Research Agent with Custom Tools 

Concepts:
a. Agent Architecture: LLM Decision node + Tool Execution node
b. Sequential Tool Execution: Reliable and Multi Tool execution and usage
c. Search Integration: Web(Tavily) Search with Content summarization and comprehension
d. Tool Execution: AI Agent performing the right tool call

Stage 3:  Research Agent with MCP 

Concepts:
a. MCP (Model Context Protocol): Protocol used for tool access
b. MCP Architecture: Client and server communication via HTTP
c. LangChain MCP Adapters: LangChain Tools integration with MCP servers
d. Local vs Remote MCP: Different Transport Mechanisms

Stage 4: Deep Research Agent: Supervisor Agent

Concepts:
a. Supervisor Pattern: Main Agent + Worker Agents
b. Parallel Research: Simultaneous work conducted independently using tool calls
c. Research Delegation: Task Assignment based on structured tools
d. Context Isolation: Separate context windows for different tasks/activities

Stage 5:  Full Multi-Agent Research System

Concepts

a. Three-Phase Architecture: Scope >> Research >> Write
b. System Integration: Combination of Scope, Multi-Agent Research and Report Generation
c. State Management: Managing Different state flows using subgraphs
d. End-to-End Workflow: From User Input >> Report Generation

This 5 Stage Implementation Plan clearly defines all the steps required to build a Deep Research Agent as well as it's co-ordination with different servers, states and tools.
