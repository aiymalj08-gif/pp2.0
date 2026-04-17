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

#  PRACTICE 7 (📱 PhoneBook (Python + PostgreSQL))

## 📌 Description

A simple console-based PhoneBook application that demonstrates integration between **Python** and **PostgreSQL** using the `psycopg2` library.

---

## 🧠 Core Idea

The project implements basic **CRUD operations**:

* Create → INSERT
* Read → SELECT
* Update → UPDATE
* Delete → DELETE

---

## ⚙️ Features

* Add contacts
* View all contacts
* Search by name or phone
* Update contact info
* Delete contacts
* Import data from CSV

---

## 🔌 Tech Stack

* Python
* PostgreSQL
* psycopg2

---

## ▶️ Run

```bash
pip install psycopg2-binary
python phonebook.py
```
# Practice 8 – PostgreSQL Functions & Stored Procedures

## Overview
This practice extends the PhoneBook app from Practice 7 by moving core data logic into the PostgreSQL database layer using PL/pgSQL functions and stored procedures.

---

## Files
| File | Description |
|---|---|
| `phonebook.py` | Main app with menu-driven interface |
| `functions.sql` | PostgreSQL functions (search, pagination) |
| `procedures.sql` | PostgreSQL stored procedures (upsert, bulk insert, delete) |
| `config.py` | Database connection settings |
| `connect.py` | psycopg2 connection helper |

---

## How to Run

**1. Set up the database**
```bash
psql -U postgres -d phonebook_db -f functions.sql
psql -U postgres -d phonebook_db -f procedures.sql
```

**2. Run the app**
```bash
python phonebook.py
```

---

## Features

### Functions
- `get_contacts_by_pattern(p_pattern)` — returns all contacts whose name or phone contains the given pattern (case-insensitive)
- `get_contacts_paginated(p_limit, p_offset)` — returns contacts in pages using `LIMIT` and `OFFSET`

### Stored Procedures
- `upsert_contact(name, phone)` — inserts a new contact; if the name already exists, updates the phone
- `bulk_insert_contacts(names[], phones[])` — loops through arrays, validates each phone with regex `^[0-9]{11}$`, skips and logs invalid entries
- `delete_contact(p_name, p_phone)` — deletes a contact by name, phone, or both

---

## Menu Options
| Option | Action |
|---|---|
| 1 | Upsert a contact |
| 2 | Bulk insert from comma-separated input |
| 3 | Search by name or phone pattern |
| 4 | View contacts by page |
| 5 | Get all contacts |
| 6 | Delete by name |
| 7 | Delete by phone |
| 8 | Import from CSV |
| 0 | Exit |

---

## Phone Validation
Phones must be exactly **11 digits** with no spaces or dashes.

✅ `79161234567`
❌ `7-916-123-45-67`
❌ `abc`


# 🎮 Practice 9 - Pygame Projects Collection

This project contains several small **Python + Pygame** applications created for practice:

- 🕒 Mickey’s Clock
- 🎵 Music Player
- 🏀 Moving Ball Animation

---

## 📁 Project Structure
