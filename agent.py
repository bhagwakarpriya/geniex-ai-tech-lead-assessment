"""Orchestrator for the IT triage agent."""

import re
from config import client, MODEL, MAX_TOKENS, MAX_HISTORY_MESSAGES
from tools import TOOLS, execute_tool
from prompts import SYSTEM_PROMPT
from parser import parse_triage_response


def _prune_history(history_list):
    """Keep only the most recent messages to prevent context exhaustion."""
    if len(history_list) > MAX_HISTORY_MESSAGES:
        del history_list[:-MAX_HISTORY_MESSAGES]
    return history_list


def triage_ticket(ticket_text, ticket_id, conversation_history):
    """Process a single ticket through the triage loop."""

    conversation_history.append({"role": "user", "content": ticket_text})
    
    max_retrieval_score = 0.0

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=conversation_history,
    )

    # Tool execution loop
    while response.stop_reason == "tool_use":
        # Find the first available tool block
        tool_block = next((b for b in response.content if b.type == "tool_use"), None)
        if not tool_block:
            break

        tool_result = execute_tool(tool_block.name, tool_block.input)
        
        # Extract the score we injected into the tool output in retrieval.py
        score_match = re.search(r"MAX_RETRIEVAL_SCORE:\s*([\d.]+)", tool_result)
        if score_match:
            max_retrieval_score = float(score_match.group(1))

        conversation_history.append(
            {"role": "assistant", "content": response.content}
        )
        conversation_history.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": tool_result,
                    }
                ],
            }
        )

        _prune_history(conversation_history)

        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversation_history,
        )

    # Extract text from the final response
    text_blocks = [b.text for b in response.content if b.type == "text"]
    raw_response = " ".join(text_blocks) if text_blocks else ""
    
    conversation_history.append({"role": "assistant", "content": response.content})
    _prune_history(conversation_history)

    result = parse_triage_response(raw_response)
    
    # Logic: Flag for review if RAG score is low OR model self-reports low confidence
    is_low_retrieval = max_retrieval_score < 0.80
    model_is_unsure = result.get("confidence") == "LOW"
    
    result["needs_human_review"] = is_low_retrieval or model_is_unsure
    result["ticket_id"] = ticket_id

    return result
