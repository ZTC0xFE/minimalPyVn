# How to use the YML with this engine now

Below is a complete guide to the revamped YAML format. We’ll cover:

1. **Overall Structure**
2. **`settings:` Block (Globals)**
3. **Section & Block Syntax**
4. **Inline Color Overrides**
5. **Example YAML File**

---

## 1. Overall Structure

Every chapter YAML now follows this pattern:

```yaml
settings:
  # (optional block) global settings for this chapter

title: "Your Chapter Title"

sections:
  section_id1:
    - "…block 1 text…"
    - "…block 2 text…"
    # etc.

  section_id2:
    - "…"
    # etc.
```

- The **`settings:`** block (if present) must come **before** `title:`.
- `title:` defines the chapter’s name (shown at the top of the VN screen).
- `sections:` groups named sections (each section is a “page”).
- Under each section ID (like `section_id1`), list lines in the order you want them rendered.

---

## 2. `settings:` Block (Globals)

Use `settings:` to set **global defaults** for any block in this chapter. All keys below are optional; if you omit one, the parser will use the built-in default.

```yaml
settings:
  text_speed:    0.05         # seconds per character (float)
  skip_enabled:  true         # allow accelerating by pressing any key (bool)
  dialogue_color: "#404040"   # background color for dialog boxes (hex only)
  thinking_color: "#323263"   # background color for thought boxes (hex only)
  font_size:     22           # base font size for all blocks (int)
  text_color:    "#EFEFEF"    # default text color (hex only)
  subtitle_color: "#C8C832"   # color for "location" blocks (hex only)
```

### Valid Keys

- `text_speed`  
  - Type: **float**  
  - Description: How many seconds each character takes to appear (typewriter effect).  
  - Example: `0.03`

- `skip_enabled`  
  - Type: **bool** (`true` or `false`)  
  - Description: If `true`, pressing any key instantly completes the typewriter animation.

- `dialogue_color` / `thinking_color` / `text_color` / `subtitle_color`  
  - Type: **string** in `"#RRGGBB"` format.  
  - Description: Each sets a default color for its respective block type.  
    - `dialogue_color`: background for **all** dialog boxes.  
    - `thinking_color`: background for **all** thought boxes.  
    - `text_color`: default color for narrative/dialog text.  
    - `subtitle_color`: color for “location” lines (the ones wrapped in `€…€`).

- `font_size`  
  - Type: **int**  
  - Description: Base font size (in pixels). Individual blocks can override this.

> **Important:**  
> - All colors in `settings:` must be **valid hex codes** (e.g. `"#FFA500"`).  
> - If you use any other format (like `"255,255,0"`), that entry is ignored and the default applies instead.

---

## 3. Section & Block Syntax

Within each section, list lines one by one. Each line falls into one of these categories:

1. **Narrative**  
   - Syntax:  
     ```
     Narrative: Your narrative text goes here.
     ```  
   - Description: Plain text appearing in white (or your `text_color` override). It’s displayed with a typewriter effect.

     > `Narrative` tag at the start isn't needed, altough, it just get overriden when place at the start anyway.

2. **Location / Subtitle**  
   - Syntax:  
     ```
     €Location Name - Time€
     ```  
   - Description: Wrapped in `€…€`, e.g. `€Town Square - Sunset€`. Rendered immediately in the `subtitle_color`. No typewriter effect.

3. **Dialog**  
   - Syntax:  
     ```
     # [CharacterName] Dialogue text here. #
     ```  
   - Description: Wrapped in `#…#`.  
   - The part inside `[CharacterName]` is the speaker label (in yellow for dialog).  
   - All dialog text appears inside a gray box (or your global `dialogue_color`) with two lines of height:  
     1. Speaker line  
     2. Dialogue text line (typewriter + inline color support).  
   - Press → to advance; ESC always jumps back to the menu.

4. **Thought**  
   - Syntax:  
     ```
     ¥ [CharacterName] Thought text here. ¥
     ```  
   - Description: Wrapped in `¥…¥`. Rendered similarly to dialog, but with a “thought” background (your `thinking_color`) and italicized text.

---

## 4. Inline Color Overrides

You can highlight **any snippet** of text inside a narrative, dialog, or thought line using:

```
[color=#RRGGBB]Text to color[/]
```

- **Example in Narrative:**  
  ```
  Narrative: This is a [color=#FF0000]warning[/] message!
  ```
  - The word “warning” appears in bright red. The rest of the line uses `text_color` (`#EFEFEF`, by default).

- **Example in Dialog:**  
  ```
  # [Alice] I feel like this [color=#00FF00]forest[/] is alive. #
  ```
  - Only “forest” is shown in green; the box background is your `dialogue_color`.

- **Example in Thought:**  
  ```
  ¥ [Bob] My heart is [color=#FF00FF]racing[/]... ¥
  ```
  - “racing” is magenta; thought box background is your `thinking_color`.

**How It Works**  
- The renderer splits the line into segments, each with its own color.  
- Text is shown character by character (typewriter).  
- Because dialog/thought boxes are fixed-height (exactly two lines), the inline snippet never forces a line break—everything stays on a single line.

> **Pro Tip:**  
> - Don’t chain multiple color tags in a single line if it makes the text too long—boxes won’t wrap. Keep inline highlights short (a word or two).

---

## 5. Example YAML File

Below is a complete example to demonstrate all features:

```yaml
settings:
  text_speed: 0.05
  skip_enabled: true
  dialogue_color: "#404040"
  thinking_color: "#323263"
  font_size: 22
  text_color: "#EFEFEF"
  subtitle_color: "#C8C832"

title: "Advanced YAML Tutorial"

sections:
  intro:
    - "Narrative: Welcome to the [color=#FF0000]Advanced Tutorial[/]! Enjoy customizing your VN."
    - "€Tutorial Room - Afternoon€"
    - "# [Zion] Let’s test [color=#00FF00]inline green[/] and [color=#0000FF]inline blue[/]. #"
    - "¥ [Hazel] My opinions can also have [color=#FF00FF]colorful thoughts[/]. ¥"

  part1:
    # Override global dialog background and font size for this line
    - "[dialogue_color=#303030;font_size=18]# [Zion] This dialog has a darker box and smaller font. #[/]"
    - "# [Hazel] Back to defaults here. #"
    # Override only font size for this single narrative line
    - "[font_size=18]Narrative: This line is slightly smaller text than usual.[/]"
    # Normal thought, no overrides
    - "¥ [Zion] Everything looks good for me. ¥"

  outro:
    - "Narrative: That’s it for the tutorial. Feel free to experiment!"
    - "# [Hazel] Bye for now! #"
    - "¥ [Zion] Until next time! ¥"
```
