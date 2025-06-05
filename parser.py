import os
import yaml

class Block:
    """
    Represents a text block in a chapter. Types:
      - "narrative": normal text.
      - "location" : subtitle/location.
      - "dialog"   : dialog (box).
      - "thinking" : thought (box).

    Each block can have style overrides via line:
      - color:          RGB tuple for text (e.g., (255,0,0))
      - font_size:      int
      - text_speed:     float (seconds per character)
      - skip_enabled:   bool
      - subtitle_color: RGB tuple for location
      - dialogue_color: RGB tuple for dialog background
      - thinking_color: RGB tuple for thought background
      - text_color:     RGB tuple for text
    """
    def __init__(self, block_type, content, speaker=None, overrides=None):
        self.type      = block_type      # "narrative", "location", "dialog", or "thinking"
        self.content   = content         # plain text, no tags
        self.speaker   = speaker or ""   # only for dialog and thinking
        self.overrides = overrides or {} # dict of override key:value pairs

class Section:
    """
    Each YAML section becomes a 'page'. Contains:
      - id:     section key (e.g., "part1", "cap2", etc.)
      - blocks: list of parsed Block() objects
    """
    def __init__(self, section_id, blocks):
        self.id     = section_id
        self.blocks = blocks

class ContentParser:
    """
    Parses a chapter YAML file, which may optionally have a "settings:" section before "title:".
    Expected structure:

      settings:                     # OPTIONAL, before "title"
        text_speed: 0.03
        skip_enabled: true
        dialogue_color: "#505050"
        thinking_color: "#463A91"
        font_size: 20
        text_color: "#FFFFFF"
        subtitle_color: "#FFFF00"

      title: "Chapter Title"
      sections:
        part1:
          - "Narrative: Narrative text here."
          - "€Location - Morning€"
          - "# [Alice] Hello!#"
          - "¥ [Alice] Her thought.¥"
          - "[color=#FF0000]Narrative: All red text.[/]"
        part2:
          - "Narrative: Another part..."
          - "# [Bob] Normal dialog.#"
          - "[dialogue_color=#303030;font_size=18]# [Bob] Special dialog. Like it?#[/]"
          - "¥ [Bob] Thought without override.¥"

    Parsing rules:
      1. Loads `settings:` (if present) into `self.settings`. Colors must be "#RRGGBB" format.
         If not, IGNORE (use default). "R,G,B" is not accepted.
      2. Gets `title:` into `self.title`.
      3. For each section in `data["sections"]`, processes each string:
         a) If the line STARTS with "[…]" and ends with "[/]", parse internal key=value;… pairs.
            For color keys (dialogue_color, thinking_color, text_color, subtitle_color), expects "#RRGGBB".
            Otherwise, ignore that color override.
            Converts numbers and bools as well. Removes the override part, leaving only the plain text.
         b) With the plain text, identifies the type:
            - Starts with "Narrative:" → narrative.
            - Between "€…€" → location.
            - Between "#…#" → dialog (tries to extract speaker in "[Name]").
            - Between "¥…¥" → thinking (tries to extract speaker).
            - Anything else → narrative.
         c) Creates `Block(type, content, speaker, overrides)` and adds to `blocks`.

      4. Stores in:
         - `self.settings` : dict with global settings, already converted (colors as tuples).
         - `self.title`    : string with the title or filename.
         - `self.sections` : dict where each key is `section_id` and value is `Section(section_id, blocks)`.
         - `self.section_ids`: ordered list of section IDs.

    All color values in `self.settings` or `overrides` are always **tuples (R,G,B)**,
    extracted from "#RRGGBB". If not in this format, the color is ignored.
    """

    def __init__(self, chapter_path):
        if not os.path.exists(chapter_path):
            raise FileNotFoundError(f"Chapter file not found:\n  {chapter_path}")

        self.chapter_path = chapter_path
        self.title        = ""
        self.settings     = {}
        self.sections     = {}
        self.section_ids  = []

        self._parse_file()

    def _parse_file(self):
        # Load YAML
        with open(self.chapter_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # 1) Parse global settings (only "#RRGGBB" colors)
        raw_settings = data.get("settings", {})
        self.settings = {}
        color_keys = ("dialogue_color", "thinking_color", "text_color", "subtitle_color")

        for key, val in raw_settings.items():
            if key in color_keys and isinstance(val, str):
                s = val.strip()
                if s.startswith("#") and len(s) == 7:
                    try:
                        r = int(s[1:3], 16)
                        g = int(s[3:5], 16)
                        b = int(s[5:7], 16)
                        self.settings[key] = (r, g, b)
                    except:
                        pass
                # Ignore other formats (e.g., "255,255,0")
            else:
                # Direct copy for other keys (text_speed, skip_enabled, font_size)
                self.settings[key] = val

        # 2) Get title
        self.title = data.get("title",
                              os.path.splitext(os.path.basename(self.chapter_path))[0])

        # 3) Process sections in order
        raw_sections = data.get("sections", {})
        for section_id, raw_list in raw_sections.items():
            if not isinstance(raw_list, list):
                continue

            blocks = []
            for raw_line in raw_list:
                line_str = raw_line.strip()
                if not line_str:
                    continue

                overrides = {}

                # 3a) Detect full-line override: [key=value;…]…[/]
                if line_str.startswith("[") and line_str.endswith("[/]"):
                    close_idx = line_str.find("]")
                    if 0 < close_idx < len(line_str) - 3:
                        settings_str = line_str[1:close_idx]
                        content_body = line_str[close_idx+1:-3].strip()

                        for pair in settings_str.split(";"):
                            if "=" not in pair:
                                continue
                            k, v = pair.split("=", 1)
                            k = k.strip()
                            v = v.strip()

                            if k == "skip_enabled":
                                overrides[k] = (v.lower() == "true")
                            elif k == "font_size":
                                try:
                                    overrides[k] = int(v)
                                except:
                                    pass
                            elif k == "text_speed":
                                try:
                                    overrides[k] = float(v)
                                except:
                                    pass
                            elif k in color_keys:
                                if v.startswith("#") and len(v) == 7:
                                    try:
                                        r = int(v[1:3], 16)
                                        g = int(v[3:5], 16)
                                        b = int(v[5:7], 16)
                                        overrides[k] = (r, g, b)
                                    except:
                                        pass
                                # Ignore other formats
                            else:
                                overrides[k] = v

                        # Replace line with content without override tags
                        line_str = content_body

                # 3b) Identify block type
                if line_str.startswith("Narrative:"):
                    content = line_str[len("Narrative:"):].lstrip()
                    blocks.append(Block("narrative", content, overrides=overrides))
                    continue

                if line_str.startswith("€") and line_str.endswith("€"):
                    content = line_str[1:-1].strip()
                    blocks.append(Block("location", content, overrides=overrides))
                    continue

                if line_str.startswith("#") and line_str.endswith("#"):
                    inner = line_str[1:-1].strip()
                    if inner.startswith("[") and "]" in inner:
                        end_br = inner.find("]")
                        speaker = inner[1:end_br]
                        content = inner[end_br+1:].lstrip()
                        blocks.append(Block("dialog", content, speaker, overrides=overrides))
                    else:
                        blocks.append(Block("dialog", inner, "", overrides=overrides))
                    continue

                if line_str.startswith("¥") and line_str.endswith("¥"):
                    inner = line_str[1:-1].strip()
                    if inner.startswith("[") and "]" in inner:
                        end_br = inner.find("]")
                        speaker = inner[1:end_br]
                        content = inner[end_br+1:].lstrip()
                        blocks.append(Block("thinking", content, speaker, overrides=overrides))
                    else:
                        blocks.append(Block("thinking", inner, "", overrides=overrides))
                    continue

                # Any other line → narrative
                blocks.append(Block("narrative", line_str, overrides=overrides))

            self.sections[section_id] = Section(section_id, blocks)
            self.section_ids.append(section_id)
