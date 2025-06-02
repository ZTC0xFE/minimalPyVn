import pygame
import time
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TEXT_SPEED

class TextRenderer:
    """
    Renders blocks of TextBlock, DialogBlock, LocationBlock, and ThinkingBlock with a typewriter effect,
    accumulating all section content on the screen and keeping styles correct when redrawing.
    """

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("consolas", 20)
        self.italic_font = pygame.font.SysFont("consolas", 20, italic=True)
        self.line_height = self.font.get_linesize()
        self.margin_x = 20

        # Reserved space for the title at the top (in pixels)
        self.title_area_height = self.line_height + 10

        # Available width for text (in pixels)
        self.text_area_width = SCREEN_WIDTH - 2 * self.margin_x

    def render_blocks_typewriter(self, blocks, title):
        """
        Receives:
          - blocks: list of blocks (TextBlock / DialogBlock / LocationBlock / ThinkingBlock)
          - title: chapter title string

        Displays typewriter effect, showing the fixed title at the top. Any key speeds up the current block,
        but discards any keys already pressed before starting.
        """
        # Clears pending events and waits for any pressed keys to be released
        pygame.event.clear()
        pygame.event.pump()
        while any(pygame.key.get_pressed()):
            pygame.event.pump()
            pygame.time.delay(10)

        # Lists to store what has already been drawn:
        text_lines = []      # [(text, y_pos), ...]         (narrative, in white)
        location_lines = []  # [(text, y_pos), ...]         (location/time, in yellow)
        dialog_boxes = []    # [(bx, by, bw, bh, nm, wrapped_dialog), ...]
        thinking_boxes = []  # [(bx, by, bw, bh, nm, wrapped_think), ...]

        # Initial vertical position (just below the title)
        y_cursor = self.title_area_height + 10

        for block in blocks:
            from parser import TextBlock, DialogBlock, LocationBlock, ThinkingBlock

            # ————— TextBlock (narrative) —————
            if isinstance(block, TextBlock):
                wrapped = self._wrap_text(block.text)

                for line in wrapped:
                    partial = ""
                    for char in line:
                        partial += char
                        # 1) Clear the screen and draw the title
                        self._draw_background_and_title(title)

                        # 2) Draw all completed location lines (in yellow)
                        for (loc_text, y_loc) in location_lines:
                            surf_loc = self.font.render(loc_text, True, (255, 255, 0))
                            self.screen.blit(surf_loc, (self.margin_x, y_loc))

                        # 3) Draw ALL completed normal text lines (in white)
                        for (t, y_pos) in text_lines:
                            surf = self.font.render(t, True, (255, 255, 255))
                            self.screen.blit(surf, (self.margin_x, y_pos))

                        # 4) Draw ALL completed thinking boxes
                        for (bx_t, by_t, bw_t, bh_t, nm_t, think_lines) in thinking_boxes:
                            pygame.draw.rect(self.screen, (30, 30, 80), (bx_t, by_t, bw_t, bh_t))
                            pygame.draw.rect(self.screen, (150, 150, 150), (bx_t, by_t, bw_t, bh_t), 2)

                            nome_txt_t = f"[{nm_t}] "
                            nome_surf_t = self.italic_font.render(nome_txt_t, True, (200, 200, 0))
                            self.screen.blit(nome_surf_t, (bx_t + 10, by_t + 10))

                            y_dt = by_t + 10 + self.line_height
                            for dln_t in think_lines:
                                dlg_surf_t = self.italic_font.render(dln_t, True, (200, 200, 200))
                                self.screen.blit(dlg_surf_t, (bx_t + 10, y_dt))
                                y_dt += self.line_height

                        # 5) Draw ALL completed dialog boxes
                        for (bx, by, bw, bh, nm, dlg_lines) in dialog_boxes:
                            pygame.draw.rect(self.screen, (50, 50, 50), (bx, by, bw, bh))
                            pygame.draw.rect(self.screen, (200, 200, 200), (bx, by, bw, bh), 2)

                            nome_txt = f"[{nm}] "
                            nome_surf = self.font.render(nome_txt, True, (255, 255, 0))
                            self.screen.blit(nome_surf, (bx + 10, by + 10))

                            y_d = by + 10 + self.line_height
                            for dln in dlg_lines:
                                dlg_surf = self.font.render(dln, True, (255, 255, 255))
                                self.screen.blit(dlg_surf, (bx + 10, y_d))
                                y_d += self.line_height

                        # 6) Draw the partial line (narrative)
                        surf = self.font.render(partial, True, (255, 255, 255))
                        self.screen.blit(surf, (self.margin_x, y_cursor))

                        pygame.display.flip()

                        # 7) Wait for TEXT_SPEED or speed up if any key is detected
                        start = time.time()
                        while time.time() - start < TEXT_SPEED:
                            for ev in pygame.event.get():
                                if ev.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()
                            if any(pygame.key.get_pressed()):
                                break
                            pygame.time.delay(1)

                    # After finishing the line, add it as completed
                    text_lines.append((line, y_cursor))
                    y_cursor += self.line_height

                # Extra space after narrative block
                y_cursor += self.line_height // 2

            # ————— DialogBlock (standard dialog box) —————
            elif isinstance(block, DialogBlock):
                nome = block.character
                texto = block.text
                wrapped_dialog = self._wrap_text(texto)

                nome_txt = f"[{nome}] "
                nome_w, _ = self.font.size(nome_txt)
                max_text_w = nome_w
                for ln in wrapped_dialog:
                    w, _ = self.font.size(ln)
                    if w > max_text_w:
                        max_text_w = w

                box_padding = 10
                box_w = max_text_w + box_padding * 2
                box_h = (1 + len(wrapped_dialog)) * self.line_height + box_padding * 3

                box_x = (SCREEN_WIDTH - box_w) // 2
                box_y = y_cursor

                current_lines = []
                for ln in wrapped_dialog:
                    partial = ""
                    for char in ln:
                        partial += char
                        # 1) Clear screen and draw title
                        self._draw_background_and_title(title)

                        # 2) Draw completed location and narrative
                        for (loc_text, y_loc) in location_lines:
                            surf_loc = self.font.render(loc_text, True, (255, 255, 0))
                            self.screen.blit(surf_loc, (self.margin_x, y_loc))
                        for (t, y_pos) in text_lines:
                            surf = self.font.render(t, True, (255, 255, 255))
                            self.screen.blit(surf, (self.margin_x, y_pos))

                        # 3) Draw completed thinking boxes
                        for (bx_t, by_t, bw_t, bh_t, nm_t, think_lines) in thinking_boxes:
                            pygame.draw.rect(self.screen, (30, 30, 80), (bx_t, by_t, bw_t, bh_t))
                            pygame.draw.rect(self.screen, (150, 150, 150), (bx_t, by_t, bw_t, bh_t), 2)

                            nome_txt_t = f"[{nm_t}] "
                            nome_surf_t = self.italic_font.render(nome_txt_t, True, (200, 200, 0))
                            self.screen.blit(nome_surf_t, (bx_t + 10, by_t + 10))

                            y_dt = by_t + 10 + self.line_height
                            for dln_t in think_lines:
                                dlg_surf_t = self.italic_font.render(dln_t, True, (200, 200, 200))
                                self.screen.blit(dlg_surf_t, (bx_t + 10, y_dt))
                                y_dt += self.line_height

                        # 4) Draw ALL completed dialog boxes
                        for (bx2, by2, bw2, bh2, nm2, dlg2) in dialog_boxes:
                            pygame.draw.rect(self.screen, (50, 50, 50), (bx2, by2, bw2, bh2))
                            pygame.draw.rect(self.screen, (200, 200, 200), (bx2, by2, bw2, bh2), 2)
                            nome_surf2 = self.font.render(f"[{nm2}] ", True, (255, 255, 0))
                            self.screen.blit(nome_surf2, (bx2 + 10, by2 + 10))
                            y_d2 = by2 + 10 + self.line_height
                            for dln2 in dlg2:
                                dlg_surf2 = self.font.render(dln2, True, (255, 255, 255))
                                self.screen.blit(dlg_surf2, (bx2 + 10, y_d2))
                                y_d2 += self.line_height

                        # 5) Draw the current dialog box
                        pygame.draw.rect(self.screen, (50, 50, 50), (box_x, box_y, box_w, box_h))
                        pygame.draw.rect(self.screen, (200, 200, 200), (box_x, box_y, box_w, box_h), 2)

                        # 6) Name in yellow
                        nome_surf = self.font.render(nome_txt, True, (255, 255, 0))
                        self.screen.blit(nome_surf, (box_x + 10, box_y + 10))

                        # 7) Already completed dialog lines
                        y_d = box_y + 10 + self.line_height
                        for dln in current_lines:
                            dlg_surf = self.font.render(dln, True, (255, 255, 255))
                            self.screen.blit(dlg_surf, (box_x + 10, y_d))
                            y_d += self.line_height

                        # 8) Current partial line
                        dlg_surf = self.font.render(partial, True, (255, 255, 255))
                        self.screen.blit(dlg_surf, (box_x + 10, y_d))

                        pygame.display.flip()

                        # 9) Wait for TEXT_SPEED or speed up if any key is detected
                        start = time.time()
                        while time.time() - start < TEXT_SPEED:
                            for ev in pygame.event.get():
                                if ev.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()
                            if any(pygame.key.get_pressed()):
                                break
                            pygame.time.delay(1)

                    current_lines.append(ln)

                dialog_boxes.append((box_x, box_y, box_w, box_h, nome, wrapped_dialog))
                y_cursor += box_h + (self.line_height // 2)

            # ————— LocationBlock (entire line in yellow) —————
            elif isinstance(block, LocationBlock):
                # Clear and draw title
                self._draw_background_and_title(title)

                # Draw everything that already exists (white text, dialogs, thoughts)
                for (loc_text, y_loc) in location_lines:
                    surf_loc = self.font.render(loc_text, True, (255, 255, 0))
                    self.screen.blit(surf_loc, (self.margin_x, y_loc))
                for (t, y_pos) in text_lines:
                    surf = self.font.render(t, True, (255, 255, 255))
                    self.screen.blit(surf, (self.margin_x, y_pos))
                for (bx_t, by_t, bw_t, bh_t, nm_t, think_lines) in thinking_boxes:
                    pygame.draw.rect(self.screen, (30, 30, 80), (bx_t, by_t, bw_t, bh_t))
                    pygame.draw.rect(self.screen, (150, 150, 150), (bx_t, by_t, bw_t, bh_t), 2)
                    nome_txt_t = f"[{nm_t}] "
                    nome_surf_t = self.italic_font.render(nome_txt_t, True, (200, 200, 0))
                    self.screen.blit(nome_surf_t, (bx_t + 10, by_t + 10))
                    y_dt = by_t + 10 + self.line_height
                    for dln_t in think_lines:
                        dlg_surf_t = self.italic_font.render(dln_t, True, (200, 200, 200))
                        self.screen.blit(dlg_surf_t, (bx_t + 10, y_dt))
                        y_dt += self.line_height
                for (bx2, by2, bw2, bh2, nm2, dlg2) in dialog_boxes:
                    pygame.draw.rect(self.screen, (50, 50, 50), (bx2, by2, bw2, bh2))
                    pygame.draw.rect(self.screen, (200, 200, 200), (bx2, by2, bw2, bh2), 2)
                    nome_surf2 = self.font.render(f"[{nm2}] ", True, (255, 255, 0))
                    self.screen.blit(nome_surf2, (bx2 + 10, by2 + 10))
                    y_d2 = by2 + 10 + self.line_height
                    for dln2 in dlg2:
                        dlg_surf2 = self.font.render(dln2, True, (255, 255, 255))
                        self.screen.blit(dlg_surf2, (bx2 + 10, y_d2))
                        y_d2 += self.line_height

                # Draw the location line in yellow
                surf_yellow = self.font.render(block.text, True, (255, 255, 0))
                self.screen.blit(surf_yellow, (self.margin_x, y_cursor))
                pygame.display.flip()

                # Small delay for the user to see
                pygame.time.delay(500)

                # Add to the list of completed locations
                location_lines.append((block.text, y_cursor))
                y_cursor += self.line_height + (self.line_height // 2)

            # ————— ThinkingBlock (italic thought box) —————
            elif isinstance(block, ThinkingBlock):
                nome = block.character
                texto = block.text

                wrapped_think = self._wrap_text(texto)

                nome_txt = f"[{nome}] "
                nome_w, _ = self.italic_font.size(nome_txt)
                max_text_w = nome_w
                for ln in wrapped_think:
                    w, _ = self.italic_font.size(ln)
                    if w > max_text_w:
                        max_text_w = w

                box_padding = 10
                box_w = max_text_w + box_padding * 2
                box_h = (1 + len(wrapped_think)) * self.line_height + box_padding * 3

                box_x = (SCREEN_WIDTH - box_w) // 2
                box_y = y_cursor

                current_lines = []
                for ln in wrapped_think:
                    partial = ""
                    for char in ln:
                        partial += char
                        # Clear screen and draw title
                        self._draw_background_and_title(title)

                        # Draw completed location and narrative
                        for (loc_text, y_loc) in location_lines:
                            surf_loc = self.font.render(loc_text, True, (255, 255, 0))
                            self.screen.blit(surf_loc, (self.margin_x, y_loc))
                        for (t, y_pos) in text_lines:
                            surf = self.font.render(t, True, (255, 255, 255))
                            self.screen.blit(surf, (self.margin_x, y_pos))

                        # Draw already completed thinking boxes
                        for (bx_t2, by_t2, bw_t2, bh_t2, nm_t2, think_lines2) in thinking_boxes:
                            pygame.draw.rect(self.screen, (30, 30, 80), (bx_t2, by_t2, bw_t2, bh_t2))
                            pygame.draw.rect(self.screen, (150, 150, 150), (bx_t2, by_t2, bw_t2, bh_t2), 2)
                            nome_surf2 = self.italic_font.render(f"[{nm_t2}] ", True, (200, 200, 0))
                            self.screen.blit(nome_surf2, (bx_t2 + 10, by_t2 + 10))
                            y_dt2 = by_t2 + 10 + self.line_height
                            for dln2 in think_lines2:
                                dlg_surf2 = self.italic_font.render(dln2, True, (200, 200, 200))
                                self.screen.blit(dlg_surf2, (bx_t2 + 10, y_dt2))
                                y_dt2 += self.line_height

                        # Draw completed dialog boxes
                        for (bx2, by2, bw2, bh2, nm2, dlg2) in dialog_boxes:
                            pygame.draw.rect(self.screen, (50, 50, 50), (bx2, by2, bw2, bh2))
                            pygame.draw.rect(self.screen, (200, 200, 200), (bx2, by2, bw2, bh2), 2)
                            nome_surf2 = self.font.render(f"[{nm2}] ", True, (255, 255, 0))
                            self.screen.blit(nome_surf2, (bx2 + 10, by2 + 10))
                            y_d2 = by2 + 10 + self.line_height
                            for dln2 in dlg2:
                                dlg_surf2 = self.font.render(dln2, True, (255, 255, 255))
                                self.screen.blit(dlg_surf2, (bx2 + 10, y_d2))
                                y_d2 += self.line_height

                        # Draw the current thinking box
                        pygame.draw.rect(self.screen, (30, 30, 80), (box_x, box_y, box_w, box_h))
                        pygame.draw.rect(self.screen, (150, 150, 150), (box_x, box_y, box_w, box_h), 2)

                        # Name in italic/light yellow
                        nome_surf = self.italic_font.render(nome_txt, True, (200, 200, 0))
                        self.screen.blit(nome_surf, (box_x + 10, box_y + 10))

                        # Already completed thought lines
                        y_d = box_y + 10 + self.line_height
                        for dln in current_lines:
                            dlg_surf = self.italic_font.render(dln, True, (200, 200, 200))
                            self.screen.blit(dlg_surf, (box_x + 10, y_d))
                            y_d += self.line_height

                        # Partial line in italic
                        dlg_surf = self.italic_font.render(partial, True, (200, 200, 200))
                        self.screen.blit(dlg_surf, (box_x + 10, y_d))

                        pygame.display.flip()

                        # Wait for TEXT_SPEED or speed up if any key is detected
                        start = time.time()
                        while time.time() - start < TEXT_SPEED:
                            for ev in pygame.event.get():
                                if ev.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()
                            if any(pygame.key.get_pressed()):
                                break
                            pygame.time.delay(1)

                    current_lines.append(ln)

                thinking_boxes.append((box_x, box_y, box_w, box_h, nome, wrapped_think))
                y_cursor += box_h + (self.line_height // 2)

        # At the end of all blocks, keep the static content on the screen
        pygame.display.flip()

    def _draw_background_and_title(self, title):
        """
        Clears the screen and draws the title at the top (centered).
        """
        self.screen.fill((0, 0, 0))
        titulo_surf = self.font.render(title, True, (255, 255, 255))
        titulo_rect = titulo_surf.get_rect(center=(SCREEN_WIDTH // 2, self.line_height // 2 + 5))
        self.screen.blit(titulo_surf, titulo_rect)

    def _wrap_text(self, text):
        """
        Breaks 'text' into several lines that fit within text_area_width.
        Returns a list of lines.
        """
        words = text.split(" ")
        lines = []
        current = ""
        for w in words:
            teste = current + ("" if current == "" else " ") + w
            largura, _ = self.font.size(teste)
            if largura <= self.text_area_width:
                current = teste
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines

    
