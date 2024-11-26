"""
A collection of regular expressions (regex patterns) for common data validation tasks across a variety of fields, including usernames, passwords, emails, phone numbers, zip codes, addresses, credit cards, IP addresses, and dates.

Each regex pattern is tailored to match specific requirements, making it easy to validate inputs that meet common standards and constraints. The module includes patterns for the following categories:

1. **Username**: Patterns for validating usernames with varying rules, such as minimum length, allowed characters, and format restrictions (e.g., starting with a letter, containing only letters and numbers, or disallowing special characters at the start/end).

2. **Password**: Patterns for validating passwords with constraints on length, complexity (e.g., containing uppercase letters, numbers, or special characters), and other criteria such as disallowing whitespace or consecutive characters.

3. **Email**: Patterns for validating emails with different levels of strictness, allowing or disallowing subdomains, Unicode characters, and enforcing specific formats in line with RFC 5322.

4. **Phone Number**: Patterns for validating phone numbers in various formats, including U.S. standard, international format, and phone numbers with extensions.

5. **Zip Code**: Patterns for validating postal codes for specific regions, including the U.S. and U.K.

6. **Address**: Patterns for validating address formats with requirements such as including a street number, street name, and potentially city/state/ZIP.

7. **Credit Card**: Patterns for validating credit card numbers across various providers (e.g., Visa, Mastercard, American Express) and formats (e.g., with or without spaces/dashes).

8. **IP Address**: Patterns for validating IP addresses in both IPv4 and IPv6 formats, with options for including port numbers.

9. **Date**: Patterns for validating date formats commonly used around the world, such as YYYY-MM-DD, MM/DD/YYYY, and DD-MM-YYYY.

Each regex pattern is accompanied by a description of the criteria it enforces and examples of inputs that would match or fail to match.
"""

# _________________________________________Username_________________________________________
USERNAME_ONLY_LETTERS_MIN_3 = r"^[A-Za-z]{3,}$"
# Description: Matches usernames with only letters, minimum 3 characters
# Example: "John" matches, "Jo" doesn't, "John123" doesn't

USERNAME_LETTERS_AND_NUMBERS_MIN_3 = r"^[A-Za-z0-9]{3,}$"
# Description: Matches usernames with letters and numbers, minimum 3 characters
# Example: "John123" matches, "Jo" doesn't, "John_doe" doesn't

USERNAME_WITH_UNDERSCORES_MIN_3 = r"^[A-Za-z0-9_]{3,}$"
# Description: Matches usernames with letters, numbers, and underscores, minimum 3 characters
# Example: "John_doe_123" matches, "Jo" doesn't, "John-doe" doesn't

USERNAME_WITH_DASHES_AND_UNDERSCORES_MIN_3 = r"^[A-Za-z0-9_-]{3,}$"
# Description: Matches usernames with letters, numbers, underscores, and dashes, minimum 3 characters
# Example: "John-doe_123" matches, "Jo" doesn't, "John@doe" doesn't

USERNAME_NO_CONSECUTIVE_SPECIAL_CHARS = r"^(?!.*[_-]{2})[A-Za-z0-9_-]{3,}$"
# Description: Matches usernames with letters, numbers, underscores, and dashes, no consecutive special characters
# Example: "John-doe_123" matches, "John__doe" doesn't

USERNAME_STARTS_WITH_LETTER = r"^[A-Za-z][A-Za-z0-9_-]{2,}$"
# Description: Matches usernames starting with a letter, followed by letters, numbers, underscores, or dashes
# Example: "John123" matches, "123John" doesn't

USERNAME_MAX_20_CHARACTERS = r"^[A-Za-z0-9_-]{3,20}$"
# Description: Matches usernames with letters, numbers, underscores, and dashes, 3-20 characters
# Example: "John_doe_123" matches, "ThisUsernameIsTooLong123" doesn't

