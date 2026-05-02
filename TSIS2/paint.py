"""
paint.py  –  Pygame Paint Application  (TSIS 2)
================================================
Extends Practice 10 & 11 with:
  • Pencil  (freehand)          – Practice 10 base
  • Rectangle, Circle, Eraser  – Practice 10 base
  • Square, Right Triangle,
    Equilateral Triangle,
    Rhombus                    – Practice 11 additions
  ──── NEW in TSIS 2 ────────────────────────────
  • Straight Line tool with live preview
  • Three brush sizes  (keys 1 / 2 / 3  or toolbar buttons)
  • Flood-Fill tool
  • Text tool  (click → type → Enter to confirm, Esc to cancel)
  • Ctrl+S  saves canvas as timestamped PNG
"""

import pygame
import sys
from datetime import datetime

import tools   # tools.py  –  all drawing logic

# ─────────────────────────────────────────────
#  Window / layout
# ─────────────────────────────────────────────
SCREEN_W  = 1000
SCREEN_H  = 750        # fits most 1080p screens
TOOLBAR_W = 170
CANVAS_X  = TOOLBAR_W
CANVAS_W  = SCREEN_W - TOOLBAR_W
CANVAS_H  = SCREEN_H

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
RED_HINT   = (255,  80,  80)

PALETTE = [
    (0,   0,   0),    (255, 255, 255),
    (200, 0,   0),    (0,   180, 0),
    (0,   0,   220),  (255, 200, 0),
    (255, 100, 0),    (180, 0,   180),
    (0,   200, 200),  (255, 150, 180),
    (100, 60,  20),   (150, 150, 150),
    (255, 255, 150),  (150, 255, 150),
    (150, 200, 255),  (255, 180, 130),
]

# ─────────────────────────────────────────────
#  Tool identifiers
# ─────────────────────────────────────────────
TOOL_PENCIL    = "pencil"
TOOL_LINE      = "line"
TOOL_RECT      = "rect"
TOOL_CIRCLE    = "circle"
TOOL_ERASER    = "eraser"
TOOL_SQUARE    = "square"
TOOL_RTRIANGLE = "rtriangle"
TOOL_ETRIANGLE = "etriangle"
TOOL_RHOMBUS   = "rhombus"
TOOL_FILL      = "fill"
TOOL_TEXT      = "text"

# Brush size presets  (stroke width in pixels)
BRUSH_SIZES = {1: 2, 2: 5, 3: 10}

# ─────────────────────────────────────────────
#  Pygame init
# ─────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Paint – TSIS 2")
clock      = pygame.time.Clock()
font_ui    = pygame.font.SysFont("Arial", 14, bold=True)
font_head  = pygame.font.SysFont("Arial", 16, bold=True)
font_text  = pygame.font.SysFont("Arial", 22)   # used by the text tool

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(WHITE)


# ─────────────────────────────────────────────
#  Toolbar geometry helpers
# ─────────────────────────────────────────────

def _btn(y): return pygame.Rect(8, y, 154, 26)

# ── Vertical layout (top → bottom, fits 750px) ──
# Title:           y=8
# "Tools" label:   y=34
# 11 tool buttons: y=50..50+(11*30)=50..380  (step 30)
# "Colour" label:  y=392
# colour swatch:   y=408
# "Brush" label:   y=440
# S/M/L buttons:   y=456
# "Palette" label: y=492
# 4 rows swatches: y=508..508+(4*30)=508..628
# Save button:     y=640
# Clear button:    y=672
# hint:            y=706

TOOL_BUTTONS = [
    (TOOL_PENCIL,    "Pencil",      _btn(50)),
    (TOOL_LINE,      "Line",        _btn(80)),
    (TOOL_RECT,      "Rect",        _btn(110)),
    (TOOL_CIRCLE,    "Circle",      _btn(140)),
    (TOOL_ERASER,    "Eraser",      _btn(170)),
    (TOOL_SQUARE,    "Square",      _btn(200)),
    (TOOL_RTRIANGLE, "R.Triangle",  _btn(230)),
    (TOOL_ETRIANGLE, "E.Triangle",  _btn(260)),
    (TOOL_RHOMBUS,   "Rhombus",     _btn(290)),
    (TOOL_FILL,      "Fill",        _btn(320)),
    (TOOL_TEXT,      "Text",        _btn(350)),
]

