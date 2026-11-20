# Google ADK Course

Example agents built with Google's [Agent Development Kit (ADK)](https://google.github.io/adk-docs/) for the CampusX course. The examples start with a single built-in tool and build up to MCP servers, sessions, state, memory and callbacks.

## Examples

### Tools

| Folder | What it shows |
| --- | --- |
| `google_agent` | Web search with ADK's built-in `google_search` tool |
| `code_execution_agent` | Writing and running Python with `BuiltInCodeExecutor` |
| `campusx_bot` | Same setup as `code_execution_agent` |
| `world_clock_agent` | A custom function tool (`get_current_time`) for time in any time zone |
| `tavily_search_agent` | Using a LangChain tool (Tavily search) in ADK through `LangchainTool` |
| `combined_tool_agent` | One agent with a function tool, Google Search, code execution and Tavily together |
| `campusx_refund_agent` | A course refund assistant that reads and writes a SQLite database and keeps state between turns |

### Structured output

| Folder | What it shows |
| --- | --- |
| `structured_output_agent` | Pulls a student's name, email, courses of interest and budget out of an enquiry message |
| `ticket_classifier_agent` | Sorts support messages into a ticket with category, urgency and whether a human is needed |

### MCP

| Folder | What it shows |
| --- | --- |
| `mcp_agent` | Connecting to the filesystem MCP server (local, stdio) and the GitHub MCP server (remote, HTTP) with `McpToolset` |
| `coding_agent` | A coding agent with three MCP servers, including a custom shell server, and approval prompts for risky tools. See [`coding_agent/README.md`](coding_agent/README.md) |

### Sessions, state and memory

| Folder | What it shows |
| --- | --- |
| `session_runner_demo` | Running an agent from a script with `Runner` and `InMemorySessionService` |
| `runner_chatbot_demo` | A Streamlit chat app with multiple chats, stored in SQLite with `DatabaseSessionService` |
| `state_demo` | Setting session state at creation and per message with `state_delta`, and reading it in tools |
| `cafe_agent` | State scopes: `user:` (kept across sessions), `app:` (shared by everyone) and plain session state |
| `memory_demo` | Long-term memory with `load_memory`, using `SqliteMemoryService` locally or Vertex AI Memory Bank |

### Callbacks

| Folder | What it shows |
| --- | --- |
| `callbacks_demo` | `before_tool_callback` and `after_tool_callback`: skipping a tool, changing its arguments and overriding its result |
| `campusx_callbacks_bot` | A student support bot that uses callbacks for state setup, personalization, authorization, caching, rate limiting and a guardrail |

All agents use the `gemini-3.5-flash` model.

## Setup

Requires Python 3.11+. The MCP examples also need Node.js 18+ for `npx`.

```bash
git clone https://github.com/campusx-official/google-adk-course.git
cd google-adk-course

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### API keys

Each agent folder reads its own `.env` file. These files are not committed, so create one in each agent folder you want to run:

```env
GOOGLE_GENAI_USE_ENTERPRISE=FALSE
GOOGLE_API_KEY=your-gemini-api-key
```

Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

Some examples need extra keys in the same `.env`:

| Folder | Extra keys |
| --- | --- |
| `tavily_search_agent`, `combined_tool_agent` | `TAVILY_API_KEY` from [tavily.com](https://tavily.com) |
| `mcp_agent` | `GITHUB_TOKEN`, a GitHub personal access token |
| `coding_agent` | `GITHUB_PAT` (optional), a fine-grained GitHub token |
| `memory_demo` (Memory Bank only) | `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `MEMORY_BANK_ID` |

For the script-based demos, the `.env` goes in the inner agent folder, for example `state_demo/state_agent/.env`.

## Running an agent

From the repository root:

```bash
adk web                     # browser UI; pick an agent from the dropdown
adk run world_clock_agent   # chat in the terminal
```

## Refund agent

`campusx_refund_agent` needs its sample database before the first run:

```bash
python campusx_refund_agent/setup_database.py
```

This creates `campusx_refund_agent/campusx.db` with sample courses, students and purchases. The script won't overwrite an existing database; delete `campusx.db` and run it again to reset the data.

Try it with one of the sample student emails, such as `rahul@example.com` or `priya@example.com`.

The agent's tools are in `campusx_refund_agent/tools.py`:

