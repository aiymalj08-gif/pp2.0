"""
racer.py  –  Core gameplay for TSIS 3 Racer.
New in TSIS 3 (builds on Practice 10 & 11):
  • Lane hazards: oil spills, speed bumps, nitro strips
  • Road obstacles: barriers and potholes
  • Three power-ups: Nitro / Shield / Repair
  • Difficulty scaling (speed, spawn rate)
  • Lives system with invincibility flash
  • Distance meter
  • HUD: active power-up + countdown
"""

import pygame
import random
import sys
import os

# ── Constants ─────────────────────────────────
SCREEN_W, SCREEN_H = 600, 800
FPS      = 60
ROAD_LEFT  = 115
ROAD_RIGHT = 485
LANE_CENTERS = [170, 295, 420]

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (200, 0,   0)
YELLOW = (255, 215, 0)
GRAY   = (100, 100, 100)
GREEN  = (0,   180, 0)
BLUE   = (0,   100, 220)
ORANGE = (255, 140, 0)
PURPLE = (160, 0,   200)
CYAN   = (0,   210, 210)

ASSET_DIR = os.path.join(os.path.dirname(__file__), "car_imgs")
SOUND_DIR = os.path.join(os.path.dirname(__file__), "sound")

# Difficulty presets  {name: (base_enemy_speed, spawn_ms, obstacle_chance)}
DIFFICULTY_PRESETS = {
    "Easy":   (3, 2000, 0.3),
    "Normal": (4, 1500, 0.5),
    "Hard":   (6, 1000, 0.8),
}

# Car colour tint map (applied via Surface.fill with BLEND_MULT)
CAR_TINTS = {
    "Red":    (255, 80,  80),
    "Blue":   (80,  80,  255),
    "Green":  (80,  255, 80),
    "Yellow": (255, 255, 80),
}


# ─────────────────────────────────────────────
#  Asset loaders
# ─────────────────────────────────────────────

def load_img(name, scale=None):
    path = os.path.join(ASSET_DIR, name)
    img  = pygame.image.load(path).convert_alpha()
    if scale:
        img = pygame.transform.scale(img, scale)
    return img


def tinted(img, colour):
    """Return a copy of img with a colour tint applied."""
    copy = img.copy()
    tint = pygame.Surface(copy.get_size(), flags=pygame.SRCALPHA)
    tint.fill((*colour, 180))
    copy.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return copy


def load_sound(name):
    path = os.path.join(SOUND_DIR, name)
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    return None


# ─────────────────────────────────────────────
#  Sprites
# ─────────────────────────────────────────────

class PlayerCar(pygame.sprite.Sprite):
    BASE_SPEED = 6

    def __init__(self, img):
        super().__init__()
        self.image     = img
        self.rect      = self.image.get_rect()
        self.rect.centerx = SCREEN_W // 2
        self.rect.bottom  = SCREEN_H - 20
        self.speed     = self.BASE_SPEED
        # Power-up state
        self.nitro_timer  = 0     # ms remaining
        self.shield_active = False
        self.active_powerup = None  # "Nitro" | "Shield" | None

    def update(self, dt):
        # Nitro countdown
        if self.nitro_timer > 0:
            self.nitro_timer -= dt
            if self.nitro_timer <= 0:
                self.nitro_timer = 0
                self.speed = self.BASE_SPEED
                self.active_powerup = None if not self.shield_active else "Shield"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        self.rect.left  = max(self.rect.left,  ROAD_LEFT)
        self.rect.right = min(self.rect.right, ROAD_RIGHT)

    def apply_nitro(self, duration_ms=4000):
        self.nitro_timer   = duration_ms
        self.speed         = self.BASE_SPEED * 2
        self.active_powerup = "Nitro"

    def apply_shield(self):
        self.shield_active  = True
        self.active_powerup = "Shield"

    def absorb_hit(self):
        """Returns True if shield absorbed the hit, False otherwise."""
        if self.shield_active:
            self.shield_active  = False
            self.active_powerup = None
            return True
        return False


class EnemyCar(pygame.sprite.Sprite):
    def __init__(self, img, speed):
        super().__init__()
        self.image = img
        self.rect  = self.image.get_rect()
        lane = random.choice(LANE_CENTERS)
        self.rect.centerx = lane
        self.rect.bottom   = 0
        self.speed = speed

    def update(self, dt=None):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H:
            self.kill()


