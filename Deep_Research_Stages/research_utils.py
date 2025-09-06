## Utils Notebook

## This python file is defined for message format and prompt format for better usability
## This python file is then referenced to use these functions for the Deep Research Stages

## Define Necessary Modules

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import json
from datetime import datetime

console = Console()

def safe_format_datetime(dt: datetime) -> str:
    """
    Cross-platform safe datetime formatting.
    Example: "Fri Sep 5, 2025 14:32:10"
    """
    try:
        # works on Linux/macOS; on Windows replace %-d with %#d
        return dt.strftime("%a %b %-d, %Y")
    except ValueError:
        # fallback for Windows
        return dt.strftime("%a %b %#d, %Y")

def format_message_content(message):
    """Convert message content to displayable string"""
    parts = []
    tool_calls_processed = False

    # Handle main content
    if isinstance(message.content, str):
        parts.append(message.content)
    elif isinstance(message.content, list):
        # Handle complex content like tool calls (Anthropic format)
        for item in message.content:
            if item.get('type') == 'text':
                parts.append(item['text'])
            elif item.get('type') == 'tool_use':
                # normalize datetime args if they exist
                clean_input = {
                    k: (safe_format_datetime(v) if isinstance(v, datetime) else v)
                    for k, v in item['input'].items()
                }
                parts.append(f"\n🔧 Tool Call: {item['name']}")
                parts.append(f"   Args: {json.dumps(clean_input, indent=2, default=str)}")
                parts.append(f"   ID: {item.get('id', 'N/A')}")
                tool_calls_processed = True
    else:
        # if content is a datetime, format it safely
        if isinstance(message.content, datetime):
            parts.append(safe_format_datetime(message.content))
        else:
            parts.append(str(message.content))

    # Handle tool calls attached to the message (OpenAI format) - only if not already processed
    if not tool_calls_processed and hasattr(message, 'tool_calls') and message.tool_calls:
        for tool_call in message.tool_calls:
            clean_args = {
                k: (safe_format_datetime(v) if isinstance(v, datetime) else v)
                for k, v in tool_call['args'].items()
            }
            parts.append(f"\n🔧 Tool Call: {tool_call['name']}")
            parts.append(f"   Args: {json.dumps(clean_args, indent=2, default=str)}")
            parts.append(f"   ID: {tool_call['id']}")

    return "\n".join(parts)

def format_messages(messages):
    """Format and display a list of messages with Rich formatting"""
    for m in messages:
        msg_type = m.__class__.__name__.replace('Message', '')
        content = format_message_content(m)

        if msg_type == 'Human':
            console.print(Panel(content, title="🧑 Human", border_style="blue"))
        elif msg_type == 'Ai':
            console.print(Panel(content, title="🤖 Assistant", border_style="green"))
        elif msg_type == 'Tool':
            console.print(Panel(content, title="🔧 Tool Output", border_style="yellow"))
        else:
            console.print(Panel(content, title=f"📝 {msg_type}", border_style="white"))

def format_message(messages):
    """Alias for format_messages for backward compatibility"""
    return format_messages(messages)

def show_prompt(prompt_text: str, title: str = "Prompt", border_style: str = "blue"):
    """
    Display a prompt with rich formatting and XML tag highlighting.
    
    Args:
        prompt_text: The prompt string to display
        title: Title for the panel (default: "Prompt")
        border_style: Border color style (default: "blue")
    """
    formatted_text = Text(prompt_text)
    formatted_text.highlight_regex(r'<[^>]+>', style="bold blue")   # Highlight XML tags
    formatted_text.highlight_regex(r'##[^#\n]+', style="bold magenta")  # Highlight headers
    formatted_text.highlight_regex(r'###[^#\n]+', style="bold cyan")    # Highlight sub-headers

    console.print(Panel(
        formatted_text,
        title=f"[bold green]{title}[/bold green]",
        border_style=border_style,
        padding=(1, 2)
    ))
