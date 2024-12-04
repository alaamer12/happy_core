"""
Basic usage examples of the Time class demonstrating core functionality.
"""

from true.time import Time, TimeFormat

def demo_basic_time_creation():
    """Demonstrate different ways to create Time objects."""
    print("=== Basic Time Creation ===")
    
    # Create time with current timestamp
    current_time = Time.now()
    print(f"Current time: {current_time}")
    
    # Create time with specific timezone
    ny_time = Time.now("America/New_York")
    print(f"New York time: {ny_time}")
    
    # Create time from timestamp
    timestamp_time = Time(1234567890.0)
    print(f"Time from timestamp: {timestamp_time}")
    
    # Create time from string
    string_time = Time("2024-02-20 15:30:00")
    print(f"Time from string: {string_time}")

def demo_time_formatting():
    """Demonstrate different time formatting options."""
    print("\n=== Time Formatting ===")
    
    time_obj = Time.now()
    
    # Different format types
    print(f"24-hour format: {time_obj.format(TimeFormat.HOUR_24)}")
    print(f"12-hour format: {time_obj.format(TimeFormat.HOUR_12)}")
    print(f"ISO format: {time_obj.format(TimeFormat.ISO)}")
    
    # Custom format
    custom_format = "%Y-%m-%d %I:%M %p"
    print(f"Custom format: {time_obj.format(custom_format=custom_format)}")
    
    # Different locales
    print(f"US locale: {time_obj.format(locale_name='en_US')}")
    print(f"French locale: {time_obj.format(locale_name='fr_FR')}")

def demo_time_components():
    """Demonstrate accessing time components."""
    print("\n=== Time Components ===")
    
    time_obj = Time.now()
    time_dict = time_obj.to_dict()
    
    print("Time components:")
    for key, value in time_dict.items():
        print(f"  {key}: {value}")
    
    print(f"\nQuarter of year: {time_obj.quarter}")
    print(f"Is DST: {time_obj.is_dst()}")

if __name__ == "__main__":
    demo_basic_time_creation()
    demo_time_formatting()
    demo_time_components()
