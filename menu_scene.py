import os
import glob
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, CHAPTERS_DIR
from parser import ContentParser
from game_scene import GameScene

class MenuScene:
    """
    Displays a list of available chapters in CHAPTERS_DIR.
    Navigate with ↑ ↓ and, by pressing ENTER, goes to GameScene.
    """
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.selected_index = 0

        # Lists all .yml files in the chapters folder
        pattern = os.path.join(CHAPTERS_DIR, "*.yml")
        self.files = sorted(glob.glob(pattern))

        # Loads titles using ContentParser (just to show in the menu)
        self.items = []
        for fpath in self.files:
            cp = ContentParser(fpath).load()
            self.items.append((fpath, cp.title))

        # Font for the menu
        self.font = pygame.font.SysFont("consolas", 24)

    def run(self):
        """
        Runs the menu loop until the user selects a chapter or closes.
        If selected, returns an instance of GameScene.
        """
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_UP:
                        self.selected_index = max(0, self.selected_index - 1)
                    elif ev.key == pygame.K_DOWN:
                        self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
                    elif ev.key == pygame.K_RETURN:
                        # Chapter selected
                        fpath, _ = self.items[self.selected_index]
                        return GameScene(self.screen, fpath)

            # Menu drawing
            self.screen.fill((0, 0, 0))
            y = 100
            for idx, (_, title) in enumerate(self.items):
                color = (255, 255, 0) if idx == self.selected_index else (255, 255, 255)
                text_surf = self.font.render(title, True, color)
                rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(text_surf, rect)
                y += 40

            # Instruction at the footer
            instr = "Use ↑ ↓ and ENTER to choose"
            instr_surf = self.font.render(instr, True, (180, 180, 180))
            instr_rect = instr_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            self.screen.blit(instr_surf, instr_rect)

            pygame.display.flip()
            self.clock.tick(30)

        return None
