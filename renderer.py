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
      - Word-wrap for narrative and dialog/thought (boxes grow to fit).
      - Dialog/thought boxes with dynamic height.
      - Footer with “End →” if last page and “Page X/Y (Last)” indicator.
    """

    INLINE_COLOR_PATTERN = re.compile(r"\[color=(#[0-9A-Fa-f]{6})\](.*?)\[/\]")

    def __init__(self, screen, settings):
        pygame.font.init()
        self.screen = screen

        # Global settings (from parser.py)
        self.text_speed            = settings.get("text_speed",    0.03)
        self.skip_enabled          = settings.get("skip_enabled",  True)
        self.dialogue_bg_default   = settings.get("dialogue_color",(80, 80,  80))
        self.thinking_bg_default   = settings.get("thinking_color",(70, 70, 113))
        self.font_size_default     = settings.get("font_size",    20)
        self.text_color_default    = settings.get("text_color",   (255,255,255))
        self.subtitle_color_default= settings.get("subtitle_color",(255,255,  0))

        # Default fonts & metrics
        self.font               = pygame.font.SysFont("consolas", self.font_size_default)
        self.italic_font        = pygame.font.SysFont("consolas", self.font_size_default, italic=True)
        self.line_height        = self.font.get_linesize()
        self.margin_x           = 20
        self.title_area_height  = self.line_height + 10
        self.text_area_width    = SCREEN_WIDTH - 2 * self.margin_x
        self.block_spacing      = 20

    def _wrap_text(self, text, font, max_width):
        """
        Breaks text into lines so each line fits within max_width.
        """
        words, lines, cur = text.split(" "), [], ""
        for w in words:
            test = cur + ("" if cur=="" else " ") + w
            if font.size(test)[0] <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def render_section(self, blocks, title, current_page, total_pages):
        # 1) Clear pending keys
        pygame.event.clear()
        pygame.event.pump()
        while any(pygame.key.get_pressed()):
            pygame.event.pump()
            pygame.time.delay(10)

        is_last = (current_page == total_pages)

        # 2) Draw background + UI
        self.screen.fill((0, 0, 0))
        self._draw_title(title)
        self._draw_footer(is_last)
        self._draw_page_indicator(current_page, total_pages)
        pygame.display.flip()

        # Initial Y position
        y = self.title_area_height + self.block_spacing

        # 3) Render each block
        for blk in blocks:
            overrides = blk.overrides or {}
            font_size = overrides.get("font_size", self.font_size_default)
            font      = pygame.font.SysFont("consolas", font_size)
            text_color= overrides.get("color", self.text_color_default)
            speed     = overrides.get("text_speed", self.text_speed)
            skip_ok   = overrides.get("skip_enabled", self.skip_enabled)

            if blk.type == "location":
                col = overrides.get("subtitle_color", self.subtitle_color_default)
                surf = font.render(blk.content, True, col)
                self.screen.blit(surf, (self.margin_x, y))
                pygame.display.flip()
                time.sleep(0.5)
                y += self.line_height + self.block_spacing

            elif blk.type == "narrative":
                # word-wrap narrative
                lines = self._wrap_text(blk.content, font, self.text_area_width)
                for line in lines:
                    y = self._typewriter_line(
                        line,
                        x=self.margin_x,
                        y=y,
                        color=text_color,
                        font=font,
                        text_speed=speed,
                        skip_enabled=skip_ok
                    )
                y += self.block_spacing

            else:  # dialog or thinking
                # choose box background and speaker font
                if blk.type == "dialog":
                    bg      = overrides.get("dialogue_color", self.dialogue_bg_default)
                    sp_font = font
                else:
                    bg      = overrides.get("thinking_color", self.thinking_bg_default)
                    sp_font = pygame.font.SysFont("consolas", font_size, italic=True)

                # wrap and compute dynamic box size
                box_w   = int(self.text_area_width * 0.7)
                wrapped = self._wrap_text(blk.content, sp_font, box_w - 20)
                box_h   = (1 + len(wrapped)) * self.line_height + 20
                box_x   = (SCREEN_WIDTH - box_w) // 2
                box_y   = y - 10

                # draw box
                pygame.draw.rect(self.screen, bg, (box_x, box_y, box_w, box_h))
                border_color = (200,200,200) if blk.type=="dialog" else (255,255,255)
                pygame.draw.rect(self.screen, border_color, (box_x, box_y, box_w, box_h), 2)

                # speaker line
                if blk.speaker:
                    spc = (255,255,0) if blk.type=="dialog" else (255,255,255)
                    sp_surf = sp_font.render(f"[{blk.speaker}]", True, spc)
                    self.screen.blit(sp_surf, (box_x + 10, box_y + 10))
                    pygame.display.flip()

                # render each wrapped line inside box
                line_y = box_y + 10 + self.line_height + 5
                for line in wrapped:
                    line_y = self._typewriter_in_box(
                        line,
                        x=box_x + 10,
                        y=line_y,
                        color=text_color,
                        font=sp_font,
                        box_x=box_x,
                        box_y=box_y,
                        box_w=box_w,
                        box_h=box_h,
                        bg_color=bg,
                        text_speed=speed,
                        skip_enabled=skip_ok
                    )
                y = box_y + box_h + self.block_spacing

            # redraw UI (preserve content)
            self._draw_title(title)
            self._draw_footer(is_last)
            self._draw_page_indicator(current_page, total_pages)
            pygame.display.flip()

        # 4) Page complete; return to navigation loop
        pygame.display.flip()

    def _typewriter_line(self, text, x, y, color, font, text_speed, skip_enabled):
        """
        Single-line typewriter with inline-color support.
        """
        segments = []
        last_end = 0
        for match in self.INLINE_COLOR_PATTERN.finditer(text):
            s, e = match.span()
            if s > last_end:
                segments.append((color, text[last_end:s]))
            hexcol, chunk = match.group(1), match.group(2)
            r = int(hexcol[1:3], 16)
            g = int(hexcol[3:5], 16)
            b = int(hexcol[5:7], 16)
            segments.append(((r, g, b), chunk))
            last_end = e
        if last_end < len(text):
            segments.append((color, text[last_end:]))

        clock = pygame.time.Clock()
        cx = x
        for seg_color, seg_text in segments:
            idx = 0
            accelerate = False
            while idx < len(seg_text):
                if accelerate:
                    disp = seg_text
                else:
                    idx += 1
                    disp = seg_text[:idx]
                rect_bg = pygame.Rect(cx, y, self.text_area_width, self.line_height)
                pygame.draw.rect(self.screen, (0,0,0), rect_bg)
                surf = font.render(disp, True, seg_color)
                self.screen.blit(surf, (cx, y))
                pygame.display.flip()

                if not accelerate:
                    start = time.time()
                    while time.time() - start < text_speed:
                        for ev in pygame.event.get():
                            if ev.type == pygame.KEYDOWN and skip_enabled:
                                accelerate = True
                        clock.tick(60)
                else:
                    break
            cx += font.size(seg_text)[0]
        return y + self.line_height

    def _typewriter_in_box(
        self, text, x, y, color, font,
        box_x, box_y, box_w, box_h, bg_color,
        text_speed, skip_enabled
    ):
        """
        Typewriter inside a box, preserving borders & inline-color.
        Clears only the wclean width so colored segments don’t leak.
        """
        segments = []
        last_end = 0
        for match in self.INLINE_COLOR_PATTERN.finditer(text):
            s, e = match.span()
            if s > last_end:
                segments.append((color, text[last_end:s]))
            hexcol, chunk = match.group(1), match.group(2)
            r = int(hexcol[1:3], 16)
            g = int(hexcol[3:5], 16)
            b = int(hexcol[5:7], 16)
            segments.append(((r, g, b), chunk))
            last_end = e
        if last_end < len(text):
            segments.append((color, text[last_end:]))

        clock = pygame.time.Clock()
        cx = x
        for seg_color, seg_text in segments:
            idx = 0
            accelerate = False
            while idx < len(seg_text):
                if accelerate:
                    disp = seg_text
                else:
                    idx += 1
                    disp = seg_text[:idx]
                wclean = font.size(disp)[0]
                pygame.draw.rect(self.screen, bg_color, (cx, y, wclean, self.line_height))
                surf = font.render(disp, True, seg_color)
                self.screen.blit(surf, (cx, y))
                pygame.display.flip()

                if not accelerate:
                    start = time.time()
                    while time.time() - start < text_speed:
                        for ev in pygame.event.get():
                            if ev.type == pygame.KEYDOWN and skip_enabled:
                                accelerate = True
                        clock.tick(60)
                else:
                    break
            cx += font.size(seg_text)[0]
        return y + self.line_height

    def _draw_title(self, title):
        surf = self.font.render(title, True, (255,255,255))
        rect = surf.get_rect(center=(SCREEN_WIDTH//2, self.line_height//2+5))
        self.screen.blit(surf, rect)

    def _draw_footer(self, is_last=False):
        if is_last:
            texto = "← Back     (ENTER repeat)     (ESC Menu)     End →"
        else:
            texto = "← Back     (ENTER repeat)     (ESC Menu)     Next →"
        footer_font = pygame.font.SysFont("consolas", 18)
        surf = footer_font.render(texto, True, (200,200,200))
        x = (SCREEN_WIDTH - surf.get_width()) // 2
        y = SCREEN_HEIGHT - 30
        self.screen.blit(surf, (x, y))

    def _draw_page_indicator(self, current_page, total_pages):
        if current_page == total_pages:
            texto = f"Page {current_page}/{total_pages} (Last)"
        else:
            texto = f"Page {current_page}/{total_pages}"
        small_font = pygame.font.SysFont("consolas", 16)
        surf = small_font.render(texto, True, (180,180,180))
        x = SCREEN_WIDTH - surf.get_width() - 20
        y = SCREEN_HEIGHT - 30 - surf.get_height() - 5
        self.screen.blit(surf, (x, y))