USERNAME_NOT_NUMERIC_ONLY = r"^(?!\d+$)[A-Za-z0-9_-]{3,}$"
# Description: Matches usernames with letters, numbers, underscores, and dashes, not entirely numeric
# Example: "John123" matches, "123456" doesn't

USERNAME_NO_PREFIX_SUFFIX = r"^(?![_-])[A-Za-z0-9_-]{3,}(?<![_-])$"
# Description: Matches usernames not starting or ending with underscore or dash
# Example: "John_doe" matches, "_John_" doesn't

USERNAME_INCLUDE_LETTER_AND_NUMBER = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9_-]{3,}$"
# Description: Matches usernames containing at least one letter and one number
# Example: "John123" matches, "JohnDoe" doesn't

USERNAME_MAX_LENGTH_15 = r"^[A-Za-z0-9_-]{3,15}$"
# Description: Matches usernames with letters, numbers, underscores, and dashes, 3-15 characters
# Example: "John_doe" matches, "ThisUsernameIsTooLong" doesn't

# _________________________________________Password_________________________________________
PASSWORD_MIN_8 = r"^.{8,}$"
# Description: Matches passwords with a minimum of 8 characters
# Example: "password123" matches, "pass" doesn't

PASSWORD_MIN_8_WITH_NUMBER = r"^(?=.*\d).{8,}$"
# Description: Matches passwords with a minimum of 8 characters, including at least one number
# Example: "password123" matches, "password" doesn't

PASSWORD_MIN_8_WITH_UPPERCASE = r"^(?=.*[A-Z]).{8,}$"
# Description: Matches passwords with a minimum of 8 characters, including at least one uppercase letter
# Example: "Password123" matches, "password123" doesn't

PASSWORD_MIN_8_WITH_NUMBER_UPPERCASE_AND_SPECIAL_CHAR = r"^(?=.*\d)(?=.*[A-Z])(?=.*[@#$%^&*]).{8,}$"
# Description: Matches passwords with a minimum of 8 characters, including at least one number, one uppercase letter, and one special character
# Example: "Password123$" matches, "password123" doesn't

PASSWORD_STRONG = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&*!]).{12,}$"
# Description: Matches strong passwords with a minimum of 12 characters, including lowercase, uppercase, number, and special character
# Example: "StrongPass123!" matches, "WeakPass" doesn't

PASSWORD_NO_WHITESPACE = r"^(?=\S{8,}).*$"
# Description: Matches passwords with a minimum of 8 characters and no whitespace
# Example: "NoSpacePass123" matches, "Space Pass 123" doesn't

PASSWORD_MAX_64_CHARACTERS = r"^.{8,64}$"
# Description: Matches passwords between 8 and 64 characters
# Example: "GoodPassword123" matches, "TooLongPassword..." (65+ chars) doesn't

PASSWORD_NO_REPEATED_CHARS = r"^(?!.*(.)\1\1).{8,}$"
# Description: Matches passwords with no more than two consecutive repeated characters
# Example: "GoodPass123" matches, "Passsword123" doesn't

PASSWORD_NO_SEQUENTIAL_CHARS = r"^(?!.*(?:abc|123)).{8,}$"
# Description: Matches passwords without common sequential characters
# Example: "RandomPass987" matches, "Password123" doesn't

# _________________________________________Email_________________________________________
EMAIL_BASIC = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
# Description: Matches basic email format
# Example: "user@example.com" matches, "user@example" doesn't

EMAIL_WITHOUT_SUBDOMAIN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,}$"
# Description: Matches email addresses without subdomains
# Example: "user@example.com" matches, "user@sub.example.com" doesn't

EMAIL_STRICT = r"^(?i)(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}|(?:\[(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\]))$"
# Description: Matches email addresses strictly according to RFC 5322
# Example: "user.name+tag@example.com" matches, "user@example" doesn't

EMAIL_ALLOWING_UNICODE = r"^[\w.!#$%&'*+/=?`{|}~-]+@[\w-]+\.[A-Za-z]{2,}$"
# Description: Matches email addresses allowing Unicode characters
# Example: "用户@例子.com" matches, "user@example" doesn't

