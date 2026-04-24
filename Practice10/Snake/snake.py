"""
snake.py  –  Pygame Snake Game
================================
Extended from the lecture example with the following additions:
  1. Border / wall collision detection  → game over if snake hits a wall
  2. Food spawns only on empty cells    → never on the snake body or walls
  3. Levels – every 4 foods collected   → new level is triggered
  4. Speed increases with each level
  5. On-screen score and level counter
  6. Full code comments
"""

import pygame
import random
import sys

CELL      = 20            # Side length of each grid cell in pixels
COLS      = 30            # Number of columns (cells)
ROWS      = 30            # Number of rows (cells)
PANEL_H   = 50            # Height of the HUD panel above the play area

SCREEN_W  = COLS * CELL                    # 600 px
SCREEN_H  = ROWS * CELL + PANEL_H         # 650 px

# Colours
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GRAY  = (30,  30,  30)
GREEN      = (0,   200, 0)
DARK_GREEN = (0,   140, 0)
RED        = (220, 0,   0)
GOLD       = (255, 215, 0)
CYAN       = (0,   220, 220)
WALL_CLR   = (80,  80,  80)
BG_CLR     = (15,  15,  15)

FOODS_PER_LEVEL = 4        # Foods needed to advance one level

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Snake")

font_large = pygame.font.SysFont("Consolas", 38, bold=True)
font_med   = pygame.font.SysFont("Consolas", 24, bold=True)
font_small = pygame.font.SysFont("Consolas", 20)

clock = pygame.time.Clock()

#  HELPER: cell-to-pixel conversion
def cell_rect(col, row):
    """Return a pygame.Rect for a grid cell, accounting for the HUD panel."""
    return pygame.Rect(col * CELL, PANEL_H + row * CELL, CELL, CELL)

def draw_grid():
    """Draw a subtle grid to make the play area visible."""
    for c in range(COLS):
        for r in range(ROWS):
            rect = cell_rect(c, r)
            pygame.draw.rect(screen, DARK_GRAY, rect, 1)


def draw_walls():
    """
    Draw the border walls.
    The playable area is (1,1) to (COLS-2, ROWS-2);
    the outer ring of cells are walls.
    """
    for c in range(COLS):
        for r in range(ROWS):
            if c == 0 or c == COLS - 1 or r == 0 or r == ROWS - 1:
                pygame.draw.rect(screen, WALL_CLR, cell_rect(c, r))


def draw_snake(body):
    """Draw each segment of the snake; head is lighter than the body."""
    for i, (c, r) in enumerate(body):
        rect   = cell_rect(c, r)
        colour = GREEN if i > 0 else (180, 255, 180)   # lighter head
        pygame.draw.rect(screen, colour, rect)
        pygame.draw.rect(screen, DARK_GREEN, rect, 2)  # border per segment


def draw_food(pos):
    """Draw the food as a red circle inside the cell."""
    c, r   = pos
    rect   = cell_rect(c, r)
    centre = rect.center
    pygame.draw.circle(screen, RED,  centre, CELL // 2 - 2)
    pygame.draw.circle(screen, (255, 100, 100), (centre[0]-3, centre[1]-3), 4)


def draw_hud(score, level):
    """Render the HUD panel at the top of the window."""
    pygame.draw.rect(screen, (20, 20, 40), (0, 0, SCREEN_W, PANEL_H))

    score_surf = font_med.render(f"Score: {score}", True, WHITE)
    level_surf = font_med.render(f"Level: {level}", True, CYAN)

    screen.blit(score_surf, (12, 12))
    screen.blit(level_surf, (SCREEN_W - level_surf.get_width() - 12, 12))


def draw_text_centre(text, font, colour, y):
    surf = font.render(text, True, colour)
    screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, y))



def spawn_food(snake_body):
    """
    Choose a random cell that is:
      - NOT a wall (outer ring)
      - NOT occupied by the snake body
    Returns (col, row).
    """
    while True:
        c = random.randint(1, COLS - 2)   # Avoid columns 0 and COLS-1 (walls)
        r = random.randint(1, ROWS - 2)   # Avoid rows    0 and ROWS-1 (walls)
        if (c, r) not in snake_body:
            return (c, r)

