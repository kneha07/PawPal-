# Phase 3: UI and Backend Integration Guide

## Overview

Your **pawpal_system.py** backend is now fully integrated with the **Streamlit app.py** UI. When a user clicks a button in the browser, your Python classes actually respond!

---

## Step 1: Establishing the Connection ✅

### Imports
The first line in `app.py` now imports your backend classes:

```python
from pawpal_system import Task, Pet, Owner, Scheduler
```

This makes all four classes available in the Streamlit app.

---

## Step 2: Managing Application Memory with `st.session_state` ✅

### The Challenge: Streamlit Reruns
Streamlit reruns your entire script from top to bottom **every time** a user interacts with the app (clicks a button, types in a text box, etc.). Without special handling, any data created would be "reborn" empty on each rerun.

### The Solution: `st.session_state`
Think of `st.session_state` as a **persistent dictionary** that survives across reruns. It's your app's "memory vault."

### How We Initialize It

```python
# Initialize Streamlit session state for persistent data across reruns
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = {}  # Dictionary: pet_name -> Pet object
if "owner_name" not in st.session_state:
    st.session_state.owner_name = ""
if "available_minutes" not in st.session_state:
    st.session_state.available_minutes = 120
```

**Key Insight:** We check `if "owner" not in st.session_state` first. If it exists, we don't create a new one. This preserves data across reruns.

### Data Flow

```
1st Rerun (User Loads App)
├─ st.session_state is empty
├─ Initialize all keys with default values
└─ Display UI with no data

User Clicks "Create Owner"
├─ Button callback triggered
├─ st.session_state.owner = Owner(...)  ← Create new object
└─ RERUN: st.session_state.owner still exists! (not recreated)

User Clicks "Add Pet"
├─ Button callback triggered
├─ st.session_state.owner.add_pet(...)  ← Modify existing object
└─ RERUN: Both owner AND its pets are preserved!
```

---

## Step 3: Wiring UI Actions to Logic ✅

### Section 1: Owner Setup

**UI Code:**
```python
if st.button("✅ Create/Update Owner", key="create_owner_btn"):
    st.session_state.owner = Owner(
        name=owner_name, 
        available_minutes=available_minutes
    )
    st.success(f"✅ Owner '{owner_name}' created...")
```

**What Happens:**
1. User enters name and available time
2. Clicks button
3. UI creates an `Owner` object from `pawpal_system.py`
4. Stores it in `st.session_state.owner`
5. Success message displays

---

### Section 2: Pet Management

**UI Code:**
```python
if st.button("🐾 Add Pet", key="add_pet_btn"):
    if pet_name in st.session_state.pets:
        st.warning(f"⚠️ Pet '{pet_name}' already exists!")
    else:
        # Create Pet object using Phase 2 logic
        new_pet = Pet(name=pet_name, species=species, age=age)
        st.session_state.pets[pet_name] = new_pet
        st.session_state.owner.add_pet(new_pet)  # Add to owner
        st.success(f"✅ Pet '{pet_name}' added!")
```

**Method Calls:**
- `Pet(name, species, age)` — Dataclass constructor from `pawpal_system.py`
- `owner.add_pet(new_pet)` — Method from Phase 2 that appends pet to owner's list

**Data Storage:**
- Local dictionary: `st.session_state.pets[pet_name] = new_pet`
- Owner's internal list: `owner.pets` also updated

---

### Section 3: Task Management

**UI Code:**
```python
if st.button("➕ Add Task", key="add_task_btn"):
    if task_name.strip():
        # Create Task object using Phase 2 logic
        new_task = Task(
            name=task_name,
            duration_minutes=duration,
            priority=priority,
            recurring=recurring,
            recurrence_pattern="daily" if recurring else None
        )
        # Add to the selected pet
        st.session_state.pets[selected_pet].add_task(new_task)
        st.success(f"✅ Task '{task_name}' added to {selected_pet}!")
```

**Method Calls:**
- `Task(...)` — Dataclass constructor from `pawpal_system.py`
- `pet.add_task(new_task)` — Method from Phase 2 that appends task to pet's list

**Chain of Operations:**
```
UI Input → Task Object → Pet.add_task() → Task stored in pet.tasks
```

---

### Section 4: Schedule Generation

**UI Code:**
```python
if st.button("🎯 Generate Schedule", key="generate_schedule_btn"):
    scheduler = Scheduler(st.session_state.owner)
    
    # Check feasibility
    is_feasible = scheduler.is_feasible()
    all_tasks = st.session_state.owner.get_all_tasks()
    total_time = st.session_state.owner.get_total_required_minutes()
    
    # Generate optimized plan
    plan = scheduler.generate_plan()
```

