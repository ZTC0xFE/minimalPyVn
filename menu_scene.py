import os
import glob
import pygame
import yaml

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, CHAPTERS_DIR
from game_scene import GameScene
from save_manager import load_progress

class MenuScene:
    """
    Displays a list of available chapters in CHAPTERS_DIR.
    For each .yml file, loads the 'title' field from the YAML.
    Sorts alphabetically by filename.
    Shows numbered (1. Chapter Title), coloring completed chapters (progress.pkl) in light blue.
    Navigate with ↑ ↓ and, when ENTER is pressed, returns the selected filename.
    """

    def __init__(self, screen):
        self.screen = screen
        self.clock  = pygame.time.Clock()
        self.font   = pygame.font.SysFont("consolas", 24)

        # 1) Lists all .yml files in the chapters folder (alphabetically)
        self.items = [os.path.basename(f) for f in glob.glob(os.path.join(CHAPTERS_DIR, "*.yml"))]
        self.items.sort()  # sort by filename

        # 2) For each filename, tries to read the YAML and extract 'title'
        self.titles = {}
        for filename in self.items:
            path = os.path.join(CHAPTERS_DIR, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    title = data.get("title", os.path.splitext(filename)[0])
            except Exception:
                title = os.path.splitext(filename)[0]
            self.titles[filename] = title

        self.selected_index = 0

        # 3) Loads saved progress (to color completed chapters)
        self.progress = load_progress()

    def run(self):
        while True:
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
                        escolhido = self.items[self.selected_index]
                        return escolhido
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

            # Draw background
            self.screen.fill((30, 30, 30))

            # Draw menu title
            title_surf = self.font.render("Chapter select", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 60))
            self.screen.blit(title_surf, title_rect)

            # Draw each numbered item: "1. Chapter Title"
            y = 140
            for idx, filename in enumerate(self.items):
                # Title from YAML
                title = self.titles.get(filename, os.path.splitext(filename)[0])
                display_text = f"{idx+1}. {title}"

                # Check if chapter is completed
                completed = False
                if filename in self.progress and self.progress[filename].get("completed", False):
                    completed = True

                # Color: orange if selected; light blue if completed; white otherwise
                if idx == self.selected_index:
                    color = (255, 180, 80)       # orange
                elif completed:
                    color = (150, 200, 255)      # light blue
                else:
                    color = (255, 255, 255)      # white

                text_surf = self.font.render(display_text, True, color)
                text_rect = text_surf.get_rect(midleft=(100, y))
                self.screen.blit(text_surf, text_rect)
                y += 40

            # Footer instruction
            instr = "Use ↑ ↓ to navigate | ENTER to choose | ESC to exit"
            instr_surf = self.font.render(instr, True, (180, 180, 180))
            instr_rect = instr_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            self.screen.blit(instr_surf, instr_rect)

            pygame.display.flip()
            self.clock.tick(30)

        return None