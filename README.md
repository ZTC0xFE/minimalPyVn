# MinimalPyVN

A minimalist visual novel engine written in Python using Pygame. This project lets you create simple visual novels with typewriter effects, dialog and thought boxes, location markers, and more, all defined in easy-to-edit YAML files.

Note that some variables are in portuguese, as this project was initially created for a personal project in. Feel free to change them to your preferred language.

---

## Features Overview

- **Typewriter Text Rendering:** Narrative, dialog, location, and thought blocks are displayed with a typewriter effect.
- **Dialog & Thought Boxes:** Dialogs appear in bordered boxes with character names; thoughts are shown in italicized boxes.
- **Location Highlighting:** Location/time information is rendered in yellow for emphasis.
- **Section Navigation:** Navigate between sections with arrow keys; repeat sections or return to the menu.
- **Progress Saving:** The progress is saved automatically each section entered, and will be resumed when enter into an chapter again.
- **YAML-Driven Content:** Chapters and sections are defined in simple YAML files for easy editing and expansion.

---

## Installation & Version Check

1. **Clone the repository:**
   
   ```sh
   git clone https://github.com/ZTC0xFE/minimalPyVn.git
   cd minimalPyVn
   ```

2. **Install dependencies:**
   
    - Requires Python 3.8+
    - Install Pygame and PyYAML:
   
   ```sh
   pip install pygame pyyaml
   ```

3. **Check your Python version:**
   
   ```sh
   python --version
   ```

---

## Customization Options
- **Window Title**:
Change the `pygame.display.set_caption` definition in `main.py` to set your visual novel's title.
- **Screen Size**:
Change the `SCREEN_WIDTH` and `SCREEN_HEIGHT` in `settings.py` to adjust the window size.
- **Text Speed**:
Modify the `TEXT_SPEED` variable in `settings.py` to control the typewriter effect speed.
- **Colors & Fonts**:
Customize colors and fonts in `renderer.py` by editing the RGB tuples and font settings in the TextRenderer class.

--- 

## YAML Format & Example

Chapters are define in `.yml` files inside the `chapters` folder. Each file should have a `title`and `sections`. Each section is a list of lines, which can be:

- **Narrative**:
Plain text for narration (no special markers).
- **Location (or subtitle)**:
Start and end with `€`, e.g. `€Location - Time€`
- **Dialog**:
Start and end with `#`, with character in brackets, e.g. `# [Name] Dialog text.#`
- **Thought**:
Start and end with `¥`, with character in brackets, e.g. `¥ [Name] Thought text.¥`

**Example:**

```yaml
title: "Chapter 1: The Beginning"
sections:
    intro:
        - "This is the beginning of our story."
        - "€Location - Morning€"
        - "# [Alice] Hello, world!#"
        - "¥ [Alice] I wonder what adventures await me.¥"
        - "Another narrative line."
```
---

## Running & Building

- **Run directly:**
Open `main.py` in your IDE of preference (e.g VSCode, PyCharm) and run it. The main menu will appear.
- **Run from command line:**
  ```sh
  python main.py
  ```
- **Build an executable:** 
Use PyInstaller to create a standalone executable:
    ```sh
    pip install pyinstaller
    pyinstaller --onefile --add-data "chapters;chapters" main.py
    ```
- On Windows, the executable will be in the `dist` folder.
- For Mac/Linux, adjust the `--add-data` syntax as needed.

---

## Feedback & Support

Suggestions, improvements, and pull requests are welcome!
If you like this project, please consider starring ⭐ it on GitHub or leaving your feedback.

Psst! Inside the `chapters` folder, you'll find a sample chapter to get you started. Feel free to modify it or create your own!




