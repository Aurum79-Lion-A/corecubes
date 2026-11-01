# CoreCubes Text Editor v1.0

A small, lightweight rich-text editor written in Python with Tkinter. Write plain text, or add headings, fonts, bold, italic and underline, then save to Markdown or to CoreCubes' own `.ccb` format.

(c) Copyright 2025-2026 Lion-A Softwares

## Features

- Plain text editing with undo/redo, find, duplicate line/selection and select all
- Rich formatting: headings (H1 to H9), any installed font, **bold**, *italic*, <u>underline</u>
- Save as plain text (`.txt`), Markdown (`.md`) or CoreCubes format (`.ccb`, as Markdown or HTML)
- Opens `.txt`, `.md` and `.ccb` files with formatting restored
- Recent files list, remembered between sessions
- Insert the current time and/or date in many formats (12h/24h, EU/US, with day name, month as text)
- Built-in Help window with license information

## Requirements

- Python 3.10 or above
- Tkinter
- Download Tkinter for Debian : `sudo apt install python3-tk`

## Installation
- Use as python file or get the setu file from releases when available
## File formats

| Format | How it is saved | Keeps formatting |
|---|---|---|
| `.txt` | Plain text. Disabled while any formatting is applied. | No |
| `.md` | Standard Markdown: `#` headings, `**bold**`, `*italic*`, `<u>underline</u>`. | Headings, bold, italic, underline (no fonts) |
| `.ccb` (Markdown) | Same as `.md`, with a `<!-- Corecubes Markdown Document -->` header line. | Headings, bold, italic, underline (no fonts) |
| `.ccb` (HTML) | HTML document with `<p>`, `<h1>`..`<h6>`, `<b>`, `<i>`, `<u>` and font spans. | Everything, including fonts and H1 to H9 |

Choose **HTML** inside `.ccb` if you want to keep custom fonts. Markdown cannot store font families, so CoreCubes warns you before saving.

When a document has formatting applied, **Save** and **Save as...** (plain text) are disabled so you do not lose formatting by accident. Use one of the formatted save options instead, or press **Clear formatting**.

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+O | Open |
| Alt+R | Recent files |
| Ctrl+S | Save |
| Ctrl+Shift+S | Save as... (plain text) |
| Ctrl+Alt+M | Save as markdown (.md) |
| Ctrl+Alt+S | Save as Corecubes format (.ccb) |
| Alt+W | Wipe (clear the document) |
| Ctrl+Q | Leave |
| Ctrl+Z / Alt+Z | Undo / Redo |
| Ctrl+D | Duplicate selection (or current line) |
| Ctrl+Shift+D | Duplicate current line to a new line |
| Ctrl+F | Find |
| Ctrl+A | Select all |
| F1 | Help |

## Recent files

The list of recently opened and saved files is stored in `recents.dat` next to the program (one path per line, newest first, at most 10). If that folder is not writable, the file is created in your user folder instead. The file is created automatically on first run.

## Limitations

- The Markdown reader understands `#` headings, `**bold**`, `*italic*` and `<u>underline</u>` only. Lists, links, code blocks and `_italic_` in Markdown files from other editors are shown as plain text, and a `*` at the start of a line can toggle italics.
- Markdown headings go up to level 6. H7 to H9 are exported as level 6 in Markdown but are preserved in HTML `.ccb` files.

## License

CoreCubes is free software, licensed under the **GNU General Public License, version 3 (GPLv3)**.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

by Mr. Cobalt, Thanks
