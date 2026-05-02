"""
main.py  –  Entry point for TSIS 3 Racer.
Orchestrates: Main Menu → Username → Game → Game Over → Leaderboard.
"""

import pygame
import sys
import os

import persistence
import ui
import racer

# ── Init ──────────────────────────────────────
pygame.init()
pygame.mixer.init()

SCREEN_W, SCREEN_H = 600, 800
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Racer – TSIS 3")
clock = pygame.time.Clock()

ASSET_DIR = os.path.join(os.path.dirname(__file__), "car_imgs")

def load_road():
    path = os.path.join(ASSET_DIR, "road.png")
    img  = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (SCREEN_W, SCREEN_H))


def main():
    settings  = persistence.load_settings()
    road_img  = load_road()
    username  = None

    while True:
        action = ui.main_menu(screen, clock, road_img)

        if action == "quit":
            pygame.quit()
            sys.exit()

        elif action == "leaderboard":
            ui.leaderboard_screen(screen, clock, road_img)

        elif action == "settings":
            ui.settings_screen(screen, clock, road_img, settings)
            # Reload after possible changes
            settings = persistence.load_settings()

        elif action == "play":
            # Ask for name once per session (or if not set yet)
            if username is None:
                username = ui.username_entry(screen, clock, road_img)

            # Run game – may loop on retry
            while True:
                score, distance, coins = racer.run_game(screen, clock, settings)

                # Save to leaderboard
                persistence.add_entry(username, score, distance, coins)

                result = ui.game_over_screen(
                    screen, clock, road_img, score, distance, coins)

                if result == "retry":
                    continue          # Play again immediately
                else:
                    break             # Back to main menu


if __name__ == "__main__":
    main()