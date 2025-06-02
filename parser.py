import yaml

class TextBlock:
    """
    Normal text block (narrative).
    """
    def __init__(self, text: str):
        self.text = text

class DialogBlock:
    """
    Dialog block: has character and speech.
    (marked as: # [Character] Speech # )
    """
    def __init__(self, character: str, text: str):
        self.character = character
        self.text = text

class LocationBlock:
    """
    Location/time block: displays the entire line in yellow.
    (marked as: €Zion's House - 8 at night€)
    """
    def __init__(self, text: str):
        # already receives the text without the “€” symbols
        self.text = text

class ThinkingBlock:
    """
    Thought block: box in italics, different from dialog.
    (marked as: ¥[Character] Thought¥)
    """
    def __init__(self, character: str, text: str):
        self.character = character
        self.text = text

class ContentParser:
    """
    Loads a .yml file (chapter) and converts it into:
      - title: title to display in the menu
      - sections: dictionary of sections, each section is a list of blocks (TextBlock/DialogBlock/LocationBlock/ThinkingBlock)
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.title = ""
        self.sections = {}

    def load(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Get the title
        self.title = data.get("title", "No title")

        # Get the sections
        raw_sections = data.get("sections", {})
        for sec_id, lines in raw_sections.items():
            bloco_list = []
            for raw in lines:
                linha = str(raw).strip()

                # — Dialog: starts and ends with '#'
                if linha.startswith("#") and linha.endswith("#"):
                    conteudo = linha[1:-1].strip()
                    if conteudo.startswith("[") and "]" in conteudo:
                        parte = conteudo.split("]", 1)
                        personagem = parte[0][1:]
                        fala = parte[1].strip()
                    else:
                        personagem = ""
                        fala = conteudo
                    bloco_list.append(DialogBlock(personagem, fala))

                # — Location/Time: starts and ends with '€'
                elif linha.startswith("€") and linha.endswith("€"):
                    conteudo = linha[1:-1].strip()
                    bloco_list.append(LocationBlock(conteudo))

                # — Thought: starts and ends with '¥'
                elif linha.startswith("¥") and linha.endswith("¥"):
                    conteudo = linha[1:-1].strip()
                    if conteudo.startswith("[") and "]" in conteudo:
                        parte = conteudo.split("]", 1)
                        personagem = parte[0][1:]
                        texto = parte[1].strip()
                    else:
                        personagem = ""
                        texto = conteudo
                    bloco_list.append(ThinkingBlock(personagem, texto))

                # — Otherwise: normal text
                else:
                    bloco_list.append(TextBlock(linha))

            self.sections[sec_id] = bloco_list

        return self
