# MinimalPyVN

A minimalist visual novel engine written in Python using Pygame. This project lets you create simple visual novels with typewriter effects, dialog and thought boxes, location markers, and more—all defined in easy-to-edit YAML files.

> **Note:** Some variable names are in Portuguese, as this project was originally developed for a personal project. Feel free to rename them to your preferred language. Also, this was created with AI assistance, so it may not follow all best practices. However, it is functional and serves as a good starting point for simple visual novels, plus, it was just for fun. Don't take it as a professional project!

---

## Features Overview

- **Typewriter Text Rendering:** Narrative, dialog, location, and thought blocks appear with a typewriter effect.
- **Dialog & Thought Boxes:** Dialogs show in bordered boxes with character names; thoughts are displayed in italicized boxes.
- **Location Highlighting:** Location/time lines render in a distinct subtitle color for emphasis.
- **Section Navigation:** Use arrow keys (←/→) to move between sections; press ENTER to repeat a section or ESC to return to the menu.
- **Progress Saving:** Your progress is saved automatically per section, so you can resume where you left off when reopening a chapter.
- **YAML-Driven Content:** Chapters and sections are defined in simple YAML files for easy editing and expansion.
- **Advanced Styling (v1.1.1):**  
  - Global settings in `settings:` (text speed, font size, colors).  
  - Inline color overrides with `[color=#RRGGBB]…[/]`.  
  - Fixed-height dialog/thought boxes to prevent layout breakage.  
  - Hex-only color support in `settings:` and overrides.

---

## Installation & Version Check

1. **Clone the repository:**
   ```sh
   git clone https://github.com/ZTC0xFE/minimalPyVn.git
   cd minimalPyVn
   ```

2. **Install dependencies:**
   - Requires **Python 3.8+**  
   - Install Pygame and PyYAML:
     ```sh
     pip install pygame pyyaml
     ```

3. **Verify your Python version:**
   ```sh
   python --version
   ```

---

## Customization Options

- **Window Title:**  
  Change the `pygame.display.set_caption` line in `main.py` to set your VN’s window title.
- **Screen Size:**  
  Adjust `SCREEN_WIDTH` and `SCREEN_HEIGHT` in `settings.py` to change the window dimensions.
- **Text Speed:**  
  Modify `TEXT_SPEED` in `settings.py` (or via chapter-specific `settings:`) to control the typewriter pace.
- **Colors & Fonts:**  
  Customize colors and fonts within `renderer.py`’s `TextRenderer` class or via the new YAML `settings:` block.

---

## YAML Format & Example

Chapters live in `.yml` files under the `chapters/` folder. Each file must include a `title:` and `sections:`. Under `sections:`, each section is a list of lines, which can be:

- **Narrative:**  
  Plain text for narration (no special markers).
- **Location (or subtitle):**  
  Wrap with `€…€`, e.g. `€Location – Time€`.
- **Dialog:**  
  Wrap with `#…#`, including a speaker in brackets, e.g. `# [Name] Dialogue text.#`.
- **Thought:**  
  Wrap with `¥…¥`, including a speaker in brackets, e.g. `¥ [Name] Thought text.¥`.

### Example Chapter

```yaml
title: "Chapter 1: The Beginning"
sections:
  intro:
    - "This is the beginning of our story."
    - "€Location – Morning€"
    - "# [Alice] Hello, world!#"
    - "¥ [Alice] I wonder what adventures await me.¥"
    - "Another narrative line."
```

---

## How to use the YML

For a comprehensive guide to the new `settings:` block and inline color overrides (v1.1.1), please see:

[See the tutorial here! ](YML_Tutorial.md)

This tutorial covers:

1. Overall Structure  
2. `settings:` Block (Globals)  
3. Section & Block Syntax  
4. Inline Color Overrides  
5. Detailed Example YAML  

---

## Running & Building

- **Run directly (IDE):**  
  Open `main.py` in your favorite IDE (e.g., VS Code, PyCharm) and run it. The main menu will appear.

- **Run from the command line:**
  ```sh
  python main.py
  ```

- **Build a standalone executable:**  
  Install PyInstaller, then package all chapters and code:
  ```sh
  pip install pyinstaller
  pyinstaller --onefile --add-data "chapters;chapters" main.py
  ```
  - On Windows, the executable appears in the `dist/` folder.  
  - On macOS/Linux, adjust the `--add-data` syntax if needed.

---

## Feedback & Support

Suggestions, improvements, and pull requests are always welcome! If you find this project helpful, please consider starring ⭐ it on GitHub or opening an issue with your feedback.

> **Tip:** Inside the `chapters/` folder, you'll find a sample `.yml` chapter. Feel free to modify or replace it as a starting point.