EMAIL_WITH_TLD_LIMIT = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}$"
# Description: Matches email addresses with top-level domains between 2 and 6 characters
# Example: "user@example.com" matches, "user@example.website" doesn't

# _________________________________________Phone_________________________________________
PHONE_NUMBER_US = r"^(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}$"
# Description: Matches US phone numbers in various formats
# Example: "(123) 456-7890" matches, "123-456-7890" matches, "1234567890" matches

PHONE_NUMBER_INTERNATIONAL = r"^\+\d{1,3}[-.\s]?\d{4,14}(?:x\d+)?$"
# Description: Matches international phone numbers with optional extension
# Example: "+1 123-456-7890" matches, "+44 20 7123 4567" matches

PHONE_NUMBER_WITH_EXTENSION = r"^(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}(?:\s?(?:ext|x)\s?\d{2,5})?$"
# Description: Matches phone numbers with optional extensions
# Example: "(123) 456-7890 ext 1234" matches, "123-456-7890 x99" matches

PHONE_NUMBER_NO_SEPARATOR = r"^\d{10}$"
# Description: Matches 10-digit phone numbers without separators
# Example: "1234567890" matches, "123-456-7890" doesn't

# _________________________________________Zip Code_________________________________________
ZIP_CODE_US = r"^\d{5}(?:[-\s]\d{4})?$"
# Description: Matches US ZIP codes with optional 4-digit extension
# Example: "12345" matches, "12345-6789" matches

ZIP_CODE_UK = r"^(GIR 0AA|(?:[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}))$"
# Description: Matches UK postcodes
# Example: "SW1A 1AA" matches, "GIR 0AA" matches

# _________________________________________Address_________________________________________
ADDRESS_WITH_NUMBER_AND_STREET = r"^\d+\s[A-Za-z\s]{2,}$"
# Description: Matches simple street addresses with number and street name
# Example: "123 Main Street" matches, "P.O. Box 123" doesn't

ADDRESS_FULL = r"^\d+\s[A-Za-z\s]{2,},\s[A-Za-z\s]{2,},\s[A-Z]{2}\s\d{5}(?:-\d{4})?$"
# Description: Matches full US addresses with street, city, state, and ZIP code
# Example: "123 Main St, Anytown, NY 12345" matches

# _________________________________________Credit Card_________________________________________
CREDIT_CARD_BASIC = r"^(?:\d[ -]*?){13,19}$"
# Description: Matches basic credit card numbers with optional spaces or dashes
# Example: "1234 5678 9012 3456" matches, "1234-5678-9012-3456" matches

CREDIT_CARD_VISA = r"^4[0-9]{12}(?:[0-9]{3})?$"
# Description: Matches Visa card numbers
# Example: "4111111111111111" matches, "5111111111111111" doesn't

CREDIT_CARD_MASTERCARD = r"^(5[1-5][0-9]{14}|2(2[2-9][0-9]{12}|[3-6][0-9]{13}|7[01][0-9]{12}|720[0-9]{12}))$"
# Description: Matches Mastercard numbers
# Example: "5555555555554444" matches, "4111111111111111" doesn't

CREDIT_CARD_AMEX = r"^3[47][0-9]{13}$"
# Description: Matches American Express card numbers
# Example: "371449635398431" matches, "4111111111111111" doesn't

CREDIT_CARD_DISCOVER = r"^(6011|65|64[4-9]|622(?:12[6-9]|1[3-9]\d|[2-8]\d\d|9[01]\d|92[0-5]))\d{12}$"
# Description: Matches Discover card numbers
# Example: "6011111111111117" matches, "4111111111111111" doesn't

CREDIT_CARD_NO_SPACES_OR_DASHES = r"^\d{16}$"
# Description: Matches 16-digit credit card numbers without spaces or dashes
# Example: "1234567890123456" matches, "1234 5678 9012 3456" doesn't

