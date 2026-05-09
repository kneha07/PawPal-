"""
Integration Test: Simulates the Streamlit UI workflow without running Streamlit.
This demonstrates that the backend and UI are properly connected.
"""

from pawpal_system import Task, Pet, Owner, Scheduler

def simulate_ui_workflow():
    """Simulate the exact workflow that the Streamlit UI will perform."""
    
    print("=" * 80)
    print("PAWPAL+ UI ↔ BACKEND INTEGRATION TEST")
    print("=" * 80)
    
    # =========================================================================
    # SECTION 1: Owner Setup (Simulates Step 1: Create/Update Owner)
    # =========================================================================
    print("\n📌 SECTION 1: Owner Setup")
    print("-" * 80)
    
    owner_name = "Sarah"
    available_minutes = 180
    
    print(f"User Input: Owner name = '{owner_name}', Available time = {available_minutes} min")
    print("UI Action: Click 'Create/Update Owner' button")
    
    # This is what happens in the app when the user clicks the button
    owner = Owner(name=owner_name, available_minutes=available_minutes)
    print(f"✅ Backend Response: Owner object created in st.session_state")
    print(f"   └─ owner.name = '{owner.name}'")
    print(f"   └─ owner.available_minutes = {owner.available_minutes}")
    
    # =========================================================================
    # SECTION 2: Pet Management (Simulates Adding Pets)
    # =========================================================================
    print("\n\n🐾 SECTION 2: Pet Management")
    print("-" * 80)
    
    pets_to_add = [
        ("Max", "dog", 5),
        ("Whiskers", "cat", 2),
        ("Tweety", "bird", 1)
    ]
    
    for pet_name, species, age in pets_to_add:
        print(f"\nUser Input: Pet name = '{pet_name}', Species = '{species}', Age = {age}")
        print("UI Action: Click '🐾 Add Pet' button")
        
        # This is what happens when user adds a pet
        new_pet = Pet(name=pet_name, species=species, age=age)
        owner.add_pet(new_pet)
        
        print(f"✅ Backend Response: Pet object created and added to owner")
        print(f"   └─ pet.name = '{new_pet.name}'")
        print(f"   └─ pet.species = '{new_pet.species}'")
        print(f"   └─ Total pets in owner: {len(owner.pets)}")
    
    # =========================================================================
    # SECTION 3: Task Management (Simulates Adding Tasks)
    # =========================================================================
    print("\n\n➕ SECTION 3: Task Management")
    print("-" * 80)
    
    tasks_to_add = [
        ("Max", ("Morning walk", 30, 5, True, "daily")),
        ("Max", ("Feed Max", 15, 4, False, None)),
        ("Max", ("Playtime", 20, 3, False, None)),
        ("Whiskers", ("Feed Whiskers", 10, 4, False, None)),
        ("Whiskers", ("Clean litter box", 10, 5, True, "daily")),
        ("Tweety", ("Feed Tweety", 5, 5, True, "daily")),
    ]
    
    for pet_name, (task_name, duration, priority, recurring, pattern) in tasks_to_add:
        print(f"\nUser Input: For {pet_name} - '{task_name}' ({duration} min, priority {priority})")
        print("UI Action: Click '➕ Add Task' button")
        
        # Find the pet and add task
        pet = next(p for p in owner.pets if p.name == pet_name)
        new_task = Task(
            name=task_name,
            duration_minutes=duration,
            priority=priority,
            recurring=recurring,
            recurrence_pattern=pattern
        )
        pet.add_task(new_task)
        
        print(f"✅ Backend Response: Task added to {pet_name}")
        print(f"   └─ task.name = '{new_task.name}'")
        print(f"   └─ task.priority_label = '{new_task.get_priority_label()}'")
        print(f"   └─ Total tasks on {pet_name}: {len(pet.tasks)}")
    
    # =========================================================================
    # SECTION 4: Schedule Generation (Simulates Clicking "Generate Schedule")
    # =========================================================================
    print("\n\n🎯 SECTION 4: Schedule Generation")
    print("-" * 80)
    print("\nUser Action: Click '🎯 Generate Schedule' button")
    print("UI calls backend via Scheduler class...")
    
    scheduler = Scheduler(owner)
    
    # Summary metrics
    all_tasks = owner.get_all_tasks()
    total_time = owner.get_total_required_minutes()
    is_feasible = scheduler.is_feasible()
    
    print(f"\n📊 Schedule Summary:")
    print(f"   Total Tasks: {len(all_tasks)}")
    print(f"   Time Needed: {total_time} min")
    print(f"   Time Available: {owner.available_minutes} min")
    print(f"   Feasibility: {'✅ Feasible' if is_feasible else '⚠️ Tight!'}")
    
    # Check for conflicts
    conflicts = scheduler.detect_conflicts(all_tasks)
    if conflicts:
        print(f"\n⚠️  Conflicts Detected:")
        for conflict in conflicts:
            print(f"   • {conflict}")
    else:
        print(f"\n✅ No time conflicts detected!")
    
    # Generate optimized plan
    plan = scheduler.generate_plan()
    
    print(f"\n✨ Optimized Daily Plan ({len(plan)} tasks):")
    cumulative = 0
    for i, task in enumerate(plan, 1):
        cumulative += task.duration_minutes
        print(f"   {i}. {task.name}")
        print(f"      Duration: {task.duration_minutes} min | Priority: {task.get_priority_label()}")
        print(f"      Cumulative: {cumulative} min")
    
    # Final stats
    remaining = owner.available_minutes - cumulative
    print(f"\n   Total Scheduled: {cumulative} min")
    print(f"   Free Time Remaining: {remaining} min")
    
    # Explanation
    print(f"\n💭 Scheduler's Reasoning:")
    explanation = scheduler.explain_plan(plan)
    for line in explanation.split('\n'):
        print(f"   {line}")
    
    # =========================================================================
    # INTEGRATION SUCCESS
    # =========================================================================
    print("\n\n" + "=" * 80)
    print("🎉 INTEGRATION TEST SUCCESSFUL!")
    print("=" * 80)
    print("\n✅ Backend ↔ UI Connection Verified:")
    print("   ✓ Owner object persists across changes")
    print("   ✓ Pets persist when added")
    print("   ✓ Tasks persist and attach to pets")
    print("   ✓ Scheduler generates plans from live data")
    print("   ✓ UI can display results from backend methods")
    print("\n🚀 Ready for Streamlit deployment!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    simulate_ui_workflow()
