"""Deletes memories from your Memory Bank.

Set USER_ID to delete one user's memories, or None to delete everything.
"""
import agentplatform

PROJECT = "adk-memory-project"
LOCATION = "us-central1"
MEMORY_BANK_ID = "8881425295005974528"

USER_ID = None          # e.g. "user" or "nitish"; None = every user

client = agentplatform.Client(project=PROJECT, location=LOCATION)
bank = f"projects/{PROJECT}/locations/{LOCATION}/reasoningEngines/{MEMORY_BANK_ID}"

deleted = 0
for memory in client.memory_banks.memories.list(name=bank):
    scope = memory.scope or {}
    if USER_ID is not None and scope.get("user_id") != USER_ID:
        continue
    client.memory_banks.memories.delete(name=memory.name)
    print(f"deleted [{scope.get('app_name')} / {scope.get('user_id')}]  {memory.fact}")
    deleted += 1

print(f"\n{deleted} memories deleted.")