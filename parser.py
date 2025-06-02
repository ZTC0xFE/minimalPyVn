import os
import yaml

class Block:
    """
    Represents a block of text in a chapter. Types:
      - "narrative": plain text (starts with "Narrative:" or no marker).
      - "location" : text between €...€.
      - "dialog"   : text between #...# (with [Name]).
      - "thinking" : text between ¥...¥ (with [Name]).
    """
    def __init__(self, block_type, content, speaker=None):
        self.type    = block_type   # "narrative", "location", "dialog", or "thinking"
        self.content = content      # text without markers
        self.speaker = speaker or ""  # only for "dialog" or "thinking"

class Section:
    """
    Represents a section ("page") with:
      - id: YAML dictionary key (e.g., "intro")
      - blocks: list of Block(), in order
    """
    def __init__(self, section_id, blocks):
        self.id = section_id
        self.blocks = blocks

class ContentParser:
    """
    Parses a YAML chapter file with structure:

      title: "Chapter Title"
      sections:
        sec1:
          - "line1"
          - "line2"
        sec2:
          - "another line"
          ...

    For each string in each section, interprets special markers:
      - narrative: starts with "Narrative:" or no marker
      - location:  starts and ends with "€"
      - dialog:    starts and ends with "#", contains "[Name]"
      - thinking:  starts and ends with "¥", contains "[Name]"

    Populates:
      self.title       = data["title"]
      self.sections    = { sec_key: Section(sec_key, [Block(), ...]), ... }
      self.section_ids = list of sec_key in original order
    """

    def __init__(self, chapter_path):
        if not os.path.exists(chapter_path):
            raise FileNotFoundError(f"Chapter file not found:\n  {chapter_path}")

        self.chapter_path = chapter_path
        self.title        = ""
        self.sections     = {}
        self.section_ids  = []

        self._parse_file()

    def _parse_file(self):
        # Load YAML
        with open(self.chapter_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Get title or fallback to filename
        self.title = data.get("title",
                              os.path.splitext(os.path.basename(self.chapter_path))[0])

        # Iterate sections in YAML order
        raw_sections = data.get("sections", {})
        for section_id, raw_list in raw_sections.items():
            if not isinstance(raw_list, list):
                continue

            blocks = []
            for raw_line in raw_list:
                line = raw_line.strip()
                if not line:
                    continue  # skip blank lines

                # Narrative: starts with "Narrative:"
                if line.startswith("Narrative:"):
                    content = line[len("Narrative:"):].lstrip()
                    blocks.append(Block("narrative", content))
                    continue

                # Location: starts and ends with "€"
                if line.startswith("€") and line.endswith("€"):
                    content = line[1:-1].strip()
                    blocks.append(Block("location", content))
                    continue

                # Dialog: starts and ends with "#"
                if line.startswith("#") and line.endswith("#"):
                    inner = line[1:-1].strip()
                    if inner.startswith("[") and "]" in inner:
                        end_br = inner.find("]")
                        speaker = inner[1:end_br]
                        content = inner[end_br+1:].lstrip()
                        blocks.append(Block("dialog", content, speaker))
                    else:
                        blocks.append(Block("dialog", inner, ""))
                    continue

                # Thinking: starts and ends with "¥"
                if line.startswith("¥") and line.endswith("¥"):
                    inner = line[1:-1].strip()
                    if inner.startswith("[") and "]" in inner:
                        end_br = inner.find("]")
                        speaker = inner[1:end_br]
                        content = inner[end_br+1:].lstrip()
                        blocks.append(Block("thinking", content, speaker))
                    else:
                        blocks.append(Block("thinking", inner, ""))
                    continue

                # Any other line: plain narrative
                blocks.append(Block("narrative", line))

            self.sections[section_id] = Section(section_id, blocks)
            self.section_ids.append(section_id)
