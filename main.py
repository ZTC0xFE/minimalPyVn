import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from menu_scene import MenuScene

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("VN Title Goes Here")

    # Initial scene: menu
    next_scene = MenuScene(screen)

    # Main loop: each scene returns the next scene
    while next_scene:
        next_scene = next_scene.run()

    # Exit the game
    pygame.quit()

if __name__ == "__main__":
    main()
