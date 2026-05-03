# main.py – Entry point for the TSIS 4 Snake game
#
# Initialises Pygame, wires together db.py, game.py, and the settings file.
# Database is optional: if psycopg2 / PostgreSQL is unavailable the game runs
# in offline mode (no leaderboard persistence).

import sys
import pygame

# ── Pygame bootstrap (must happen before game.py loads) ─────────────────────
pygame.init()

from config import SCREEN_W, SCREEN_H
import game as g

# Inject shared pygame objects into game module
g.screen     = pygame.display.set_mode((SCREEN_W, SCREEN_H))
g.clock      = pygame.time.Clock()
g.font_large = pygame.font.SysFont("Consolas", 38, bold=True)
g.font_med   = pygame.font.SysFont("Consolas", 24, bold=True)
g.font_small = pygame.font.SysFont("Consolas", 20)
pygame.display.set_caption("Snake – TSIS 4")

# ── Optional database ────────────────────────────────────────────────────────
DB_AVAILABLE = False
try:
    import db
    db.init_db()
    DB_AVAILABLE = True
except Exception as e:
    print(f"[DB] Offline mode – {e}")


def main():
    # 1. Load settings
    settings = g.load_settings()

    # 2. Username entry (always shown; used for DB or just displayed)
    username  = g.screen_username()
    player_id = None

    if DB_AVAILABLE:
        try:
            player_id = db.get_or_create_player(username)
        except Exception as e:
            print(f"[DB] Could not resolve player: {e}")

    while True:
        # 3. Main menu
        action = g.screen_main_menu()

        if action == "quit":
            pygame.quit(); sys.exit()

        elif action == "leaderboard":
            rows = []
            if DB_AVAILABLE:
                try:
                    rows = db.get_leaderboard()
                except Exception as e:
                    print(f"[DB] Leaderboard error: {e}")
            g.screen_leaderboard(rows)

        elif action == "settings":
            settings = g.screen_settings(settings)
            g.save_settings(settings)

        elif action == "play":
            while True:
                # Fetch personal best before each game
                personal_best = 0
                if DB_AVAILABLE and player_id:
                    try:
                        personal_best = db.get_personal_best(player_id)
                    except Exception:
                        pass

                # Run a game session
                score, level = g.run_game(settings, personal_best)

                # Persist result
                if DB_AVAILABLE and player_id:
                    try:
                        db.save_session(player_id, score, level)
                        personal_best = db.get_personal_best(player_id)
                    except Exception as e:
                        print(f"[DB] Save error: {e}")

                # Game-over screen
                outcome = g.screen_game_over(score, level, personal_best)
                if outcome == "retry":
                    continue         # Play again
                else:
                    break            # Return to main menu


if __name__ == "__main__":
    main()