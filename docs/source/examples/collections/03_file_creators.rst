File Creators and Metadata
==========================

This example demonstrates the usage of file creators and metadata operations in the True-Core collections module.

Key Concepts
------------

1. File Creators
   - Specialized classes for creating dummy files of various types
   - Support for common file formats (PDF, DOCX, JPG, etc.)
   - Customizable file sizes and content

2. DummyFile Class
   - Unified interface for creating multiple file types
   - Support for custom file types with custom headers
   - Batch file creation capabilities

3. Multimedia Creation
   - Create test images with specified dimensions
   - Generate test videos from images
   - Create audio files with specified duration and frequency

4. File Metadata
   - Access basic file properties (name, size, extension)
   - Calculate file checksums (MD5)
   - Get comprehensive file statistics

Example Code
------------

Creating Files with Specific Creators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../../true/demos/collections/03_file_creators.py
   :language: python
   :lines: 17-32
   :caption: File Creator Examples

Using the DummyFile Class
~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../../true/demos/collections/03_file_creators.py
   :language: python
   :lines: 34-51
   :caption: DummyFile Usage Examples

Creating Multimedia Files
~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../../true/demos/collections/03_file_creators.py
   :language: python
   :lines: 53-71
   :caption: Multimedia Creation Examples

Working with File Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../../true/demos/collections/03_file_creators.py
   :language: python
   :lines: 73-102
   :caption: File Metadata Examples

Key Features
------------

1. File Creation
   - Support for multiple file formats
   - Customizable file sizes
   - Custom headers for specialized formats

2. Multimedia Support
   - Image generation
   - Video creation
   - Audio file generation

3. Metadata Operations
   - Basic file properties
   - File