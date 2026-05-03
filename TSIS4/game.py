# game.py – All game entities, drawing helpers, and screen functions
#
# Covers:
#   • Food  (weighted, timed, poison)
#   • PowerUp  (speed boost / slow motion / shield)
#   • Obstacle  (static wall blocks, level 3+)
#   • All draw_* helpers
#   • All screen functions (main menu, game over, leaderboard, settings)
#   • run_game()  – the core game loop

import pygame
import random
import sys
import json
from pathlib import Path

from config import *

# ── Module-level pygame objects (initialised in main.py before import) ────────
screen = None
clock  = None
font_large = font_med = font_small = None

SETTINGS_FILE = Path(__file__).parent / "settings.json"


# ═══════════════════════════════════════════════════════════════════════════════
#  SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

def load_settings() -> dict:
    defaults = {"snake_color": list(GREEN), "grid_overlay": True, "sound": False}
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
            defaults.update(data)
        except Exception:
            pass
    return defaults


def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)


# ═══════════════════════════════════════════════════════════════════════════════
#  DRAWING HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def cell_rect(col, row) -> pygame.Rect:
    return pygame.Rect(col * CELL, PANEL_H + row * CELL, CELL, CELL)


def draw_grid():
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, DARK_GRAY, cell_rect(c, r), 1)


def draw_walls():
    for c in range(COLS):
        for r in range(ROWS):
            if c == 0 or c == COLS - 1 or r == 0 or r == ROWS - 1:
                pygame.draw.rect(screen, WALL_CLR, cell_rect(c, r))


def draw_obstacles(obstacles: list):
    for (c, r) in obstacles:
        rect = cell_rect(c, r)
        pygame.draw.rect(screen, OBSTACLE_CLR, rect)
        pygame.draw.rect(screen, (80, 50, 20), rect, 2)


def draw_snake(body: list, snake_color: tuple):
    head_color = tuple(min(255, v + 80) for v in snake_color)
    dark_color = tuple(max(0, v - 60) for v in snake_color)
    for i, (c, r) in enumerate(body):
        rect   = cell_rect(c, r)
        colour = snake_color if i > 0 else head_color
        pygame.draw.rect(screen, colour, rect)
        pygame.draw.rect(screen, dark_color, rect, 2)


