"""
Examples of enum metadata and serialization features.
"""

from enum import Enum

from true.enums_toolkits import metadata, MetadataConfig, SerializedEnumMeta


def demo_basic_metadata():
    """Demonstrate basic metadata usage."""
    print("=== Basic Metadata ===")

    # Create enum with default metadata
    @metadata()
    class Status(Enum):
        PENDING = 0
        ACTIVE = 1
        INACTIVE = 2

    print("Default metadata:")
    for member in Status:
        print(f"\n{member.describe}")


#
def demo_custom_metadata():
    """Demonstrate custom metadata configuration."""
    print("\n=== Custom Metadata ===")
    #
    # Create custom metadata config
    config = MetadataConfig(
        include_bit_length=True,
        include_type_info=True,
        custom_attributes={
            "Category": "System Status",
            "Reversible": True
        },
        default_value="Unknown"
    )

    #
    @metadata(config)
    class ProcessState(Enum):
        STARTING = 0
        RUNNING = 1
        STOPPING = 2
        STOPPED = 3

    #
    print("Custom metadata configuration:")
    for member in ProcessState:
        print(f"\n{member.describe}")
    #
    # Set custom description
    try:
        ProcessState.set_description(ProcessState.STARTING, "Process is actively executing tasks")
        print(f"\nCustom description for RUNNING:")
        print(ProcessState.RUNNING.describe)
    except Exception as e:
        print(f"Error setting description: {e}")


#
def demo_serialization():
    """Demonstrate serialization features."""
    print("\n=== Serialization ===")

    #
    #     # Create enum with serialization support
    class Color(Enum, metaclass=SerializedEnumMeta):
        RED = "#FF0000"
        GREEN = "#00FF00"
        BLUE = "#0000FF"

    #
    # Convert to dictionary
    color_dict = Color.to_dict()
    print("Enum as dictionary:")
    for name, value in color_dict.items():
        print(f"{name}: {value}")
    #
    # Create new enum from dictionary
    members = {
        "SUCCESS": 200,
        "NOT_FOUND": 404,
        "ERROR": 500
    }
    #
    StatusCode = Color.from_dict("StatusCode", members)
    print("\nEnum from dictionary:")
    for member in StatusCode:
        print(f"{member.name}: {member.value}")

    #     # JSON serialization
    json_data = Color.to_json()
    print("\nEnum as JSON:")
    print(json_data)
    #
    # Create enum from JSON
    json_members = '{"SMALL": 1, "MEDIUM": 2, "LARGE": 3}'
    Size = Color.from_json("Size", json_members)
    print("\nEnum from JSON:")
    for member in Size:
        print(f"{member.name}: {member.value}")


#
def demo_combined_features():
    """Demonstrate combination of metadata and serialization."""
    print("\n=== Combined Features ===")

    @metadata(MetadataConfig(
        custom_attributes={"API_Version": "1.0"}
    ))
    class ApiStatus(Enum, metaclass=SerializedEnumMeta):
        OK = {"code": 200, "message": "Success"}
        ERROR = {"code": 500, "message": "Internal Error"}
        NOT_FOUND = {"code": 404, "message": "Resource Not Found"}

    #
    # Show metadata
    print("API Status with metadata:")
    for member in ApiStatus:
        print(f"\n{member.describe}")

    #     # Serialize
    print("\nAPI Status as dictionary:")
    api_dict = ApiStatus.to_dict()
    for name, value in api_dict.items():
        print(f"{name}: {value}")


if __name__ == "__main__":
    demo_basic_metadata()
    demo_custom_metadata()
    demo_serialization()
    demo_combined_features()
