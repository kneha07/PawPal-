"""
Demo script for PawPal+ — creates a realistic scenario and displays today's schedule.
NOW WITH PHASE 4 FEATURES: Sorting, Filtering, Recurring Tasks, Advanced Conflicts
"""

from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # Create Owner
    owner = Owner("Sarah", available_minutes=180)  # 3 hours available
    
    # Create first pet: Max (Dog)
    max_dog = Pet("Max", "Dog", 5)
    max_dog.add_task(Task("Morning walk", 30, 5, recurring=True, recurrence_pattern="daily", scheduled_time="08:00"))
    max_dog.add_task(Task("Feed Max", 15, 4, scheduled_time="12:00"))
    max_dog.add_task(Task("Playtime in backyard", 25, 3))
    max_dog.add_task(Task("Evening walk", 30, 5, recurring=True, recurrence_pattern="daily", scheduled_time="18:00"))
    
    # Create second pet: Whiskers (Cat)
    whiskers_cat = Pet("Whiskers", "Cat", 2)
    whiskers_cat.add_task(Task("Feed Whiskers", 10, 4, scheduled_time="12:30"))
    whiskers_cat.add_task(Task("Clean litter box", 10, 5))
    whiskers_cat.add_task(Task("Play with toy mouse", 15, 2))
    
    # Create third pet: Tweety (Bird)
    tweety_bird = Pet("Tweety", "Bird", 1)
    tweety_bird.add_task(Task("Feed Tweety", 5, 5, scheduled_time="08:00"))
    tweety_bird.add_task(Task("Change water", 5, 4))
    tweety_bird.add_task(Task("Clean cage", 20, 3))
    
    # Add pets to owner
    owner.add_pet(max_dog)
    owner.add_pet(whiskers_cat)
    owner.add_pet(tweety_bird)
    
    # Create scheduler
    scheduler = Scheduler(owner)
    
    # Print system overview
    print("\n" + "=" * 70)
    print("🐾 PAWPAL+ DAILY SCHEDULE GENERATOR 🐾 [Phase 4: Smart Algorithms]")
    print("=" * 70)
    
    print(f"\n📌 Owner: {owner.name}")
    print(f"📌 Available Time: {owner.available_minutes} minutes")
    print(f"📌 Pets: {', '.join([p.name for p in owner.pets])}")
    
    # Collect all tasks
    all_tasks = owner.get_all_tasks()
    total_time_needed = owner.get_total_required_minutes()
    
    print(f"\n📊 Task Summary:")
    print(f"   Total tasks: {len(all_tasks)}")
    print(f"   Total time needed: {total_time_needed} minutes")
    print(f"   Time available: {owner.available_minutes} minutes")
    print(f"   Feasible? {'✅ Yes' if scheduler.is_feasible() else '❌ No'}")
    
    # Display all tasks grouped by pet
    print(f"\n📋 All Tasks by Pet:")
    for pet in owner.pets:
        print(f"\n   🐕 {pet.name} ({pet.species}, age {pet.age}):")
        for task in pet.tasks:
            time_info = f" @ {task.scheduled_time}" if task.scheduled_time else ""
            print(f"      • {task.name}: {task.duration_minutes}min | Priority: {task.get_priority_label()}{time_info}")
    
    # [PHASE 4] ✨ DEMONSTRATION: Sorting by Time
    print(f"\n{'=' * 70}")
    print(f"✨ PHASE 4 FEATURE: Smart Sorting by Time")
    print(f"{'=' * 70}")
    scheduled_tasks = [t for t in all_tasks if t.scheduled_time]
    sorted_by_time = scheduler.sort_by_time(scheduled_tasks)
    print(f"\n📅 Tasks Sorted by Scheduled Time:")
    if sorted_by_time:
        for i, task in enumerate(sorted_by_time, 1):
            print(f"   {i}. {task.name:30} @ {task.scheduled_time} ({task.duration_minutes}min)")
    else:
        print(f"   (No scheduled tasks yet)")
    
    # [PHASE 4] ✨ DEMONSTRATION: Filtering by Priority
    print(f"\n{'─' * 70}")
    print(f"✨ PHASE 4 FEATURE: Smart Filtering by Priority")
    print(f"{'─' * 70}")
    high_priority_tasks = scheduler.filter_tasks_by_status(all_tasks, "pending")
    print(f"\n🔴 High Priority (5) Tasks Only:")
    for pet in owner.pets:
        high_pri = pet.filter_tasks_by_priority(5)
        if high_pri:
            print(f"   {pet.name}: {', '.join([t.name for t in high_pri])}")
    
    # [PHASE 4] ✨ DEMONSTRATION: Filtering by Pet
    print(f"\n{'─' * 70}")
    print(f"✨ PHASE 4 FEATURE: Smart Filtering by Pet")
    print(f"{'─' * 70}")
    print(f"\n🐾 Filtering Max's Tasks from Full Task List:")
    max_tasks = scheduler.filter_tasks_by_pet(all_tasks, "Max")
    for task in max_tasks:
        print(f"   • {task.name}")
    
    # [PHASE 4] ✨ DEMONSTRATION: Time-Based Conflict Detection
    print(f"\n{'─' * 70}")
    print(f"✨ PHASE 4 FEATURE: Advanced Conflict Detection (Time-Based)")
    print(f"{'─' * 70}")
    conflicts = scheduler.detect_conflicts(all_tasks)
    if conflicts:
        print(f"\n⚠️  Scheduling Conflicts Detected:")
        for conflict in conflicts:
            print(f"   • {conflict}")
    else:
        print(f"\n✅ No scheduling conflicts detected!")
    
    # Generate and display optimized plan
    plan = scheduler.generate_plan()
    
    print(f"\n✨ TODAY'S OPTIMIZED SCHEDULE ✨")
    print(f"{'─' * 70}")
    
    if not plan:
        print("   ⚠️  No tasks could fit in the available time budget.")
    else:
        cumulative_time = 0
        for i, task in enumerate(plan, 1):
            cumulative_time += task.duration_minutes
            status_icon = "✓"
            time_info = f" @ {task.scheduled_time}" if task.scheduled_time else ""
            print(f"\n   {i}. {status_icon} {task.name}{time_info}")
            print(f"      Duration: {task.duration_minutes} min | Priority: {task.get_priority_label()}")
            print(f"      Time elapsed: {cumulative_time} min / {owner.available_minutes} min")
    
    print(f"\n{'─' * 70}")
    print(f"   Total scheduled: {sum(t.duration_minutes for t in plan)} minutes")
    print(f"   Remaining free time: {owner.available_minutes - sum(t.duration_minutes for t in plan)} minutes")
    
    # [PHASE 4] ✨ DEMONSTRATION: Recurring Task Automation
    print(f"\n{'=' * 70}")
    print(f"✨ PHASE 4 FEATURE: Recurring Task Automation")
    print(f"{'=' * 70}")
    print(f"\n🔄 Processing Recurring Tasks (Creating Next Occurrences):")
    recurring_updates = scheduler.process_recurring_tasks()
    if recurring_updates:
        for pet_name, new_tasks in recurring_updates.items():
            print(f"   {pet_name}: {len(new_tasks)} new recurring task(s) created")
            for task in new_tasks:
                print(f"      → {task.name} (next occurrence)")
    else:
        print(f"   (No recurring tasks completed yet)")
    
    # Display explanation
    print(f"\n💭 Scheduler's Reasoning:")
    print(f"{'─' * 70}")
    explanation = scheduler.explain_plan(plan)
    for line in explanation.split('\n'):
        print(f"   {line}")
    
    print("\n" + "=" * 70)
    print("📚 Phase 4 Features: Smart Sorting | Flexible Filtering | Auto-Recurring | Conflict Detection")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