def draw_food(food):
    c, r    = food.pos
    rect    = cell_rect(c, r)
    centre  = rect.center
    pygame.draw.circle(screen, food.color, centre, CELL // 2 - 2)
    pygame.draw.circle(screen, WHITE, (centre[0] - 3, centre[1] - 3), 3)
    # Timer bar
    elapsed  = pygame.time.get_ticks() - food.spawn_time
    ratio    = max(0.0, 1.0 - elapsed / food.lifetime)
    bar_w    = int(CELL * ratio)
    bar_rect = pygame.Rect(rect.x, rect.y + CELL - 3, bar_w, 3)
    pygame.draw.rect(screen, food.color, bar_rect)


def draw_poison(poison):
    if poison is None:
        return
    c, r   = poison.pos
    rect   = cell_rect(c, r)
    centre = rect.center
    pygame.draw.circle(screen, DARK_RED, centre, CELL // 2 - 2)
    # Skull-ish X
    pygame.draw.line(screen, WHITE,
                     (centre[0] - 5, centre[1] - 5),
                     (centre[0] + 5, centre[1] + 5), 2)
    pygame.draw.line(screen, WHITE,
                     (centre[0] + 5, centre[1] - 5),
                     (centre[0] - 5, centre[1] + 5), 2)


def draw_powerup(powerup):
    if powerup is None:
        return
    c, r   = powerup.pos
    rect   = cell_rect(c, r)
    centre = rect.center
    colors = {
        "speed":  ORANGE,
        "slow":   BLUE,
        "shield": PURPLE,
    }
    col = colors.get(powerup.kind, WHITE)
    pygame.draw.circle(screen, col, centre, CELL // 2 - 2)
    labels = {"speed": "»", "slow": "«", "shield": "★"}
    lbl = font_small.render(labels.get(powerup.kind, "?"), True, WHITE)
    screen.blit(lbl, lbl.get_rect(center=centre))
    # Timer bar
    elapsed  = pygame.time.get_ticks() - powerup.spawn_time
    ratio    = max(0.0, 1.0 - elapsed / POWERUP_FIELD_DURATION)
    bar_w    = int(CELL * ratio)
    bar_rect = pygame.Rect(rect.x, rect.y + CELL - 3, bar_w, 3)
    pygame.draw.rect(screen, col, bar_rect)


def draw_hud(score, level, personal_best, shield_active, effect_label):
    pygame.draw.rect(screen, (20, 20, 40), (0, 0, SCREEN_W, PANEL_H))
    score_surf = font_med.render(f"Score:{score}", True, WHITE)
    level_surf = font_med.render(f"Lv:{level}", True, CYAN)
    pb_surf    = font_small.render(f"Best:{personal_best}", True, GOLD)
    screen.blit(score_surf, (8, 6))
    screen.blit(level_surf, (160, 6))
    screen.blit(pb_surf,    (8, 30))
    if shield_active:
        sh = font_small.render("SHIELD", True, PURPLE)
        screen.blit(sh, (SCREEN_W - sh.get_width() - 8, 30))
    if effect_label:
        eff = font_small.render(effect_label, True, ORANGE)
        screen.blit(eff, (SCREEN_W - eff.get_width() - 8, 8))


def draw_text_centre(text, font, colour, y):
    surf = font.render(text, True, colour)
    screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, y))


def draw_button(text, rect: pygame.Rect, hover: bool):
    col = (70, 70, 120) if hover else (40, 40, 80)
    pygame.draw.rect(screen, col, rect, border_radius=8)
    pygame.draw.rect(screen, CYAN, rect, 2, border_radius=8)
    lbl = font_med.render(text, True, WHITE)
    screen.blit(lbl, lbl.get_rect(center=rect.center))


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTITIES
# ═══════════════════════════════════════════════════════════════════════════════

class Food:
    TYPES = [
        {"color": RED,  "score": 10, "weight": 60, "lifetime": 6000},
        {"color": GOLD, "score": 25, "weight": 30, "lifetime": 4500},
        {"color": CYAN, "score": 50, "weight": 10, "lifetime": 3000},
    ]

    def __init__(self, snake_body, obstacles):
        self.obstacles = obstacles
        self.spawn(snake_body)

    def spawn(self, snake_body):
        t = random.choices(self.TYPES, weights=[x["weight"] for x in self.TYPES])[0]
        self.color      = t["color"]
        self.score      = t["score"]
        self.lifetime   = t["lifetime"]
        self.pos        = _free_cell(snake_body, self.obstacles)
        self.spawn_time = pygame.time.get_ticks()

    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime


class PoisonFood:
    LIFETIME = 7000  # ms

    def __init__(self, snake_body, obstacles):
        self.pos        = _free_cell(snake_body, obstacles)
        self.spawn_time = pygame.time.get_ticks()

    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time > self.LIFETIME


class PowerUp:
    KINDS = ["speed", "slow", "shield"]

    def __init__(self, snake_body, obstacles, food_pos):
        self.kind       = random.choice(self.KINDS)
        self.pos        = _free_cell(snake_body, obstacles, exclude={food_pos})
        self.spawn_time = pygame.time.get_ticks()

    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time > POWERUP_FIELD_DURATION


# ═══════════════════════════════════════════════════════════════════════════════
#  OBSTACLE GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_obstacles(level: int, snake_body: list) -> list:
    """
    Place OBSTACLES_PER_LEVEL * (level - 2) wall blocks starting from level 3.
    Guarantees no block is placed on the snake body or adjacent to the head.
    """
    if level < 3:
        return []

    count      = OBSTACLES_PER_LEVEL * (level - 2)
    forbidden  = set(snake_body)
    # Also forbid cells adjacent to the head so the snake isn't immediately trapped
    hc, hr = snake_body[0]
    for dc, dr in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        forbidden.add((hc + dc, hr + dr))

    blocks = []
    attempts = 0
    while len(blocks) < count and attempts < 2000:
        attempts += 1
        c = random.randint(2, COLS - 3)
        r = random.randint(2, ROWS - 3)
        if (c, r) not in forbidden and (c, r) not in blocks:
            blocks.append((c, r))
    return blocks


# ═══════════════════════════════════════════════════════════════════════════════
#  UTILITY
# ═══════════════════════════════════════════════════════════════════════════════

def _free_cell(snake_body, obstacles, exclude: set | None = None) -> tuple:
    """Pick a random cell not occupied by the snake, obstacles, or exclude set."""
    occupied = set(snake_body) | set(obstacles)
    if exclude:
        occupied |= exclude
    while True:
        c = random.randint(1, COLS - 2)
        r = random.randint(1, ROWS - 2)
        if (c, r) not in occupied:
            return (c, r)


# ═══════════════════════════════════════════════════════════════════════════════
#  SCREENS
# ═══════════════════════════════════════════════════════════════════════════════

def screen_username() -> str:
    """
    Display a text-input prompt and return the entered username.
    Supports backspace; Enter confirms; minimum 1 character.
    """
    username = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.unicode.isprintable() and len(username) < 16:
                    username += event.unicode

        screen.fill(BG_CLR)
        draw_text_centre("SNAKE",             font_large, GREEN,  120)
        draw_text_centre("Enter your name:",  font_med,   WHITE,  240)

        # Input box
        box = pygame.Rect(SCREEN_W // 2 - 160, 290, 320, 44)
        pygame.draw.rect(screen, (40, 40, 80), box, border_radius=6)
        pygame.draw.rect(screen, CYAN,         box, 2, border_radius=6)
        name_surf = font_med.render(username + "_", True, WHITE)
        screen.blit(name_surf, name_surf.get_rect(center=box.center))

        draw_text_centre("Press ENTER to continue", font_small, GOLD, 360)
        pygame.display.flip()
        clock.tick(30)


def screen_main_menu() -> str:
    """
    Show the main menu.  Returns one of: 'play', 'leaderboard', 'settings', 'quit'.
    """
    buttons = {
        "play":        pygame.Rect(SCREEN_W // 2 - 110, 260, 220, 48),
        "leaderboard": pygame.Rect(SCREEN_W // 2 - 110, 330, 220, 48),
        "settings":    pygame.Rect(SCREEN_W // 2 - 110, 400, 220, 48),
        "quit":        pygame.Rect(SCREEN_W // 2 - 110, 470, 220, 48),
    }
    labels = {
        "play": "Play", "leaderboard": "Leaderboard",
        "settings": "Settings", "quit": "Quit",
    }

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for key, rect in buttons.items():
                    if rect.collidepoint(mx, my):
                        return key

        screen.fill(BG_CLR)
        draw_text_centre("SNAKE", font_large, GREEN, 150)
        draw_text_centre("Arrow Keys / WASD to move", font_small, WHITE, 210)
        for key, rect in buttons.items():
            draw_button(labels[key], rect, rect.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(30)


def screen_game_over(score, level, personal_best) -> str:
    """Returns 'retry' or 'menu'."""
    btn_retry = pygame.Rect(SCREEN_W // 2 - 120, 400, 220, 48)
    btn_menu  = pygame.Rect(SCREEN_W // 2 - 120, 465, 220, 48)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_retry.collidepoint(mx, my): return "retry"
                if btn_menu.collidepoint(mx, my):  return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return "retry"
                if event.key == pygame.K_ESCAPE: return "menu"

        screen.fill(BG_CLR)
        draw_text_centre("GAME OVER",             font_large, RED,   160)
        draw_text_centre(f"Score : {score}",      font_med,   WHITE, 260)
        draw_text_centre(f"Level  : {level}",     font_med,   CYAN,  305)
        draw_text_centre(f"Best   : {personal_best}", font_med, GOLD, 350)
        draw_button("Retry",     btn_retry, btn_retry.collidepoint(mx, my))
        draw_button("Main Menu", btn_menu,  btn_menu.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(30)


def screen_leaderboard(rows: list):
    """Display top-10 table; Back button returns."""
    btn_back = pygame.Rect(SCREEN_W // 2 - 80, SCREEN_H - 70, 160, 44)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_back.collidepoint(mx, my):
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        screen.fill(BG_CLR)
        draw_text_centre("LEADERBOARD", font_large, GOLD, 30)

        # Header
        hdr = font_small.render(
            f"{'#':<4}{'Name':<16}{'Score':>7}{'Lv':>5}{'Date':>13}", True, CYAN)
        screen.blit(hdr, (30, 90))
        pygame.draw.line(screen, CYAN, (30, 115), (SCREEN_W - 30, 115), 1)

        for i, row in enumerate(rows):
            rank, uname, score, lv, date = row
            color  = GOLD if rank == 1 else WHITE
            line   = f"{rank:<4}{str(uname):<16}{score:>7}{lv:>5}{str(date):>13}"
            surf   = font_small.render(line, True, color)
            screen.blit(surf, (30, 125 + i * 28))

        draw_button("Back", btn_back, btn_back.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(30)


def screen_settings(settings: dict) -> dict:
    """
    Settings screen: toggle grid, toggle sound, cycle snake color.
    Returns updated settings dict (caller saves to disk).
    """
    COLOR_OPTIONS = [
        ("Green",  [0, 200, 0]),
        ("Blue",   [50, 100, 255]),
        ("Orange", [255, 140, 0]),
        ("Purple", [160, 32, 240]),
        ("White",  [220, 220, 220]),
    ]

    # Find current color index
    def color_idx():
        for i, (_, c) in enumerate(COLOR_OPTIONS):
            if c == settings["snake_color"]:
                return i
        return 0

    col_idx = color_idx()

    btn_grid  = pygame.Rect(SCREEN_W // 2 - 140, 220, 280, 44)
    btn_sound = pygame.Rect(SCREEN_W // 2 - 140, 285, 280, 44)
    btn_col_l = pygame.Rect(SCREEN_W // 2 - 160, 350, 44, 44)
    btn_col_r = pygame.Rect(SCREEN_W // 2 + 116, 350, 44, 44)
    btn_save  = pygame.Rect(SCREEN_W // 2 - 100, 450, 200, 48)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_grid.collidepoint(mx, my):
                    settings["grid_overlay"] = not settings["grid_overlay"]
                if btn_sound.collidepoint(mx, my):
                    settings["sound"] = not settings["sound"]
                if btn_col_l.collidepoint(mx, my):
                    col_idx = (col_idx - 1) % len(COLOR_OPTIONS)
                    settings["snake_color"] = COLOR_OPTIONS[col_idx][1]
                if btn_col_r.collidepoint(mx, my):
                    col_idx = (col_idx + 1) % len(COLOR_OPTIONS)
                    settings["snake_color"] = COLOR_OPTIONS[col_idx][1]
                if btn_save.collidepoint(mx, my):
                    return settings

        screen.fill(BG_CLR)
        draw_text_centre("SETTINGS", font_large, CYAN, 80)

        grid_lbl  = f"Grid Overlay: {'ON' if settings['grid_overlay'] else 'OFF'}"
        sound_lbl = f"Sound: {'ON' if settings['sound'] else 'OFF'}"
        draw_button(grid_lbl,  btn_grid,  btn_grid.collidepoint(mx, my))
        draw_button(sound_lbl, btn_sound, btn_sound.collidepoint(mx, my))

        # Color picker
        cname, cval = COLOR_OPTIONS[col_idx]
        pygame.draw.rect(screen, tuple(cval),
                         pygame.Rect(SCREEN_W // 2 - 110, 350, 220, 44), border_radius=6)
        pygame.draw.rect(screen, WHITE,
                         pygame.Rect(SCREEN_W // 2 - 110, 350, 220, 44), 2, border_radius=6)
        csurf = font_med.render(cname, True, BLACK if sum(cval) > 400 else WHITE)
        screen.blit(csurf, csurf.get_rect(center=(SCREEN_W // 2, 372)))
        draw_button("<", btn_col_l, btn_col_l.collidepoint(mx, my))
        draw_button(">", btn_col_r, btn_col_r.collidepoint(mx, my))
        draw_text_centre("Snake Color", font_small, WHITE, 325)

        draw_button("Save & Back", btn_save, btn_save.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(30)


# ═══════════════════════════════════════════════════════════════════════════════
#  LEVEL-UP BANNER
# ═══════════════════════════════════════════════════════════════════════════════

def show_level_up(level: int):
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 1200:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        overlay = pygame.Surface((SCREEN_W, 80), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, SCREEN_H // 2 - 40))
        draw_text_centre(f"LEVEL {level}!", font_large, GOLD, SCREEN_H // 2 - 20)
        pygame.display.flip()
        clock.tick(30)


# ═══════════════════════════════════════════════════════════════════════════════
#  CORE GAME LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def run_game(settings: dict, personal_best: int) -> tuple[int, int]:
    """
    Run one game session.
    Returns (score, level_reached).
    """
    snake_color = tuple(settings["snake_color"])
    show_grid   = settings["grid_overlay"]

    # ── Snake initialisation ──────────────────────────────────────────────────
    sc, sr = COLS // 2, ROWS // 2
    body   = [(sc, sr), (sc - 1, sr), (sc - 2, sr)]
    direction = (1, 0)
    next_dir  = (1, 0)

    score       = 0
    level       = 1
    foods_eaten = 0

    obstacles = []   # Level 3+ blocks

    food   = Food(body, obstacles)
    poison = None          # PoisonFood | None
    powerup = None         # PowerUp | None

    # Poison spawn schedule
    POISON_INTERVAL = 8000   # ms between poison spawns
    last_poison_spawn = pygame.time.get_ticks()

    # Power-up spawn schedule
    POWERUP_INTERVAL = 12000
    last_powerup_spawn = pygame.time.get_ticks()

    # Active effect state
    effect_kind      = None   # "speed" | "slow" | "shield" | None
    effect_end_time  = 0
    shield_active    = False
    speed_multiplier = 1.0

    def move_delay() -> int:
        base = max(MIN_DELAY, BASE_DELAY - (level - 1) * SPEED_STEP)
        if effect_kind == "speed":
            return max(MIN_DELAY, int(base * 0.55))
        if effect_kind == "slow":
            return int(base * 1.7)
        return base

    last_move_time = pygame.time.get_ticks()

    while True:
        now = pygame.time.get_ticks()

        # ── Events ───────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP,    pygame.K_w) and direction != (0,  1):
                    next_dir = (0, -1)
                if event.key in (pygame.K_DOWN,  pygame.K_s) and direction != (0, -1):
                    next_dir = (0,  1)
                if event.key in (pygame.K_LEFT,  pygame.K_a) and direction != (1,  0):
                    next_dir = (-1, 0)
                if event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                    next_dir = (1,  0)

        # ── Effect expiry ─────────────────────────────────────────────────────
        if effect_kind and now > effect_end_time:
            effect_kind = None

        # ── Spawn poison periodically ─────────────────────────────────────────
        if poison is None and now - last_poison_spawn > POISON_INTERVAL:
            poison = PoisonFood(body, obstacles)
            last_poison_spawn = now

        if poison and poison.is_expired():
            poison = None
            last_poison_spawn = now

        # ── Spawn power-up periodically ───────────────────────────────────────
        if powerup is None and now - last_powerup_spawn > POWERUP_INTERVAL:
            powerup = PowerUp(body, obstacles, food.pos)
            last_powerup_spawn = now

        if powerup and powerup.is_expired():
            powerup = None
            last_powerup_spawn = now

        # ── Food expiry ───────────────────────────────────────────────────────
        if food.is_expired():
            food.spawn(body)

        # ── Move tick ────────────────────────────────────────────────────────
        if now - last_move_time >= move_delay():
            last_move_time = now
            direction      = next_dir

            hc = body[0][0] + direction[0]
            hr = body[0][1] + direction[1]
            new_head = (hc, hr)

            # Wall collision
            if hc <= 0 or hc >= COLS - 1 or hr <= 0 or hr >= ROWS - 1:
                if shield_active:
                    shield_active = False
                    # Bounce back: just don't move
                    hc, hr = body[0]
                    new_head = (hc, hr)
                    body.insert(0, new_head)
                    body.pop()
                else:
                    return score, level

            # Self collision
            elif new_head in body:
                if shield_active:
                    shield_active = False
                else:
                    return score, level

            # Obstacle collision
            elif new_head in obstacles:
                if shield_active:
                    shield_active = False
                else:
                    return score, level

            else:
                body.insert(0, new_head)

                # ── Eat regular food ─────────────────────────────────────────
                if new_head == food.pos:
                    score       += food.score
                    foods_eaten += 1
                    food.spawn(body)

                    if foods_eaten >= FOODS_PER_LEVEL:
                        foods_eaten = 0
                        level      += 1
                        # Regenerate obstacles for new level
                        obstacles = generate_obstacles(level, body)
                        # Redraw before banner
                        _render(screen, show_grid, body, snake_color,
                                obstacles, food, poison, powerup,
                                score, level, personal_best,
                                shield_active, effect_kind)
                        show_level_up(level)

                # ── Eat poison ───────────────────────────────────────────────
                elif poison and new_head == poison.pos:
                    poison = None
                    last_poison_spawn = now
                    body.pop()          # Remove tail first (no grow)
                    if len(body) > 1:
                        body.pop()      # Shorten by 2 total
                    else:
                        return score, level  # Too short → game over
                    continue            # Skip normal tail removal

                # ── Collect power-up ─────────────────────────────────────────
                elif powerup and new_head == powerup.pos:
                    kind = powerup.kind
                    powerup = None
                    last_powerup_spawn = now

                    if kind == "shield":
                        shield_active = True
                        effect_kind   = None
                    else:
                        effect_kind     = kind
                        effect_end_time = now + POWERUP_EFFECT_DURATION

                    body.pop()   # Power-up doesn't grow snake

                else:
                    body.pop()   # Normal move: remove tail

        # ── Render ───────────────────────────────────────────────────────────
        effect_label = None
        if effect_kind:
            remaining = max(0, effect_end_time - pygame.time.get_ticks()) // 1000
            effect_label = f"{'FAST' if effect_kind == 'speed' else 'SLOW'} {remaining}s"

        _render(screen, show_grid, body, snake_color,
                obstacles, food, poison, powerup,
                score, level, personal_best,
                shield_active, effect_label)
        clock.tick(120)


def _render(screen, show_grid, body, snake_color,
            obstacles, food, poison, powerup,
            score, level, personal_best,
            shield_active, effect_label):
    screen.fill(BG_CLR)
    if show_grid:
        draw_grid()
    draw_walls()
    draw_obstacles(obstacles)
    draw_food(food)
    draw_poison(poison)
    draw_powerup(powerup)
    draw_snake(body, snake_color)
    draw_hud(score, level, personal_best, shield_active, effect_label)
    pygame.display.flip()