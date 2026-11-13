"""Run this ONCE to create a Memory Bank. It prints the ID to put in .env."""
import os

import agentplatform
from dotenv import load_dotenv

load_dotenv("memory_agent/.env")

client = agentplatform.Client(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
)

memory_bank = client.memory_banks.create()   # takes a minute or two

print("Created:", memory_bank.name)
print("Add this line to memory_agent/.env:")
print("MEMORY_BANK_ID=" + memory_bank.name.split("/")[-1])