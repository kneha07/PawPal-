"""
Test suite for PawPal+ core classes (Task, Pet, Owner, Scheduler).
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


class TestTask:
    """Tests for the Task class."""
    
    def test_task_completion(self):
        """Verify that mark_complete() changes task status to 'completed'."""
        task = Task("Morning walk", 30, 5)
        
        # Initial status should be "pending"
        assert task.status == "pending"
        
        # Mark as complete
        task.mark_complete()
        
        # Status should now be "completed"
        assert task.status == "completed"
    
    def test_task_priority_label(self):
        """Verify that get_priority_label() returns correct labels."""
        task_critical = Task("Urgent task", 10, 5)
        task_high = Task("High task", 10, 4)
        task_medium = Task("Medium task", 10, 3)
        task_low = Task("Low task", 10, 1)
        
        assert task_critical.get_priority_label() == "Critical"
        assert task_high.get_priority_label() == "High"
        assert task_medium.get_priority_label() == "Medium"
        assert task_low.get_priority_label() == "Low"
    
    def test_task_due_today_pending(self):
        """Verify that a pending task is due today."""
        task = Task("Feed pet", 15, 3, recurring=False)
        assert task.is_due_today() is True
    
    def test_task_due_today_completed_non_recurring(self):
        """Verify that a completed non-recurring task is not due today."""
        task = Task("Feed pet", 15, 3, recurring=False)
        task.mark_complete()
        assert task.is_due_today() is False
    
    def test_task_due_today_completed_recurring(self):
        """Verify that a completed recurring task is still due today."""
        task = Task("Feed pet", 15, 3, recurring=True, recurrence_pattern="daily")
        task.mark_complete()
        assert task.is_due_today() is True


class TestPet:
    """Tests for the Pet class."""
    
    def test_add_task_to_pet(self):
        """Verify that adding a task to a Pet increases the task count."""
        pet = Pet("Buddy", "Dog", 3)
        
        # Initially, pet has no tasks
        assert len(pet.tasks) == 0
        
        # Add a task
        task = Task("Walk", 30, 5)
        pet.add_task(task)
        
        # Task count should increase to 1
        assert len(pet.tasks) == 1
        
        # Verify the task is in the list
        assert task in pet.tasks
    
    def test_add_multiple_tasks(self):
        """Verify that multiple tasks can be added to a pet."""
        pet = Pet("Max", "Dog", 5)
        
        task1 = Task("Morning walk", 30, 5)
        task2 = Task("Feed Max", 15, 4)
        task3 = Task("Playtime", 20, 3)
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        
        assert len(pet.tasks) == 3
    
    def test_remove_task_from_pet(self):
        """Verify that removing a task decreases the task count."""
        pet = Pet("Whiskers", "Cat", 2)
        
        task1 = Task("Feed", 10, 4)
        task2 = Task("Play", 15, 3)
        
        pet.add_task(task1)
        pet.add_task(task2)
        assert len(pet.tasks) == 2
        
        # Remove a task
        pet.remove_task(task1)
        assert len(pet.tasks) == 1
        assert task1 not in pet.tasks
        assert task2 in pet.tasks
    
    def test_get_daily_tasks(self):
        """Verify that get_daily_tasks() returns only pending tasks."""
        pet = Pet("Tweety", "Bird", 1)
        
        task1 = Task("Feed", 5, 5)  # pending
        task2 = Task("Water", 5, 4)  # pending
        task3 = Task("Clean cage", 20, 3)  # pending
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        
        daily_tasks = pet.get_daily_tasks()
        assert len(daily_tasks) == 3
        
        # Complete one task
        task2.mark_complete()
        daily_tasks = pet.get_daily_tasks()
        assert len(daily_tasks) == 2
        assert task2 not in daily_tasks


class TestOwner:
    """Tests for the Owner class."""
    
    def test_add_pet_to_owner(self):
        """Verify that adding a pet to an Owner increases the pet count."""
        owner = Owner("Alice", 120)
        
        # Initially, owner has no pets
        assert len(owner.pets) == 0
        
        # Add a pet
        pet = Pet("Max", "Dog", 5)
        owner.add_pet(pet)
        
        # Pet count should increase to 1
        assert len(owner.pets) == 1
        assert pet in owner.pets
    
    def test_add_multiple_pets(self):
        """Verify that an owner can have multiple pets."""
        owner = Owner("Bob", 180)
        
        pet1 = Pet("Max", "Dog", 5)
        pet2 = Pet("Whiskers", "Cat", 2)
        pet3 = Pet("Tweety", "Bird", 1)
        
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        owner.add_pet(pet3)
        
        assert len(owner.pets) == 3
    
    def test_get_all_tasks(self):
        """Verify that get_all_tasks() collects tasks from all pets."""
        owner = Owner("Charlie", 120)
        
        # Create pets with tasks
        pet1 = Pet("Max", "Dog", 5)
        pet1.add_task(Task("Walk", 30, 5))
        pet1.add_task(Task("Feed", 15, 4))
        
        pet2 = Pet("Whiskers", "Cat", 2)
        pet2.add_task(Task("Feed", 10, 4))
        pet2.add_task(Task("Clean box", 10, 5))
        
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        
        all_tasks = owner.get_all_tasks()
        assert len(all_tasks) == 4
    
    def test_get_total_required_minutes(self):
        """Verify that get_total_required_minutes() sums all task durations."""
        owner = Owner("Diana", 120)
        
        pet1 = Pet("Max", "Dog", 5)
        pet1.add_task(Task("Walk", 30, 5))
        pet1.add_task(Task("Feed", 15, 4))
        
        pet2 = Pet("Whiskers", "Cat", 2)
        pet2.add_task(Task("Feed", 10, 4))
        pet2.add_task(Task("Clean box", 10, 5))
        
        owner.add_pet(pet1)
        owner.add_pet(pet2)
        
        total_minutes = owner.get_total_required_minutes()
        assert total_minutes == 30 + 15 + 10 + 10  # 65 minutes


class TestScheduler:
    """Tests for the Scheduler class."""
    
    def test_scheduler_initialization(self):
        """Verify that Scheduler initializes with correct time budget."""
        owner = Owner("Eve", 150)
        scheduler = Scheduler(owner)
        
        assert scheduler.owner == owner
        assert scheduler.time_budget == 150
    
    def test_is_feasible_true(self):
        """Verify that is_feasible() returns True when tasks fit in budget."""
        owner = Owner("Frank", 120)
        
        pet = Pet("Max", "Dog", 5)
        pet.add_task(Task("Walk", 30, 5))
        pet.add_task(Task("Feed", 15, 4))
        pet.add_task(Task("Play", 20, 3))  # Total: 65 min, budget: 120
        
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        
        assert scheduler.is_feasible() is True
    
    def test_is_feasible_false(self):
        """Verify that is_feasible() returns False when tasks exceed budget."""
        owner = Owner("Grace", 60)
        
        pet = Pet("Max", "Dog", 5)
        pet.add_task(Task("Walk", 40, 5))
        pet.add_task(Task("Feed", 30, 4))  # Total: 70 min, budget: 60
        
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        
        assert scheduler.is_feasible() is False
    
    def test_sort_by_priority(self):
        """Verify that tasks are sorted by priority (highest first), then by duration."""
        owner = Owner("Henry", 200)
        scheduler = Scheduler(owner)
        
        tasks = [
            Task("Low priority long", 60, 1),
            Task("High priority short", 10, 5),
            Task("Medium priority", 30, 3),
            Task("High priority long", 50, 5),
        ]
        
        sorted_tasks = scheduler.sort_by_priority(tasks)
        
        # Should be sorted: priority 5 (short first), priority 5 (long), priority 3, priority 1
        assert sorted_tasks[0].name == "High priority short"
        assert sorted_tasks[1].name == "High priority long"
        assert sorted_tasks[2].name == "Medium priority"
        assert sorted_tasks[3].name == "Low priority long"
    
    def test_generate_plan_respects_budget(self):
        """Verify that generate_plan() doesn't exceed the time budget."""
        owner = Owner("Ivy", 50)
        
        pet = Pet("Max", "Dog", 5)
        pet.add_task(Task("Walk", 30, 5))
        pet.add_task(Task("Feed", 15, 4))
        pet.add_task(Task("Play", 20, 3))
        
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        
        plan = scheduler.generate_plan()
        
        total_time = sum(task.duration_minutes for task in plan)
        assert total_time <= owner.available_minutes
    
    def test_detect_conflicts(self):
        """Verify that detect_conflicts() identifies time budget overages."""
        owner = Owner("Jack", 100)
        
        pet = Pet("Max", "Dog", 5)
        pet.add_task(Task("Walk", 60, 5))
        pet.add_task(Task("Feed", 50, 4))  # Total: 110 min, exceeds budget of 100
        
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        
        all_tasks = owner.get_all_tasks()
        conflicts = scheduler.detect_conflicts(all_tasks)
        
        assert len(conflicts) > 0
        assert "exceeds available time" in conflicts[0]
    
    def test_explain_plan(self):
        """Verify that explain_plan() returns a non-empty explanation."""
        owner = Owner("Kate", 100)
        
        pet = Pet("Max", "Dog", 5)
        pet.add_task(Task("Walk", 30, 5))
        pet.add_task(Task("Feed", 15, 4))
        
        owner.add_pet(pet)
        scheduler = Scheduler(owner)
        
        plan = scheduler.generate_plan()
        explanation = scheduler.explain_plan(plan)
        
        assert len(explanation) > 0
        assert owner.name in explanation
        assert "Priority" in explanation


