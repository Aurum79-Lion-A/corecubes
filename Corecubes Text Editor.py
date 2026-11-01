# CoreCubes
# (c) Copyright 2025-2026 Lion-A Softwares
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime
from html.parser import HTMLParser
import html
import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, font, messagebox, simpledialog, ttk

BODY_SIZE = 11
FMT_PREFIX = "fmt|"
HEADING_SIZES = {
    "H1": 28, "H2": 24, "H3": 20, "H4": 18, "H5": 16,
    "H6": 14, "H7": 13, "H8": 12, "H9": 11,
}
MAX_RECENTS = 10
NAV_KEYS = {"Left", "Right", "Up", "Down", "Home", "End", "Prior", "Next"}
APP_DIR = os.path.dirname(
    os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__)
)
RECENTS_NAME = "recents.dat"

LICENSE_TEXT = """CoreCubes
(c) Copyright 2025-2026 Lion-A Softwares

CoreCubes is licensed under the GNU General Public License, version 3 (GPLv3).

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW. THE PROGRAM IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.

IN NO EVENT WILL ANY COPYRIGHT HOLDER BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
"""


def resolve_recents_path():
  # Once programin klasoru, yazilamiyorsa kullanici klasoru.
  for folder in (APP_DIR, os.path.expanduser("~")):
    path = os.path.join(folder, RECENTS_NAME)
    try:
      with open(path, "a", encoding="utf-8"):
        pass
      return path
    except OSError:
      continue
  return None


class CorecubesHTMLParser(HTMLParser):
  SKIP_TAGS = {"head", "title", "style", "script"}

  def __init__(self):
    super().__init__()
    self.lines = []
    self.family_stack = []
    self.current_heading = "None"
    self.bold_stack = 0
    self.italic_stack = 0
    self.underline_stack = 0
    self.skip_depth = 0
    self.in_block = False

  def handle_starttag(self, tag, attrs):
    tag = tag.lower()
    if tag in self.SKIP_TAGS:
      self.skip_depth += 1
    elif tag == "br":
      self.lines.append([])
    elif tag == "p":
      self.lines.append([])
      self.in_block = True
    elif re.fullmatch(r"h[1-6]", tag):
      self.lines.append([])
      self.in_block = True
      level = int(tag[1])
      for name, value in attrs:
        if name == "data-level" and value and value.isdigit():
          level = max(1, min(int(value), 9))
      self.current_heading = f"H{level}"
    elif tag in ("b", "strong"):
      self.bold_stack += 1
    elif tag in ("i", "em"):
      self.italic_stack += 1
    elif tag == "u":
      self.underline_stack += 1
    elif tag == "span":
      fam = None
      for name, value in attrs:
        if name == "style" and value:
          m = re.search(r"font-family\s*:\s*([^;]+)", value)
          if m:
            fam = m.group(1).split(",")[0].strip().strip("'\"")
      self.family_stack.append(fam)

  def handle_endtag(self, tag):
    tag = tag.lower()
    if tag in self.SKIP_TAGS:
      self.skip_depth = max(0, self.skip_depth - 1)
    elif tag == "p":
      self.in_block = False
    elif re.fullmatch(r"h[1-6]", tag):
      self.in_block = False
      self.current_heading = "None"
    elif tag in ("b", "strong"):
      self.bold_stack = max(0, self.bold_stack - 1)
    elif tag in ("i", "em"):
      self.italic_stack = max(0, self.italic_stack - 1)
    elif tag == "u":
      self.underline_stack = max(0, self.underline_stack - 1)
    elif tag == "span":
      if self.family_stack:
        self.family_stack.pop()

  def handle_data(self, data):
    if self.skip_depth or not self.in_block or not data or not self.lines:
      return
    family = next((f for f in reversed(self.family_stack) if f), None)
    fmt = (
        family,
        self.current_heading,
        self.bold_stack > 0,
        self.italic_stack > 0,
        self.underline_stack > 0,
    )
    self.lines[-1].append((data, fmt))


