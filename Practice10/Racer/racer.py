"""
racer.py  –  Pygame Racer Game
================================
Based on the CodersLegacy pygame tutorial (parts 1-3) with extra features:
  * Randomly appearing coins on the road
  * Coin counter shown in the top-right corner
  * Full comments throughout
"""

import pygame
import random
import sys
import os

pygame.init()

SCREEN_W, SCREEN_H = 600, 800          # Window dimensions
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Racer")

clock = pygame.time.Clock()
FPS   = 60                             # Target frames per second

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (200, 0,   0)
YELLOW = (255, 215, 0)
GRAY   = (100, 100, 100)

ASSET_DIR = os.path.join(os.path.dirname(__file__), "car_imgs")

def load_img(name, scale=None):
    """Load an image by filename, optionally scaling it."""
    img = pygame.image.load(os.path.join(ASSET_DIR, name)).convert_alpha()
    if scale:
        img = pygame.transform.scale(img, scale)
    return img

road_img     = load_img("road.png",      (SCREEN_W, SCREEN_H))
player_img   = load_img("redcar.png",    (50, 80))
enemy_img    = load_img("bluecar.png",   (50, 80))
coin_img     = load_img("coin.png",      (28, 28))

font_large = pygame.font.SysFont("Arial", 36, bold=True)
font_small = pygame.font.SysFont("Arial", 24, bold=True)


#  Road geometry
#   The drivable area is between x=115 and x=485
ROAD_LEFT  = 115
ROAD_RIGHT = 485

# Three lane centre positions
LANE_CENTERS = [170, 295, 420]


class PlayerCar(pygame.sprite.Sprite):
    """
    The player-controlled car.
    Moves left/right with arrow keys; stays within road bounds.
    """
    SPEED = 6                          # Pixels per frame for lateral movement

    def __init__(self):
        super().__init__()
        self.image  = player_img
        self.rect   = self.image.get_rect()
        # Start at the bottom centre of the road
        self.rect.centerx = SCREEN_W // 2
        self.rect.bottom   = SCREEN_H - 20

    def update(self):
        """Handle keyboard input and clamp to road boundaries."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.SPEED

        # Clamp so the car doesn't leave the drivable road
        self.rect.left  = max(self.rect.left,  ROAD_LEFT)
        self.rect.right = min(self.rect.right, ROAD_RIGHT)


class EnemyCar(pygame.sprite.Sprite):
    """
    An oncoming enemy car that scrolls from top to bottom.
    Spawns in a random lane and moves at a configurable speed.
    """
    def __init__(self, speed):
        super().__init__()
        self.image = enemy_img
        self.rect  = self.image.get_rect()

        # Pick a random lane and position just above the top of the screen
        lane = random.choice(LANE_CENTERS)
        self.rect.centerx = lane
        self.rect.bottom   = 0
        self.speed = speed             # Pixels per frame (increases with score)

    def update(self):
        """Move downward only; removal is handled in run_game to track score."""
        self.rect.y += self.speed


class Coin(pygame.sprite.Sprite):
    """
    A collectible coin that scrolls from top to bottom.
    Spawns randomly on the road; disappears when collected or off-screen.
    """
    SPEED = 4                          # Coins move slightly slower than enemies

    def __init__(self):
        super().__init__()
        self.image = coin_img
        self.rect  = self.image.get_rect()

        # Random x position anywhere on the road
        self.rect.centerx = random.randint(ROAD_LEFT + 14, ROAD_RIGHT - 14)
        self.rect.bottom   = 0         # Start just above the screen

    def update(self):
        """Move downward; remove when off-screen."""
        self.rect.y += self.SPEED
        if self.rect.top > SCREEN_H:
            self.kill()

class ScrollingRoad:
    """
    Creates the illusion of forward motion by scrolling the road image downward.
    Two copies of the road tile are drawn back-to-back so the seam is invisible.
    """
    def __init__(self, speed=3):
        self.speed = speed
        self.y1    = 0               # Top of first tile
        self.y2    = -SCREEN_H       # Top of second tile (above screen)

    def update(self):
        """Advance both tiles; wrap the one that goes off-screen."""
        self.y1 += self.speed
        self.y2 += self.speed
        if self.y1 >= SCREEN_H:
            self.y1 = self.y2 - SCREEN_H
        if self.y2 >= SCREEN_H:
            self.y2 = self.y1 - SCREEN_H

    def draw(self, surface):
        surface.blit(road_img, (0, self.y1))
        surface.blit(road_img, (0, self.y2))


def draw_hud(surface, score, coins, lives=0):
    """Render the score (top-left) and coin count (top-right)."""
    score_surf = font_small.render(f"Score: {score}", True, WHITE)
    surface.blit(score_surf, (10, 10))

    # Coin counter – top right (with coin icon)
    coin_text = font_small.render(f"x {coins}", True, YELLOW)
    cx = SCREEN_W - coin_text.get_width() - 40
    surface.blit(coin_img, (SCREEN_W - coin_text.get_width() - 70, 8))
    surface.blit(coin_text, (cx, 10))


def draw_text_centre(surface, text, font, colour, y):
    """Draw text horizontally centred at the given y coordinate."""
    surf = font.render(text, True, colour)
    surface.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, y))


def show_start_screen():
    """Blocking loop that shows the title until the player presses Enter."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return                 # Start the game

        screen.blit(road_img, (0, 0))
        draw_text_centre(screen, "RACER",          font_large, YELLOW,  200)
        draw_text_centre(screen, "Arrow Keys: Move", font_small, WHITE, 300)
        draw_text_centre(screen, "Avoid enemies – collect coins!", font_small, WHITE, 340)
        draw_text_centre(screen, "Press ENTER to start", font_small, WHITE, 420)
        pygame.display.flip()
        clock.tick(FPS)


