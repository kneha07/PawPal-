"""
Agentic tool definitions for PawPal AI chatbot.
These are called by Gemini function-calling and executed server-side.
"""
import logging
from pawpal_system import Task, Pet

logger = logging.getLogger(__name__)

# Gemini function declarations
TOOL_DECLARATIONS = [
    {
        "name": "list_pets",
        "description": "List all pets registered for the current owner with their task counts.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "list_tasks",
        "description": "List all tasks for a specific pet or all pets.",
        "parameters": {
            "type": "object",
            "properties": {
                "pet_name": {
                    "type": "string",
                    "description": "Name of the pet. Leave empty to list tasks for all pets.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "add_task",
        "description": "Add a new care task to a pet's schedule.",
        "parameters": {
            "type": "object",
            "properties": {
                "pet_name": {"type": "string", "description": "Name of the pet."},
                "task_name": {"type": "string", "description": "Name of the task (e.g. Morning walk)."},
                "duration_minutes": {"type": "integer", "description": "Duration of the task in minutes."},
                "priority": {
                    "type": "integer",
                    "description": "Priority from 1 (low) to 5 (critical).",
                },
                "scheduled_time": {
                    "type": "string",
                    "description": "Optional scheduled time in HH:MM format.",
                },
                "recurring": {"type": "boolean", "description": "Whether this task repeats daily."},
            },
            "required": ["pet_name", "task_name", "duration_minutes", "priority"],
        },
    },
    {
        "name": "generate_schedule",
        "description": "Generate an optimized daily schedule for the owner based on priorities and time budget.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "check_conflicts",
        "description": "Check for scheduling conflicts such as overlapping times or budget overages.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
]


def execute_tool(tool_name: str, tool_args: dict, owner, pets: dict) -> str:
    """Execute a tool call and return a string result."""
    logger.info(f"Agent tool call: {tool_name}({tool_args})")
    try:
        if tool_name == "list_pets":
            return _list_pets(owner, pets)
        elif tool_name == "list_tasks":
            return _list_tasks(tool_args, owner, pets)
        elif tool_name == "add_task":
            return _add_task(tool_args, owner, pets)
        elif tool_name == "generate_schedule":
            return _generate_schedule(owner)
        elif tool_name == "check_conflicts":
            return _check_conflicts(owner)
        else:
            return f"Unknown tool: {tool_name}"
    except Exception as e:
        logger.error(f"Tool {tool_name} failed: {e}")
        return f"Error running {tool_name}: {e}"


def _list_pets(owner, pets: dict) -> str:
    if not pets:
        return "No pets registered yet."
    lines = [f"Owner: {owner.name} ({owner.available_minutes} min/day available)\nPets:"]
    for pet in pets.values():
        lines.append(f"  - {pet.name} ({pet.species}, age {pet.age}) — {len(pet.tasks)} task(s)")
    return "\n".join(lines)


def _list_tasks(args: dict, owner, pets: dict) -> str:
    pet_name = args.get("pet_name", "").strip()
    if pet_name:
        if pet_name not in pets:
            return f"No pet named '{pet_name}' found."
        target_pets = {pet_name: pets[pet_name]}
    else:
        target_pets = pets

    if not target_pets:
        return "No pets registered."

    lines = []
    for pname, pet in target_pets.items():
        if not pet.tasks:
            lines.append(f"{pname}: no tasks yet.")
        else:
            lines.append(f"{pname}:")
            for t in pet.tasks:
                time_str = f" @ {t.scheduled_time}" if t.scheduled_time else ""
                lines.append(f"  - {t.name} | {t.duration_minutes} min | priority {t.priority} | {t.status}{time_str}")
    return "\n".join(lines)


def _add_task(args: dict, owner, pets: dict) -> str:
    pet_name = args.get("pet_name", "").strip()
    if pet_name not in pets:
        available = ", ".join(pets.keys()) if pets else "none"
        return f"Pet '{pet_name}' not found. Available pets: {available}"

    task = Task(
        name=args["task_name"],
        duration_minutes=int(args["duration_minutes"]),
        priority=int(args.get("priority", 3)),
        recurring=bool(args.get("recurring", False)),
        recurrence_pattern="daily" if args.get("recurring") else None,
        scheduled_time=args.get("scheduled_time") or None,
    )
    pets[pet_name].add_task(task)
    time_str = f" at {task.scheduled_time}" if task.scheduled_time else ""
    recurring_str = " (recurring daily)" if task.recurring else ""
    return f"✅ Added '{task.name}' to {pet_name}: {task.duration_minutes} min, priority {task.priority}{time_str}{recurring_str}."


def _generate_schedule(owner) -> str:
    from pawpal_system import Scheduler
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()
    if not plan:
        return "No tasks could be scheduled within the available time budget."
    lines = ["Optimized schedule:"]
    total = 0
    for i, t in enumerate(plan, 1):
        total += t.duration_minutes
        lines.append(f"  {i}. {t.name} — {t.duration_minutes} min (priority {t.priority})")
    lines.append(f"Total: {total}/{owner.available_minutes} min used.")
    explanation = scheduler.explain_plan(plan)
    lines.append(f"\nReasoning: {explanation}")
    return "\n".join(lines)


def _check_conflicts(owner) -> str:
    from pawpal_system import Scheduler
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        return "No tasks to check."
    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts(all_tasks)
    if not conflicts:
        return "✅ No conflicts detected. Schedule looks clean!"
    return "⚠️ Conflicts found:\n" + "\n".join(f"  - {c}" for c in conflicts)