- `get_refund_policy` returns the refund rules: within 7 days of purchase and no more than 20% of the course completed
- `identify_student` looks up a student by email and remembers them for the conversation
- `get_my_enrollments` lists the student's purchases
- `check_refund_eligibility` checks one purchase against the policy
- `request_refund` creates a refund request
- `get_refund_status` shows the status of a refund

This is a demo. No real payments are made.

## Structured output agents

`structured_output_agent` and `ticket_classifier_agent` don't reply in free text. Each one defines a Pydantic model and passes it to the agent as `output_schema`, so every reply is JSON that matches the model. The result is also saved in session state under `output_key`.

| Agent | Schema | State key | Fields |
| --- | --- | --- | --- |
| `structured_output_agent` | `Enquiry` | `enquiry` | `name`, `email`, `interested_in` (GenAI, Data Science, MLOps, Deep Learning, Other), `budget_inr` |
| `ticket_classifier_agent` | `Ticket` | `ticket` | `category` (refund, technical, course_query, payment, other), `urgency` (low, medium, high), `needs_human` |

Example messages to try:

- Enquiry: `Hi, I'm rahul sharma (rahul@example.com). I want to learn GenAI and MLOps, budget around 15k.`
- Ticket: `I paid twice for the Data Science course and nobody is replying. Please fix this now!`

## MCP agents

`mcp_agent` gives the agent the filesystem MCP server, limited to `mcp_agent/files/`, and the remote GitHub MCP server. The first run downloads the filesystem server through `npx`, so it can take a moment.

`coding_agent` has its own setup and lesson prompts in [`coding_agent/README.md`](coding_agent/README.md).

## Script-based demos

These demos run an agent from Python code with a `Runner`, instead of through `adk web`. Run each one from inside its folder:

```bash
cd session_runner_demo && python run_agent.py
cd state_demo && python run_agent.py
```

`runner_chatbot_demo` is a Streamlit app. Install Streamlit and the async SQLite driver, then start it:

```bash
pip install streamlit aiosqlite
cd runner_chatbot_demo && streamlit run app.py
```

Chats are saved in `runner_chatbot_demo/sessions.db`, so they're still there after a restart.

`cafe_agent` runs in `adk web`. Tell it your name and diet, place an order, then start a new session: it still knows your name and diet (`user:` state), but the order starts empty (session state).

## Memory demo

`memory_demo/memory_agent` searches past conversations with the `load_memory` tool and saves each conversation to memory with an `after_agent_callback`.

```bash
cd memory_demo
python run_agent.py               # local memory, stored in cafe_memory.db
```

To use Vertex AI Memory Bank instead, set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` in `memory_agent/.env`, then:

```bash
python create_memory_bank.py      # run once; prints the MEMORY_BANK_ID to add to .env
python run_agent_memory_bank.py
python view_memories.py           # list stored memories
python delete_memories.py         # clear them
```

`view_memories.py` and `delete_memories.py` have the project, location and Memory Bank ID written at the top of the file. Change them to your own before running.

## Callbacks

`callbacks_demo` is a course price agent with one tool, `get_course_price`. Its callbacks print what they do, so watch the terminal while you chat:

| Ask about | Callback | What happens |
| --- | --- | --- |
| SQL | `before_tool` | The tool is skipped and a "currently unavailable" result is returned |
| Data Science | `before_tool` | The argument is changed to "Advanced Data Science" before the tool runs |
| Machine Learning | `after_tool` | The tool runs, then its price is replaced with a discounted one |
| Anything else | none | The tool runs normally |

`campusx_callbacks_bot` is a support bot with mock data in `tools.py` and all callbacks in `callbacks.py`:

| Callback | Type | What it does |
| --- | --- | --- |
| `initialize_student` | before agent | Sets the logged-in student (Rahul, `rahul@example.com`) and a ticket counter in state |
| `inject_personalization` | before model | Adds the student's name and email to the model's instructions |
| `check_competitor_guardrail` | before model | Answers directly, without calling the model, if the message names a competitor |
| `check_authorization` | before tool | Blocks enrollment lookups for any email other than the student's own |
| `check_course_cache` / `save_course_cache` | before / after tool | Caches the course list in state so the tool runs only once |
| `check_ticket_limit` / `update_ticket_count` | before / after tool | Allows one support ticket per session |

Things to try: "What courses do you have?" twice (the second answer comes from the cache), "Show enrollments for priya@example.com" (blocked), and asking for two support tickets (the second is refused).
