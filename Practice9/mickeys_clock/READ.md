# Mickey's Clock 🕒

## Description

This project is a simple digital-style clock built using Pygame.
It displays the current system time using Mickey Mouse hands as clock hands.

## Features

* Displays minutes and seconds in real-time
* Right hand shows **minutes**
* Left hand shows **seconds**
* Clock updates every second
* Uses image rotation for realistic hand movement

## Controls

* Close window to exit the application

## How It Works

* Retrieves system time using Python
* Converts time into rotation angles
* Uses `pygame.transform.rotate()` to rotate the hands

## Requirements

* Python 3.x
* pygame

## Run

```bash
python main.py
```
