"""
paint.py  –  Pygame Paint Application
========================================
Based on the NerdParadise pygame tutorial (part 6) with extra tools:
  1. Pencil  – freehand drawing (original)
  2. Rectangle – drag to draw a filled / outlined rectangle
  3. Circle    – drag to draw a filled / outlined circle
  4. Eraser    – erase with a configurable brush
  5. Color selection palette
  6. Brush-size control

Full code comments throughout.
"""

import pygame
import sys

# ─────────────────────────────────────────────
#  Window / layout constants
# ─────────────────────────────────────────────
SCREEN_W   = 900
SCREEN_H   = 700
TOOLBAR_W  = 160          # Left-side toolbar width
CANVAS_X   = TOOLBAR_W    # Canvas starts after the toolbar
CANVAS_W   = SCREEN_W - TOOLBAR_W
CANVAS_H   = SCREEN_H

# ─────────────────────────────────────────────
#  Colours
# ─────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
DARK       = (30,  30,  30)
LIGHT_GRAY = (200, 200, 200)
MID_GRAY   = (120, 120, 120)
PANEL_BG   = (45,  45,  55)
HIGHLIGHT  = (100, 180, 255)

# Palette: a curated selection of colours
PALETTE = [
    (0,   0,   0),        # Black
    (255, 255, 255),      # White
    (200, 0,   0),        # Red
    (0,   180, 0),        # Green
    (0,   0,   220),      # Blue
    (255, 200, 0),        # Yellow
    (255, 100, 0),        # Orange
    (180, 0,   180),      # Purple
    (0,   200, 200),      # Cyan
    (255, 150, 180),      # Pink
    (100, 60,  20),       # Brown
    (150, 150, 150),      # Gray
    (255, 255, 150),      # Light yellow
    (150, 255, 150),      # Light green
    (150, 200, 255),      # Light blue
    (255, 180, 130),      # Peach
]

# Tools
TOOL_PENCIL  = "pencil"
TOOL_RECT    = "rect"
TOOL_CIRCLE  = "circle"
TOOL_ERASER  = "eraser"

# ─────────────────────────────────────────────
#  Pygame initialisation
# ─────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint")

clock = pygame.time.Clock()

font      = pygame.font.SysFont("Arial", 15, bold=True)
font_head = pygame.font.SysFont("Arial", 17, bold=True)


# ══════════════════════════════════════════════
#  CANVAS
# ══════════════════════════════════════════════

# A separate Surface is used as the persistent canvas so that in-progress
# drag operations (rect / circle) can be previewed without permanently
# marking the canvas until the mouse button is released.
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(WHITE)


# ══════════════════════════════════════════════
#  TOOLBAR LAYOUT HELPERS
# ══════════════════════════════════════════════

def label(surface, text, x, y, colour=LIGHT_GRAY):
    """Draw a small label on the toolbar."""
    surface.blit(font.render(text, True, colour), (x, y))