# _________________________________________IP Address_________________________________________
IPV4_BASIC = r"^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}$"
# Description: Matches IPv4 addresses
# Example: "192.168.0.1" matches, "256.1.2.3" doesn't

IPV6_BASIC = r"^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4})$"
# Description: Matches basic IPv6 addresses
# Example: "2001:0db8:85a3:0000:0000:8a2e:0370:7334" matches

IPV4_WITH_PORT = r"^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}(:\d{1,5})?$"
# Description: Matches IPv4 addresses with optional port number
# Example: "192.168.0.1:8080" matches, "192.168.0.1" matches

IP_ADDRESS_BOTH_IPV4_IPV6 = r"^((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}|([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4})$"
# Description: Matches both IPv4 and IPv6 addresses
# Example: "192.168.0.1" matches, "2001:0db8:85a3:0000:0000:8a2e:0370:7334" matches

# _________________________________________Date_________________________________________
DATE_YYYY_MM_DD = r"^(?:(?:19|20)\d\d)-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$"
# Description: Matches dates in YYYY-MM-DD format
# Example: "2023-05-15" matches, "2023/05/15" doesn't

DATE_MM_DD_YYYY = r"^(0[1-9]|1[0-2])\/(0[1-9]|[12]\d|3[01])\/((19|20)\d\d)$"
# Description: Matches dates in MM/DD/YYYY format
# Example: "05/15/2023" matches, "13/15/2023" doesn't

DATE_DD_MM_YYYY = r"^(0[1-9]|[12]\d|3[01])\-(0[1-9]|1[0-2])\-(19|20)\d\d$"
# Description: Matches dates in DD-MM-YYYY format
# Example: "15-05-2023" matches, "32-05-2023" doesn't

DATETIME_ISO8601 = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])T([01]\d|2[0-3]):[0-5]\d:[0-5]\d(Z|[+-][01]\d:[0-5]\d)$"
# Description: Matches dates and times in ISO 8601 format
# Example: "2023-05-15T14:30:00Z" matches, "2023-05-15 14:30:00" doesn't

DATE_WITH_MONTH_NAME = r"^(0?[1-9]|[12]\d|3[01])\s(January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}$"
# Description: Matches dates with full month names
# Example: "15 May 2023" matches, "32 May 2023" doesn't

DATE_WITH_ABBREVIATED_MONTH = r"^(0?[1-9]|[12]\d|3[01])\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4}$"
# Description: Matches dates with abbreviated month names
# Example: "15 May 2023" matches, "32 May 2023" doesn't

# _________________________________________Time_________________________________________
TIME_24_HOUR = r"^([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$"
# Description: Matches 24-hour time format with optional seconds
# Example: "14:30" matches, "14:30:45" matches, "25:00" doesn't

TIME_12_HOUR_WITH_AM_PM = r"^(0[1-9]|1[0-2]):[0-5]\d\s?(AM|PM|am|pm)$"
# Description: Matches 12-hour time format with AM/PM indicator
# Example: "02:30 PM" matches, "14:30 PM" doesn't

# _________________________________________URL_________________________________________
URL_BASIC = r"^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/?$"
# Description: Matches basic URL format
# Example: "https://www.example.com" matches, "https://example" doesn't

URL_PATH_ONLY = r"^\/(?:[^\/\0]+\/)*[^\/\0]*$"
# Description: Matches URL paths without domain
# Example: "/path/to/page" matches, "https://example.com/path" doesn't

URL_WITH_QUERY_PARAMETERS = r"^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/?(\?[;&a-z\d%_.~+=-]*)?$"
# Description: Matches URLs with optional query parameters
# Example: "https://www.example.com/page?param1=value1&param2=value2" matches

URL_SECURE = r"^https:\/\/([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/?$"
# Description: Matches secure (HTTPS) URLs only
# Example: "https://www.example.com" matches, "http://www.example.com" doesn't

