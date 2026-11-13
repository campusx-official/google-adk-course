"""Prints every fact stored in your Memory Bank, grouped by user."""
import agentplatform

PROJECT = "adk-memory-project"
LOCATION = "us-central1"
MEMORY_BANK_ID = "8881425295005974528"

client = agentplatform.Client(project=PROJECT, location=LOCATION)
memories = client.memory_banks.memories.list(
    name=f"projects/{PROJECT}/locations/{LOCATION}/reasoningEngines/{MEMORY_BANK_ID}"
)

found = False
for memory in memories:
    found = True
    scope = memory.scope or {}
    print(f"[{scope.get('app_name')} / {scope.get('user_id')}]  {memory.fact}")
if not found:
    print("(no memories yet)")