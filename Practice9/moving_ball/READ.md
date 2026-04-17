# Moving Ball Game 🔴

## Description

A simple interactive game where a red ball moves on the screen using keyboard controls.

## Features

* Red ball (50x50 pixels, radius 25)
* Moves with arrow keys
* Movement step: 20 pixels
* Boundary checking (ball cannot leave screen)
* Smooth rendering with frame control

## Controls

* **Arrow Keys** → Move the ball
* Close window to exit

## How It Works

* Draws ball using `pygame.draw.circle()`
* Detects keyboard input
* Checks screen boundaries before updating position

## Requirements

* Python 3.x
* pygame

## Run

```bash
python main.py
```
