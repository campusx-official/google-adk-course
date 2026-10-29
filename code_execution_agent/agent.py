from google.adk.agents.llm_agent import Agent
from google.adk.code_executors import BuiltInCodeExecutor

root_agent = Agent(
    model='gemini-3.5-flash',
    name='root_agent',
    description="A helpful assistant that can write and run Python code.",
    instruction=(
        "Answer user questions accurately. "
        "When a question involves calculations, data analysis, or anything "
        "that benefits from running code, write Python and execute it, "
        "then explain the result."
    ),
    code_executor=BuiltInCodeExecutor(),
)