URL_WITH_PORT = r"^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6}):\d{1,5}([\/\w .-]*)*\/?$"
# Description: Matches URLs with port numbers
# Example: "http://www.example.com:8080" matches, "http://www.example.com" doesn't

URL_WITH_SUBDOMAIN = r"^(https?:\/\/)?([a-z0-9-]+\.)+[a-z0-9]{2,}([\/\w .-]*)*\/?$"
# Description: Matches URLs with subdomains
# Example: "https://subdomain.example.com" matches, "https://example" doesn't

# _________________________________________File path_________________________________________
FILE_PATH_WINDOWS = r"^[a-zA-Z]:\\(?:[^\\/:*?""<>|\r\n]+\\)*[^\\/:*?""<>|\r\n]*$"
# Description: Matches Windows file paths
# Example: "C:\folder\file.txt" matches, "/home/user/file.txt" doesn't

FILE_PATH_UNIX = r"^\/(?:[^\/\0]+\/)*[^\/\0]*$"
# Description: Matches Unix-like file paths
# Example: "/home/user/file.txt" matches, "C:\folder\file.txt" doesn't

# _________________________________________Color codes_________________________________________
HEX_COLOR_CODE = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
# Description: Matches hexadecimal color codes
# Example: "#FF0000" matches, "#GG0000" doesn't

RGB_COLOR_CODE = r"^rgb\((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d),(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d),(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\)$"
# Description: Matches RGB color codes
# Example: "rgb(255,0,0)" matches, "rgb(256,0,0)" doesn't

# _________________________________________UUID_________________________________________
UUID = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
# Description: Matches version 4 UUIDs
# Example: "123e4567-e89b-12d3-a456-426614174000" matches, "123e4567-e89b-12d3-a456-42661417400" doesn't


# _________________________________________VERSIONS_________________________________________
SEMVER_STYLE = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
# Description: Matches semantic versioning format
# Example: "1.2.3" matches, "1.2.3-alpha.1" matches as well

DATE_VERSION_STYLE = r"^(19|20)\d\d\.(0[1-9]|1[0-2])\.(0[1-9]|[12][0-9]|3[01])$"
# Description: Matches date versioning format
# Example: "2020.01.01" matches, "2020.1.1" doesn't

CALVER_STYLE = r"^(19|20)\d\d\.(0[1-9]|[1-4][0-9]|5[0-3])$"
# Description: Matches calendar versioning format
# Example: "2020.01" matches, "2020.1" doesn't

MAJOR_MINOR_VERSION_STYLE = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)$"
# Description: Matches major and minor versioning format
# Example: "1.2" matches, "1.2.3" doesn't

MAJOR_MINOR_PATCH_TAG_STYLE = r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-(alpha|beta|rc)\.(0|[1-9]\d*))?$"
# Description: Matches major, minor, and patch versioning format with optional pre-release tags
# Example: "1.2.3" matches, "1.2.3-alpha.1" matches as well

# _________________________________________Other_________________________________________
ONLY_NUMBERS = r"^\d+$"
# Description: Matches strings containing only numbers
# Example: "12345" matches, "123abc" doesn't

ONLY_LOWER_CASE = r"^[a-z]+$"
# Description: Matches strings containing only lowercase letters
# Example: "abcde" matches, "ABCDE" doesn't

ONLY_UPPER_CASE = r"^[A-Z]+$"
# Description: Matches strings containing only uppercase letters
# Example: "ABCDE" matches, "abcde" doesn't

ONLY_LETTERS = r"^[a-zA-Z]+$"
# Description: Matches strings containing only letters (upper or lowercase)
# Example: "ABCDEabcde" matches, "ABCDE123" doesn't

ONLY_ALPHANUMERIC = r"^[a-zA-Z0-9]+$"
# Description: Matches strings containing only letters and numbers
# Example: "ABC123" matches, "ABC_123" doesn't
