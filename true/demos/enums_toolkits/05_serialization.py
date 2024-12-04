from enum import Enum
from true.enums_toolkits import SerializedEnumMeta, metadata, MetadataConfig

# Create a test enum with metadata
@metadata(MetadataConfig(include_bit_length=True, custom_attributes={'category': 'http_status'}))
class HttpStatus(Enum, metaclass=SerializedEnumMeta):
    SUCCESS = 200
    NOT_FOUND = 404
    ERROR = 500

# Test serialization
print("\nOriginal enum:")
for status in HttpStatus:
    print(f"{status.name}: {status.value}")

# Convert to dict and back
dict_data = HttpStatus.to_dict()
print("\nSerialized dict:", dict_data)

# Create new enum from dict
NewHttpStatus = HttpStatus.from_dict("NewHttpStatus", dict_data['members'])

print("\nDeserialized enum:")
for status in NewHttpStatus:
    print(f"{status.name}: {status.value}")

# Test metadata preservation
if hasattr(NewHttpStatus, '_metadata_config'):
    print("\nMetadata preserved:", NewHttpStatus._metadata_config.__dict__)