def show_game_over(score, coins):
    """Blocking loop for the game-over screen."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True        # Restart
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        screen.blit(road_img, (0, 0))
        draw_text_centre(screen, "GAME OVER",         font_large, RED,    220)
        draw_text_centre(screen, f"Score : {score}",  font_small, WHITE,  320)
        draw_text_centre(screen, f"Coins : {coins}",  font_small, YELLOW, 360)
        draw_text_centre(screen, "ENTER – restart  |  ESC – quit", font_small, WHITE, 440)
        pygame.display.flip()
        clock.tick(FPS)


# ══════════════════════════════════════════════
#  MAIN GAME LOOP
# ══════════════════════════════════════════════

def run_game():
    """Core gameplay loop. Returns when the player loses all lives."""

    score       = 0
    coins_count = 0
    enemy_speed = 4                    # Starts at 4, increases with score avoided

    player      = PlayerCar()
    all_sprites = pygame.sprite.Group(player)
    enemy_group = pygame.sprite.Group()
    coin_group  = pygame.sprite.Group()

    ENEMY_INTERVAL = 1500              # ms between enemy spawns
    COIN_INTERVAL  = 2500              # ms between coin spawns

    pygame.time.set_timer(pygame.USEREVENT + 1, ENEMY_INTERVAL)
    pygame.time.set_timer(pygame.USEREVENT + 2, COIN_INTERVAL)

    road = ScrollingRoad(speed=5)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # Enemy spawn timer fired
            if event.type == pygame.USEREVENT + 1:
                e = EnemyCar(enemy_speed)
                enemy_group.add(e)
                all_sprites.add(e)

            # Coin spawn timer fired (random chance: 70%)
            if event.type == pygame.USEREVENT + 2:
                if random.random() < 0.70:
                    c = Coin()
                    coin_group.add(c)
                    all_sprites.add(c)

        road.update()
        all_sprites.update()

        # Score +1 for each enemy car that passes below the screen (avoided)
        for enemy in list(enemy_group):
            if enemy.rect.top > SCREEN_H:
                score += 1
                enemy.kill()

        # Remove coins that go off screen
        for coin in list(coin_group):
            if coin.rect.top > SCREEN_H:
                coin.kill()

        # Speed up enemies every 3 avoided cars
        enemy_speed = 4 + score // 3

        # Collision with enemy → instant game over (no lives)
        if pygame.sprite.spritecollideany(player, enemy_group):
            return score, coins_count

        # Collect coins
        collected = pygame.sprite.spritecollide(player, coin_group, True)
        coins_count += len(collected)

        # Draw
        road.draw(screen)
        screen.blit(player.image, player.rect)

        for sprite in enemy_group:
            screen.blit(sprite.image, sprite.rect)
        for sprite in coin_group:
            screen.blit(sprite.image, sprite.rect)

        draw_hud(screen, score, coins_count, 0)

        pygame.display.flip()


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════

def main():
    show_start_screen()
    while True:
        final_score, final_coins = run_game()
        if not show_game_over(final_score, final_coins):
            break


if __name__ == "__main__":
    main()