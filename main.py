# main.py
import pygame
from menu_scene import MenuScene
from game_scene import GameScene
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT),
        pygame.RESIZABLE
    )
    pygame.display.set_caption("Title goes here uwu")

    while True:
        # 1) Main menu screen
        menu = MenuScene(screen)
        chosen = menu.run()  # returns string "chapter_name.yml"

        # 2) Upon selection, enter GameScene
        game = GameScene(screen, chosen)
        game.run()
        # When game.run() finishes, return to menu

if __name__ == "__main__":
    main()
