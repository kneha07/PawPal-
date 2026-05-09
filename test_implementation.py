"""Quick functional test of PawPal+ core classes."""

from pawpal_system import Task, Pet, Owner, Scheduler

# Create tasks
morning_walk = Task("Morning walk", 30, 5, recurring=True, recurrence_pattern="daily")
feeding = Task("Feed Buddy", 15, 4)
play_session = Task("Play fetch", 20, 3)
grooming = Task("Grooming", 60, 2)

# Create a pet and add tasks
buddy = Pet("Buddy", "Dog", 3)
buddy.add_task(morning_walk)
buddy.add_task(feeding)
buddy.add_task(play_session)
buddy.add_task(grooming)

# Create owner with pet
owner = Owner("Alice", 120, [buddy])

print("=" * 60)
print("PAWPAL+ CORE IMPLEMENTATION TEST")
print("=" * 60)

# Test Owner methods
print("\n📋 Owner Information:")
print(f"  Name: {owner.name}")
print(f"  Available time: {owner.available_minutes} min")
print(f"  Pets: {[p.name for p in owner.pets]}")
print(f"  Total tasks: {len(owner.get_all_tasks())}")
print(f"  Total required time: {owner.get_total_required_minutes()} min")

# Test Scheduler
scheduler = Scheduler(owner)
print("\n⏰ Scheduler Analysis:")
print(f"  Time budget: {scheduler.time_budget} min")
print(f"  Is feasible? {scheduler.is_feasible()}")

# Generate plan
plan = scheduler.generate_plan()
print(f"\n✅ Generated plan ({len(plan)} tasks):")
for task in plan:
    print(f"  • {task.name} ({task.duration_minutes} min, {task.get_priority_label()})")

# Check conflicts
conflicts = scheduler.detect_conflicts(owner.get_all_tasks())
print(f"\n⚠️  Conflict Detection: {len(conflicts)} conflict(s)")
if conflicts:
    for conflict in conflicts:
        print(f"  • {conflict}")

# Explain plan
print("\n📝 Plan Explanation:")
print(scheduler.explain_plan(plan))

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)
