import pygame
import time
import re
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class TextRenderer:
    """
    Renders:
      - Centered title at the top.
      - All blocks (narration, location, dialog, thought) accumulated on a page.
      - Typewriter effect, character by character, supporting inline color overrides: [color=#RRGGBB]text[/].
      - Dialog/thought boxes with fixed height (2 lines), no unwanted line breaks.
      - Footer with “End →” if last page and “Page X/Y (Last)” indicator.
    """

    # Regex for [color=#RRGGBB]...[/] inline color tags
    INLINE_COLOR_PATTERN = re.compile(r"\[color=(#[0-9A-Fa-f]{6})\](.*?)\[/\]")

    def __init__(self, screen, settings):
        pygame.font.init()
        self.screen = screen

        # Global settings (from parser.py)
        self.text_speed = settings.get("text_speed", 0.03)
        self.skip_enabled = settings.get("skip_enabled", True)

        self.dialogue_bg_default = settings.get("dialogue_color", (80, 80, 80))
        self.thinking_bg_default = settings.get("thinking_color", (70, 70, 113))

        self.font_size_default = settings.get("font_size", 20)
        self.text_color_default = settings.get("text_color", (255, 255, 255))
        self.subtitle_color_default = settings.get("subtitle_color", (255, 255, 0))

        # Default fonts
        self.font = pygame.font.SysFont("consolas", self.font_size_default)
        self.italic_font = pygame.font.SysFont("consolas", self.font_size_default, italic=True)

        # Layout metrics
        self.line_height = self.font.get_linesize()
        self.margin_x = 20
        self.title_area_height = self.line_height + 10
        self.text_area_width = SCREEN_WIDTH - 2 * self.margin_x
        self.block_spacing = 20

    def render_section(self, blocks, title, current_page, total_pages):
        """
        Renders a section as a full page:
          1. Clears event buffer and waits for all keys to be released.
          2. Draws black screen, title, footer, and page indicator.
          3. For each block:
             - location: simple text with subtitle_color.
             - narrative: typewriter effect, supports inline color.
             - dialog: fixed box (2 lines) + typewriter, inline color.
             - thinking: fixed box (2 lines, italic) + typewriter, inline color.
             After each block, redraws title/footer/indicator without erasing previous content.
          4. Waits for player action (←/→/ENTER/ESC).
        """
        # 1) Clear pending events and wait for all keys to be released
        pygame.event.clear()
        pygame.event.pump()
        while any(pygame.key.get_pressed()):
            pygame.event.pump()
            pygame.time.delay(10)

        is_last = (current_page == total_pages)

        # 2) Draw black screen + title + footer + page indicator
        self.screen.fill((0, 0, 0))
        self._draw_title(title)
        self._draw_footer(is_last)
        self._draw_page_indicator(current_page, total_pages)
        pygame.display.flip()

        # Initial Y position (below title)
        y = self.title_area_height + self.block_spacing

        # 3) Iterate over blocks
        for blk in blocks:
            overrides = blk.overrides or {}

            # Font and colors, considering block-level overrides
            font_size = overrides.get("font_size", self.font_size_default)
            font = pygame.font.SysFont("consolas", font_size)
            text_color = overrides.get("color", self.text_color_default)
            speed = overrides.get("text_speed", self.text_speed)
            skip_ok = overrides.get("skip_enabled", self.skip_enabled)

            if blk.type == "location":
                # Subtitle with override or default color
                subtitle_color = overrides.get("subtitle_color", self.subtitle_color_default)
                loc_font = font
                loc_surf = loc_font.render(blk.content, True, subtitle_color)
                self.screen.blit(loc_surf, (self.margin_x, y))
                pygame.display.flip()
                time.sleep(0.5)
                y += self.line_height + self.block_spacing

            elif blk.type == "narrative":
                # Narrative text with inline color, single line
                y = self._typewriter_line(
                    blk.content,
                    x=self.margin_x,
                    y=y,
                    color=text_color,
                    font=font,
                    text_speed=speed,
                    skip_enabled=skip_ok
                )
                y += self.block_spacing

            elif blk.type in ("dialog", "thinking"):
                # Dialog or thought box (fixed height: 2 lines + padding)
                if blk.type == "dialog":
                    box_bg = overrides.get("dialogue_color", self.dialogue_bg_default)
                    txt_font = font
                else:
                    box_bg = overrides.get("thinking_color", self.thinking_bg_default)
                    txt_font = pygame.font.SysFont("consolas", font_size, italic=True)

                # Fixed box dimensions (up to 2 lines)
                box_w = int(self.text_area_width * 0.7)
                box_h = self.line_height * 2 + 20
                box_x = (SCREEN_WIDTH - box_w) // 2
                box_y = y - 10

                # Draw box background and border
                pygame.draw.rect(self.screen, box_bg, (box_x, box_y, box_w, box_h))
                border_color = (200, 200, 200) if blk.type == "dialog" else (255, 255, 255)
                pygame.draw.rect(self.screen, border_color, (box_x, box_y, box_w, box_h), 2)

                # Line 1: speaker (if present)
                if blk.speaker:
                    speaker_txt = f"[{blk.speaker}]"
                    speaker_color = (255, 255, 0) if blk.type == "dialog" else (255, 255, 255)
                    speaker_surf = txt_font.render(speaker_txt, True, speaker_color)
                    self.screen.blit(speaker_surf, (box_x + 10, box_y + 10))
                    pygame.display.flip()

                # Line 2: content with typewriter and inline color, single line
                start_y = box_y + 10 + self.line_height + 5
                self._typewriter_in_box(
                    blk.content,
                    x=box_x + 10,
                    y=start_y,
                    color=text_color,
                    font=txt_font,
                    box_x=box_x,
                    box_y=box_y,
                    box_w=box_w,
                    box_h=box_h,
                    bg_color=box_bg,
                    text_speed=speed,
                    skip_enabled=skip_ok
                )

                y = box_y + box_h + self.block_spacing

            # After each block, redraw title/footer/indicator (preserving content)
            self._draw_title(title)
            self._draw_footer(is_last)
            self._draw_page_indicator(current_page, total_pages)
            pygame.display.flip()

        # 4) Page complete; wait for action
        pygame.display.flip()

    def _typewriter_line(self, text, x, y, color, font, text_speed, skip_enabled):
        """
        Renders `text` character by character at (x, y).
        Supports inline color overrides: [color=#RRGGBB]...[/].
        If `skip_enabled` is True and any key is pressed, displays the rest instantly.
        No line breaks; renders as a single line.
        Returns y + line_height.
        """
        segments = []
        last_end = 0

        for match in self.INLINE_COLOR_PATTERN.finditer(text):
            start, end = match.span()
            hex_color = match.group(1)
            chunk = match.group(2)

            if start > last_end:
                normal_txt = text[last_end:start]
                segments.append((color, normal_txt))

            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            segments.append(((r, g, b), chunk))

            last_end = end

        if last_end < len(text):
            remainder = text[last_end:]
            segments.append((color, remainder))

        clock = pygame.time.Clock()
        cx = x  # cursor X

        for seg_color, seg_text in segments:
            idx = 0
            length = len(seg_text)
            accelerate = False
            partial = ""

            while idx < length:
                if accelerate:
                    partial = seg_text
                    rect_bg = pygame.Rect(cx, y, self.text_area_width - (cx - x), self.line_height)
                    pygame.draw.rect(self.screen, (0, 0, 0), rect_bg)
                    surf = font.render(partial, True, seg_color)
                    self.screen.blit(surf, (cx, y))
                    pygame.display.flip()
                    break

                partial = seg_text[: idx + 1 ]
                idx += 1

                rect_bg = pygame.Rect(cx, y, self.text_area_width - (cx - x), self.line_height)
                pygame.draw.rect(self.screen, (0, 0, 0), rect_bg)

                surf = font.render(partial, True, seg_color)
                self.screen.blit(surf, (cx, y))
                pygame.display.flip()

                start = time.time()
                while time.time() - start < text_speed:
                    for ev in pygame.event.get():
                        if ev.type == pygame.KEYDOWN and skip_enabled:
                            accelerate = True
                    clock.tick(60)

            seg_px_w = font.size(seg_text)[0]
            cx += seg_px_w

        return y + self.line_height

    def _typewriter_in_box(
        self, text, x, y, color, font,
        box_x, box_y, box_w, box_h,
        bg_color, text_speed, skip_enabled
    ):
        """
        Like `_typewriter_line`, but inside a box with `bg_color`.
        Renders all `text` in a single line, supports inline color.
        If `skip_enabled` is True and any key is pressed, displays the rest instantly.
        No line breaks. Clears only the box's inner area, preserving borders.
        """
        segments = []
        last_end = 0

        for match in self.INLINE_COLOR_PATTERN.finditer(text):
            start, end = match.span()
            hex_color = match.group(1)
            chunk = match.group(2)

            if start > last_end:
                normal_txt = text[last_end:start]
                segments.append((color, normal_txt))

            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            segments.append(((r, g, b), chunk))

            last_end = end

        if last_end < len(text):
            remainder = text[last_end:]
            segments.append((color, remainder))

        clock = pygame.time.Clock()
        cx = x  # cursor X inside the box

        for seg_color, seg_text in segments:
            idx = 0
            length = len(seg_text)
            accelerate = False
            partial = ""

            while idx < length:
                if accelerate:
                    partial = seg_text
                    rect_bg = pygame.Rect(cx, y, box_w - 20 - (cx - x), self.line_height)
                    pygame.draw.rect(self.screen, bg_color, rect_bg)
                    surf = font.render(partial, True, seg_color)
                    self.screen.blit(surf, (cx, y))
                    pygame.display.flip()
                    break

                partial = seg_text[: idx + 1 ]
                idx += 1

                rect_bg = pygame.Rect(cx, y, box_w - 20 - (cx - x), self.line_height)
                pygame.draw.rect(self.screen, bg_color, rect_bg)

                surf = font.render(partial, True, seg_color)
                self.screen.blit(surf, (cx, y))
                pygame.display.flip()

                start = time.time()
                while time.time() - start < text_speed:
                    for ev in pygame.event.get():
                        if ev.type == pygame.KEYDOWN and skip_enabled:
                            accelerate = True
                    clock.tick(60)

            seg_px_w = font.size(seg_text)[0]
            cx += seg_px_w

    def _draw_title(self, title):
        """
        Draws the centered title at the top.
        """
        titulo_surf = self.font.render(title, True, (255, 255, 255))
        titulo_rect = titulo_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                    self.line_height // 2 + 5))
        self.screen.blit(titulo_surf, titulo_rect)

    def _draw_footer(self, is_last=False):
        """
        Draws the fixed footer bar:
          ← Back     (ENTER repeat)     Next →     (ESC Menu)
        If is_last=True, shows "End →" instead of "Next →".
        """
        if is_last:
            texto = "← Back     (ENTER repeat)     (ESC Menu)     End →"
        else:
            texto = "← Back     (ENTER repeat)     (ESC Menu)     Next →"

        footer_font = pygame.font.SysFont("consolas", 18)
        surf = footer_font.render(texto, True, (200, 200, 200))
        x = (SCREEN_WIDTH - surf.get_width()) // 2
        y = SCREEN_HEIGHT - 30
        self.screen.blit(surf, (x, y))

    def _draw_page_indicator(self, current_page, total_pages):
        """
        Draws "Page X/Y" at the bottom right, above the footer.
        If current_page == total_pages, adds "(Last)".
        """
        if current_page == total_pages:
            texto = f"Page {current_page}/{total_pages} (Last)"
        else:
            texto = f"Page {current_page}/{total_pages}"

        small_font = pygame.font.SysFont("consolas", 16)
        surf = small_font.render(texto, True, (180, 180, 180))
        x = SCREEN_WIDTH - surf.get_width() - 20
        y = SCREEN_HEIGHT - 30 - surf.get_height() - 5
        self.screen.blit(surf, (x, y))