class Coin(pygame.sprite.Sprite):
    """Base coin – worth 1 point (Practice 10/11 base, kept as-is)."""
    SPEED = 4

    def __init__(self, img):
        super().__init__()
        self.image = img
        self.rect  = self.image.get_rect()
        self.rect.centerx = random.randint(ROAD_LEFT + 14, ROAD_RIGHT - 14)
        self.rect.bottom   = 0
        self.value = 1

    def update(self, dt=None):
        self.rect.y += self.SPEED
        if self.rect.top > SCREEN_H:
            self.kill()


class HeavyCoin(Coin):
    """Worth 5 points (weighted coin from Practice 11)."""
    def __init__(self, img):
        super().__init__(img)
        self.value = 5
        # Tint gold/orange to distinguish
        tinted_img = img.copy()
        tint = pygame.Surface(tinted_img.get_size(), flags=pygame.SRCALPHA)
        tint.fill((255, 160, 0, 200))
        tinted_img.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.image = tinted_img


# ── Lane Hazards ──────────────────────────────

class OilSpill(pygame.sprite.Sprite):
    """Oil spill – slows the player for 1 second on contact."""
    SPEED = 3

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((60, 24), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (30, 30, 30, 200), (0, 0, 60, 24))
        self.rect  = self.image.get_rect()
        lane = random.choice(LANE_CENTERS)
        self.rect.centerx = lane
        self.rect.bottom   = 0

    def update(self, dt=None):
        self.rect.y += self.SPEED
        if self.rect.top > SCREEN_H:
            self.kill()


