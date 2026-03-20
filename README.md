# PRACTICE 1 (Python Basics)

- **Variables** – cells that temporarily store a value  
- **Data types** – boolean / int / float / string …  
- **Indentation** – defines a block of code  

# PRACTICE 2 (Python Control Flow Basics)

- **Boolean** – True/False operators: `and` / `or`  
- **For / While loops**  
  - `for` – iterates when the number of iterations is known  
  - `while` – iterates until a condition is met  
- **If / Elif / Else** – used for different conditions to control output  
- **Shorthand writings in Python** – writing compact code lines

# PRACTICE 3 (Python Functions, Lambda, OOP & Inheritance)

## Functions

* **Function** – a reusable block of code that performs a specific task (`def`)
* **Parameters & Arguments** – values passed into a function
* **Default arguments** – parameter already has a preset value
* **Return statement (`return`)** – sends a result back to where the function was called
* ***args** – allows a function to accept many positional arguments (tuple)
* ****kwargs** – allows a function to accept named arguments (dictionary)

## Lambda Functions

* **Lambda function** – a small anonymous one-line function (`lambda x: x+1`)
* **map()** – applies a function to every element of a list
* **filter()** – selects elements that satisfy a condition
* **sorted(key=lambda …)** – custom sorting using a rule

## Classes (OOP Basics)

* **Class** – a blueprint/template for creating objects
* **Object (instance)** – a real entity created from a class
* **Attributes (variables)** – data stored inside an object
* **Methods (functions inside class)** – behaviors of an object
* **`__init__` constructor** – automatically runs when an object is created
* **Class variables** – shared by all objects of the class
* **Instance variables** – belong to a specific object
* **Class method (`@classmethod`)** – works with the class itself using `cls`

## Inheritance & Polymorphism

* **Inheritance** – a class (child) gets properties and methods from another class (parent)
* **`super()`** – calls the parent class constructor or method
* **Method overriding** – child class replaces a parent method with its own implementation
* **Multiple inheritance** – a class inherits from more than one parent class
* **Polymorphism** – same method name behaves differently depending on the object

# PRACTICE 4 (Python Iterators, Generators, Dates, Math, and JSON)

## Python Iterators & Generators

- **Iterator** – an object that can be iterated (looped) over using `iter()` and `next()`.
- **Generator** – a special function that yields values one at a time using `yield`.
- **`yield` statement** – pauses the function and returns a value, remembers state for next call.
- **Creating generators**:
  - Generate squares of numbers
  - Generate even numbers in a range
  - Generate numbers divisible by 3 and 4
  - Generate numbers in a given range or descending order

---

## Python Date & Time

- **`datetime` module** – used for date and time operations.
- **`datetime.now()`** – current date and time.
- **`timedelta(days=n)`** – time difference object used to add or subtract time.
- **Subtract days** – `new_date = current_date - timedelta(days=5)`
- **Yesterday / Today / Tomorrow** – calculate using `timedelta(days=±1)`
- **Drop microseconds** – `datetime.replace(microsecond=0)`
- **Difference in seconds** – `(date2 - date1).total_seconds()`

---

## Python Math Module

- **`math` module** – provides mathematical functions and constants.
- **Convert degrees to radians** – `math.radians(degree)`
- **Area of a trapezoid** – `0.5 * (base1 + base2) * height`
- **Area of regular polygon** – `(n * s^2) / (4 * math.tan(math.pi / n))`
  - `n` = number of sides, `s` = side length
- **Area of parallelogram** – `base * height`

---

## Python JSON Parsing

- **JSON (JavaScript Object Notation)** – a structured data format.
- **`json` module** – used to parse (`json.load()`) and create (`json.dump()`) JSON.
- **Read JSON file** – `with open("file.json", "r") as file: data = json.load(file)`
- **Access nested JSON**:
  - Use dictionary keys: `data["imdata"]`  
  - Access each item: `for item in data["imdata"]`  
  - Access nested attributes: `item["l1PhysIf"]["attributes"]`
- **Formatted output**:
  - Use `f"{value:width}"` to align columns
  - `width` = minimum number of characters for that column

---
# Practice5 – Receipt Parsing with Python RegEx

This project demonstrates how to extract structured data from a raw receipt using Python and regular expressions.

## Features
- Extract prices
- Extract product names
- Calculate total
- Extract date and time
- Extract payment method
- Output structured JSON

## Run

python receipt_parser.py

# Practice6

This repository contains examples of:

- File handling in Python
- Directory management
- Built-in functions

## Topics Covered

- File modes (r, w, a, x)
- Reading files (read, readline, readlines)
- Writing and appending files
- shutil file operations
- Directory management using os
- Built-in functions: map, filter, reduce, enumerate, zip, sorted

## Author
Student practice repository