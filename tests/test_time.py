from datetime import datetime, timezone, timedelta

import pytest
import unittest
import time
from happy_core.time import Time, TimeFormat, TimeUnit, timer, \
    Schedule, Event
from happy_core.exceptions import ScheduleConflictError


@pytest.fixture(scope="function")
def utc_time():
    return Time("2024-01-01 12:00:00")


@pytest.fixture
def ny_time():
    return Time("2024-01-01 12:00:00", "America/New_York")


# @pytest.mark.slow
def test_timer():
    @timer
    def dummy_function():
        time.sleep(0.1)
        return "done"

    start = time.time()
    result = dummy_function()
    end = time.time()

    assert result == "done"
    assert (end - start) >= 0.1  # Ensure 'timer' is working


class TestTimeInitialization:
    def test_init_with_none(self):
        """Test initialization with no parameters"""
        time = Time()
        assert isinstance(time.datetime, datetime)
        assert time.timezone == "UTC"

    def test_init_with_timestamp(self):
        """Test initialization with timestamp"""
        timestamp = 1704110400.0  # 2024-01-01 12:00:00 UTC
        time = Time(time_input=timestamp, timezone_name="UTC")
        assert time.datetime.year == 2024
        assert time.datetime.month == 1
        assert time.datetime.day == 1
        assert time.datetime.hour == 12

    def test_init_with_datetime_string(self):
        """Test initialization with datetime string"""
        time = Time("2024-01-01 12:00:00")
        assert time.datetime.year == 2024
        assert time.datetime.month == 1
        assert time.datetime.hour == 12

    def test_init_with_datetime_object(self):
        """Test initialization with a datetime object"""
        dt = datetime(2024, 1, 1, 12, tzinfo=timezone.utc)
        time = Time(dt)
        assert time.datetime == dt

    # def test_init_with_invalid_input(self):
    #     """Test initialization with invalid input"""
    #     with pytest.raises(ValueError):
    #         Time([1, 2, 3])


class TestTimeProperties:
    def test_quarter(self, utc_time):
        """Test quarter property"""
        assert utc_time.quarter == 1
        march_time = Time("2024-03-15 12:00:00")
        assert march_time.quarter == 1
        april_time = Time("2024-04-01 12:00:00")
        assert april_time.quarter == 2

    def test_timezone_property(self, ny_time):
        """Test timezone property"""
        assert ny_time.timezone == "America/New_York"


class TestTimeOperations:
    def test_floor(self, utc_time):
        """Test floor operation"""
        time = Time("2024-01-01 12:34:56")
        assert time.floor(TimeUnit.HOURS).datetime.minute == 0
        assert time.floor(TimeUnit.DAYS).datetime.hour == 0
        assert time.floor(TimeUnit.MONTHS).datetime.day == 1

    def test_ceil(self, utc_time):
        """Test ceil operation"""
        time = Time("2024-01-01 12:34:56")
        next_hour = time.ceil(TimeUnit.HOURS)
        assert next_hour.datetime.hour == 13
        assert next_hour.datetime.minute == 0

    def test_round(self, utc_time):
        """Test round operation"""
        time = Time("2024-01-01 12:29:00")
        rounded = time.round(TimeUnit.HOURS)
        assert rounded.datetime.hour == 12

        time = Time("2024-01-01 12:31:00")
        rounded = time.round(TimeUnit.HOURS)
        assert rounded.datetime.hour == 13

    def test_is_between(self):
        """Test is_between method"""
        start = Time("2024-01-01 12:00:00")
        middle = Time("2024-01-01 13:00:00")
        end = Time("2024-01-01 14:00:00")

        assert middle.is_between(start, end)
        assert not end.is_between(start, middle)
        assert start.is_between(start, end, inclusive=True)
        assert not start.is_between(start, end, inclusive=False)


class TestTimeFormatting:
    def test_format_12_hour(self, utc_time):
        """Test 12-hour time formatting"""
        formatted = utc_time.format(TimeFormat.HOUR_12)
        assert "12:00:00 PM" in formatted

    def test_format_24_hour(self, utc_time):
        """Test 24-hour time formatting"""
        formatted = utc_time.format(TimeFormat.HOUR_24)
        assert "12:00:00" in formatted

    def test_format_iso(self, utc_time):
        """Test ISO format"""
        formatted = utc_time.format(TimeFormat.ISO)
        assert "2024-01-01T12:00:00" in formatted

    def test_format_custom(self, utc_time):
        """Test custom format"""
        formatted = utc_time.format(TimeFormat.CUSTOM, "%Y-%m-%d")
        assert formatted == "2024-01-01"


class TestTimeArithmetic:
    def test_add_time_units(self, utc_time):
        """Test adding time units"""
        new_time = utc_time.add(1, TimeUnit.HOURS)
        assert new_time.datetime.hour == 13

        new_time = utc_time.add(1, TimeUnit.DAYS)
        assert new_time.datetime.day == 2

    def test_time_difference(self):
        """Test time difference calculation"""
        time1 = Time("2024-01-01 12:00:00")
        time2 = Time("2024-01-01 13:00:00")

        assert time2.difference(time1, TimeUnit.HOURS) == 1
        assert time2.difference(time1, TimeUnit.MINUTES) == 60
        assert time2.difference(time1, TimeUnit.SECONDS) == 3600

    def test_addition_operator(self, utc_time):
        """Test addition operator"""
        new_time = utc_time + timedelta(hours=1)
        assert new_time.datetime.hour == 13

        new_time = utc_time + 3600  # Add 1 hour in seconds
        assert new_time.datetime.hour == 13

    def test_subtraction_operator(self, utc_time):
        """Test subtraction operator"""
        new_time = utc_time - timedelta(hours=1)
        assert new_time.datetime.hour == 11

        new_time = utc_time - 3600  # Subtract 1 hour in seconds
        assert new_time.datetime.hour == 11


