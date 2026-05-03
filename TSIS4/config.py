# config.py – Shared constants for the Snake game

CELL    = 20
COLS    = 30
ROWS    = 30
PANEL_H = 50

SCREEN_W = COLS * CELL          # 600
SCREEN_H = ROWS * CELL + PANEL_H  # 650

FOODS_PER_LEVEL = 4

# Default colours
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GRAY  = (30,  30,  30)
GREEN      = (0,   200, 0)
DARK_GREEN = (0,   140, 0)
RED        = (220, 0,   0)
DARK_RED   = (139, 0,   0)
GOLD       = (255, 215, 0)
CYAN       = (0,   220, 220)
PURPLE     = (160, 32,  240)
ORANGE     = (255, 140, 0)
BLUE       = (50,  100, 255)
WALL_CLR   = (80,  80,  80)
BG_CLR     = (15,  15,  15)
OBSTACLE_CLR = (120, 80, 40)

# Speed settings
BASE_DELAY = 200
SPEED_STEP = 20
MIN_DELAY  = 60

# Power-up durations (ms)
POWERUP_FIELD_DURATION = 8000   # disappears from field after 8 s
POWERUP_EFFECT_DURATION = 5000  # effect lasts 5 s

# Obstacle count per level (starts at level 3)
OBSTACLES_PER_LEVEL = 5