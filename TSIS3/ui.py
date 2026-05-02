"""
ui.py  –  All non-gameplay Pygame screens for TSIS 3 Racer.
Screens:
  • username_entry()   – type your name before playing
  • main_menu()        – Play / Leaderboard / Settings / Quit
  • settings_screen()  – sound toggle, car colour, difficulty
  • leaderboard_screen() – top 10 table
  • game_over_screen() – score summary, Retry / Main Menu
"""

import pygame
import sys
import persistence

# ── Colours ───────────────────────────────────
WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
GRAY    = (80,  80,  80)
LGRAY   = (160, 160, 160)
YELLOW  = (255, 215, 0)
RED     = (200, 0,   0)
GREEN   = (0,   180, 0)
BLUE    = (0,   120, 220)
ORANGE  = (255, 140, 0)
PANEL   = (30,  30,  50)
DARK    = (15,  15,  25)

CAR_COLOURS = ["Red", "Blue", "Green", "Yellow"]
DIFFICULTIES = ["Easy", "Normal", "Hard"]


# ─────────────────────────────────────────────
#  Shared drawing helpers
# ─────────────────────────────────────────────

def _btn_rect(cx, y, w=260, h=46):
    return pygame.Rect(cx - w // 2, y, w, h)


def draw_button(surface, rect, text, font,
                fg=WHITE, bg=GRAY, hover=False, active=False):
    colour = (100, 180, 255) if active else ((110, 110, 110) if hover else bg)
    pygame.draw.rect(surface, colour, rect, border_radius=8)
    pygame.draw.rect(surface, LGRAY,  rect, 2, border_radius=8)
    img = font.render(text, True, fg)
    surface.blit(img, (rect.centerx - img.get_width()  // 2,
                       rect.centery - img.get_height() // 2))


def draw_title(surface, text, font, y, colour=YELLOW):
    img = font.render(text, True, colour)
    surface.blit(img, (surface.get_width() // 2 - img.get_width() // 2, y))


def draw_bg(surface, road_img):
    surface.fill(DARK)
    # dim road background
    tmp = road_img.copy()
    tmp.set_alpha(60)
    surface.blit(tmp, (0, 0))


def clicked(rect, pos):
    return rect.collidepoint(pos)


# ─────────────────────────────────────────────
#  Username entry
# ─────────────────────────────────────────────

def username_entry(screen, clock, road_img):
    """
    Blocking screen.  Returns the player's name string (non-empty).
    """
    W, H   = screen.get_size()
    font_h = pygame.font.SysFont("Arial", 40, bold=True)
    font_b = pygame.font.SysFont("Arial", 26, bold=True)
    font_s = pygame.font.SysFont("Arial", 20)

    name = ""
    cursor_visible = True
    cursor_timer   = 0

    while True:
        dt = clock.tick(60)
        cursor_timer += dt
        if cursor_timer >= 500:
            cursor_visible = not cursor_visible
            cursor_timer   = 0

        mouse_pos = pygame.mouse.get_pos()
        ok_rect   = _btn_rect(W // 2, H // 2 + 80)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 16:
                    name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if clicked(ok_rect, mouse_pos) and name.strip():
                    return name.strip()

        draw_bg(screen, road_img)
        draw_title(screen, "RACER",         font_h, H // 2 - 180)
        draw_title(screen, "Enter your name", font_b, H // 2 - 110, WHITE)

        # Input box
        box = pygame.Rect(W // 2 - 150, H // 2 - 60, 300, 50)
        pygame.draw.rect(screen, (50, 50, 70), box, border_radius=6)
        pygame.draw.rect(screen, LGRAY, box, 2, border_radius=6)
        display = name + ("|" if cursor_visible else " ")
        txt_img  = font_b.render(display, True, WHITE)
        screen.blit(txt_img, (box.x + 10,
                               box.centery - txt_img.get_height() // 2))

        hover = clicked(ok_rect, mouse_pos)
        draw_button(screen, ok_rect, "START", font_b,
                    bg=GREEN if name.strip() else GRAY, hover=hover)

        hint = font_s.render("Press Enter or click START", True, LGRAY)
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H // 2 + 140))

        pygame.display.flip()


# ─────────────────────────────────────────────
#  Main Menu
# ─────────────────────────────────────────────

def main_menu(screen, clock, road_img):
    """
    Returns one of: 'play' | 'leaderboard' | 'settings' | 'quit'
    """
    W, H   = screen.get_size()
    font_h = pygame.font.SysFont("Arial", 52, bold=True)
    font_b = pygame.font.SysFont("Arial", 28, bold=True)

    cx = W // 2
    buttons = [
        ("play",        "▶  Play",        _btn_rect(cx, H // 2 - 60)),
        ("leaderboard", "🏆  Leaderboard", _btn_rect(cx, H // 2 + 10)),
        ("settings",    "⚙  Settings",    _btn_rect(cx, H // 2 + 80)),
        ("quit",        "✕  Quit",         _btn_rect(cx, H // 2 + 150)),
    ]

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for action, _, rect in buttons:
                    if clicked(rect, mouse_pos):
                        return action

        draw_bg(screen, road_img)
        draw_title(screen, "RACER",           font_h, H // 2 - 170, YELLOW)
        draw_title(screen, "Arrow Keys to Move", pygame.font.SysFont("Arial", 20),
                   H // 2 - 110, LGRAY)

        for action, label, rect in buttons:
            hover = clicked(rect, mouse_pos)
            col   = RED if action == "quit" else GRAY
            draw_button(screen, rect, label, font_b, bg=col, hover=hover)

        pygame.display.flip()


# ─────────────────────────────────────────────
#  Settings screen
# ─────────────────────────────────────────────

def settings_screen(screen, clock, road_img, settings: dict):
    """
    Mutates and saves `settings` in place.
    Returns when the player clicks Back.
    """
    W, H   = screen.get_size()
    font_h = pygame.font.SysFont("Arial", 40, bold=True)
    font_b = pygame.font.SysFont("Arial", 24, bold=True)
    font_s = pygame.font.SysFont("Arial", 20)
    cx     = W // 2

    back_rect  = _btn_rect(cx, H - 100, 200, 42)

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        # Build option rects fresh each frame (they depend on current values)
        sound_rect  = _btn_rect(cx + 100, H // 2 - 120, 140, 38)
        diff_rects  = [_btn_rect(cx - 120 + i * 130, H // 2 - 30, 120, 38)
                       for i in range(3)]
        color_rects = [_btn_rect(cx - 180 + i * 120, H // 2 + 70, 110, 38)
                       for i in range(4)]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Sound toggle
                if clicked(sound_rect, mouse_pos):
                    settings["sound"] = not settings["sound"]
                    persistence.save_settings(settings)
                # Difficulty
                for i, r in enumerate(diff_rects):
                    if clicked(r, mouse_pos):
                        settings["difficulty"] = DIFFICULTIES[i]
                        persistence.save_settings(settings)
                # Car colour
                for i, r in enumerate(color_rects):
                    if clicked(r, mouse_pos):
                        settings["car_color"] = CAR_COLOURS[i]
                        persistence.save_settings(settings)
                # Back
                if clicked(back_rect, mouse_pos):
                    return

        draw_bg(screen, road_img)
        draw_title(screen, "SETTINGS", font_h, 60)

        # Sound toggle
        lbl = font_b.render("Sound:", True, WHITE)
        screen.blit(lbl, (cx - 180, H // 2 - 112))
        s_active = settings["sound"]
        draw_button(screen, sound_rect,
                    "ON" if s_active else "OFF", font_b,
                    bg=GREEN if s_active else RED,
                    active=False,
                    hover=clicked(sound_rect, mouse_pos))

        # Difficulty
        lbl = font_b.render("Difficulty:", True, WHITE)
        screen.blit(lbl, (cx - 180, H // 2 - 22))
        for i, r in enumerate(diff_rects):
            active = (settings["difficulty"] == DIFFICULTIES[i])
            draw_button(screen, r, DIFFICULTIES[i], font_s,
                        active=active, hover=clicked(r, mouse_pos))

        # Car colour
        lbl = font_b.render("Car Colour:", True, WHITE)
        screen.blit(lbl, (cx - 180, H // 2 + 78))
        colour_map = {"Red": RED, "Blue": BLUE, "Green": GREEN, "Yellow": YELLOW}
        for i, r in enumerate(color_rects):
            active = (settings["car_color"] == CAR_COLOURS[i])
            draw_button(screen, r, CAR_COLOURS[i], font_s,
                        bg=colour_map[CAR_COLOURS[i]],
                        active=active, hover=clicked(r, mouse_pos))

        draw_button(screen, back_rect, "◀  Back", font_b,
                    hover=clicked(back_rect, mouse_pos))

        pygame.display.flip()


# ─────────────────────────────────────────────
#  Leaderboard screen
# ─────────────────────────────────────────────

def leaderboard_screen(screen, clock, road_img):
    """Display top 10 scores. Returns when Back is clicked."""
    W, H   = screen.get_size()
    font_h = pygame.font.SysFont("Arial", 40, bold=True)
    font_b = pygame.font.SysFont("Arial", 22, bold=True)
    font_s = pygame.font.SysFont("Arial", 18)
    cx     = W // 2

    back_rect = _btn_rect(cx, H - 80, 200, 42)
    entries   = persistence.load_leaderboard()

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if clicked(back_rect, mouse_pos):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return

        draw_bg(screen, road_img)
        draw_title(screen, "LEADERBOARD", font_h, 30, YELLOW)

        # Header row
        header = font_b.render(
            f"{'#':<4}{'Name':<14}{'Score':>8}{'Dist':>8}{'Coins':>7}",
            True, LGRAY)
        screen.blit(header, (cx - header.get_width() // 2, 100))
        pygame.draw.line(screen, LGRAY,
                         (cx - 200, 128), (cx + 200, 128), 1)

        if not entries:
            msg = font_s.render("No entries yet – play a game!", True, LGRAY)
            screen.blit(msg, (cx - msg.get_width() // 2, 160))
        else:
            for rank, e in enumerate(entries, 1):
                colour = YELLOW if rank == 1 else (LGRAY if rank <= 3 else WHITE)
                row = font_s.render(
                    f"{rank:<4}{e['name']:<14}{e['score']:>8}"
                    f"{e['distance']:>7}m{e['coins']:>6}",
                    True, colour)
                screen.blit(row, (cx - row.get_width() // 2, 128 + rank * 30))

        draw_button(screen, back_rect, "◀  Back", font_b,
                    hover=clicked(back_rect, mouse_pos))
        pygame.display.flip()


# ─────────────────────────────────────────────
#  Game Over screen
# ─────────────────────────────────────────────

def game_over_screen(screen, clock, road_img,
                     score, distance, coins):
    """
    Returns 'retry' or 'menu'.
    """
    W, H   = screen.get_size()
    font_h = pygame.font.SysFont("Arial", 52, bold=True)
    font_b = pygame.font.SysFont("Arial", 28, bold=True)
    font_s = pygame.font.SysFont("Arial", 22)
    cx     = W // 2

    retry_rect = _btn_rect(cx - 145, H // 2 + 100, 240, 46)
    menu_rect  = _btn_rect(cx + 145, H // 2 + 100, 240, 46)

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if clicked(retry_rect, mouse_pos):
                    return "retry"
                if clicked(menu_rect, mouse_pos):
                    return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "retry"
                if event.key == pygame.K_ESCAPE:
                    return "menu"

        draw_bg(screen, road_img)
        draw_title(screen, "GAME OVER", font_h, H // 2 - 200, RED)

        stats = [
            (f"Score    : {score}",    WHITE),
            (f"Distance : {distance} m", WHITE),
            (f"Coins    : {coins}",    YELLOW),
        ]
        for i, (text, col) in enumerate(stats):
            img = font_s.render(text, True, col)
            screen.blit(img, (cx - img.get_width() // 2,
                               H // 2 - 90 + i * 44))

        draw_button(screen, retry_rect, "↺  Retry",     font_b,
                    bg=GREEN, hover=clicked(retry_rect, mouse_pos))
        draw_button(screen, menu_rect,  "⌂  Main Menu", font_b,
                    bg=BLUE,  hover=clicked(menu_rect,  mouse_pos))

        pygame.display.flip()