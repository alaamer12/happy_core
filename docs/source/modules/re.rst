Regular Expression Patterns
===========================

.. module:: true.re

The ``re`` module provides a comprehensive collection of pre-defined regular expressions for common data validation tasks. These patterns are designed to handle various validation scenarios across different fields, making input validation simpler and more reliable.

Categories
----------

The module includes patterns for the following categories:

1. **Username Validation**
2. **Password Validation**
3. **Email Validation**
4. **Phone Number Validation**
5. **Zip Code Validation**
6. **Address Validation**
7. **Credit Card Validation**
8. **IP Address Validation**
9. **Date Validation**
10. **URL Validation**

Username Patterns
-----------------

.. py:data:: USERNAME_ONLY_LETTERS_MIN_3
   :type: str

   Matches usernames containing only letters with a minimum length of 3 characters.

   **Example:**
   
   - "John" matches
   - "Jo" doesn't match (too short)
   - "John123" doesn't match (contains numbers)

.. py:data:: USERNAME_LETTERS_AND_NUMBERS_MIN_3
   :type: str

   Matches usernames containing letters and numbers with a minimum length of 3 characters.

   **Example:**
   
   - "John123" matches
   - "Jo" doesn't match (too short)
   - "John@123" doesn't match (contains special characters)

Password Patterns
-----------------

.. py:data:: PASSWORD_MIN_8_WITH_NUMBER
   :type: str

   Matches passwords with a minimum length of 8 characters that include at least one number.

   **Example:**
   
   - "password123" matches
   - "password" doesn't match (no number)
   - "pass123" doesn't match (too short)

.. py:data:: PASSWORD_MIN_8_WITH_UPPERCASE
   :type: str

   Matches passwords with a minimum length of 8 characters that include at least one uppercase letter.

   **Example:**
   
   - "Password123" matches
   - "password123" doesn't match (no uppercase)
   - "Pass123" doesn't match (too short)

Credit Card Patterns
--------------------

.. py:data:: CREDIT_CARD_BASIC
   :type: str

   Matches basic credit card numbers with optional spaces or dashes.

   **Example:**
   
   - "1234 5678 9012 3456" matches
   - "1234-5678-9012-3456" matches
   - "1234.5678.9012.3456" doesn't match (invalid separator)

URL Patterns
------------

.. py:data:: URL_WITH_PORT
   :type: str

   Matches URLs that include a port number.

   **Example:**
   
   - "http://www.example.com:8080" matches
   - "http://www.example.com" doesn't match (no port)

.. py:data:: URL_WITH_SUBDOMAIN
   :type: str

   Matches URLs that include subdomains.

   **Example:**
   
   - "http://sub.example.com" matches
   - "https://sub.sub2.example.com" matches
   - "not-a-url" doesn't match

Usage
-----

To use these patterns in your code:

.. code-block:: python

   from true.re import USERNAME_ONLY_LETTERS_MIN_3
   import re

   # Validate a username
   username = "John"
   if re.match(USERNAME_ONLY_LETTERS_MIN_3, username):
       print("Valid username!")
   else:
       print("Invalid username!")