"""Main entry point for batch IT helpdesk ticket triage.

Run with:
```
python main.py
```
"""

import json
import logging
from agent import triage_ticket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    
    tickets = [
        (
            "TKT-001",
            "My laptop won't connect to the VPN. I've tried restarting multiple times "
            "and keep getting error code 619. This started after the Windows update last night."
        ),
        (
            "TKT-002",
            "I need access to the Salesforce sandbox environment for UAT testing next week. "
            "My manager has approved this — ref: approval email from Sarah dated 12 Feb."
        ),
        (
            "TKT-003",
            "Excel keeps crashing whenever I open files larger than 10MB. "
            "Running Office 365, Windows 11. Started happening after I added a new add-in."
        ),
    ]

    results = {"succeeded": 0, "failed": 0, "errors": []}

    for ticket_id, ticket_text in tickets:
        try:
            print(f"\nProcessing {ticket_id}...")
            
            # FIX: Fresh history per ticket
            conversation_history = []
            
            result = triage_ticket(ticket_text, ticket_id, conversation_history)
            
            print(json.dumps(result, indent=2))
            results["succeeded"] += 1
            
        except Exception as e:
            logger.error(f"Failed to process {ticket_id}: {e}")
            results["failed"] += 1
            results["errors"].append({"ticket_id": ticket_id, "error": str(e)})

    print(f"\nBatch complete: {results['succeeded']} succeeded, {results['failed']} failed")


if __name__ == "__main__":
    main()