class SpeedBump(pygame.sprite.Sprite):
    """Speed bump – instant brief slowdown on contact."""
    SPEED = 3

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((80, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (180, 140, 0, 230), (0, 0, 80, 16),
                         border_radius=4)
        # Stripe pattern
        for x in range(0, 80, 16):
            pygame.draw.rect(self.image, (220, 220, 0, 230), (x, 0, 8, 16))
        self.rect = self.image.get_rect()
        lane = random.choice(LANE_CENTERS)
        self.rect.centerx = lane
        self.rect.bottom   = 0

    def update(self, dt=None):
        self.rect.y += self.SPEED
        if self.rect.top > SCREEN_H:
            self.kill()


class NitroStrip(pygame.sprite.Sprite):
    """Nitro strip – gives a temporary speed boost (road event)."""
    SPEED = 3

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((90, 18), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 220, 255, 200), (0, 0, 90, 18),
                         border_radius=4)
        txt = pygame.font.SysFont("Arial", 12, bold=True).render("NITRO", True, BLACK)
        self.image.blit(txt, (90 // 2 - txt.get_width() // 2, 2))
        self.rect = self.image.get_rect()
        lane = random.choice(LANE_CENTERS)
        self.rect.centerx = lane
        self.rect.bottom   = 0

    def update(self, dt=None):
        self.rect.y += self.SPEED
        if self.rect.top > SCREEN_H:
            self.kill()


# ── Road Obstacles ────────────────────────────

class Barrier(pygame.sprite.Sprite):
    """A concrete barrier that blocks the lane – fatal collision."""
    SPEED = 3

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((54, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (180, 180, 180, 255), (0, 0, 54, 30),
                         border_radius=4)
        pygame.draw.rect(self.image, RED, (0, 0, 54, 10), border_radius=4)
        self.rect  = self.image.get_rect()
        lane = random.choice(LANE_CENTERS)
        self.rect.centerx = lane
        self.rect.bottom   = 0

    def update(self, dt=None):
        self.rect.y += self.SPEED
        if self.rect.top > SCREEN_H:
            self.kill()


class Pothole(pygame.sprite.Sprite):
    """Pothole – triggers a slowdown effect."""
    SPEED = 3

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((36, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (40, 30, 20, 200), (0, 0, 36, 20))
        self.rect  = self.image.get_rect()
        lane = random.choice(LANE_CENTERS)
        self.rect.centerx = lane
        self.rect.bottom   = 0

    def update(self, dt=None):
        self.rect.y += self.SPEED
        if self.rect.top > SCREEN_H:
            self.kill()


# ── Power-Ups ─────────────────────────────────

class PowerUp(pygame.sprite.Sprite):
    SPEED    = 3
    LIFETIME = 8000   # ms before auto-disappear

    def __init__(self, kind, colour, label):
        super().__init__()
        self.kind  = kind
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.image, colour, (20, 20), 20)
        pygame.draw.circle(self.image, WHITE,  (20, 20), 20, 2)
        txt = pygame.font.SysFont("Arial", 10, bold=True).render(label, True, WHITE)
        self.image.blit(txt, (20 - txt.get_width() // 2,
                               20 - txt.get_height() // 2))
        self.rect  = self.image.get_rect()
        lane = random.choice(LANE_CENTERS)
        self.rect.centerx = lane
        self.rect.bottom   = 0
        self.age   = 0

    def update(self, dt=0):
        self.rect.y += self.SPEED
        self.age    += dt
        if self.rect.top > SCREEN_H or self.age > self.LIFETIME:
            self.kill()


def make_powerup():
    choices = [
        ("Nitro",  CYAN,   "NIT"),
        ("Shield", ORANGE, "SHL"),
        ("Repair", GREEN,  "REP"),
    ]
    kind, colour, label = random.choice(choices)
    return PowerUp(kind, colour, label)


# ─────────────────────────────────────────────
#  Scrolling road
# ─────────────────────────────────────────────

class ScrollingRoad:
    def __init__(self, img, speed=5):
        self.img   = img
        self.speed = speed
        self.y1    = 0
        self.y2    = -SCREEN_H

    def update(self):
        self.y1 += self.speed
        self.y2 += self.speed
        if self.y1 >= SCREEN_H:
            self.y1 = self.y2 - SCREEN_H
        if self.y2 >= SCREEN_H:
            self.y2 = self.y1 - SCREEN_H

    def draw(self, surface):
        surface.blit(self.img, (0, self.y1))
        surface.blit(self.img, (0, self.y2))


# ─────────────────────────────────────────────
#  HUD
# ─────────────────────────────────────────────

def draw_hud(surface, score, coins, lives, distance,
             player, font_small, coin_img):
    # Score
    surface.blit(font_small.render(f"Score: {score}", True, WHITE), (10, 10))
    # Lives
    surface.blit(font_small.render(f"Lives: {lives}", True, WHITE), (10, 36))
    # Distance
    surface.blit(font_small.render(f"Dist: {distance}m", True, WHITE), (10, 62))

    # Coin counter top-right
    coin_text = font_small.render(f"x {coins}", True, YELLOW)
    cx = SCREEN_W - coin_text.get_width() - 40
    surface.blit(coin_img, (SCREEN_W - coin_text.get_width() - 70, 8))
    surface.blit(coin_text, (cx, 10))

    # Active power-up
    if player.active_powerup:
        label = player.active_powerup
        if player.nitro_timer > 0:
            secs  = player.nitro_timer / 1000
            label = f"NITRO {secs:.1f}s"
        elif player.shield_active:
            label = "SHIELD"
        img = font_small.render(label, True, CYAN)
        surface.blit(img, (SCREEN_W // 2 - img.get_width() // 2, 10))


# ─────────────────────────────────────────────
#  Main gameplay function
# ─────────────────────────────────────────────

def run_game(screen, clock, settings):
    """
    Run one round of the game.
    Returns (score, distance, coins_count).
    """
    pygame.mixer.init()

    # ── Load assets ───────────────────────────
    road_img   = load_img("road.png",     (SCREEN_W, SCREEN_H))

    # Try common filenames from both practice versions
    for name in ("car.png", "redcar.png", "player.png"):
        try:
            raw_player = load_img(name, (50, 80)); break
        except Exception:
            pass

    tint_colour = CAR_TINTS.get(settings.get("car_color", "Red"), CAR_TINTS["Red"])
    player_img  = tinted(raw_player, tint_colour)

    for name in ("enemy_car.png", "bluecar.png", "enemy.png"):
        try:
            enemy_img = load_img(name, (50, 80)); break
        except Exception:
            pass

    coin_img = load_img("coin.png", (28, 28))

    # ── Sounds ────────────────────────────────
    crash_snd  = load_sound("crash_lose.mp3")
    coin_snd   = load_sound("coin.mp3")
    powerup_snd = load_sound("coin.mp3")   # reuse if no dedicated sound

    if settings.get("sound", True):
        bg = os.path.join(SOUND_DIR, "background.mp3")
        if os.path.exists(bg):
            pygame.mixer.music.load(bg)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)

    # ── Difficulty ────────────────────────────
    diff = settings.get("difficulty", "Normal")
    base_speed, spawn_ms, obs_chance = DIFFICULTY_PRESETS.get(
        diff, DIFFICULTY_PRESETS["Normal"])

    # ── State ─────────────────────────────────
    score       = 0
    coins_count = 0
    distance    = 0
    lives       = 3
    enemy_speed = base_speed

    # Slowdown effect state
    slow_timer = 0     # ms of remaining slowdown

    player      = PlayerCar(player_img)
    all_sprites = pygame.sprite.Group(player)
    enemy_group = pygame.sprite.Group()
    coin_group  = pygame.sprite.Group()
    hazard_group  = pygame.sprite.Group()   # oil, bump, nitro strip
    obstacle_group = pygame.sprite.Group()  # barriers, potholes
    powerup_group  = pygame.sprite.Group()

    # Timer events
    EVT_ENEMY   = pygame.USEREVENT + 1
    EVT_COIN    = pygame.USEREVENT + 2
    EVT_HAZARD  = pygame.USEREVENT + 3
    EVT_POWERUP = pygame.USEREVENT + 4

    pygame.time.set_timer(EVT_ENEMY,   spawn_ms)
    pygame.time.set_timer(EVT_COIN,    2500)
    pygame.time.set_timer(EVT_HAZARD,  3000)
    pygame.time.set_timer(EVT_POWERUP, 7000)

    road = ScrollingRoad(road_img, speed=5)

    font_small = pygame.font.SysFont("Arial", 22, bold=True)

    # Invincibility after hit
    invincible       = False
    invincible_timer = 0
    INVINCIBLE_MS    = 2000

    frame = 0

    while True:
        dt = clock.tick(FPS)
        frame += 1

        # Distance increases each frame
        distance += 1

        # ── Events ────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == EVT_ENEMY:
                e = EnemyCar(enemy_img, enemy_speed)
                # Safe spawn: skip if too close to player
                if abs(e.rect.centerx - player.rect.centerx) > 40 or e.rect.bottom < player.rect.top - 100:
                    enemy_group.add(e)
                    all_sprites.add(e)

            if event.type == EVT_COIN:
                # Weighted coins: 20 % chance of heavy coin (Practice 11)
                if random.random() < 0.70:
                    if random.random() < 0.2:
                        c = HeavyCoin(coin_img)
                    else:
                        c = Coin(coin_img)
                    coin_group.add(c)
                    all_sprites.add(c)

            if event.type == EVT_HAZARD:
                if random.random() < obs_chance:
                    # Choose hazard type
                    choice = random.random()
                    if choice < 0.3:
                        h = OilSpill()
                    elif choice < 0.55:
                        h = SpeedBump()
                    elif choice < 0.75:
                        h = NitroStrip()
                    elif choice < 0.88:
                        h = Barrier()
                    else:
                        h = Pothole()

                    if isinstance(h, (Barrier, Pothole)):
                        obstacle_group.add(h)
                    else:
                        hazard_group.add(h)
                    all_sprites.add(h)

            if event.type == EVT_POWERUP:
                if random.random() < 0.5:
                    pu = make_powerup()
                    powerup_group.add(pu)
                    all_sprites.add(pu)

        # ── Update ────────────────────────────

        # Slowdown effect (oil / pothole)
        if slow_timer > 0:
            slow_timer -= dt
            player.speed = max(2, PlayerCar.BASE_SPEED // 2)
        elif player.nitro_timer <= 0:
            player.speed = PlayerCar.BASE_SPEED

        road.update()
        player.update(dt)
        enemy_group.update()
        coin_group.update()
        hazard_group.update(dt)
        obstacle_group.update()
        powerup_group.update(dt)

        # Difficulty scaling: speed up every 200 distance units
        enemy_speed = base_speed + distance // 200

        # Invincibility countdown
        if invincible:
            invincible_timer -= dt
            if invincible_timer <= 0:
                invincible = False

        # ── Collisions ────────────────────────

        # Enemy cars → lose life
        if not invincible:
            hit = pygame.sprite.spritecollideany(player, enemy_group)
            if hit:
                if not player.absorb_hit():
                    if crash_snd and settings.get("sound", True):
                        crash_snd.play()
                    lives -= 1
                    invincible       = True
                    invincible_timer = INVINCIBLE_MS
                    if lives <= 0:
                        pygame.mixer.music.stop()
                        _stop_timers([EVT_ENEMY, EVT_COIN, EVT_HAZARD, EVT_POWERUP])
                        return score, distance // 10, coins_count
                hit.kill()

        # Barriers → lose life
        if not invincible:
            hit = pygame.sprite.spritecollideany(player, obstacle_group)
            if hit and isinstance(hit, Barrier):
                if not player.absorb_hit():
                    if crash_snd and settings.get("sound", True):
                        crash_snd.play()
                    lives -= 1
                    invincible       = True
                    invincible_timer = INVINCIBLE_MS
                    if lives <= 0:
                        pygame.mixer.music.stop()
                        _stop_timers([EVT_ENEMY, EVT_COIN, EVT_HAZARD, EVT_POWERUP])
                        return score, distance // 10, coins_count
                hit.kill()

        # Potholes → slow down
        pothole_hit = pygame.sprite.spritecollideany(player, obstacle_group)
        if pothole_hit and isinstance(pothole_hit, Pothole):
            slow_timer = 1500
            pothole_hit.kill()

        # Hazard: oil spill → slow
        oil_hit = pygame.sprite.spritecollide(
            player, hazard_group, False,
            lambda p, h: isinstance(h, OilSpill) and p.rect.colliderect(h.rect))
        for h in oil_hit:
            slow_timer = 1500
            h.kill()

        # Hazard: speed bump → brief slow
        bump_hit = pygame.sprite.spritecollide(
            player, hazard_group, False,
            lambda p, h: isinstance(h, SpeedBump) and p.rect.colliderect(h.rect))
        for h in bump_hit:
            slow_timer = 600
            h.kill()

        # Hazard: nitro strip → boost
        nitro_hit = pygame.sprite.spritecollide(
            player, hazard_group, False,
            lambda p, h: isinstance(h, NitroStrip) and p.rect.colliderect(h.rect))
        for h in nitro_hit:
            player.apply_nitro(3000)
            h.kill()

        # Coins
        collected = pygame.sprite.spritecollide(player, coin_group, True)
        if collected:
            if coin_snd and settings.get("sound", True):
                coin_snd.play()
            for c in collected:
                coins_count += c.value
                score       += c.value * 10

        # Power-ups
        pu_hit = pygame.sprite.spritecollide(player, powerup_group, True)
        for pu in pu_hit:
            if powerup_snd and settings.get("sound", True):
                powerup_snd.play()
            if pu.kind == "Nitro":
                player.apply_nitro(4000)
            elif pu.kind == "Shield":
                player.apply_shield()
            elif pu.kind == "Repair":
                lives = min(lives + 1, 5)

        # Score from distance
        score = coins_count * 10 + distance // 10

        # ── Draw ──────────────────────────────
        road.draw(screen)

        for sprite in obstacle_group:
            screen.blit(sprite.image, sprite.rect)
        for sprite in hazard_group:
            screen.blit(sprite.image, sprite.rect)
        for sprite in coin_group:
            screen.blit(sprite.image, sprite.rect)
        for sprite in powerup_group:
            screen.blit(sprite.image, sprite.rect)
        for sprite in enemy_group:
            screen.blit(sprite.image, sprite.rect)

        # Player flicker while invincible
        if invincible and (pygame.time.get_ticks() // 150) % 2 == 0:
            pass
        else:
            # Shield glow
            if player.shield_active:
                pygame.draw.circle(screen, ORANGE,
                                   player.rect.center,
                                   max(player.rect.width, player.rect.height) // 2 + 6,
                                   3)
            screen.blit(player.image, player.rect)

        draw_hud(screen, score, coins_count, lives, distance // 10,
                 player, font_small, coin_img)

        pygame.display.flip()


def _stop_timers(events):
    for e in events:
        pygame.time.set_timer(e, 0)