def show_start_screen():
    """Show the title / instructions screen until the player presses Enter."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

        screen.fill(BG_CLR)
        draw_text_centre("SNAKE",                       font_large, GREEN, 160)
        draw_text_centre("Arrow Keys or WASD: Move",   font_small, WHITE, 270)
        draw_text_centre("Don't hit the walls or yourself!", font_small, WHITE, 310)
        draw_text_centre("Every 4 foods = next level",  font_small, CYAN,  350)
        draw_text_centre("Press ENTER to play",         font_med,   GOLD,  430)
        pygame.display.flip()
        clock.tick(30)


def show_game_over(score, level):
    """Show the game-over screen until the player restarts or quits."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True    # Restart
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        screen.fill(BG_CLR)
        draw_text_centre("GAME OVER",              font_large, RED,   200)
        draw_text_centre(f"Score : {score}",       font_med,   WHITE, 300)
        draw_text_centre(f"Level : {level}",       font_med,   CYAN,  340)
        draw_text_centre("ENTER – restart  |  ESC – quit", font_small, WHITE, 430)
        pygame.display.flip()
        clock.tick(30)


def show_level_up(level):
    """Brief non-blocking banner when the player levels up."""
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 1200:   # Show for 1.2 s
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        # Overlay semi-transparent panel
        overlay = pygame.Surface((SCREEN_W, 80), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, SCREEN_H // 2 - 40))
        draw_text_centre(f"LEVEL {level}!", font_large, GOLD, SCREEN_H // 2 - 20)
        pygame.display.flip()
        clock.tick(30)

def run_game():
    """
    Core gameplay.  Returns (score, level) when the snake dies.

    Direction encoding: (Δcol, Δrow)
      UP    = (0, -1)
      DOWN  = (0,  1)
      LEFT  = (-1, 0)
      RIGHT = (1,  0)
    """

    # ── Initial snake: three cells long, pointing right ──
    start_col, start_row = COLS // 2, ROWS // 2
    body      = [(start_col, start_row),
                 (start_col - 1, start_row),
                 (start_col - 2, start_row)]
    direction = (1, 0)             # Moving right
    next_dir  = direction          # Buffer for the next direction

    food = spawn_food(body)

    score         = 0
    level         = 1
    foods_eaten   = 0              # Running count since last level-up

    # ── Speed: base delay between moves (ms) ─
    BASE_DELAY  = 200              # Level 1: one move every 200 ms
    SPEED_STEP  = 20               # Each level reduces delay by 20 ms
    MIN_DELAY   = 60               # Fastest the snake can go

    def move_delay():
        """Current delay in ms based on the current level."""
        return max(MIN_DELAY, BASE_DELAY - (level - 1) * SPEED_STEP)

    last_move_time = pygame.time.get_ticks()   # Timestamp of the last move

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                # Arrow keys OR WASD – cannot reverse direction
                if event.key in (pygame.K_UP,    pygame.K_w) and direction != (0,  1):
                    next_dir = (0, -1)
                if event.key in (pygame.K_DOWN,  pygame.K_s) and direction != (0, -1):
                    next_dir = (0,  1)
                if event.key in (pygame.K_LEFT,  pygame.K_a) and direction != (1,  0):
                    next_dir = (-1, 0)
                if event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                    next_dir = (1,  0)

        now = pygame.time.get_ticks()
        if now - last_move_time >= move_delay():
            last_move_time = now
            direction      = next_dir   # Apply buffered direction

            # Calculate new head position
            head_c = body[0][0] + direction[0]
            head_r = body[0][1] + direction[1]
            new_head = (head_c, head_r)

            # ── Collision: wall
            if head_c <= 0 or head_c >= COLS - 1 or head_r <= 0 or head_r >= ROWS - 1:
                return score, level    # Hit a wall → game over

            # ── Collision: self 
            if new_head in body:
                return score, level    # Hit itself → game over

            # Prepend the new head
            body.insert(0, new_head)

            # ── Eating food 
            if new_head == food:
                score       += 10 * level        # More points at higher levels
                foods_eaten += 1
                food = spawn_food(body)           # Respawn food on empty cell

                # Level up every FOODS_PER_LEVEL foods
                if foods_eaten >= FOODS_PER_LEVEL:
                    foods_eaten  = 0
                    level       += 1
                    # Draw the current frame, then show the level-up banner
                    screen.fill(BG_CLR)
                    draw_grid()
                    draw_walls()
                    draw_snake(body)
                    draw_food(food)
                    draw_hud(score, level)
                    pygame.display.flip()
                    show_level_up(level)           # Brief pause with banner
            else:
                body.pop()             # Remove tail (snake doesn't grow)

        screen.fill(BG_CLR)
        draw_grid()
        draw_walls()
        draw_food(food)
        draw_snake(body)
        draw_hud(score, level)
        pygame.display.flip()

        clock.tick(120)                # High cap; actual speed governed by move_delay

def main():
    show_start_screen()
    while True:
        final_score, final_level = run_game()
        if not show_game_over(final_score, final_level):
            break


if __name__ == "__main__":
    main()