import os
import sys

# Window size
SCREEN_WIDTH = 1150
SCREEN_HEIGHT = 625

# Folder where the chapters (.yml) will be
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")

# Text speed (seconds per character)
TEXT_SPEED = 0.03