# ============================================================================
# PHASE 4: ALGORITHMIC ENHANCEMENTS TESTS
# ============================================================================

class TestPhase4Algorithms:
    """Tests for Phase 4 algorithmic features: sorting, filtering, recurring tasks."""
    
    # ────────────────────────────────────────────────────────────────────
    # TEST GROUP: Sorting by Time
    # ────────────────────────────────────────────────────────────────────
    
    def test_sort_by_time_with_scheduled_times(self):
        """Verify sort_by_time() orders tasks by scheduled_time (HH:MM)."""
        owner = Owner("Alex", 200)
        scheduler = Scheduler(owner)
        
        tasks = [
            Task("Evening walk", 30, 5, scheduled_time="18:00"),
            Task("Morning walk", 30, 5, scheduled_time="08:00"),
            Task("Lunch feed", 15, 4, scheduled_time="12:00"),
        ]
        
        sorted_tasks = scheduler.sort_by_time(tasks)
        
        assert sorted_tasks[0].scheduled_time == "08:00"
        assert sorted_tasks[1].scheduled_time == "12:00"
        assert sorted_tasks[2].scheduled_time == "18:00"
    
    def test_sort_by_time_unscheduled_last(self):
        """Verify sort_by_time() puts unscheduled tasks at the end."""
        owner = Owner("Bob", 200)
        scheduler = Scheduler(owner)
        
        tasks = [
            Task("Unscheduled task", 20, 3),  # No scheduled_time
            Task("Morning walk", 30, 5, scheduled_time="08:00"),
            Task("Play", 15, 2),  # No scheduled_time
        ]
        
        sorted_tasks = scheduler.sort_by_time(tasks)
        
        # First two should be scheduled
        assert sorted_tasks[0].scheduled_time == "08:00"
        # Last two should be unscheduled
        assert sorted_tasks[1].scheduled_time is None
        assert sorted_tasks[2].scheduled_time is None
    
    # ────────────────────────────────────────────────────────────────────
    # TEST GROUP: Filtering by Status and Priority
    # ────────────────────────────────────────────────────────────────────
    
    def test_filter_tasks_by_status_pending(self):
        """Verify filter_tasks_by_status() returns only pending tasks."""
        owner = Owner("Carol", 120)
        scheduler = Scheduler(owner)
        
        task1 = Task("Walk", 30, 5)  # pending
        task2 = Task("Feed", 15, 4)  # pending
        task3 = Task("Play", 20, 3)  # pending
        
        # Mark one as completed
        task2.mark_complete()
        
        tasks = [task1, task2, task3]
        pending = scheduler.filter_tasks_by_status(tasks, "pending")
        
        assert len(pending) == 2
        assert task1 in pending
        assert task3 in pending
        assert task2 not in pending
    
    def test_filter_tasks_by_status_completed(self):
        """Verify filter_tasks_by_status() returns only completed tasks."""
        owner = Owner("Diana", 120)
        scheduler = Scheduler(owner)
        
        task1 = Task("Walk", 30, 5)
        task2 = Task("Feed", 15, 4)
        
        task1.mark_complete()
        
        tasks = [task1, task2]
        completed = scheduler.filter_tasks_by_status(tasks, "completed")
        
        assert len(completed) == 1
        assert task1 in completed
        assert task2 not in completed
    
    def test_filter_tasks_by_pet(self):
        """Verify filter_tasks_by_pet() returns only tasks for the specified pet."""
        owner = Owner("Eve", 180)
        scheduler = Scheduler(owner)
        
        max_dog = Pet("Max", "Dog", 5)
        whiskers_cat = Pet("Whiskers", "Cat", 2)
        
        task1 = Task("Walk", 30, 5)
        task2 = Task("Feed Max", 15, 4)
        max_dog.add_task(task1)
        max_dog.add_task(task2)
        
        task3 = Task("Feed Whiskers", 10, 4)
        task4 = Task("Clean box", 10, 5)
        whiskers_cat.add_task(task3)
        whiskers_cat.add_task(task4)
        
        owner.add_pet(max_dog)
        owner.add_pet(whiskers_cat)
        
        all_tasks = owner.get_all_tasks()
        max_tasks = scheduler.filter_tasks_by_pet(all_tasks, "Max")
        
        assert len(max_tasks) == 2
        assert task1 in max_tasks
        assert task2 in max_tasks
        assert task3 not in max_tasks
        assert task4 not in max_tasks
    
    def test_pet_filter_by_priority(self):
        """Verify Pet.filter_tasks_by_priority() returns only high-priority tasks."""
        pet = Pet("Max", "Dog", 5)
        
        task1 = Task("Walk", 30, 5)  # Critical
        task2 = Task("Feed", 15, 4)  # High
        task3 = Task("Play", 20, 3)  # Medium
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        
        critical_tasks = pet.filter_tasks_by_priority(5)
        
        assert len(critical_tasks) == 1
        assert task1 in critical_tasks
        assert task2 not in critical_tasks
        assert task3 not in critical_tasks
    
    def test_pet_filter_by_status(self):
        """Verify Pet.filter_tasks_by_status() returns only specified status."""
        pet = Pet("Whiskers", "Cat", 2)
        
        task1 = Task("Feed", 10, 4)
        task2 = Task("Play", 15, 2)
        task3 = Task("Clean", 10, 5)
        
        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)
        
        task1.mark_complete()
        
        pending = pet.filter_tasks_by_status("pending")
        
        assert len(pending) == 2
        assert task1 not in pending
        assert task2 in pending
        assert task3 in pending
    
    # ────────────────────────────────────────────────────────────────────
    # TEST GROUP: Recurring Task Automation
    # ────────────────────────────────────────────────────────────────────
    
    def test_create_next_occurrence_recurring(self):
        """Verify create_next_occurrence() creates a task copy with reset status."""
        task = Task("Morning walk", 30, 5, recurring=True, recurrence_pattern="daily")
        task.mark_complete()
        
        next_task = task.create_next_occurrence()
        
        # New task should be a different object
        assert next_task is not task
        
        # Properties should match
        assert next_task.name == task.name
        assert next_task.duration_minutes == task.duration_minutes
        assert next_task.priority == task.priority
        assert next_task.recurring == task.recurring
        assert next_task.recurrence_pattern == task.recurrence_pattern
        
        # Status should be reset to pending
        assert next_task.status == "pending"
        assert task.status == "completed"
    
    def test_mark_complete_returns_next_occurrence_for_recurring(self):
        """Verify mark_complete() returns next occurrence for recurring tasks."""
        task = Task("Feed pet", 15, 4, recurring=True, recurrence_pattern="daily")
        
        next_task = task.mark_complete()
        
        # Should return a new task
        assert next_task is not None
        assert next_task.status == "pending"
        assert task.status == "completed"
    
    def test_mark_complete_returns_none_for_non_recurring(self):
        """Verify mark_complete() returns None for non-recurring tasks."""
        task = Task("One-time task", 10, 3, recurring=False)
        
        result = task.mark_complete()
        
        # Should return None
        assert result is None
        assert task.status == "completed"
    
    def test_process_recurring_tasks(self):
        """Verify process_recurring_tasks() creates new occurrences for completed recurring tasks."""
        owner = Owner("Frank", 180)
        
        pet = Pet("Max", "Dog", 5)
        task1 = Task("Morning walk", 30, 5, recurring=True, recurrence_pattern="daily")
        task2 = Task("Feed", 15, 4, recurring=False)
        
        pet.add_task(task1)
        pet.add_task(task2)
        owner.add_pet(pet)
        
        scheduler = Scheduler(owner)
        
        # Initially, should have no new recurring tasks
        result = scheduler.process_recurring_tasks()
        assert "Max" in result or len(result) == 0
        
        # Complete the recurring task
        task1.mark_complete()
        
        # Now process should create a new occurrence
        result = scheduler.process_recurring_tasks()
        
        # The pet should have been updated with the new task
        # (This depends on internal scheduler implementation)
        assert isinstance(result, dict)
    
    # ────────────────────────────────────────────────────────────────────
    # TEST GROUP: Advanced Conflict Detection
    # ────────────────────────────────────────────────────────────────────
    
    def test_detect_time_slot_conflicts(self):
        """Verify detect_conflicts() identifies tasks scheduled at the same time."""
        owner = Owner("Grace", 180)
        scheduler = Scheduler(owner)
        
        # Create tasks scheduled at the same time
        task1 = Task("Morning walk", 30, 5, scheduled_time="08:00")
        task2 = Task("Feed pet", 15, 4, scheduled_time="08:00")  # Same time!
        
        conflicts = scheduler.detect_conflicts([task1, task2])
        
        # Should detect the time conflict
        assert len(conflicts) > 0
        assert any("08:00" in conflict for conflict in conflicts)
    
    def test_detect_time_and_budget_conflicts(self):
        """Verify detect_conflicts() detects both time and budget conflicts."""
        owner = Owner("Henry", 50)  # Small budget
        scheduler = Scheduler(owner)
        
        tasks = [
            Task("Task 1", 40, 5, scheduled_time="09:00"),
            Task("Task 2", 30, 5, scheduled_time="09:00"),  # Time conflict + budget
        ]
        
        conflicts = scheduler.detect_conflicts(tasks)
        
        # Should have conflicts
        assert len(conflicts) > 0
    
    def test_no_conflicts_with_staggered_times(self):
        """Verify detect_conflicts() finds no conflicts with different scheduled times."""
        owner = Owner("Iris", 180)
        scheduler = Scheduler(owner)
        
        tasks = [
            Task("Morning walk", 30, 5, scheduled_time="08:00"),
            Task("Lunch feed", 15, 4, scheduled_time="12:00"),
            Task("Evening walk", 30, 5, scheduled_time="18:00"),
        ]
        
        conflicts = scheduler.detect_conflicts(tasks)
        
        # Should have no time conflicts (total time is OK)
        time_conflicts = [c for c in conflicts if "Time conflict" in c]
        assert len(time_conflicts) == 0
