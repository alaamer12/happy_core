"""
Examples of using the Schedule and Event classes for advanced time management.
"""

from true.time import Time, TimeUnit, Event, Schedule


def demo_basic_scheduling():
    """Demonstrate basic scheduling operations."""
    print("=== Basic Scheduling ===")

    # Create a schedule
    schedule = Schedule()

    # Create some events
    meeting = Event(
        name="Team Meeting",
        start_time=Time.now(),
        end_time=Time.now().add(1, TimeUnit.HOURS),
        description="Weekly team sync",
        tags=["meeting", "team"]
    )

    lunch = Event(
        name="Lunch Break",
        start_time=Time.now().add(2, TimeUnit.HOURS),
        end_time=Time.now().add(3, TimeUnit.HOURS),
        tags=["break"]
    )

    # Add events to schedule
    schedule.add_event(meeting)
    schedule.add_event(lunch)

    print(f"Schedule has {len(schedule)} events")
    print(f"Schedule: {schedule}")


def demo_event_operations():
    """Demonstrate event manipulation and querying."""
    print("\n=== Event Operations ===")

    schedule = Schedule()

    # Create an event
    event = Event(
        name="Project Review",
        start_time=Time.now(),
        end_time=Time.now().add(2, TimeUnit.HOURS),
        tags=["meeting", "project"]
    )

    schedule.add_event(event)

    # Update event
    schedule.update_event(
        "Project Review",
        description="Quarterly project review meeting",
        priority=1
    )

    # Get event duration
    event = [e for e in schedule if e.name == "Project Review"][0]
    print(f"Event duration: {event.duration(TimeUnit.MINUTES)} minutes")

    # Remove event
    schedule.remove_event("Project Review")
    print(f"Events after removal: {len(schedule)}")


def demo_schedule_analysis():
    """Demonstrate schedule analysis features."""
    print("\n=== Schedule Analysis ===")

    schedule = Schedule()

    # Add multiple events
    events = [
        Event(
            name="Meeting 1",
            start_time=Time.now(),
            end_time=Time.now().add(1, TimeUnit.HOURS),
            tags=["meeting"]
        ),
        Event(
            name="Meeting 2",
            start_time=Time.now().add(2, TimeUnit.HOURS),
            end_time=Time.now().add(3, TimeUnit.HOURS),
            tags=["meeting"]
        ),
        Event(
            name="Break",
            start_time=Time.now().add(4, TimeUnit.HOURS),
            end_time=Time.now().add(5, TimeUnit.HOURS),
            tags=["break"]
        )
    ]

    for event in events:
        schedule.add_event(event)

    # Get schedule statistics
    start_time = Time.now()
    end_time = Time.now().add(6, TimeUnit.HOURS)
    stats = schedule.get_statistics(start_time, end_time)

    print("Schedule Statistics:")
    print(f"Total events: {stats['total_events']}")
    print(f"Total duration: {stats['total_duration']} minutes")
    print("Tags distribution:", stats['tags_distribution'])

    # Find free slots
    free_slots = schedule.find_free_slots(
        start_time,
        end_time,
        duration=30,
        unit=TimeUnit.MINUTES
    )
    print(free_slots)


def demo_conflict_detection():
    """Demonstrate schedule conflict detection."""
    print("\n=== Conflict Detection ===")

    schedule = Schedule()

    # Create overlapping events
    event1 = Event(
        name="Event 1",
        start_time=Time.now(),
        end_time=Time.now().add(2, TimeUnit.HOURS)
    )

    event2 = Event(
        name="Event 2",
        start_time=Time.now().add(1, TimeUnit.HOURS),
        end_time=Time.now().add(3, TimeUnit.HOURS)
    )

    # Add first event
    schedule.add_event(event1)
    print("Added first event")

    # Try to add conflicting event
    try:
        schedule.add_event(event2)
    except Exception as e:
        print(f"Conflict detected: {e}")


if __name__ == "__main__":
    demo_basic_scheduling()
    demo_event_operations()
    demo_schedule_analysis()
    demo_conflict_detection()
