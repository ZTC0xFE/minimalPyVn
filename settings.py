import os
import sys

# Window size
SCREEN_WIDTH = 1150
SCREEN_HEIGHT = 625

# Directory for chapter files (.yml)
BASE_DIR     = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")

# File to store progress (pickle)
SAVE_FILE    = os.path.join(BASE_DIR, "progress.pkl")

# Text speed (seconds per character)
TEXT_SPEED = 0.03
