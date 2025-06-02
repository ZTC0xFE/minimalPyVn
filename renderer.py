import pygame
import time
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TEXT_SPEED

class TextRenderer:
    """
    Renders:
      - Centered title at the top.
      - All accumulated blocks (narration, location, dialog, thinking) as a full page.
      - Dialogs in a centered dark gray box with white text.
      - Thoughts in a centered dark blue box with italic white text.
      - Typewriter acceleration without skipping sections.
      - Footer bar and "Page X/Y" indicator at the bottom right, including "ESC Menu".
        When current_page == total_pages, footer shows "End →" instead of "Next →".
    """

    def __init__(self, screen):
        pygame.font.init()
        self.screen = screen

        # Fonts
        self.font        = pygame.font.SysFont("consolas", 20)
        self.italic_font = pygame.font.SysFont("consolas", 20, italic=True)

        # Line height (pixels)
        self.line_height = self.font.get_linesize()
        # Horizontal margin (pixels)
        self.margin_x    = 20

        # Reserved space for title (pixels)
        self.title_area_height = self.line_height + 10

        # Available text width (pixels)
        self.text_area_width   = SCREEN_WIDTH - 2 * self.margin_x

        # Vertical spacing between blocks (pixels)
        self.block_spacing = 20

    def render_section(self, blocks, title, current_page, total_pages):
        """
        Renders a full section (list of blocks) as a single page:
          1) Clears event buffer and waits for key release.
          2) Draws background, title, footer, and page indicator (with "(Última)" if last).
          3) For each block:
               • location: yellow text.
               • narrative: white text, typewriter effect.
               • dialog: centered gray box, [speaker] + typewriter.
               • thinking: centered dark blue box, italic typewriter.
             After each block, redraws title/footer/indicator.
          4) Waits for next action.
        """
        # 1) Clear pending events and wait for key release
        pygame.event.clear()
        pygame.event.pump()
        while any(pygame.key.get_pressed()):
            pygame.event.pump()
            pygame.time.delay(10)

        is_last = (current_page == total_pages)

        # 2) Draw background, title, footer, and page indicator
        self.screen.fill((0, 0, 0))
        self._draw_title(title)
        self._draw_footer(is_last=is_last)
        self._draw_page_indicator(current_page, total_pages)
        pygame.display.flip()

        # Initial Y position (below title)
        y = self.title_area_height + self.block_spacing

        # 3) Render each block
        for blk in blocks:
            if blk.type == "location":
                # Yellow text, no typewriter
                loc_surf = self.font.render(blk.content, True, (255, 255, 0))
                self.screen.blit(loc_surf, (self.margin_x, y))
                pygame.display.flip()
                time.sleep(0.5)
                y += self.line_height + self.block_spacing

            elif blk.type == "narrative":
                # White narrative text, typewriter effect
                y = self._typewriter_line(blk.content, self.margin_x, y, (255, 255, 255))
                y += self.block_spacing

            elif blk.type == "dialog":
                # Centered dark gray dialog box
                box_w = int(self.text_area_width * 0.7)
                box_h = self.line_height * 2 + 20
                box_x = (SCREEN_WIDTH - box_w) // 2
                box_y = y - 10

                # Dark gray background
                pygame.draw.rect(self.screen, (80, 80, 80), (box_x, box_y, box_w, box_h))
                # Light border
                pygame.draw.rect(self.screen, (200, 200, 200), (box_x, box_y, box_w, box_h), 2)

                # Line 1: speaker in yellow
                if blk.speaker:
                    nome_txt = f"[{blk.speaker}]"
                else:
                    nome_txt = ""
                nome_surf = self.font.render(nome_txt, True, (255, 255, 0))
                self.screen.blit(nome_surf, (box_x + 10, box_y + 10))
                pygame.display.flip()

                # Line 2: dialog content, typewriter effect
                y_text = box_y + 10 + self.line_height + 5
                self._typewriter_in_box(
                    blk.content,
                    x=box_x + 10,
                    y=y_text,
                    color=(255, 255, 255),
                    box_x=box_x,
                    box_y=box_y,
                    box_w=box_w,
                    box_h=box_h,
                    bg_color=(80, 80, 80),
                    italic=False
                )

                y = box_y + box_h + self.block_spacing

            elif blk.type == "thinking":
                # Centered dark blue thought box
                box_w = int(self.text_area_width * 0.7)
                box_h = self.line_height * 2 + 20
                box_x = (SCREEN_WIDTH - box_w) // 2
                box_y = y - 10

                # Dark blue background
                pygame.draw.rect(self.screen, (70, 70, 113), (box_x, box_y, box_w, box_h))
                # White border
                pygame.draw.rect(self.screen, (255, 255, 255), (box_x, box_y, box_w, box_h), 2)

                # Line 1: speaker in italic white
                if blk.speaker:
                    nome_txt = f"[{blk.speaker}]"
                    nome_surf = self.italic_font.render(nome_txt, True, (255, 255, 255))
                    self.screen.blit(nome_surf, (box_x + 10, box_y + 10))
                    pygame.display.flip()

                # Line 2: thought content, italic typewriter
                y_text = box_y + 10 + self.line_height + 5
                self._typewriter_in_box(
                    blk.content,
                    x=box_x + 10,
                    y=y_text,
                    color=(255, 255, 255),
                    box_x=box_x,
                    box_y=box_y,
                    box_w=box_w,
                    box_h=box_h,
                    bg_color=(70, 70, 113),
                    italic=True
                )

                y = box_y + box_h + self.block_spacing

            # After each block, redraw title/footer/indicator
            self._draw_title(title)
            self._draw_footer(is_last=is_last)
            self._draw_page_indicator(current_page, total_pages)
            pygame.display.flip()

        # 4) Wait for next action
        pygame.display.flip()

    def _typewriter_line(self, text, x, y, color, italic=False):
        """
        Renders text at (x, y) with typewriter effect.
        If any key is pressed, displays the rest instantly.
        Returns y + line_height.
        """
        displayed = ""
        clock = pygame.time.Clock()
        font = self.italic_font if italic else self.font

        idx = 0
        length = len(text)
        acelerar = False

        while idx < length:
            if acelerar:
                displayed = text
                rect_bg = pygame.Rect(x, y, self.text_area_width, self.line_height)
                pygame.draw.rect(self.screen, (0, 0, 0), rect_bg)
                surf = font.render(displayed, True, color)
                self.screen.blit(surf, (x, y))
                pygame.display.flip()
                break

            displayed += text[idx]
            idx += 1

            rect_bg = pygame.Rect(x, y, self.text_area_width, self.line_height)
            pygame.draw.rect(self.screen, (0, 0, 0), rect_bg)

            surf = font.render(displayed, True, color)
            self.screen.blit(surf, (x, y))
            pygame.display.flip()

            start = time.time()
            while time.time() - start < TEXT_SPEED:
                for ev in pygame.event.get():
                    if ev.type == pygame.KEYDOWN:
                        acelerar = True
                clock.tick(60)

        return y + self.line_height

    def _typewriter_in_box(self, text, x, y, color, box_x, box_y, box_w, box_h, bg_color, italic=False):
        """
        Renders text character by character inside a box with background color bg_color.
        If any key is pressed, displays the rest instantly.
        Only clears the box's inner area, preserving borders and speaker.
        """
        displayed = ""
        clock = pygame.time.Clock()
        font = self.italic_font if italic else self.font

        idx = 0
        length = len(text)
        acelerar = False

        while idx < length:
            if acelerar:
                displayed = text
                rect_bg = pygame.Rect(x, y, box_w - 20, self.line_height)
                pygame.draw.rect(self.screen, bg_color, rect_bg)
                surf = font.render(displayed, True, color)
                self.screen.blit(surf, (x, y))
                pygame.display.flip()
                break

            displayed += text[idx]
            idx += 1

            rect_bg = pygame.Rect(x, y, box_w - 20, self.line_height)
            pygame.draw.rect(self.screen, bg_color, rect_bg)

            surf = font.render(displayed, True, color)
            self.screen.blit(surf, (x, y))
            pygame.display.flip()

            start = time.time()
            while time.time() - start < TEXT_SPEED:
                for ev in pygame.event.get():
                    if ev.type == pygame.KEYDOWN:
                        acelerar = True
                clock.tick(60)

    def _draw_title(self, title):
        """
        Draws the centered title at the top.
        """
        titulo_surf = self.font.render(title, True, (255, 255, 255))
        titulo_rect = titulo_surf.get_rect(center=(SCREEN_WIDTH // 2, self.line_height // 2 + 5))
        self.screen.blit(titulo_surf, titulo_rect)

    def _draw_footer(self, is_last=False):
        """
        Draws the fixed footer bar.
        If is_last is True, displays "End →" instead of "Next →".
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
        Draws "Page X/Y" at the bottom right above the footer.
        If current_page == total_pages, appends "(Last)".
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