class CorecubesMarkdownParser:

  def __init__(self):
    self.lines = []

  def parse(self, content):
    self.lines = []
    raw_lines = content.split("\n")
    skip_blank = False
    for line in raw_lines:
      if line.startswith("<!-- Corecubes Markdown Document -->"):
        skip_blank = True
        continue
      if skip_blank:
        skip_blank = False
        if not line.strip():
          continue

      heading = "None"
      match = re.match(r"^(\#{1,6})\s+(.*)$", line)
      if match:
        hashes, rest = match.groups()
        heading = f"H{len(hashes)}"
        line_text = rest
      else:
        line_text = line

      if not line_text:
        self.lines.append([])
        continue

      self.lines.append(self.parse_inline(line_text, heading))

  def parse_inline(self, text, heading):
    pattern = re.compile(r"(\*\*|\*|<u>|</u>)")
    tokens = pattern.split(text)
    segments = []
    bold = False
    italic = False
    underline = False

    for token in tokens:
      if not token:
        continue
      if token == "**":
        bold = not bold
      elif token == "*":
        italic = not italic
      elif token == "<u>":
        underline = True
      elif token == "</u>":
        underline = False
      else:
        fmt = (None, heading, bold, italic, underline)
        segments.append((token, fmt))
    return segments


class CorecubesEditor:

  def __init__(self, root):
    self.root = root
    self.root.title("CoreCubes - Untitled")
    self.root.geometry("1050x600")

    self.current_file_path = None
    self.recents_path = resolve_recents_path()
    self.recent_files = self.load_recents()
    self.has_styling = False
    self._updating_toolbar = False
    self._toolbar_override = False
    # tag adi -> format demeti (tag adini ayristirmak yerine dogrudan arama)
    self.fmt_by_tag = {}

    families = sorted({f for f in font.families() if not f.startswith("@")})
    self.default_family = "Courier"
    for candidate in ("Consolas", "Courier New", "DejaVu Sans Mono"):
      if candidate in families:
        self.default_family = candidate
        break
    if self.default_family not in families:
      families.insert(0, self.default_family)
    self.font_families = families

    self.toolbar_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)
    self.toolbar_frame.pack(side="top", fill="x")

    self.scrollbar = tk.Scrollbar(self.root)
    self.scrollbar.pack(fill="y", side="right")

    self.text_area = tk.Text(
        self.root,
        wrap="word",
        undo=True,
        font=(self.default_family, BODY_SIZE),
        yscrollcommand=self.scrollbar.set,
    )
    self.text_area.pack(fill="both", expand=True, side="left")
    self.scrollbar.config(command=self.text_area.yview)
    self.text_area.config(
        inactiveselectbackground=self.text_area.cget("selectbackground")
    )

    self.create_menu()
    self.create_toolbar_widgets()
    self.bind_shortcuts()

    self.text_area.bind("<KeyPress>", self.on_key_press, add="+")
    self.root.protocol("WM_DELETE_WINDOW", self.leave_app)

  def create_menu(self):
    self.menubar = tk.Menu(self.root)

    self.file_menu = tk.Menu(self.menubar, tearoff=0)
    self.file_menu.add_command(
        label="Open", command=self.open_file, accelerator="Ctrl+O"
    )
    self.file_menu.add_command(
        label="Recents", command=self.show_recents, accelerator="Alt+R"
    )
    self.file_menu.add_separator()
    self.file_menu.add_command(
        label="Save", command=self.save_file, accelerator="Ctrl+S"
    )
    self.file_menu.add_command(
        label="Save as...", command=self.save_as_file, accelerator="Ctrl+Shift+S"
    )
    self.file_menu.add_command(
        label="Save as Markdown (.md)",
        command=self.save_as_md,
        accelerator="Ctrl+Alt+M",
    )
    self.file_menu.add_command(
        label="Save as Corecubes format (.ccb)",
        command=self.save_as_ccb,
        accelerator="Ctrl+Alt+S",
    )
    self.file_menu.add_separator()
    self.file_menu.add_command(
        label="Wipe", command=self.wipe_text, accelerator="Alt+W"
    )
    self.file_menu.add_command(
        label="Leave", command=self.leave_app, accelerator="Ctrl+Q"
    )
    self.menubar.add_cascade(label="File", menu=self.file_menu)

    quick_menu = tk.Menu(self.menubar, tearoff=0)
    quick_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
    quick_menu.add_command(label="Redo", command=self.redo, accelerator="Alt+Z")
    quick_menu.add_separator()
    quick_menu.add_command(
        label="Copy",
        command=lambda: self.text_area.event_generate("<<Copy>>"),
        accelerator="Ctrl+C",
    )
    quick_menu.add_command(
        label="Paste",
        command=lambda: self.text_area.event_generate("<<Paste>>"),
        accelerator="Ctrl+V",
    )
    quick_menu.add_command(
        label="Cut",
        command=lambda: self.text_area.event_generate("<<Cut>>"),
        accelerator="Ctrl+X",
    )
    quick_menu.add_separator()
    quick_menu.add_command(
        label="Duplicate", command=self.duplicate_selection, accelerator="Ctrl+D"
    )
    quick_menu.add_command(
        label="Duplicate to New Line",
        command=self.duplicate_to_new_line,
        accelerator="Ctrl+Shift+D",
    )
    quick_menu.add_separator()
    quick_menu.add_command(
        label="Select all", command=self.select_all, accelerator="Ctrl+A"
    )
    quick_menu.add_command(
        label="Erase", command=self.wipe_text, accelerator="Del"
    )
    quick_menu.add_command(
        label="Find", command=self.find_text, accelerator="Ctrl+F"
    )
    self.menubar.add_cascade(label="Quick", menu=quick_menu)

    time_menu = tk.Menu(self.menubar, tearoff=0)

    def add_time(label, fmt):
      time_menu.add_command(
          label=label, command=lambda: self.insert_datetime(fmt)
      )

    add_time("Paste time (12h format)", "%I:%M:%S %p")
    add_time("Paste time (24h format)", "%H:%M:%S")
    add_time("Paste date (EU)", "%d/%m/%Y")
    add_time("Paste date (US)", "%m/%d/%Y")
    add_time("Paste date (EU) + day", "%A, %d/%m/%Y")
    add_time("Paste date (US) + day", "%A, %m/%d/%Y")
    time_menu.add_separator()
    add_time("Paste time (12h)+date (EU)", "%I:%M:%S %p - %d/%m/%Y")
    add_time("Paste time (24h)+date (EU)", "%H:%M:%S - %d/%m/%Y")
    add_time("Paste time (12h)+date (US)", "%I:%M:%S %p - %m/%d/%Y")
    add_time("Paste time (24h)+date (US)", "%H:%M:%S - %m/%d/%Y")
    add_time("Paste time (12h)+date (EU) + day", "%I:%M:%S %p - %A, %d/%m/%Y")
    add_time("Paste time (24h)+date (EU) + day", "%H:%M:%S - %A, %d/%m/%Y")
    add_time("Paste time (12h)+date (US) + day", "%I:%M:%S %p - %A, %m/%d/%Y")
    add_time("Paste time (24h)+date (US) + day", "%H:%M:%S - %A, %m/%d/%Y")
    time_menu.add_separator()
    add_time("Paste date (EU) (month as text)", "%d %B %Y")
    add_time("Paste date (US) (month as text)", "%B %d, %Y")
    add_time("Paste date (EU) + day (month as text)", "%A, %d %B %Y")
    add_time("Paste date (US) + day (month as text)", "%A, %B %d, %Y")
    time_menu.add_separator()
    add_time("Paste time (12h)+date (EU) (month as text)", "%I:%M:%S %p - %d %B %Y")
    add_time("Paste time (24h)+date (EU) (month as text)", "%H:%M:%S - %d %B %Y")
    add_time("Paste time (12h)+date (US) (month as text)", "%I:%M:%S %p - %B %d, %Y")
    add_time("Paste time (24h)+date (US) (month as text)", "%H:%M:%S - %B %d, %Y")
    add_time("Paste time (12h)+date (EU) + day (month as text)", "%I:%M:%S %p - %A, %d %B %Y")
    add_time("Paste time (24h)+date (EU) + day (month as text)", "%H:%M:%S - %A, %d %B %Y")
    add_time("Paste time (12h)+date (US) + day (month as text)", "%I:%M:%S %p - %A, %B %d, %Y")
    add_time("Paste time (24h)+date (US) + day (month as text)", "%H:%M:%S - %A, %B %d, %Y")

    self.menubar.add_cascade(label="Time", menu=time_menu)
    self.menubar.add_command(label="Help", command=self.show_help)
    self.root.config(menu=self.menubar)

  def create_toolbar_widgets(self):
    label_font = (self.default_family, 9)

    tk.Label(self.toolbar_frame, text="Heading:", font=label_font, padx=5).pack(
        side="left"
    )
    self.heading_var = tk.StringVar(value="None")
    self.heading_box = ttk.Combobox(
        self.toolbar_frame,
        textvariable=self.heading_var,
        values=["None"] + list(HEADING_SIZES),
        state="readonly",
        width=6,
    )
    self.heading_box.pack(side="left", padx=2)
    self.heading_box.bind(
        "<<ComboboxSelected>>", lambda e: self.apply_format(is_heading=True)
    )

    tk.Label(self.toolbar_frame, text="Font:", font=label_font, padx=5).pack(
        side="left"
    )
    self.font_var = tk.StringVar(value=self.default_family)
    self.font_box = ttk.Combobox(
        self.toolbar_frame,
        textvariable=self.font_var,
        values=self.font_families,
        state="readonly",
        width=22,
    )
    self.font_box.pack(side="left", padx=2)
    self.font_box.bind("<<ComboboxSelected>>", lambda e: self.apply_format())

    self.bold_var = tk.BooleanVar(value=False)
    self.italic_var = tk.BooleanVar(value=False)
    self.underline_var = tk.BooleanVar(value=False)
    for text, var in (
        ("Bold", self.bold_var),
        ("Italic", self.italic_var),
        ("Underline", self.underline_var),
    ):
      tk.Checkbutton(
          self.toolbar_frame,
          text=text,
          variable=var,
          command=self.apply_format,
          font=label_font,
      ).pack(side="left", padx=5)

    tk.Button(
        self.toolbar_frame,
        text="Clear formatting",
        command=self.clear_format,
        font=label_font,
    ).pack(side="left", padx=10)

  def toolbar_format(self):
    return (
        self.font_var.get(),
        self.heading_var.get(),
        self.bold_var.get(),
        self.italic_var.get(),
        self.underline_var.get(),
    )

  def is_default_format(self, fmt):
    return fmt == (self.default_family, "None", False, False, False)

  @staticmethod
  def make_tag_name(fmt):
    family, heading, bold, italic, underline = fmt
    return (
        f"{FMT_PREFIX}{family}|{heading}|{int(bold)}|{int(italic)}|{int(underline)}"
    )

  def parse_fmt(self, tag):
    if tag in self.fmt_by_tag:
      return self.fmt_by_tag[tag]
    parts = tag.split("|")
    if len(parts) >= 6:
      family = "|".join(parts[1:-4])
      heading, b, i, u = parts[-4:]
      return (family, heading, b == "1", i == "1", u == "1")
    return (self.default_family, "None", False, False, False)

  @staticmethod
  def fmt_font(fmt):
    family, heading, bold, italic, underline = fmt
    styles = [
        name
        for name, on in (("bold", bold), ("italic", italic), ("underline", underline))
        if on
    ]
    return (family, HEADING_SIZES.get(heading, BODY_SIZE), *styles)

  def apply_format(self, is_heading=False):
    if self._updating_toolbar:
      return

    self._toolbar_override = True

    ta = self.text_area
    try:
      start, end = ta.index(tk.SEL_FIRST), ta.index(tk.SEL_LAST)
    except tk.TclError:
      start = end = ta.index("insert")

    if is_heading:
      if end != start and end.endswith(".0"):
        end = ta.index(f"{end}-1c")
      start = ta.index(f"{start} linestart")
      end = ta.index(f"{end} lineend")

      current_fmt = self.get_current_format_at(start)
      new_heading = self.heading_var.get()
      fmt = (
          current_fmt[0],
          new_heading,
          current_fmt[2],
          current_fmt[3],
          current_fmt[4],
      )
      self.tag_range_for_property(start, end, fmt)
    else:
      if start == end:
        return

      current_fmt = self.get_current_format_at(start)
      fam = self.font_var.get()
      b = self.bold_var.get()
      i = self.italic_var.get()
      u = self.underline_var.get()
      fmt = (fam, current_fmt[1], b, i, u)
      self.tag_range_for_property(start, end, fmt)

    self.check_styling_status()
    ta.focus_set()

  def get_current_format_at(self, index):
    ta = self.text_area
    fmt = (self.default_family, "None", False, False, False)
    for tag in ta.tag_names(index):
      if tag.startswith(FMT_PREFIX):
        fmt = self.parse_fmt(tag)
        break
    return fmt

  def tag_range_for_property(self, start, end, new_fmt):
    ta = self.text_area
    for tag in ta.tag_names():
      if tag.startswith(FMT_PREFIX):
        ta.tag_remove(tag, start, end)

    if not self.is_default_format(new_fmt):
      name = self.make_tag_name(new_fmt)
      self.fmt_by_tag[name] = new_fmt
      ta.tag_configure(name, font=self.fmt_font(new_fmt))
      ta.tag_add(name, start, end)
      try:
        ta.tag_raise("sel")
      except tk.TclError:
        pass

  def on_key_press(self, event):
    if event.keysym == "Return":
      self.root.after_idle(lambda: self.heading_var.set("None"))
      return
    if not event.char or not event.char.isprintable():
      return
    if event.state & 0x4:
      return
    self.root.after_idle(self.format_typed)

  def format_typed(self):
    ta = self.text_area
    if ta.index("insert").endswith(".0"):
      return
    fmt = self.toolbar_format()
    if fmt[1] != "None" or not self.is_default_format(fmt):
      self.tag_range_for_property("insert-1c", "insert", fmt)
    self.check_styling_status()

  def clear_format(self):
    self._updating_toolbar = True
    self._toolbar_override = True
    self.heading_var.set("None")
    self.font_var.set(self.default_family)
    self.bold_var.set(False)
    self.italic_var.set(False)
    self.underline_var.set(False)
    self._updating_toolbar = False

    try:
      start, end = (
          self.text_area.index(tk.SEL_FIRST),
          self.text_area.index(tk.SEL_LAST),
      )
    except tk.TclError:
      start = "1.0"
      end = "end"

    for tag in self.text_area.tag_names():
      if tag.startswith(FMT_PREFIX):
        self.text_area.tag_remove(tag, start, end)
    self.check_styling_status()

  def check_styling_status(self):
    self.has_styling = any(
        self.text_area.tag_ranges(tag)
        for tag in self.text_area.tag_names()
        if tag.startswith(FMT_PREFIX)
    )
    state = "disabled" if self.has_styling else "normal"
    self.file_menu.entryconfig("Save", state=state)
    self.file_menu.entryconfig("Save as...", state=state)

  def bind_key(self, sequence, func):
    def handler(event):
      func()
      return "break"

    self.text_area.bind(sequence, handler)
    self.root.bind(sequence, handler)

  def bind_shortcuts(self):
    self.bind_key("<F1>", self.show_help)
    self.bind_key("<Control-o>", self.open_file)
    self.bind_key("<Alt-r>", self.show_recents)
    self.bind_key("<Control-s>", self.save_file)
    self.bind_key("<Control-Shift-S>", self.save_as_file)
    self.bind_key("<Control-Alt-s>", self.save_as_ccb)
    self.bind_key("<Control-Alt-m>", self.save_as_md)
    self.bind_key("<Alt-w>", self.wipe_text)
    self.bind_key("<Control-q>", self.leave_app)
    self.bind_key("<Control-d>", self.duplicate_selection)
    self.bind_key("<Control-Shift-D>", self.duplicate_to_new_line)
    self.bind_key("<Control-f>", self.find_text)
    self.bind_key("<Control-a>", self.select_all)
    self.bind_key("<Control-z>", self.undo)
    self.bind_key("<Alt-z>", self.redo)

  def get_text(self):
    return self.text_area.get("1.0", "end-1c")

  def load_recents(self):
    # recents.dat yoksa bos liste doner ilk kayitta olusturulur
    if not self.recents_path:
      return []
    try:
      with open(self.recents_path, "r", encoding="utf-8") as f:
        paths = [line.strip() for line in f if line.strip()]
    except (OSError, UnicodeDecodeError):
      return []
    unique = []
    for path in paths:
      if path not in unique:
        unique.append(path)
    return unique[:MAX_RECENTS]

  def save_recents(self):
    if not self.recents_path:
      return
    try:
      with open(self.recents_path, "w", encoding="utf-8") as f:
        f.write("\n".join(self.recent_files))
    except OSError as e:
      messagebox.showerror("Error", f"Could not write {self.recents_path}:\n{e}")

  def add_recent(self, file_path):
    if file_path in self.recent_files:
      self.recent_files.remove(file_path)
    self.recent_files.insert(0, file_path)
    del self.recent_files[MAX_RECENTS:]
    self.save_recents()

  def load_file(self, file_path):
    try:
      with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    except Exception as e:
      messagebox.showerror("Error", f"Could not open file:\n{e}")
      return False

    self.text_area.delete("1.0", tk.END)

    if file_path.endswith(".ccb") and ("<!DOCTYPE html>" in content or "<html>" in content):
      parser = CorecubesHTMLParser()
      parser.feed(content)
      parser.close()
      lines_data = parser.lines
    elif file_path.lower().endswith(".md") or (
        file_path.endswith(".ccb")
        and "<!-- Corecubes Markdown Document -->" in content
    ):
      parser = CorecubesMarkdownParser()
      parser.parse(content)
      lines_data = parser.lines
    else:
      lines_data = None

    if lines_data is not None:
      for line_idx, line in enumerate(lines_data):
        if line_idx > 0:
          self.text_area.insert(tk.END, "\n")
        for text, fmt in line:
          if fmt:
            fam = fmt[0] if fmt[0] else self.default_family
            real_fmt = (fam, fmt[1], fmt[2], fmt[3], fmt[4])
            if not self.is_default_format(real_fmt):
              tag_name = self.make_tag_name(real_fmt)
              self.fmt_by_tag[tag_name] = real_fmt
              self.text_area.tag_configure(tag_name, font=self.fmt_font(real_fmt))
              self.text_area.insert(tk.END, text, (tag_name,))
            else:
              self.text_area.insert(tk.END, text)
          else:
            self.text_area.insert(tk.END, text)
    else:
      self.text_area.insert("1.0", content)

    self.text_area.edit_reset()
    self.current_file_path = file_path
    self.root.title(f"Corecubes - {os.path.basename(file_path)}")
    self.add_recent(file_path)
    self.check_styling_status()
    return True

  def open_file(self):
    file_path = filedialog.askopenfilename(
        defaultextension=".txt",
        filetypes=[
            ("All Files", "*.*"),
            ("Text Files", "*.txt"),
            ("Markdown Files", "*.md"),
            ("Corecubes Files", "*.ccb"),
        ],
    )
    if file_path:
      self.load_file(file_path)

  def show_recents(self):
    if not self.recent_files:
      messagebox.showinfo("Recents", "No recent files found.")
      return
    recents_window = tk.Toplevel(self.root)
    recents_window.title("Recent Files")
    recents_window.geometry("400x300")

    lb = tk.Listbox(recents_window, font=(self.default_family, 10))
    lb.pack(fill="both", expand=True, padx=10, pady=10)
    for path in self.recent_files:
      lb.insert(tk.END, path)

    def open_selected(event):
      selection = lb.curselection()
      if selection:
        file_path = lb.get(selection[0])
        if self.load_file(file_path):
          recents_window.destroy()

    lb.bind("<Double-Button-1>", open_selected)

  def save_file(self):
    if self.has_styling:
      messagebox.showwarning(
          "Warning", "Cannot save as text file because formattings are applied!"
      )
      return
    if self.current_file_path:
      try:
        with open(self.current_file_path, "w", encoding="utf-8") as f:
          f.write(self.get_text())
        self.add_recent(self.current_file_path)
      except Exception as e:
        messagebox.showerror("Error", f"Could not save file:\n{e}")
    else:
      self.save_as_file()

  def save_as_file(self):
    if self.has_styling:
      messagebox.showwarning(
          "Warning", "Cannot save as text file because formattings are applied!"
      )
      return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if file_path:
      try:
        with open(file_path, "w", encoding="utf-8") as f:
          f.write(self.get_text())
        self.current_file_path = file_path
        self.root.title(f"Corecubes - {os.path.basename(file_path)}")
        self.add_recent(file_path)
      except Exception as e:
        messagebox.showerror("Error", f"Could not save file:\n{e}")

  def get_lines(self):
    lines = [[]]
    active = []
    for key, value, _ in self.text_area.dump(
        "1.0", "end-1c", text=True, tag=True
    ):
      if key == "tagon" and value.startswith(FMT_PREFIX):
        if value not in active:
          active.append(value)
      elif key == "tagoff" and value.startswith(FMT_PREFIX):
        if value in active:
          active.remove(value)
      elif key == "text":
        fmt = self.parse_fmt(active[-1]) if active else None
        for k, part in enumerate(value.split("\n")):
          if k > 0:
            lines.append([])
          if part:
            lines[-1].append((part, fmt))
    return lines

  @staticmethod
  def wrap_text(text, left, right):
    if not text.strip():
      return text
    lead = text[: len(text) - len(text.lstrip())]
    trail = text[len(text.rstrip()) :]
    core = text.strip()
    return f"{lead}{left}{core}{right}{trail}"

  @staticmethod
  def line_heading(line):
    for _, fmt in line:
      if fmt and fmt[1] != "None":
        return int(fmt[1][1])
    return None

  def export_markdown(self, header=True):
    out = []
    for line in self.get_lines():
      s = ""
      for text, fmt in line:
        if fmt:
          _, _, bold, italic, underline = fmt
          if bold:
            text = self.wrap_text(text, "**", "**")
          if italic:
            text = self.wrap_text(text, "*", "*")
          if underline:
            text = self.wrap_text(text, "<u>", "</u>")
        s += text
      level = self.line_heading(line)
      if level:
        s = "#" * min(level, 6) + " " + s
      out.append(s)
    body = "\n".join(out)
    if header:
      return "<!-- Corecubes Markdown Document -->\n\n" + body
    return body

  def export_html(self):
    body = []
    for line in self.get_lines():
      inner = ""
      for text, fmt in line:
        s = html.escape(text)
        if fmt:
          family, _, bold, italic, underline = fmt
          if family != self.default_family:
            safe_family = html.escape(family, quote=False)
            s = f'<span style="font-family: \'{safe_family}\'">{s}</span>'
          if bold:
            s = f"<b>{s}</b>"
          if italic:
            s = f"<i>{s}</i>"
          if underline:
            s = f"<u>{s}</u>"
        inner += s
      level = self.line_heading(line)
      if level:
        n = min(level, 6)
        extra = f' data-level="{level}"' if level > 6 else ""
        body.append(f"<h{n}{extra}>{inner}</h{n}>")
      elif inner:
        body.append(f"<p>{inner}</p>")
      else:
        body.append("<br>")
    return (
        "<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"utf-8\">\n"
        "<title>Corecubes Document</title>\n"
        "<style>p{white-space:pre-wrap;margin:0}</style>\n"
        "</head>\n<body>\n" + "\n".join(body) + "\n</body>\n</html>"
    )

  def save_as_md(self):
    uses_fonts = any(
        fmt and fmt[0] != self.default_family
        for line in self.get_lines()
        for _, fmt in line
    )
    if uses_fonts:
      if not messagebox.askokcancel(
          "Font Override Warning",
          "Markdown format does not support custom font families! "
          "Applied custom fonts will be dropped in the .md file.",
      ):
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".md",
        filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")],
    )
    if not file_path:
      return
    try:
      with open(file_path, "w", encoding="utf-8") as f:
        f.write(self.export_markdown(header=False))
      self.current_file_path = file_path
      self.root.title(f"Corecubes - {os.path.basename(file_path)}")
      self.add_recent(file_path)
    except Exception as e:
      messagebox.showerror("Error", f"Could not save .md file:\n{e}")

  def save_as_ccb(self):
    choice = {}

    dialog = tk.Toplevel(self.root)
    dialog.title("Corecubes Format")
    dialog.geometry("320x150")
    dialog.resizable(False, False)
    dialog.grab_set()

    tk.Label(
        dialog,
        text="Choose format for .ccb file:",
        font=(self.default_family, 10),
        pady=15,
    ).pack()

    def select(fmt):
      if fmt == "md":
        messagebox.showwarning(
            "Font Override Warning",
            "Markdown format does not support custom font families! Applied custom fonts will be overridden in Markdown."
        )
      choice["format"] = fmt
      dialog.destroy()

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=10)
    tk.Button(
        btn_frame,
        text="Markdown",
        command=lambda: select("md"),
        width=10,
        font=(self.default_family, 10),
    ).pack(side="left", padx=10)
    tk.Button(
        btn_frame,
        text="HTML",
        command=lambda: select("html"),
        width=10,
        font=(self.default_family, 10),
    ).pack(side="left", padx=10)

    self.root.wait_window(dialog)

    if "format" not in choice:
      return

    format_choice = choice["format"]
    file_path = filedialog.asksaveasfilename(
        defaultextension=".ccb", filetypes=[("Corecubes Files", "*.ccb")]
    )
    if file_path:
      try:
        if format_choice == "html":
          content = self.export_html()
        else:
          content = self.export_markdown()
        with open(file_path, "w", encoding="utf-8") as f:
          f.write(content)
        self.current_file_path = file_path
        self.root.title(f"Corecubes - {os.path.basename(file_path)}")
        self.add_recent(file_path)
        messagebox.showinfo(
            "Success",
            f"Saved successfully as Corecubes format ({format_choice.upper()})!",
        )
      except Exception as e:
        messagebox.showerror("Error", f"Could not save .ccb file:\n{e}")

  def show_help(self):
    win = tk.Toplevel(self.root)
    win.title("Help - About CoreCubes")
    win.geometry("560x420")
    win.transient(self.root)

    btn = tk.Button(win, text="OK", width=10, command=win.destroy)
    btn.pack(side="bottom", pady=8)

    scroll = tk.Scrollbar(win)
    scroll.pack(side="right", fill="y")
    box = tk.Text(
        win,
        wrap="word",
        font=(self.default_family, 10),
        padx=10,
        pady=10,
        yscrollcommand=scroll.set,
    )
    box.pack(side="left", fill="both", expand=True)
    scroll.config(command=box.yview)
    box.insert("1.0", LICENSE_TEXT)
    box.config(state="disabled")
    win.bind("<Escape>", lambda e: win.destroy())
    btn.focus_set()

  def wipe_text(self):
    self.text_area.delete("1.0", tk.END)
    self.check_styling_status()

  def leave_app(self):
    if messagebox.askokcancel("Quit", "Do you want to leave CoreCubes? Unsaved changes will be discarded."):
      self.root.destroy()

  def undo(self):
    try:
      self.text_area.edit_undo()
    except tk.TclError:
      pass
    self.check_styling_status()

  def redo(self):
    try:
      self.text_area.edit_redo()
    except tk.TclError:
      pass
    self.check_styling_status()

  def select_all(self):
    self.text_area.tag_add("sel", "1.0", "end-1c")

  def duplicate_selection(self):
    try:
      selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
      self.text_area.insert(tk.SEL_LAST, " " + selected_text)
    except tk.TclError:
      line_text = self.text_area.get("insert linestart", "insert lineend")
      self.text_area.insert("insert lineend", " " + line_text)

  def duplicate_to_new_line(self):
    line_text = self.text_area.get("insert linestart", "insert lineend")
    self.text_area.insert("insert lineend", "\n" + line_text)

  def find_text(self):
    target = simpledialog.askstring("Find", "Enter text to find:")
    if not target:
      return
    ta = self.text_area
    pos = ta.search(target, "insert", stopindex="end", nocase=True)
    if not pos:
      pos = ta.search(target, "1.0", stopindex="end", nocase=True)
    if pos:
      end = f"{pos}+{len(target)}c"
      ta.tag_remove("sel", "1.0", "end")
      ta.tag_add("sel", pos, end)
      ta.mark_set("insert", end)
      ta.see(pos)
      ta.focus_set()
    else:
      messagebox.showinfo("Not Found", f"'{target}' was not found.")

  def insert_datetime(self, date_format):
    current_time = datetime.now().strftime(date_format)
    self.text_area.insert(tk.INSERT, current_time)


if __name__ == "__main__":
  root = tk.Tk()
  app = CorecubesEditor(root)
  root.mainloop()
  
  #by Mr. Cobalt - Lion-A Softwares
  #Contact : mrcobalt.info@gmail.com