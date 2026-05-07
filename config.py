"""Configuration for the IT Helpdesk Triage Agent."""

import anthropic

client = anthropic.Anthropic()

# Model settings
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1024

# Conversation management
MAX_HISTORY_MESSAGES = 10

# RAG retrieval settings
# Adjusted to 0.75 to resolve Error 619 retrieval failure
SIMILARITY_THRESHOLD = 0.75
RETRIEVAL_TOP_K = 3
