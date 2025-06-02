import os
import pygame
from parser import ContentParser
from renderer import TextRenderer

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, CHAPTERS_DIR
from save_manager import load_progress, save_progress

class GameScene:
    """
    Shows each chapter section as a full “page”.
    - ←/→/ENTER/ESC for navigation.
    - ESC returns to menu anytime.
    - Progress is saved in progress.pkl.
    """

    def __init__(self, screen, chapter_filename):
        self.screen           = screen
        self.chapter_filename = chapter_filename
        self.full_path        = os.path.join(CHAPTERS_DIR, chapter_filename)

        # Parse chapter: get title and sections
        parser = ContentParser(self.full_path)
        self.title       = parser.title
        self.sections    = parser.sections    # dict: { section_id: Section(...) }
        self.section_ids = parser.section_ids # ordered list

        self.total_pages = len(self.section_ids)
        self.current_i   = 0  # index 0..total_pages-1

        self.renderer = TextRenderer(screen)

        # Load progress
        self.progress = load_progress()
        if chapter_filename not in self.progress:
            self.progress[chapter_filename] = {"last_page": 0, "completed": False}

        # Restart if already completed
        if self.progress[chapter_filename].get("completed", False):
            self.current_i = 0
            self.progress[chapter_filename]["last_page"] = 0
            self.progress[chapter_filename]["completed"] = False
            save_progress(self.progress)
        else:
            last = self.progress[chapter_filename].get("last_page", 0)
            if 0 <= last < self.total_pages:
                self.current_i = last
            else:
                self.current_i = 0

    def run(self):
        clock = pygame.time.Clock()

        while True:
            # Render current section as a full page
            sec_id = self.section_ids[self.current_i]
            section = self.sections[sec_id]
            blocks  = section.blocks

            self.renderer.render_section(
                blocks,
                self.title,
                current_page = self.current_i + 1,
                total_pages  = self.total_pages
            )

            # Clear pending events
            pygame.event.clear()
            pygame.event.pump()

            # Wait for ←/→/ENTER/ESC
            choice = self._navigation_loop()

            if choice == "voltar":
                if self.current_i == 0:
                    # First section + ← returns to menu
                    self._save_and_return_menu()
                    return
                else:
                    self.current_i -= 1

            elif choice == "proximo":
                if self.current_i == self.total_pages - 1:
                    # Last section + → returns to menu
                    self._save_and_return_menu()
                    return
                else:
                    self.current_i += 1

            elif choice == "mesma":
                # Redraw same section
                pass

            elif choice == "menu":
                # ESC pressed → return to menu
                self._save_and_return_menu()
                return

            # Update progress
            self._update_progress()
            clock.tick(60)

    def _navigation_loop(self):
        """
        Waits for ←, →, ENTER or ESC.
        Returns "voltar", "proximo", "mesma" or "menu".
        """
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_LEFT:
                        return "voltar"
                    elif ev.key == pygame.K_RIGHT:
                        return "proximo"
                    elif ev.key == pygame.K_RETURN:
                        return "mesma"
                    elif ev.key == pygame.K_ESCAPE:
                        return "menu"
            pygame.time.delay(10)

    def _update_progress(self):
        """
        Save last_page and completed in progress.pkl.
        """
        cap = self.chapter_filename
        self.progress[cap]["last_page"] = self.current_i
        self.progress[cap]["completed"] = (self.current_i == self.total_pages - 1)
        save_progress(self.progress)

    def _save_and_return_menu(self):
        """
        Save progress and return to menu.
        """
        save_progress(self.progress)
        # main.py will call MenuScene on return