class TestTimeConversion:
    def test_timezone_conversion(self, ny_time, utc_time):
        """Test timezone conversion"""
        utc_time = Time("2024-01-01 12:00:00", "UTC")
        ny_time = utc_time.to_timezone("America/New_York")

        assert ny_time.timezone == "America/New_York"

    def test_to_dict(self, utc_time):
        """Test dictionary conversion"""
        time_dict = utc_time.to_dict()
        assert isinstance(time_dict, dict)
        assert time_dict['year'] == 2024
        assert time_dict['month'] == 1
        assert time_dict['day'] == 1
        assert time_dict['hour'] == 12


class TestTimeComparison:
    def test_equality(self):
        """Test time equality comparison"""
        time1 = Time("2024-01-01 12:00:00")
        time2 = Time("2024-01-01 12:00:00")
        time3 = Time("2024-01-01 13:00:00")

        assert time1 == time2
        assert time1 != time3

    def test_ordering(self):
        """Test time ordering comparison"""
        time1 = Time("2024-01-01 12:00:00")
        time2 = Time("2024-01-01 13:00:00")

        assert time1 < time2
        assert time2 > time1


class TestTimeStaticMethods:
    def test_min_max(self):
        """Test min and max static methods"""
        time1 = Time("2024-01-01 12:00:00")
        time2 = Time("2024-01-01 13:00:00")
        time3 = Time("2024-01-01 14:00:00")

        assert Time.min(time1, time2, time3) == time1
        assert Time.max(time1, time2, time3) == time3

    def test_available_timezones(self):
        """Test getting available timezones"""
        timezones = Time.get_available_timezones()
        assert isinstance(timezones, list)
        assert "UTC" in timezones
        assert "America/New_York" in timezones

class TestSchedule(unittest.TestCase):
    def setUp(self):
        self.schedule = Schedule()
        self.now = Time.now()

    def test_add_event(self):
        event = Event("Test Event", self.now, self.now.add(1, TimeUnit.HOURS))
        self.schedule.add_event(event)
        self.assertEqual(len(self.schedule), 1)

    def test_remove_event(self):
        event = Event("Test Event", self.now, self.now.add(1, TimeUnit.HOURS))
        self.schedule.add_event(event)
        removed = self.schedule.remove_event("Test Event")
        self.assertEqual(removed.name, "Test Event")
        self.assertEqual(len(self.schedule), 0)

    def test_update_event(self):
        event = Event("Test Event", self.now, self.now.add(1, TimeUnit.HOURS))
        self.schedule.add_event(event)
        updated = self.schedule.update_event("Test Event", description="Updated description")
        self.assertEqual(updated.description, "Updated description")

    def test_get_events(self):
        event1 = Event("Event 1", self.now, self.now.add(1, TimeUnit.HOURS), tags=["work"])
        event2 = Event("Event 2", self.now.add(2, TimeUnit.HOURS), self.now.add(3, TimeUnit.HOURS), tags=["personal"])
        self.schedule.add_event(event1)
        self.schedule.add_event(event2)
        events = self.schedule.get_events(self.now, self.now.add(4, TimeUnit.HOURS), tags=["work"])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].name, "Event 1")

    def test_find_free_slots(self):
        event = Event("Test Event", self.now.add(1, TimeUnit.HOURS), self.now.add(2, TimeUnit.HOURS))
        self.schedule.add_event(event)
        free_slots = self.schedule.find_free_slots(self.now, self.now.add(3, TimeUnit.HOURS), 30)
        self.assertEqual(len(free_slots), 1)

    def test_get_statistics(self):
        event1 = Event("Event 1", self.now, self.now.add(1, TimeUnit.HOURS), tags=["work"])
        event2 = Event("Event 2", self.now.add(2, TimeUnit.HOURS), self.now.add(3, TimeUnit.HOURS), tags=["personal"])
        self.schedule.add_event(event1)
        self.schedule.add_event(event2)
        stats = self.schedule.get_statistics(self.now, self.now.add(4, TimeUnit.HOURS))
        self.assertEqual(stats['total_events'], 2)
        self.assertEqual(stats['unique_tags'], 2)

    def test_conflict_detection(self):
        event1 = Event("Event 1", self.now, self.now.add(1, TimeUnit.HOURS))
        event2 = Event("Event 2", self.now.add(30, TimeUnit.MINUTES), self.now.add(90, TimeUnit.MINUTES))
        self.schedule.add_event(event1)
        with self.assertRaises(ScheduleConflictError):
            self.schedule.add_event(event2)

    # TODO: Add tests for recurring events
    # def test_recurring_event(self):
    #     event = Event("Recurring Event", self.now, self.now.add(1, TimeUnit.HOURS), recurrence='daily')
    #     self.schedule.add_event(event)
    #     next_occurrence = event.get_next_occurrence()
    #     self.assertIsNotNone(next_occurrence)
    #     self.assertEqual(next_occurrence.start_time, self.now.add(1, TimeUnit.DAYS))
    #     self.assertEqual(next_occurrence.end_time, self.now.add(1, TimeUnit.DAYS).add(1, TimeUnit.HOURS))

if __name__ == '__main__':
    unittest.main()