def draw_button(surface, rect, text, active=False):
    """
    Draw a toolbar button.
    Active (selected) buttons are highlighted in HIGHLIGHT colour.
    """
    colour = HIGHLIGHT if active else MID_GRAY
    pygame.draw.rect(surface, colour, rect, border_radius=6)
    pygame.draw.rect(surface, DARK,   rect, 2, border_radius=6)
    txt = font.render(text, True, BLACK if active else WHITE)
    surface.blit(txt, (rect.x + (rect.w - txt.get_width()) // 2,
                       rect.y + (rect.h - txt.get_height()) // 2))


def palette_rect(index):
    """Return the screen Rect for palette colour swatch at the given index."""
    cols = 4                            # 4 swatches per row
    size = 30                           # Each swatch is 30×30 px
    gap  = 4
    col  = index % cols
    row  = index // cols
    x    = 8 + col * (size + gap)
    y    = 430 + row * (size + gap)
    return pygame.Rect(x, y, size, size)


def brush_minus_rect():
    return pygame.Rect(8,  370, 36, 28)


def brush_plus_rect():
    return pygame.Rect(52, 370, 36, 28)


# ══════════════════════════════════════════════
#  TOOLBAR DRAWING
# ══════════════════════════════════════════════

def draw_toolbar(active_tool, current_colour, brush_size):
    """Render the entire left-side toolbar."""
    panel = pygame.Rect(0, 0, TOOLBAR_W, SCREEN_H)
    pygame.draw.rect(screen, PANEL_BG, panel)
    pygame.draw.line(screen, MID_GRAY, (TOOLBAR_W, 0), (TOOLBAR_W, SCREEN_H), 2)

    # ── Title ──────────────────────────────
    head = font_head.render("🎨 Paint", True, WHITE)
    screen.blit(head, (TOOLBAR_W // 2 - head.get_width() // 2, 10))

    # ── Tool buttons ───────────────────────
    label(screen, "Tools", 8, 50)
    tools = [
        (TOOL_PENCIL,  "✏ Pencil",  pygame.Rect(8, 68,  144, 32)),
        (TOOL_RECT,    "▭ Rect",    pygame.Rect(8, 106, 144, 32)),
        (TOOL_CIRCLE,  "○ Circle",  pygame.Rect(8, 144, 144, 32)),
        (TOOL_ERASER,  "⌫ Eraser",  pygame.Rect(8, 182, 144, 32)),
    ]
    for tool_id, tool_label, rect in tools:
        draw_button(screen, rect, tool_label, active=(active_tool == tool_id))

    # ── Current colour preview ─────────────
    label(screen, "Colour", 8, 226)
    colour_rect = pygame.Rect(8, 244, 144, 36)
    pygame.draw.rect(screen, current_colour, colour_rect, border_radius=6)
    pygame.draw.rect(screen, WHITE, colour_rect, 2, border_radius=6)

    # ── Brush size ─────────────────────────
    label(screen, f"Brush: {brush_size}px", 8, 306)
    # Minus button
    draw_button(screen, brush_minus_rect(), "–")
    draw_button(screen, brush_plus_rect(),  "+")
    # Preview dot
    dot_x, dot_y = 108, 384
    pygame.draw.circle(screen, current_colour, (dot_x, dot_y), min(brush_size, 24))
    pygame.draw.circle(screen, MID_GRAY,       (dot_x, dot_y), min(brush_size, 24), 1)

    # ── Clear canvas button ─────────────────
    draw_button(screen, pygame.Rect(8, 628, 144, 32), "Clear Canvas")

    # ── Colour palette ─────────────────────
    label(screen, "Palette", 8, 412)
    for i, col in enumerate(PALETTE):
        r = palette_rect(i)
        pygame.draw.rect(screen, col,   r, border_radius=4)
        pygame.draw.rect(screen, WHITE, r, 1, border_radius=4)  # border


# ══════════════════════════════════════════════
#  CANVAS DRAWING UTILITIES
# ══════════════════════════════════════════════

def canvas_pos(mx, my):
    """Convert screen mouse coordinates to canvas-local coordinates."""
    return mx - CANVAS_X, my


def pencil_draw(surface, pos, colour, size):
    """Draw a filled circle at pos (freehand pencil stroke)."""
    pygame.draw.circle(surface, colour, pos, size)


def erase(surface, pos, size):
    """Erase by drawing a white circle – effectively paints with the background."""
    pygame.draw.circle(surface, WHITE, pos, size)


def draw_rect_shape(surface, start, end, colour, fill=True):
    """Draw a rectangle from start to end corner."""
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    if w > 0 and h > 0:
        if fill:
            pygame.draw.rect(surface, colour, (x, y, w, h))
        else:
            pygame.draw.rect(surface, colour, (x, y, w, h), 3)


def draw_circle_shape(surface, start, end, colour, fill=True):
    """Draw an ellipse inscribed in the bounding box defined by start and end."""
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    if w > 0 and h > 0:
        rect = pygame.Rect(x, y, w, h)
        if fill:
            pygame.draw.ellipse(surface, colour, rect)
        else:
            pygame.draw.ellipse(surface, colour, rect, 3)


# ══════════════════════════════════════════════
#  MAIN APPLICATION LOOP
# ══════════════════════════════════════════════

def main():
    # ── Application state ───────────────────
    active_tool    = TOOL_PENCIL       # Currently selected tool
    current_colour = BLACK             # Currently selected drawing colour
    brush_size     = 6                 # Radius for pencil / eraser
    drawing        = False             # True while mouse button is held
    drag_start     = None              # Canvas-local start of the current drag

    last_pos = None                    # Previous mouse position (for pencil smoothing)

    while True:

        # ── Events ──────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ── Mouse button DOWN ──────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Clicks inside the TOOLBAR
                if mx < TOOLBAR_W:

                    # Tool buttons
                    if pygame.Rect(8,  68,  144, 32).collidepoint(mx, my):
                        active_tool = TOOL_PENCIL
                    elif pygame.Rect(8, 106, 144, 32).collidepoint(mx, my):
                        active_tool = TOOL_RECT
                    elif pygame.Rect(8, 144, 144, 32).collidepoint(mx, my):
                        active_tool = TOOL_CIRCLE
                    elif pygame.Rect(8, 182, 144, 32).collidepoint(mx, my):
                        active_tool = TOOL_ERASER

                    # Brush size buttons
                    elif brush_minus_rect().collidepoint(mx, my):
                        brush_size = max(1, brush_size - 2)
                    elif brush_plus_rect().collidepoint(mx, my):
                        brush_size = min(60, brush_size + 2)

                    # Clear canvas button
                    elif pygame.Rect(8, 628, 144, 32).collidepoint(mx, my):
                        canvas.fill(WHITE)

                    # Colour palette swatches
                    else:
                        for i, col in enumerate(PALETTE):
                            if palette_rect(i).collidepoint(mx, my):
                                current_colour = col
                                # Switching to a colour automatically selects pencil
                                if active_tool == TOOL_ERASER:
                                    active_tool = TOOL_PENCIL
                                break

                # Clicks inside the CANVAS
                else:
                    drawing   = True
                    drag_start = canvas_pos(mx, my)
                    last_pos   = drag_start
                    # Pencil / eraser: start drawing immediately on click
                    if active_tool == TOOL_PENCIL:
                        pencil_draw(canvas, drag_start, current_colour, brush_size)
                    elif active_tool == TOOL_ERASER:
                        erase(canvas, drag_start, brush_size)

            # ── Mouse button UP ────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and drag_start is not None:
                    end_pos = canvas_pos(*event.pos)
                    # Commit rectangle / circle to the permanent canvas on release
                    if active_tool == TOOL_RECT:
                        draw_rect_shape(canvas, drag_start, end_pos, current_colour, fill=False)
                    elif active_tool == TOOL_CIRCLE:
                        draw_circle_shape(canvas, drag_start, end_pos, current_colour, fill=False)
                drawing    = False
                drag_start = None
                last_pos   = None

            # ── Mouse MOTION while button held ──
            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my   = event.pos
                cur_pos  = canvas_pos(mx, my)

                if active_tool == TOOL_PENCIL:
                    # Interpolate between last and current position for smooth strokes
                    if last_pos:
                        pygame.draw.line(canvas, current_colour, last_pos, cur_pos,
                                         brush_size * 2)
                    pencil_draw(canvas, cur_pos, current_colour, brush_size)
                    last_pos = cur_pos

                elif active_tool == TOOL_ERASER:
                    if last_pos:
                        pygame.draw.line(canvas, WHITE, last_pos, cur_pos,
                                         brush_size * 2)
                    erase(canvas, cur_pos, brush_size)
                    last_pos = cur_pos

                # Rect and circle: preview only – committed on mouse-up

        # ── Rendering ───────────────────────

        # 1. Draw toolbar background
        draw_toolbar(active_tool, current_colour, brush_size)

        # 2. Blit the permanent canvas onto the screen
        screen.blit(canvas, (CANVAS_X, 0))

        # 3. Preview of in-progress rect / circle drag
        if drawing and drag_start and active_tool in (TOOL_RECT, TOOL_CIRCLE):
            mx, my   = pygame.mouse.get_pos()
            cur_pos  = canvas_pos(mx, my)

            # Composite a transparent overlay for the preview
            preview = canvas.copy()
            if active_tool == TOOL_RECT:
                draw_rect_shape(preview, drag_start, cur_pos, current_colour, fill=False)
            elif active_tool == TOOL_CIRCLE:
                draw_circle_shape(preview, drag_start, cur_pos, current_colour, fill=False)            
                screen.blit(preview, (CANVAS_X, 0))

        # 4. Eraser cursor – show a circle where the eraser will act
        if active_tool == TOOL_ERASER:
            mx, my = pygame.mouse.get_pos()
            if mx >= CANVAS_X:
                pygame.draw.circle(screen, MID_GRAY, (mx, my), brush_size,     1)
                pygame.draw.circle(screen, BLACK,    (mx, my), brush_size + 1, 1)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()