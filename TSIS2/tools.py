"""
tools.py  –  Drawing tool implementations for Paint (TSIS 2)
All shape/drawing functions live here; paint.py imports them.
"""

import pygame
import math
from collections import deque

WHITE = (255, 255, 255)


# ──────────────────────────────────────────────
#  Freehand / Pencil
# ──────────────────────────────────────────────

def pencil_draw(surface, pos, colour, size):
    """Draw a filled circle at pos (single pencil dot)."""
    pygame.draw.circle(surface, colour, pos, max(1, size // 2))


def pencil_line(surface, start, end, colour, size):
    """Connect two pencil positions with a smooth line."""
    pygame.draw.line(surface, colour, start, end, max(1, size))


# ──────────────────────────────────────────────
#  Straight Line
# ──────────────────────────────────────────────

def draw_line(surface, start, end, colour, size):
    """Draw a straight line from start to end."""
    pygame.draw.line(surface, colour, start, end, max(1, size))


# ──────────────────────────────────────────────
#  Eraser
# ──────────────────────────────────────────────

def erase(surface, pos, size):
    """Erase by painting white at pos."""
    pygame.draw.circle(surface, WHITE, pos, max(1, size))


def erase_line(surface, start, end, size):
    """Erase a line segment (smooth eraser)."""
    pygame.draw.line(surface, WHITE, start, end, max(1, size * 2))


# ──────────────────────────────────────────────
#  Rectangle
# ──────────────────────────────────────────────

def draw_rect_shape(surface, start, end, colour, size=2, fill=False):
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    if w > 0 and h > 0:
        if fill:
            pygame.draw.rect(surface, colour, (x, y, w, h))
        else:
            pygame.draw.rect(surface, colour, (x, y, w, h), max(1, size))


# ──────────────────────────────────────────────
#  Circle / Ellipse
# ──────────────────────────────────────────────

def draw_circle_shape(surface, start, end, colour, size=2, fill=False):
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    if w > 0 and h > 0:
        rect = pygame.Rect(x, y, w, h)
        if fill:
            pygame.draw.ellipse(surface, colour, rect)
        else:
            pygame.draw.ellipse(surface, colour, rect, max(1, size))


# ──────────────────────────────────────────────
#  Square
# ──────────────────────────────────────────────

def draw_square(surface, start, end, colour, size=2, fill=False):
    side = min(abs(end[0] - start[0]), abs(end[1] - start[1]))
    x, y = start
    if end[0] < start[0]:
        x -= side
    if end[1] < start[1]:
        y -= side
    if side > 0:
        if fill:
            pygame.draw.rect(surface, colour, (x, y, side, side))
        else:
            pygame.draw.rect(surface, colour, (x, y, side, side), max(1, size))


# ──────────────────────────────────────────────
#  Right Triangle
# ──────────────────────────────────────────────

def draw_right_triangle(surface, start, end, colour, size=2, fill=False):
    x1, y1 = start
    x2, y2 = end
    points = [(x1, y1), (x2, y1), (x1, y2)]
    if fill:
        pygame.draw.polygon(surface, colour, points)
    else:
        pygame.draw.polygon(surface, colour, points, max(1, size))


# ──────────────────────────────────────────────
#  Equilateral Triangle
# ──────────────────────────────────────────────

def draw_equilateral_triangle(surface, start, end, colour, size=2, fill=False):
    x1, y1 = start
    x2, y2 = end
    side   = abs(x2 - x1)
    height = int((math.sqrt(3) / 2) * side)
    points = [
        (x1,            y2),
        (x1 + side,     y2),
        (x1 + side // 2, y2 - height),
    ]
    if fill:
        pygame.draw.polygon(surface, colour, points)
    else:
        pygame.draw.polygon(surface, colour, points, max(1, size))


# ──────────────────────────────────────────────
#  Rhombus
# ──────────────────────────────────────────────

def draw_rhombus(surface, start, end, colour, size=2, fill=False):
    x1, y1 = start
    x2, y2 = end
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    points = [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]
    if fill:
        pygame.draw.polygon(surface, colour, points)
    else:
        pygame.draw.polygon(surface, colour, points, max(1, size))


# ──────────────────────────────────────────────
#  Flood Fill  (BFS, exact colour match)
# ──────────────────────────────────────────────

def flood_fill(surface, pos, new_colour):
    """
    BFS flood-fill starting at pixel pos on surface.
    Replaces all connected pixels of the same original colour
    with new_colour.  Uses pygame's pixel array for speed.
    """
    x0, y0 = int(pos[0]), int(pos[1])
    w, h    = surface.get_width(), surface.get_height()

    # Clamp to surface bounds
    if not (0 <= x0 < w and 0 <= y0 < h):
        return

    target_colour = surface.get_at((x0, y0))[:3]   # RGB only
    new_rgb       = new_colour[:3]

    if target_colour == new_rgb:
        return   # Nothing to do

    # Lock surface for fast pixel access
    surface.lock()
    visited = [[False] * h for _ in range(w)]
    queue   = deque()
    queue.append((x0, y0))
    visited[x0][y0] = True

    while queue:
        cx, cy = queue.popleft()
        surface.set_at((cx, cy), new_colour)

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[nx][ny]:
                if surface.get_at((nx, ny))[:3] == target_colour:
                    visited[nx][ny] = True
                    queue.append((nx, ny))

    surface.unlock()


# ──────────────────────────────────────────────
#  Text rendering
# ──────────────────────────────────────────────

def render_text(surface, text, pos, colour, font):
    """Permanently blit text onto surface at pos."""
    img = font.render(text, True, colour)
    surface.blit(img, pos)