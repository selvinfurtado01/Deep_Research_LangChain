## This is a python file used to integrate all components of the research system (Scope, Research Brief, Multi-Agent System)
## Here, the final report will be generated using the compressed findings from the multi-agent system

"""
Full Multi-Agent Research System

This module integrates all components of the research system:
- User clarification and scoping
- Research brief generation  
- Multi-agent research coordination
- Final report generation

The system orchestrates the complete research workflow from initial user
input through final report delivery.
"""

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from research_stage_prompt.prompts import get_today_str
from deep_research_prompts.prompts import final_report_generation_prompt
from state_scope import AgentState, AgentInputState
from research_agent_scope import clarify_with_user, write_research_brief
from supervisor_multi_agent import supervisor_agent

## Model Configuration

from langchain.chat_models import init_chat_model
writer_model = init_chat_model(model="ollama:granite3.3:8b", max_tokens=32000)

## Final Report Generation

from state_scope import AgentState

async def final_report_generation(state: AgentState):
    """
    Final report generation node.
    
    Synthesizes all research findings into a comprehensive final report
    """
    
    notes = state.get("notes", [])
    
    findings = "\n".join(notes)

    final_report_prompt = final_report_generation_prompt.format(
        research_brief=state.get("research_brief", ""),
        findings=findings,
        date=get_today_str()
    )
    
    final_report = await writer_model.ainvoke([HumanMessage(content=final_report_prompt)])
    
    return {
        "final_report": final_report.content, 
        "messages": ["Here is the final report: " + final_report.content],
    }

## Complete Agent workflow
deep_researcher_builder = StateGraph(AgentState, input_schema=AgentInputState)

## Add agent nodes
deep_researcher_builder.add_node("clarify_with_user", clarify_with_user)
deep_researcher_builder.add_node("write_research_brief", write_research_brief)
deep_researcher_builder.add_node("supervisor_subgraph", supervisor_agent)
deep_researcher_builder.add_node("final_report_generation", final_report_generation)

## Add agent edges
deep_researcher_builder.add_edge(START, "clarify_with_user")
deep_researcher_builder.add_edge("write_research_brief", "supervisor_subgraph")
deep_researcher_builder.add_edge("supervisor_subgraph", "final_report_generation")
deep_researcher_builder.add_edge("final_report_generation", END)

## Compile the agent workflow
agent = deep_researcher_builder.compile()