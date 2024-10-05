from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()



setup(
    name='happy',
    version='0.2.0',
    packages=find_packages(),
    url='https://github/alaamer12/happy',
    license='MIT',
    author='Alaamer',
    author_email='alaamerthefirst@gmail.com',
    description='This is my first package',
    long_description="This is my first package printing only hello 'name' function",
    long_description_content_type='text/markdown',
    install_requires=[],
    keywords=['hello', 'name'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
