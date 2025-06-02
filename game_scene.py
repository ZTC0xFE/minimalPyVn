import pygame
from parser import ContentParser
from renderer import TextRenderer
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class GameScene:
    """
    Displays section by section, calling render_blocks_typewriter to type out all content.
    Always shows the arrows “← Back” and “Next →” in the footer.
    If on the last section, “→” returns to the Menu.
    The chapter title appears in all sections, but is NOT redrawn in the navigation bar.
    """

    def __init__(self, screen, chapter_path):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.chapter_path = chapter_path

        cp = ContentParser(chapter_path).load()
        self.title = cp.title
        self.section_ids = list(cp.sections.keys())
        self.sections = cp.sections

        self.renderer = TextRenderer(screen)
        self.current_index = 0

        self.font = pygame.font.SysFont("consolas", 22)

    def run(self):
        """
        Main loop:
          1) Types out the entire current section (render_blocks_typewriter).
          2) Displays the fixed navigation bar in the footer.
          3) Waits for arrow key or ENTER:
             - LEFT: goes back (or, if it's the first section, returns to the menu).
             - RIGHT: goes to the next (or, if it's the last, returns to the menu).
             - ENTER: repeats the current section.
        """
        while True:
            sec_id = self.section_ids[self.current_index]
            blocos = self.sections[sec_id]

            # 1) Types out all content of the current section, passing the title
            self.renderer.render_blocks_typewriter(blocos, self.title)

            # 2) Displays the navigation bar and waits for input
            escolha = self._navigation_loop()
            if escolha == "voltar":
                if self.current_index == 0:
                    from menu_scene import MenuScene
                    return MenuScene(self.screen)
                else:
                    self.current_index -= 1

            elif escolha == "proximo":
                # If it's the last section, return to the menu
                if self.current_index == len(self.section_ids) - 1:
                    from menu_scene import MenuScene
                    return MenuScene(self.screen)
                else:
                    self.current_index += 1
            # If escolha == "mesma", repeat the same section

    def _navigation_loop(self):
        """
        Draws in the footer: “← Back    (ENTER repeats)    Next →”
        The screen already contains all section content (including title). Only the
        bottom area is overlaid to highlight the instructions, without redrawing the title.
        Waits for LEFT / RIGHT / ENTER:
          - LEFT: "voltar"
          - RIGHT: "proximo"
          - ENTER: "mesma" (repeats)
        """
        while True:
            # Overlay semi-transparent footer
            footer_h = 50
            footer_y = SCREEN_HEIGHT - footer_h
            s = pygame.Surface((SCREEN_WIDTH, footer_h))
            s.set_alpha(200)
            s.fill((0, 0, 0))
            self.screen.blit(s, (0, footer_y))

            # Builds the navigation string
            prompt = ""
            if self.current_index > 0:
                prompt += "← Back   "
            else:
                prompt += "           "
            prompt += "(ENTER repeats)   "
            if self.current_index < len(self.section_ids) - 1:
                prompt += "   Next →"
            else:
                prompt += "   (End) →"

            surf = self.font.render(prompt, True, (200, 200, 200))
            rect = surf.get_rect(center=(SCREEN_WIDTH // 2, footer_y + footer_h // 2))
            self.screen.blit(surf, rect)

            pygame.display.flip()

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

            pygame.time.delay(10)