**Method Calls (All from Phase 2):**
- `Scheduler(owner)` — Constructor takes the owner instance
- `scheduler.is_feasible()` — Returns boolean: can all tasks fit?
- `owner.get_all_tasks()` — Aggregates tasks from all pets
- `owner.get_total_required_minutes()` — Calculates total time needed
- `scheduler.generate_plan()` — Returns optimized task list
- `task.get_priority_label()` — Converts priority 1-5 to readable labels
- `scheduler.explain_plan(plan)` — Returns human-readable explanation

**Data Flow:**
```
Owner with Pets
    ↓
Scheduler receives Owner
    ↓
Collects all tasks via get_all_tasks()
    ↓
Checks feasibility & generates plan
    ↓
UI displays results with explain_plan()
```

---

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT APP (app.py)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Interaction                                           │
│  ┌────────────────────────────────┐                         │
│  │ Enter owner name               │  ← st.text_input()      │
│  │ Enter available time           │  ← st.number_input()    │
│  │ Click "Create Owner"           │  ← st.button()          │
│  └────────────────────────────────┘                         │
│            ↓                                                  │
│  st.session_state.owner = Owner(name, available_minutes)   │
│            ↓                                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ PAWPAL_SYSTEM.PY (Backend Logic)                        ││
│  ├─────────────────────────────────────────────────────────┤│
│  │ class Owner:                                            ││
│  │   +add_pet(pet)                                         ││
│  │   +get_all_tasks()                                      ││
│  │   +get_total_required_minutes()                         ││
│  ├─────────────────────────────────────────────────────────┤│
│  │ class Pet:                                              ││
│  │   +add_task(task)                                       ││
│  │   +get_daily_tasks()                                    ││
│  ├─────────────────────────────────────────────────────────┤│
│  │ class Task:                                             ││
│  │   +mark_complete()                                      ││
│  │   +get_priority_label()                                 ││
│  ├─────────────────────────────────────────────────────────┤│
│  │ class Scheduler:                                        ││
│  │   +generate_plan()                                      ││
│  │   +detect_conflicts()                                   ││
│  │   +explain_plan()                                       ││
│  └─────────────────────────────────────────────────────────┘│
│            ↑                                                  │
│  st.session_state.owner methods called by UI                │
│            ↑                                                  │
│  Results displayed via st.table(), st.info(), etc.          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Integration Points

### 1. **Persistence via `st.session_state`**
- Owner object persists across all page visits
- Pets dictionary preserves Pet objects
- No data loss on button clicks

### 2. **Direct Method Calls**
```python
# UI directly calls backend methods
owner.add_pet(new_pet)          # Phase 2 method
pet.add_task(new_task)          # Phase 2 method
scheduler.generate_plan()       # Phase 2 method
task.get_priority_label()       # Phase 2 method
```

### 3. **Object Aggregation**
- Single `Owner` object holds all `Pet` objects
- Each `Pet` holds all its `Task` objects
- `Scheduler` receives the complete `Owner` hierarchy

### 4. **Data Display**
- UI reads from live objects: `owner.pets`, `pet.tasks`
- Calls methods for formatted output: `task.get_priority_label()`
- Passes data to Streamlit components: `st.table()`, `st.info()`

---

## Running the App

### Start the Streamlit Server
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### What You Can Do
1. ✅ Create an owner with available time
2. ✅ Add multiple pets
3. ✅ Add tasks to each pet with priority levels
4. ✅ Generate optimized schedules
5. ✅ View conflict detection
6. ✅ Read scheduling explanations

---

## Session State Flow Example

```python
# Page Load (1st Run)
if "owner" not in st.session_state:
    st.session_state.owner = None  # Create slot

# User Creates Owner
st.session_state.owner = Owner("Sarah", 180)
# Session now contains: {"owner": Owner("Sarah", 180), ...}

# Page Reruns (due to any UI interaction)
# The `if "owner" not in st.session_state:` check finds it EXISTS
# So we DON'T recreate it, and the data persists!

# User Adds Pet
st.session_state.owner.add_pet(Pet("Max", "dog", 5))
# Session still contains the same owner, now with pets attached

# Page Reruns (again)
# Owner, pets, and tasks all still exist!
```

---

## Integration Verification

Run the integration test to verify everything works:
```bash
python3 test_ui_integration.py
```

This simulates the entire workflow without needing Streamlit running.

---

## Next Steps

Your app is now ready to use! The integration is complete:

✅ **Backend → UI:** Classes properly imported  
✅ **UI → Backend:** Session state persists objects  
✅ **Data Flow:** UI components wire directly to logic methods  
✅ **Verification:** Integration test proves it works  

Try running the Streamlit app with:
```bash
streamlit run app.py
```

Enjoy your fully functional PawPal+ system! 🐾
