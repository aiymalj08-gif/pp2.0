import pygame
from player import MusicPlayer

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen settings
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Music Player")

# Colors
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GRAY   = (40, 40, 40)
GREEN  = (0, 200, 100)
YELLOW = (255, 220, 0)
CYAN   = (0, 200, 255)

# Fonts
font_large  = pygame.font.SysFont("Arial", 28, bold=True)
font_medium = pygame.font.SysFont("Arial", 22)
font_small  = pygame.font.SysFont("Arial", 17)

# Create music player (point to your music folder)
player = MusicPlayer("music")

clock = pygame.time.Clock()

# Game loop
running = True
while running:
    screen.fill(GRAY)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:       # Play
                player.play()
            elif event.key == pygame.K_s:     # Stop
                player.stop()
            elif event.key == pygame.K_n:     # Next
                player.next_track()
            elif event.key == pygame.K_b:     # Back/Previous
                player.prev_track()
            elif event.key == pygame.K_q:     # Quit
                running = False

    # Draw UI
    # Title
    title = font_large.render("🎵 Music Player", True, CYAN)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

    # Current track
    track_label = font_small.render("Now Playing:", True, WHITE)
    screen.blit(track_label, (SCREEN_WIDTH // 2 - track_label.get_width() // 2, 110))

    track_info = player.get_current_track_name()

    if " - " in track_info:
        artist, title = track_info.split(" - ", 1)
    else:
        artist, title = "Unknown Artist", track_info

    # Draw title (bigger)
    title_text = font_medium.render(title, True, YELLOW)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 140))

    # Draw artist (smaller, below)
    artist_text = font_small.render(artist, True, WHITE)
    screen.blit(artist_text, (SCREEN_WIDTH // 2 - artist_text.get_width() // 2, 170))

    # Status
    status = font_medium.render(player.get_status(), True, GREEN)
    screen.blit(status, (SCREEN_WIDTH // 2 - status.get_width() // 2, 190))

    # Track number
    if player.playlist:
        track_num = font_small.render(
            f"Track {player.current_index + 1} of {len(player.playlist)}",
            True, WHITE
        )
        screen.blit(track_num, (SCREEN_WIDTH // 2 - track_num.get_width() // 2, 230))

    # Controls guide
    controls = [
        "P = Play",
        "S = Stop",
        "N = Next Track",
        "B = Previous Track",
        "Q = Quit"
    ]
    y_pos = 290
    for control in controls:
        text = font_small.render(control, True, (180, 180, 180))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
        y_pos += 22

    pygame.display.flip()
    clock.tick(60)

pygame.quit()