BRUSH_BTNS = [
    (1, "S", pygame.Rect(8,   456, 46, 26)),
    (2, "M", pygame.Rect(60,  456, 46, 26)),
    (3, "L", pygame.Rect(112, 456, 46, 26)),
]

SAVE_BTN  = pygame.Rect(8, 640, 154, 26)
CLEAR_BTN = pygame.Rect(8, 672, 154, 26)

def palette_rect(i):
    cols, size, gap = 4, 28, 3
    return pygame.Rect(
        8  + (i % cols) * (size + gap),
        508 + (i // cols) * (size + gap),
        size, size,
    )


# ─────────────────────────────────────────────
#  Toolbar rendering
# ─────────────────────────────────────────────

def _lbl(text, x, y, col=LIGHT_GRAY):
    screen.blit(font_ui.render(text, True, col), (x, y))


def _draw_btn(rect, text, active=False):
    col = HIGHLIGHT if active else MID_GRAY
    pygame.draw.rect(screen, col,  rect, border_radius=5)
    pygame.draw.rect(screen, DARK, rect, 2, border_radius=5)
    img = font_ui.render(text, True, BLACK if active else WHITE)
    screen.blit(img, (rect.x + (rect.w - img.get_width())  // 2,
                      rect.y + (rect.h - img.get_height()) // 2))


def draw_toolbar(active_tool, colour, brush_key):
    pygame.draw.rect(screen, PANEL_BG, (0, 0, TOOLBAR_W, SCREEN_H))
    pygame.draw.line(screen, MID_GRAY, (TOOLBAR_W, 0), (TOOLBAR_W, SCREEN_H), 2)

    # ── Title ───────────────────────────────────
    h = font_head.render("Paint", True, WHITE)
    screen.blit(h, (TOOLBAR_W // 2 - h.get_width() // 2, 8))

    # ── Tool buttons ────────────────────────────
    _lbl("Tools", 8, 34)
    for tid, lbl, rect in TOOL_BUTTONS:
        _draw_btn(rect, lbl, active=(active_tool == tid))

    # ── Colour swatch ───────────────────────────
    _lbl("Colour", 8, 392)
    cr = pygame.Rect(8, 408, 154, 26)
    pygame.draw.rect(screen, colour, cr, border_radius=5)
    pygame.draw.rect(screen, WHITE,  cr, 2, border_radius=5)

    # ── Brush size ──────────────────────────────
    _lbl("Brush  (keys 1 / 2 / 3)", 8, 440)
    for key, lbl, rect in BRUSH_BTNS:
        active = (brush_key == key)
        col    = HIGHLIGHT if active else MID_GRAY
        pygame.draw.rect(screen, col,  rect, border_radius=5)
        pygame.draw.rect(screen, DARK, rect, 2, border_radius=5)
        img = font_ui.render(f"{lbl} {BRUSH_SIZES[key]}px", True,
                             BLACK if active else WHITE)
        screen.blit(img, (rect.x + (rect.w - img.get_width())  // 2,
                          rect.y + (rect.h - img.get_height()) // 2))

    # ── Palette ─────────────────────────────────
    _lbl("Palette", 8, 492)
    for i, col in enumerate(PALETTE):
        r = palette_rect(i)
        pygame.draw.rect(screen, col,   r, border_radius=3)
        pygame.draw.rect(screen, WHITE, r, 1, border_radius=3)

    # ── Save / Clear ────────────────────────────
    _draw_btn(SAVE_BTN,  "Save  (Ctrl+S)")
    _draw_btn(CLEAR_BTN, "Clear Canvas")

    # ── Hint ────────────────────────────────────
    _lbl("Ctrl+S = save PNG", 8, 706, MID_GRAY)


# ─────────────────────────────────────────────
#  Coordinate helper
# ─────────────────────────────────────────────

def canvas_pos(mx, my):
    """Screen → canvas-local coordinates."""
    return mx - CANVAS_X, my


# ─────────────────────────────────────────────
#  Save canvas
# ─────────────────────────────────────────────

def save_canvas():
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"canvas_{ts}.png"
    pygame.image.save(canvas, name)
    print(f"Saved: {name}")
    return name


# ─────────────────────────────────────────────
#  Dispatch: draw shape on a surface
# ─────────────────────────────────────────────

SHAPE_TOOLS = {
    TOOL_RECT,
    TOOL_CIRCLE,
    TOOL_SQUARE,
    TOOL_RTRIANGLE,
    TOOL_ETRIANGLE,
    TOOL_RHOMBUS,
    TOOL_LINE,
}


def commit_shape(surface, tool, start, end, colour, size):
    """Permanently draw a drag-based shape onto surface."""
    if tool == TOOL_RECT:
        tools.draw_rect_shape(surface, start, end, colour, size)
    elif tool == TOOL_CIRCLE:
        tools.draw_circle_shape(surface, start, end, colour, size)
    elif tool == TOOL_SQUARE:
        tools.draw_square(surface, start, end, colour, size)
    elif tool == TOOL_RTRIANGLE:
        tools.draw_right_triangle(surface, start, end, colour, size)
    elif tool == TOOL_ETRIANGLE:
        tools.draw_equilateral_triangle(surface, start, end, colour, size)
    elif tool == TOOL_RHOMBUS:
        tools.draw_rhombus(surface, start, end, colour, size)
    elif tool == TOOL_LINE:
        tools.draw_line(surface, start, end, colour, size)


# ─────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────

def main():
    active_tool   = TOOL_PENCIL
    current_colour = BLACK
    brush_key     = 1          # 1=small 2=medium 3=large
    drawing       = False
    drag_start    = None
    last_pos      = None

    # ── Text-tool state ───────────────────
    text_active   = False      # True while typing
    text_pos      = (0, 0)     # Canvas-local anchor
    text_buffer   = ""

    # ── Save notification ─────────────────
    save_msg      = ""
    save_msg_timer = 0

    while True:
        brush_size = BRUSH_SIZES[brush_key]

        # ── Events ────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ── Keyboard ──────────────────
            if event.type == pygame.KEYDOWN:

                # Text tool: intercept all keys while typing
                if text_active:
                    if event.key == pygame.K_RETURN:
                        # Commit text to canvas
                        if text_buffer:
                            tools.render_text(
                                canvas, text_buffer, text_pos,
                                current_colour, font_text
                            )
                        text_active  = False
                        text_buffer  = ""
                    elif event.key == pygame.K_ESCAPE:
                        text_active = False
                        text_buffer = ""
                    elif event.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text_buffer += event.unicode
                    continue   # Don't process other shortcuts while typing

                # Brush size shortcuts
                if event.key == pygame.K_1:
                    brush_key = 1
                elif event.key == pygame.K_2:
                    brush_key = 2
                elif event.key == pygame.K_3:
                    brush_key = 3

                # Ctrl+S  – save
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    name = save_canvas()
                    save_msg       = f"Saved: {name}"
                    save_msg_timer = 180   # frames (~3 s at 60 fps)

            # ── Mouse button DOWN ──────────
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # ── Toolbar clicks ─────────
                if mx < TOOLBAR_W:
                    # Tool buttons
                    for tid, _, rect in TOOL_BUTTONS:
                        if rect.collidepoint(mx, my):
                            active_tool  = tid
                            text_active  = False
                            text_buffer  = ""
                            break

                    # Brush size buttons
                    for key, _, rect in BRUSH_BTNS:
                        if rect.collidepoint(mx, my):
                            brush_key = key
                            break

                    # Save button
                    if SAVE_BTN.collidepoint(mx, my):
                        name = save_canvas()
                        save_msg       = f"Saved: {name}"
                        save_msg_timer = 180

                    # Clear button
                    if CLEAR_BTN.collidepoint(mx, my):
                        canvas.fill(WHITE)

                    # Palette swatches
                    for i, col in enumerate(PALETTE):
                        if palette_rect(i).collidepoint(mx, my):
                            current_colour = col
                            if active_tool == TOOL_ERASER:
                                active_tool = TOOL_PENCIL
                            break

                # ── Canvas clicks ──────────
                else:
                    cp = canvas_pos(mx, my)

                    # Text tool: start typing at click position
                    if active_tool == TOOL_TEXT:
                        text_active = True
                        text_pos    = cp
                        text_buffer = ""
                        continue

                    # Fill tool: immediate action on click
                    if active_tool == TOOL_FILL:
                        tools.flood_fill(canvas, cp, current_colour)
                        continue

                    drawing    = True
                    drag_start = cp
                    last_pos   = cp

                    if active_tool == TOOL_PENCIL:
                        tools.pencil_draw(canvas, cp, current_colour, brush_size)
                    elif active_tool == TOOL_ERASER:
                        tools.erase(canvas, cp, brush_size)

            # ── Mouse button UP ────────────
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drawing and drag_start is not None:
                    end_pos = canvas_pos(*event.pos)
                    if active_tool in SHAPE_TOOLS:
                        commit_shape(canvas, active_tool, drag_start,
                                     end_pos, current_colour, brush_size)
                drawing    = False
                drag_start = None
                last_pos   = None

            # ── Mouse MOTION ───────────────
            if event.type == pygame.MOUSEMOTION and drawing:
                mx, my  = event.pos
                cur_pos = canvas_pos(mx, my)

                if active_tool == TOOL_PENCIL:
                    if last_pos:
                        tools.pencil_line(canvas, last_pos, cur_pos,
                                          current_colour, brush_size)
                    tools.pencil_draw(canvas, cur_pos, current_colour, brush_size)
                    last_pos = cur_pos

                elif active_tool == TOOL_ERASER:
                    if last_pos:
                        tools.erase_line(canvas, last_pos, cur_pos, brush_size)
                    tools.erase(canvas, cur_pos, brush_size)
                    last_pos = cur_pos

                # Shape tools: preview rendered in the drawing section below

        # ─── Rendering ────────────────────

        # 1. Toolbar
        draw_toolbar(active_tool, current_colour, brush_key)

        # 2. Permanent canvas
        screen.blit(canvas, (CANVAS_X, 0))

        # 3. Live preview for drag-based shapes (Line included)
        if drawing and drag_start and active_tool in SHAPE_TOOLS:
            mx, my  = pygame.mouse.get_pos()
            cur_pos = canvas_pos(mx, my)
            preview = canvas.copy()
            commit_shape(preview, active_tool, drag_start,
                         cur_pos, current_colour, brush_size)
            screen.blit(preview, (CANVAS_X, 0))

        # 4. Text-tool cursor / live text preview
        if text_active:
            # Show what is typed so far
            preview_img = font_text.render(text_buffer + "|", True, current_colour)
            tx = text_pos[0] + CANVAS_X
            ty = text_pos[1]
            screen.blit(preview_img, (tx, ty))

        # 5. Eraser cursor ring
        if active_tool == TOOL_ERASER:
            mx, my = pygame.mouse.get_pos()
            if mx >= CANVAS_X:
                pygame.draw.circle(screen, MID_GRAY, (mx, my), brush_size,     1)
                pygame.draw.circle(screen, BLACK,    (mx, my), brush_size + 1, 1)

        # 6. Save notification banner
        if save_msg_timer > 0:
            save_msg_timer -= 1
            banner = font_ui.render(save_msg, True, WHITE)
            bx = CANVAS_X + 10
            by = SCREEN_H - 30
            pygame.draw.rect(screen, (30, 120, 30),
                             (bx - 4, by - 4,
                              banner.get_width() + 8,
                              banner.get_height() + 8),
                             border_radius=4)
            screen.blit(banner, (bx, by))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()