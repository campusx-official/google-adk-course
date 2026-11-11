from google.adk.agents import Agent
from google.adk.tools import ToolContext

# Single source of truth for the menu: used by the tools AND the instruction
MENU = {
    "paneer roll": {"price": 120, "veg": True},
    "veg sandwich": {"price": 90, "veg": True},
    "masala dosa": {"price": 100, "veg": True},
    "chicken roll": {"price": 150, "veg": False},
    "egg sandwich": {"price": 100, "veg": False},
    "cold coffee": {"price": 80, "veg": True},
}
DEFAULT_SPECIAL = "Masala dosa with free cold coffee"

# Menu text for the LLM, built from MENU (so prices are never written twice)
MENU_TEXT = "\n".join(
    f"- {item.title()} {info['price']} ({'veg' if info['veg'] else 'non-veg'})"
    for item, info in MENU.items()
)


# USER scope: facts about the customer, kept for every future order
def save_preference(name: str, diet: str, tool_context: ToolContext) -> dict:
    """Save the customer's name and diet ("veg" or "non-veg").
    Call this when the customer tells you their name or diet."""
    tool_context.state["user:name"] = name
    tool_context.state["user:diet"] = diet.lower()
    return {"status": "saved"}


# SESSION scope: this chat is one order
def add_to_order(item: str, tool_context: ToolContext) -> dict:
    """Add a menu item to the current order."""
    item = item.lower()
    if item not in MENU:
        return {"status": "error", "message": f"{item} is not on the menu."}
    order = tool_context.state.get("order", [])
    order = order + [item]                       # build a new list, then write it back
    tool_context.state["order"] = order
    total = sum(MENU[i]["price"] for i in order)
    return {"status": "added", "order": order, "total_inr": total}


# APP scope: the same for every customer
def get_todays_special(tool_context: ToolContext) -> dict:
    """Get today's special."""
    special = tool_context.state.get("app:todays_special")
    if special is None:
        special = DEFAULT_SPECIAL
        tool_context.state["app:todays_special"] = special   # seed once, for everyone
    return {"special": special}


root_agent = Agent(
    model="gemini-3.5-flash",
    name="cafe_agent",
    description="Takes food orders at CampusX Cafe.",
    instruction="""You are the order assistant at CampusX Cafe.

Menu (price in Rs):
""" + MENU_TEXT + """

Customer name: {user:name?}
Customer diet: {user:diet?}
Current order: {order?}
Today's special: {app:todays_special?}

- Greet the customer by name if you know it.
- When the customer shares their name or diet, call save_preference.
- When they want an item, call add_to_order.
- If today's special is unknown, call get_todays_special and mention it.
- Never suggest non-veg items to a veg customer.
Keep replies short.""",
    tools=[save_preference, add_to_order, get_todays_special],
)