import unittest

from clara.index import PythonParsing, NotebookParsing, JavascriptParsing


class TestPythonParsing(unittest.TestCase):
    def setUp(self):
        self.example_code = """import os

def hello(text):
    print(text)

class Simple:
    def __init__(self):
        self.a = 1

hello("Hello!")"""

        self.expected_simplified_code = """import os

# Code for: def hello(text):

# Code for: class Simple:

hello("Hello!")"""

        self.expected_extracted_code = [
            "def hello(text):\n" "    print(text)",
            "class Simple:\n" "    def __init__(self):\n" "        self.a = 1",
        ]

    def test_extract_functions_classes(self):
        parser = PythonParsing(self.example_code)
        extracted_code = parser.extract_functions_classes()
        self.assertEqual(extracted_code, self.expected_extracted_code)

    def test_simplify_code(self):
        parser = PythonParsing(self.example_code)
        simplified_code = parser.simplify_code()
        self.assertEqual(simplified_code, self.expected_simplified_code)


class TestNotebookParsing(unittest.TestCase):
    def setUp(self):
        self.example_notebook = """
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Example Notebook"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "def hello(text):\\n",
    "    print(text)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "class Simple:\\n",
    "    def __init__(self):\\n",
    "        self.a = 1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "hello(\\"Hello!\\")"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 5
}
"""

        self.expected_simplified_markdown = """# Example Notebook

```python
import os
```

```python
def hello(text):
    print(text)
```

```python
class Simple:
    def __init__(self):
        self.a = 1
```

```python
hello("Hello!")
```"""

        self.expected_extracted_code = []

    def test_extract_functions_classes(self):
        parser = NotebookParsing(self.example_notebook)
        extracted_code = parser.extract_functions_classes()
        self.assertEqual(extracted_code, self.expected_extracted_code)

    def test_simplify_code(self):
        parser = NotebookParsing(self.example_notebook)
        simplified_markdown = parser.simplify_code()
        self.assertEqual(simplified_markdown, self.expected_simplified_markdown)


class TestJavascriptParsing(unittest.TestCase):
    def setUp(self):
        self.example_code = """const os = require('os');

function hello(text) {
    console.log(text);
}

class Simple {
    constructor() {
        this.a = 1;
    }
}

hello("Hello!");"""

        self.expected_simplified_code = """const os = require('os');

// Code for: function hello(text) {

// Code for: class Simple {

hello("Hello!");"""

        self.expected_extracted_code = [
            "function hello(text) {\n    console.log(text);\n}",
            "class Simple {\n    constructor() {\n        this.a = 1;\n    }\n}",
        ]

    def test_extract_functions_classes(self):
        parser = JavascriptParsing(self.example_code)
        extracted_code = parser.extract_functions_classes()
        self.assertEqual(extracted_code, self.expected_extracted_code)

    def test_simplify_code(self):
        parser = JavascriptParsing(self.example_code)
        simplified_code = parser.simplify_code()
        self.assertEqual(simplified_code, self.expected_simplified_code)
