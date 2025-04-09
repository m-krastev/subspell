import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import difflib
from pathlib import Path
import threading
import logging
import traceback
import time
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
import webbrowser

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("subspell-gui")

# Import local modules
try:
    from .spellchecker import SpellChecker
    from .subtitle import parse_subtitle_file, write_subtitle_file
    from .config import ConfigManager
except ImportError:
    # Handle direct script execution
    from subspell.spellchecker import SpellChecker
    from subspell.subtitle import parse_subtitle_file, write_subtitle_file
    from subspell.config import ConfigManager

@dataclass
class Subtitle:
    """Represents a single subtitle entry."""
    line_num: int
    original: str
    changed: str

    def __post_init__(self):
        """Initialize changed text to match original if not set."""
        if not hasattr(self, 'changed') or not self.changed:
            self.changed = self.original

    @property
    def is_changed(self) -> bool:
        """Check if the subtitle has been modified."""
        return self.original != self.changed

    def get_diffs(self) -> List[Tuple[int, Tuple[int, int], str]]:
        """
        Calculate the differences between original and changed text.
        
        Returns:
            List of tuples containing (type, span, string) where:
            - type: 1 for insertion, -1 for deletion
            - span: tuple of (start_index, length)
            - string: the text that was inserted or deleted
        """
        if not self.is_changed:
            return []
        
        # Compare text directly
        diffs = list(difflib.ndiff(self.original, self.changed))

        return diffs

    def change_type(self) -> str:
        """
        Determine the type of changes made to the subtitle.
        
        Returns:
            'addition' if only insertions
            'deletion' if only deletions
            'mixed' if both insertions and deletions
            'unchanged' if no changes
        """
        if not self.is_changed:
            return 'unchanged'

        diffs = self.get_diffs()
        has_additions = any(diff[0] == "+" for diff in diffs)
        has_deletions = any(diff[0] == "-" for diff in diffs)
        
        if has_additions and has_deletions:
            return 'mixed'
        elif has_additions:
            return 'addition'
        elif has_deletions:
            return 'deletion'
        return 'unchanged'

class ModernTheme:
    """Modern theme colors and styles."""
    
    LIGHT_THEME = {
        "bg": "#ffffff",
        "fg": "#000000",
        "select_bg": "#0078d7",
        "select_fg": "#ffffff",
        "button_bg": "#f0f0f0",
        "button_fg": "#000000",
        "button_active_bg": "#e0e0e0",
        "diff_add_bg": "#e6ffe6",
        "diff_add_fg": "#006600",
        "diff_del_bg": "#ffe6e6",
        "diff_del_fg": "#cc0000",
        "diff_header_bg": "#f0f0f0",
        "diff_header_fg": "#000000",
        "status_bg": "#f0f0f0",
        "status_fg": "#000000",
        "text_bg": "#ffffff",
        "text_fg": "#000000",
        "separator": "#e0e0e0"
    }
    
    DARK_THEME = {
        "bg": "#2d2d2d",
        "fg": "#ffffff",
        "select_bg": "#0078d7",
        "select_fg": "#ffffff",
        "button_bg": "#3d3d3d",
        "button_fg": "#ffffff",
        "button_active_bg": "#4d4d4d",
        "diff_add_bg": "#1a3d1a",
        "diff_add_fg": "#99ff99",
        "diff_del_bg": "#3d1a1a",
        "diff_del_fg": "#ff9999",
        "diff_header_bg": "#3d3d3d",
        "diff_header_fg": "#ffffff",
        "status_bg": "#3d3d3d",
        "status_fg": "#ffffff",
        "text_bg": "#2d2d2d",
        "text_fg": "#ffffff",
        "separator": "#4d4d4d"
    }

class ModernButton(ttk.Button):
    """Modern styled button with hover effects."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_enter(self, e):
        self.state(["active"])
        
    def _on_leave(self, e):
        self.state(["!active"])

class ModernDiffViewer(ttk.Frame):
    """Modern widget to display and interact with text differences."""

    def __init__(self, master, app=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.app = app or master
        self.theme = app.theme if hasattr(app, 'theme') else ModernTheme.LIGHT_THEME

        # Create styles for different row heights
        self.style = ttk.Style()
        
        # Configure base styles
        self.style.configure("Treeview", rowheight=20)
        self.style.configure("Treeview.Row", padding=2)
        self.style.configure("TFrame", background=self.theme["text_bg"])
        self.style.configure("TLabel", background=self.theme["text_bg"], foreground=self.theme["text_fg"])
        
        # Configure Treeview colors
        self.style.map(
            "Treeview",
            background=[("selected", self.theme["select_bg"])],
            foreground=[("selected", self.theme["select_fg"])],
            fieldbackground=[("selected", self.theme["select_bg"])]
        )

        # Create main container with padding
        self.main_container = ttk.Frame(self, style="TFrame")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create toolbar frame
        self.toolbar = ttk.Frame(self.main_container, style="TFrame")
        self.toolbar.pack(fill=tk.X, pady=(0, 10))

        # Create buttons with modern styling
        self.apply_all_btn = ModernButton(
            self.toolbar,
            text="Apply All Changes",
            command=self.apply_all_changes,
            style="Modern.TButton"
        )
        self.apply_all_btn.pack(side=tk.LEFT, padx=5)

        self.apply_selected_btn = ModernButton(
            self.toolbar,
            text="Apply Selected Changes",
            command=self.apply_selected_changes,
            style="Modern.TButton"
        )
        self.apply_selected_btn.pack(side=tk.LEFT, padx=5)

        # Add separator
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Add reject all changes button
        self.reject_all_btn = ModernButton(
            self.toolbar,
            text="Reject All Changes",
            command=self.reject_all_changes,
            style="Modern.TButton"
        )
        self.reject_all_btn.pack(side=tk.LEFT, padx=5)

        # Add keep original button
        self.keep_original_btn = ModernButton(
            self.toolbar,
            text="Keep Original",
            command=self.keep_original,
            style="Modern.TButton"
        )
        self.keep_original_btn.pack(side=tk.LEFT, padx=5)

        # Add separator
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Add filter button
        self.show_only_changes = False
        self.filter_btn = ModernButton(
            self.toolbar,
            text="Show Only Changes",
            command=self.toggle_filter,
            style="Modern.TButton"
        )
        self.filter_btn.pack(side=tk.LEFT, padx=5)

        # Create the listview frame
        self.listview_frame = ttk.Frame(self.main_container, style="TFrame")
        self.listview_frame.pack(fill=tk.BOTH, expand=True)

        # Create the listview
        self.listview = ttk.Treeview(
            self.listview_frame,
            columns=("line", "original", "corrected"),
            show="headings",
            selectmode="extended",
            style="Treeview"
        )
        
        # Configure columns
        self.listview.heading("line", text="Line")
        self.listview.heading("original", text="Original")
        self.listview.heading("corrected", text="Corrected")
        
        # Configure line column to be compact and non-stretching
        self.listview.column("line", width=30, minwidth=30, stretch=0, anchor=tk.CENTER)
        self.listview.column("original", width=300)
        self.listview.column("corrected", width=300)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.listview_frame, orient=tk.VERTICAL, command=self.listview.yview)
        self.listview.configure(yscrollcommand=scrollbar.set)
        
        # Pack the listview and scrollbar
        self.listview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection event
        self.listview.bind("<<TreeviewSelect>>", self.on_selection_change)
        
        # Bind double-click event for editing
        self.listview.bind("<Double-1>", self.on_double_click)
        
        # Bind edit events
        self.listview.bind("<<TreeviewCellEdited>>", self.on_cell_edited)

        # Track changes and selections
        self.changes = []
        self.selected_changes = set()
        self.subtitles: List[Subtitle] = []
        self.editing_item = None

        # Configure initial theme
        self.update_theme(self.theme)

    def show_subtitles(self, subtitles: List[Subtitle]):
        """Show subtitles in the listview with character-level diff highlighting."""
        self.clear()
        self.subtitles = subtitles
        
        # Get the default font metrics using a temporary label
        temp_label = ttk.Label(self, text="M")
        base_height = temp_label.winfo_reqheight()
        temp_label.destroy()
        
        # Calculate maximum lines needed
        max_lines = 1
        for subtitle in subtitles:
            if not (self.show_only_changes and not subtitle.is_changed):
                original_lines = subtitle.original.count('\n') + subtitle.original.count('\\N') + 1
                changed_lines = subtitle.changed.count('\n') + subtitle.changed.count('\\N') + 1
                max_lines = max(max_lines, original_lines, changed_lines)
        
        # Calculate row height based on base height and number of lines
        # Add padding for better readability
        padding = base_height * 0.5  # 50% of base height for padding
        row_height = base_height * max_lines + padding
        
        # Ensure minimum height for readability
        min_height = base_height * 1.5  # 150% of base height
        row_height = max(row_height, min_height)
        
        # Set the row height
        self.style.configure("Treeview", rowheight=int(row_height))
        
        for subtitle in subtitles:
            # Skip unchanged items if filter is active
            is_changed = subtitle.is_changed
            if self.show_only_changes and not is_changed:
                continue

            item = self.listview.insert(
                "",
                tk.END,
                values=(str(subtitle.line_num), subtitle.original, subtitle.changed),
                tags=subtitle.change_type(),
            )

            if is_changed:
                self.changes.append(len(self.subtitles) - 1)

        # Force a redraw to ensure proper height
        self.listview.update_idletasks()
        self.listview.update()

    def clear(self):
        """Clear the diff view."""
        self.listview.delete(*self.listview.get_children())
        self.changes = []
        self.selected_changes = set()
        self.subtitles = []

    def on_double_click(self, event):
        """Handle double-click events for editing."""
        region = self.listview.identify_region(event.x, event.y)
        if region == "cell":
            column = self.listview.identify_column(event.x)
            item = self.listview.identify_row(event.y)

            if item and column:
                # Get the column number (1-based)
                col_num = int(column[1])
                if col_num in [
                    2,
                    3,
                ]:  # Only allow editing original and corrected columns
                    # Get the current value
                    current_value = self.listview.item(item)["values"][col_num - 1]

                    # Create text widget for multiline editing
                    text_widget = tk.Text(self.listview, wrap=tk.WORD, height=5)
                    text_widget.insert("1.0", current_value)
                    text_widget.tag_add("sel", "1.0", tk.END)
                    text_widget.focus_set()

                    # Position the text widget
                    x, y, w, h = self.listview.bbox(item, column)
                    text_widget.place(x=x, y=y, width=w, height=max(h * 3, 100))

                    def finish_editing(event):
                        new_value = text_widget.get("1.0", tk.END).strip()
                        values = list(self.listview.item(item)["values"])
                        values[col_num - 1] = new_value
                        self.listview.item(item, values=values)

                        # Update the subtitle
                        item_idx = self.listview.index(item)
                        if item_idx < len(self.subtitles):
                            subtitle = self.subtitles[item_idx]
                            if col_num == 2:  # Original column
                                subtitle.original = new_value
                            else:  # Corrected column
                                subtitle.changed = new_value

                            # Update changed status
                            is_changed = subtitle.is_changed
                            if is_changed and item_idx not in self.changes:
                                self.changes.append(item_idx)
                            elif not is_changed and item_idx in self.changes:
                                self.changes.remove(item_idx)

                            self.update_changed_items()

                        text_widget.destroy()
                        self.listview.focus_set()

                    def handle_return(event):
                        if event.state & 0x1:  # Shift is pressed
                            text_widget.insert(tk.INSERT, "\\N")
                            return "break"  # Prevent default behavior
                        else:
                            finish_editing(event)
                            return "break"  # Prevent default behavior

                    text_widget.bind("<Return>", handle_return)
                    text_widget.bind("<Escape>", lambda e: text_widget.destroy())
                    text_widget.bind("<FocusOut>", finish_editing)

    def on_cell_edited(self, event):
        """Handle cell edit completion."""
        item = self.listview.focus()
        column = self.listview.identify_column(
            self.listview.winfo_pointerx() - self.listview.winfo_rootx()
        )

        if item and column:
            # Get the column number (1-based)
            col_num = int(column[1])
            if col_num in [2, 3]:  # Only handle original and corrected columns
                new_value = self.listview.item(item)["values"][col_num - 1]

                # Update the subtitle
                item_idx = self.listview.index(item)
                if item_idx < len(self.subtitles):
                    subtitle = self.subtitles[item_idx]
                    if col_num == 2:  # Original column
                        subtitle.original = new_value
                    else:  # Corrected column
                        subtitle.changed = new_value

                    # Update changed status
                    if subtitle.is_changed and item_idx not in self.changes:
                        self.changes.append(item_idx)
                    elif not subtitle.is_changed and item_idx in self.changes:
                        self.changes.remove(item_idx)

                    self.update_changed_items()

    def update_changed_items(self):
        """Update the appearance of changed items."""
        # Configure tag styles
        self.listview.tag_configure(
            "addition",
            background=self.theme["diff_add_bg"],
            foreground=self.theme["diff_add_fg"],
        )
        self.listview.tag_configure(
            "deletion",
            background=self.theme["diff_del_bg"],
            foreground=self.theme["diff_del_fg"],
        )
        self.listview.tag_configure(
            "mixed",
            background="#fff3cd",  # Light yellow
            foreground="#856404",  # Dark yellow
        )
        self.listview.tag_configure(
            "unchanged",
            background=self.theme["text_bg"],
            foreground=self.theme["text_fg"],
        )

        # Update tags for all items
        for item in self.listview.get_children():
            item_idx = self.listview.index(item)
            if item_idx < len(self.subtitles):
                subtitle = self.subtitles[item_idx]
                change_type = subtitle.change_type()
                tag = change_type if change_type != "unchanged" else "unchanged"
                self.listview.item(item, tags=(tag,))

    def update_theme(self, theme):
        """Update the widget's theme colors."""
        self.theme = theme

        # Configure base styles
        self.style.configure("Treeview", rowheight=20)
        self.style.configure("Treeview.Row", padding=2)
        self.style.configure("TFrame", background=self.theme["text_bg"])
        self.style.configure(
            "TLabel", background=self.theme["text_bg"], foreground=self.theme["text_fg"]
        )

        # Configure Treeview colors
        self.style.map(
            "Treeview",
            background=[("selected", self.theme["select_bg"])],
            foreground=[("selected", self.theme["select_fg"])],
            fieldbackground=[("selected", self.theme["select_bg"])],
        )

        # Update tags and force a redraw
        self.update_changed_items()

        # Recalculate and apply row heights if we have subtitles
        if self.subtitles:
            max_lines = 1
            for subtitle in self.subtitles:
                if not (self.show_only_changes and not subtitle.is_changed):
                    original_lines = (
                        subtitle.original.count("\n")
                        + subtitle.original.count("\\N")
                        + 1
                    )
                    changed_lines = (
                        subtitle.changed.count("\n") + subtitle.changed.count("\\N") + 1
                    )
                    max_lines = max(max_lines, original_lines, changed_lines)

            row_height = 20 + (max_lines - 1) * 15
            self.style.configure("Treeview", rowheight=row_height)

        self.listview.update_idletasks()
        self.listview.update()

    def on_selection_change(self, event):
        """Handle selection changes in the listview."""
        selected_items = self.listview.selection()
        self.selected_changes = set()

        for item in selected_items:
            item_idx = self.listview.index(item)
            if item_idx < len(self.subtitles):
                self.selected_changes.add(item_idx)

    def apply_selected_changes(self):
        """Apply only selected changes."""
        if not self.selected_changes:
            messagebox.showinfo("Information", "No changes selected to apply.")
            return
        self.app.apply_changes(self.selected_changes)

    def apply_all_changes(self):
        """Apply all changes."""
        # Create a set of all indices that have changes
        all_changes = set(range(len(self.subtitles)))
        self.app.apply_changes(all_changes)

    def reject_all_changes(self):
        """Reject all changes by resetting changed text to original text."""
        for subtitle in self.subtitles:
            subtitle.changed = subtitle.original
        self.show_subtitles(self.subtitles)
        self.app.status_var.set("All changes rejected")

    def keep_original(self):
        """Keep original text by setting changed text to original text."""
        for subtitle in self.subtitles:
            subtitle.changed = subtitle.original
        self.show_subtitles(self.subtitles)
        self.app.status_var.set("Original text restored")

    def get_selected_changes(self) -> List[Tuple]:
        """Return the list of selected changes."""
        return [self.subtitles[idx] for idx in self.selected_changes]

    def toggle_filter(self):
        """Toggle between showing all items and only changed items."""
        self.show_only_changes = not self.show_only_changes
        self.filter_btn.configure(
            text="Show All" if self.show_only_changes else "Show Only Changes"
        )
        self.show_subtitles(self.subtitles)  # Refresh the display with current filter


class ModernSubSpellGUI(tk.Tk):
    """Modern main application window for SubSpell GUI."""

    def __init__(self):
        super().__init__()

        # Initialize configuration manager
        self.config = ConfigManager()

        self.title("SubSpell - Subtitle Spell Checker")

        # Set window size and position from config
        window_size = self.config.get("window_size", "1200x800")
        window_position = self.config.get("window_position")
        self.geometry(window_size)
        if window_position:
            self.geometry(f"+{window_position[0]}+{window_position[1]}")

        # Set theme based on config
        theme_setting = self.config.get("theme", "system")
        if theme_setting == "system":
            self.dark_mode = self.is_system_dark_mode()
        else:
            self.dark_mode = theme_setting == "dark"
        self.theme = (
            ModernTheme.DARK_THEME if self.dark_mode else ModernTheme.LIGHT_THEME
        )

        # Configure ttk styles
        self.style = ttk.Style()
        self.style.configure("Modern.TButton", padding=5)

        # Configure root window style
        self.style.configure("TFrame", background=self.theme["bg"])
        self.style.configure(
            "TLabel", background=self.theme["bg"], foreground=self.theme["fg"]
        )

        # Initialize variables
        self.spellchecker = None
        self.current_file = None
        self.subtitle_data = None
        self.subtitles: List[Subtitle] = []  # Global state of subtitles

        # Create the main layout
        self.create_menu()
        self.create_toolbar()
        self.create_widgets()
        self.create_status_bar()

        # Check for API key on startup
        self.check_api_key_on_startup()

        # Bind window close event to save state
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle window closing event."""
        # Save window position and size
        x = self.winfo_x()
        y = self.winfo_y()
        width = self.winfo_width()
        height = self.winfo_height()
        self.config.update({
            "window_position": [x, y],
            "window_size": f"{width}x{height}",
        })
        self.destroy()

    def is_system_dark_mode(self) -> bool:
        """Detect if the system is using dark mode."""
        try:
            if sys.platform == "darwin":  # macOS
                import subprocess

                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleInterfaceStyle"],
                    capture_output=True,
                    text=True,
                )
                return result.stdout.strip().lower() == "dark"
            elif sys.platform == "win32":  # Windows
                import winreg

                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(
                    registry,
                    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                )
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return value == 0
            else:  # Linux and others
                try:
                    import subprocess

                    result = subprocess.run(
                        [
                            "gsettings",
                            "get",
                            "org.gnome.desktop.interface",
                            "color-scheme",
                        ],
                        capture_output=True,
                        text=True,
                    )
                    return "dark" in result.stdout.lower()
                except:
                    return False
        except:
            return False  # Default to light theme if detection fails

    def create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Subtitle File", command=self.open_file)
        file_menu.add_command(label="Save Corrected Subtitle", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(
            label="Configure API Key", command=self.configure_api_key
        )
        tools_menu.add_command(
            label="Configure LLM Prompt", command=self.configure_prompt
        )
        tools_menu.add_command(label="Toggle Dark Mode", command=self.toggle_theme)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        # Set the menu bar using the correct method
        self["menu"] = menubar

    def create_toolbar(self):
        """Create the toolbar with common actions."""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        # Open file button
        self.open_btn = ModernButton(
            toolbar, text="Open File", command=self.open_file, style="Modern.TButton"
        )
        self.open_btn.pack(side=tk.LEFT, padx=2)

        # Check spelling button
        self.check_btn = ModernButton(
            toolbar,
            text="Check Spelling",
            command=self.check_spelling,
            style="Modern.TButton",
        )
        self.check_btn.pack(side=tk.LEFT, padx=2)

        # Save button
        self.save_btn = ModernButton(
            toolbar, text="Save", command=self.save_file, style="Modern.TButton"
        )
        self.save_btn.pack(side=tk.LEFT, padx=2)

        # Add separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Theme toggle button
        self.theme_btn = ModernButton(
            toolbar,
            text="Toggle Theme",
            command=self.toggle_theme,
            style="Modern.TButton",
        )
        self.theme_btn.pack(side=tk.LEFT, padx=2)

    def create_widgets(self):
        """Create the main application widgets."""
        # Create main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create the diff viewer as the main widget
        self.diff_viewer = ModernDiffViewer(main_container, app=self)
        self.diff_viewer.pack(fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        """Create the status bar."""
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            background=self.theme["status_bg"],
            foreground=self.theme["status_fg"],
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Ready")

    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.dark_mode = not self.dark_mode
        self.theme = (
            ModernTheme.DARK_THEME if self.dark_mode else ModernTheme.LIGHT_THEME
        )

        # Save theme preference
        self.config.set("theme", "dark" if self.dark_mode else "light")

        # Update root window style
        self.style.configure("TFrame", background=self.theme["bg"])
        self.style.configure(
            "TLabel", background=self.theme["bg"], foreground=self.theme["fg"]
        )

        # Update text widgets
        self.diff_viewer.update_theme(self.theme)

        # Update status bar
        self.status_bar.configure(
            background=self.theme["status_bg"], foreground=self.theme["status_fg"]
        )

    def open_file(self):
        """Open a subtitle file."""
        filepath = filedialog.askopenfilename(
            title="Open Subtitle File",
            filetypes=[
                ("Subtitle files", "*.srt *.ass *.ssa"),
                ("SRT files", "*.srt"),
                ("ASS/SSA files", "*.ass *.ssa"),
                ("All files", "*.*"),
            ],
        )

        if not filepath:
            return

        try:
            self.current_file = filepath
            self.subtitle_data = parse_subtitle_file(filepath)

            # Initialize subtitles list
            self.subtitles = []
            for i, subtitle in enumerate(self.subtitle_data, 1):
                self.subtitles.append(Subtitle(i, subtitle["text"], subtitle["text"]))

            # Display subtitles in the diff viewer
            self.diff_viewer.show_subtitles(self.subtitles)

            filename = os.path.basename(filepath)
            self.status_var.set(
                f"Loaded {filename} with {len(self.subtitles)} subtitle entries"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load subtitle file: {str(e)}")

    def check_spelling(self):
        """Check spelling of the text in the listview."""
        if not self.subtitles:
            messagebox.showinfo("Information", "No text to check.")
            return

        # Create progress dialog
        progress_dialog = tk.Toplevel(self)
        progress_dialog.title("Processing")
        progress_dialog.geometry("300x150")
        progress_dialog.transient(self)
        progress_dialog.grab_set()
        progress_dialog.configure(bg=self.theme["bg"])

        # Add progress label
        ttk.Label(
            progress_dialog, text="Checking spelling...", font=("TkDefaultFont", 10)
        ).pack(pady=10)

        # Add progress bar
        progress_bar = ttk.Progressbar(
            progress_dialog, mode="indeterminate", length=200
        )
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        progress_bar.start()

        # Add status label
        status_label = ttk.Label(
            progress_dialog, text="This may take a while...", font=("TkDefaultFont", 9)
        )
        status_label.pack(pady=5)

        # Check API key
        api_key = self.config.get("api_key", "")
        if not api_key:
            progress_dialog.destroy()
            messagebox.showwarning(
                "API Key Required", "Please configure your Gemini API key first."
            )
            self.configure_api_key()
            return

        # Initialize spellchecker if needed
        if self.spellchecker is None:
            if not self.initialize_spellchecker():
                progress_dialog.destroy()
                return

        # Set status and disable check button
        self.status_var.set("Checking spelling...")
        self.check_btn.config(state=tk.DISABLED)
        self.update_idletasks()

        # Create result container
        result_container = {"result": None, "error": None}

        # Start spell check thread
        spell_check_thread = threading.Thread(
            target=self.run_spell_check_blocking,
            args=(self.subtitles, time.strftime("%Y%m%d-%H%M%S"), result_container),
            daemon=True,
        )
        spell_check_thread.start()

        # Update UI while waiting
        while spell_check_thread.is_alive():
            self.update()
            time.sleep(0.1)

        # Process results
        progress_bar.stop()
        progress_dialog.destroy()
        self.check_btn.config(state=tk.NORMAL)

        error = result_container["error"]
        result = result_container["result"]

        if error:
            self.handle_spell_check_error(error)
            return

        if not result:
            self.handle_empty_result()
            return

        self.handle_spell_check_success(result)

    def handle_spell_check_error(self, error):
        """Handle spell check errors."""
        error_message = str(error)
        exception_type = type(error).__name__
        logger.error(f"Spell check failed: {exception_type}: {error_message}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        messagebox.showerror(
            "Error",
            f"Failed to check spelling:\n\nType: {exception_type}\nError: {error_message}\n\n"
            "See console for detailed traceback.",
        )
        self.status_var.set("Spell check failed.")

    def handle_empty_result(self):
        """Handle empty spell check results."""
        logger.error("Received empty response from spellchecker")
        messagebox.showerror(
            "Error",
            "Received empty response from the spellchecker.\n"
            "Check the console for more details.",
        )
        self.status_var.set("Spell check failed: Empty response.")

    def handle_spell_check_success(self, corrected_subtitles):
        """Handle successful spell check results."""
        logger.info(
            f"Correction completed. {len(corrected_subtitles)} subtitles processed"
        )

        # Update global state with corrected subtitles
        self.subtitles = corrected_subtitles

        try:
            logger.info("Showing corrected subtitles")
            self.diff_viewer.show_subtitles(self.subtitles)
            self.status_var.set("Spell check completed. Select changes to apply.")
        except Exception as e:
            logger.error(f"Error showing subtitles: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Failed to display changes: {str(e)}")
            self.status_var.set("Failed to display changes.")

    def run_spell_check_blocking(
        self, subtitles: List[Subtitle], timestamp, result_container
    ):
        """Run spell check in a blocking manner."""
        try:
            logger.info(f"Starting spell check. {len(subtitles)} subtitles to process")
            start_time = time.time()

            texts = [
                subtitle.original.replace("\\N", "§LINEBREAK§").replace("<*>", "§TAG§")
                for subtitle in subtitles
            ]
            texts = self.spellchecker.correct_subtitles(texts, 0)

            logger.info(
                f"Spell check completed. {len(texts)} subtitles processed. Time taken: {time.time() - start_time:.2f} seconds"
            )

            # Parse corrected text back into subtitles
            corrected_subtitles = []
            for i, subtitle_text in enumerate(texts):
                # Replace §LINEBREAK§ with \N for subtitle format
                subtitle_text = (
                    subtitle_text.strip()
                    .replace("§LINEBREAK§", "\\N")
                    .replace("§TAG§", "<*>")
                )
                if i < len(subtitles):
                    corrected_subtitles.append(
                        Subtitle(
                            subtitles[i].line_num, subtitles[i].original, subtitle_text
                        )
                    )
                else:
                    # Handle case where spellchecker returned more subtitles than original
                    corrected_subtitles.append(
                        Subtitle(i + 1, subtitle_text, subtitle_text)
                    )

            result_container["result"] = corrected_subtitles

        except Exception as e:
            logger.error(
                f"Exception in run_spell_check thread: {type(e).__name__}: {str(e)}"
            )
            logger.error(f"Traceback: {traceback.format_exc()}")
            result_container["error"] = e

    def save_file(self):
        """Save the subtitle file."""
        if not self.current_file or not self.subtitle_data:
            messagebox.showinfo("Information", "No subtitle file is currently loaded.")
            return

        default_name = (
            f"{Path(self.current_file).stem}_corrected{Path(self.current_file).suffix}"
        )
        filepath = filedialog.asksaveasfilename(
            title="Save Subtitle File",
            defaultextension=Path(self.current_file).suffix,
            initialfile=default_name,
            filetypes=[
                ("Subtitle files", f"*{Path(self.current_file).suffix}"),
                ("All files", "*.*"),
            ],
        )

        if not filepath:
            return

        try:
            # Map subtitles back to the original format
            for subtitle in self.subtitles:
                if subtitle.line_num <= len(self.subtitle_data):
                    # Update the text while preserving all other metadata
                    self.subtitle_data[subtitle.line_num - 1]["text"] = subtitle.changed

            # Write the subtitles to the new file
            write_subtitle_file(self.subtitle_data, filepath)

            messagebox.showinfo("Success", f"Subtitle file saved to {filepath}")
            self.status_var.set(f"Saved subtitle to {os.path.basename(filepath)}")

        except Exception as e:
            logger.error(f"Error saving subtitle file: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Failed to save subtitle file: {str(e)}")

    def configure_api_key(self):
        """Configure the API key for the spellchecker."""
        dialog = tk.Toplevel(self)
        dialog.title("Configure API Key")
        dialog.geometry("500x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=self.theme["bg"])

        # Add instruction text
        instruction_frame = ttk.Frame(dialog)
        instruction_frame.pack(fill=tk.X, padx=20, pady=10)

        instructions = ttk.Label(
            instruction_frame,
            text="Enter your Gemini API key. If you don't have one, you can get it from:\nhttps://aistudio.google.com/apikey",
            wraplength=460,
            justify=tk.LEFT,
            font=("TkDefaultFont", 10),
        )
        instructions.pack(anchor=tk.W)

        link_label = ttk.Label(
            instruction_frame,
            text="Get API key",
            foreground="blue",
            cursor="hand2",
            font=("TkDefaultFont", 10),
        )
        link_label.pack(anchor=tk.W)
        link_label.bind(
            "<Button-1>", lambda e: self.open_url("https://aistudio.google.com/apikey")
        )

        ttk.Separator(dialog, orient="horizontal").pack(fill=tk.X, padx=20, pady=5)

        ttk.Label(
            dialog, text="Gemini API key:", font=("TkDefaultFont", 10, "bold")
        ).pack(pady=5, padx=20, anchor=tk.W)

        # Get current key from config or environment
        current_key = self.config.get("api_key", "") or os.environ.get(
            "GEMINI_API_KEY", ""
        )
        api_key_var = tk.StringVar(value=current_key)
        api_key_entry = ttk.Entry(
            dialog, textvariable=api_key_var, width=50, font=("TkDefaultFont", 10)
        )
        api_key_entry.pack(pady=5, padx=20, fill=tk.X)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=15)

        def save_api_key():
            api_key = api_key_var.get().strip()
            if api_key:
                logger.info(f"Setting new API key: {'*' * 8}")
                # Save to both config and environment
                self.config.set("api_key", api_key)
                os.environ["GEMINI_API_KEY"] = api_key

                self.status_var.set("Testing API key...")
                dialog.configure(cursor="wait")
                button_frame.configure(cursor="wait")
                self.update_idletasks()

                save_btn.configure(state="disabled")
                cancel_btn.configure(state="disabled")

                def test_api_key():
                    success = False
                    error_msg = ""

                    try:
                        logger.info("Testing new API key...")
                        self.spellchecker = None
                        success = self.initialize_spellchecker()
                        logger.info(f"API key test result: {success}")
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"API key test failed: {str(e)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")

                    self.after(0, lambda: finish_api_key_test(success, error_msg))

                def finish_api_key_test(success, error_msg):
                    dialog.configure(cursor="")
                    button_frame.configure(cursor="")
                    save_btn.configure(state="normal")
                    cancel_btn.configure(state="normal")

                    if success:
                        logger.info("API key validated successfully")
                        messagebox.showinfo(
                            "Success", "API key validated and saved successfully!"
                        )
                        dialog.destroy()
                    else:
                        logger.error(f"API key validation failed: {error_msg}")
                        messagebox.showerror(
                            "Error",
                            f"Failed to validate API key: {error_msg or 'Unknown error'}\n\n"
                            "See console for detailed error information.",
                        )
                        self.status_var.set("API key validation failed.")

                threading.Thread(target=test_api_key, daemon=True).start()
            else:
                logger.warning("Empty API key submitted")
                messagebox.showwarning("Warning", "Please enter a valid API key.")

        save_btn = ModernButton(
            button_frame, text="Save", command=save_api_key, style="Modern.TButton"
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ModernButton(
            button_frame, text="Cancel", command=dialog.destroy, style="Modern.TButton"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def open_url(self, url):
        """Open a URL in the default web browser."""
        webbrowser.open(url)

    def initialize_spellchecker(self):
        """Initialize the spellchecker."""
        try:
            # Get API key from config or environment
            api_key = self.config.get("api_key", "") or os.environ.get("GEMINI_API_KEY")
            if not api_key:
                logger.error("No Gemini API key configured")
                raise ValueError("Gemini API key is not configured")

            self.status_var.set("Initializing spellchecker...")
            self.update_idletasks()

            # Get LLM settings from config or environment
            llm_prompt = self.config.get("llm_prompt", "") or os.environ.get(
                "SUBSPELL_LLM_PROMPT"
            )
            temperature = float(
                self.config.get("temperature", 0.2)
                or os.environ.get("SUBSPELL_TEMPERATURE", 0.2)
            )
            top_k = int(
                self.config.get("top_k", 40) or os.environ.get("SUBSPELL_TOP_K", 40)
            )
            top_p = float(
                self.config.get("top_p", 0.95) or os.environ.get("SUBSPELL_TOP_P", 0.95)
            )
            model = self.config.get("model", "gemini-2.0-flash") or os.environ.get(
                "SUBSPELL_MODEL", "gemini-2.0-flash"
            )

            logger.info(f"Initializing SpellChecker with API key: {'*' * 8}")
            self.spellchecker = SpellChecker(
                api_key=api_key,
                system_instruction=llm_prompt,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                model=model,
            )
            logger.info(f"SpellChecker initialized: {type(self.spellchecker)}")

            try:
                logger.debug("Testing spellchecker with a simple test")
                test_result = self.spellchecker.correct_text("тест")
                if test_result:
                    logger.info("Spellchecker test successful")
                else:
                    logger.warning("Spellchecker test returned empty result")
            except Exception as e:
                logger.warning(f"Spellchecker test failed: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                messagebox.showerror(
                    "Error",
                    f"Failed to initialize spellchecker:\n\n{type(e).__name__}: {str(e)}\n\n"
                    "See console for detailed traceback.",
                )
                self.status_var.set("Initialization failed.")
                return False
            return True
        except Exception as e:
            logger.error(
                f"Failed to initialize spellchecker: {type(e).__name__}: {str(e)}"
            )
            logger.error(f"Traceback: {traceback.format_exc()}")
            messagebox.showerror(
                "Error",
                f"Failed to initialize spellchecker:\n\n{type(e).__name__}: {str(e)}\n\n"
                "See console for detailed traceback.",
            )
            self.status_var.set("Initialization failed.")
            return False

    def check_api_key_on_startup(self):
        """Check if API key is set on startup and prompt if not."""
        # Get API key from config or environment
        api_key = self.config.get("api_key", "") or os.environ.get("GEMINI_API_KEY", "")

        if not api_key:
            messagebox.showinfo(
                "API Key Required",
                "No Gemini API key found. Please configure your API key before using the application.",
            )
            self.configure_api_key()

    def apply_changes(self, selected_indices: Set[int]):
        """Apply selected changes from the diff viewer."""
        if not self.subtitles:
            messagebox.showinfo("Information", "No corrections available to apply.")
            return

        if len(selected_indices) == len(self.subtitles):
            # Apply all changes
            for subtitle in self.subtitles:
                subtitle.original = subtitle.changed
            self.diff_viewer.show_subtitles(self.subtitles)
            self.status_var.set("Applied all changes")
            return

        # Apply only selected changes
        for idx in selected_indices:
            if idx < len(self.subtitles):
                self.subtitles[idx].original = self.subtitles[idx].changed

        self.diff_viewer.show_subtitles(self.subtitles)
        self.status_var.set(f"Applied {len(selected_indices)} changes")

    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About SubSpell",
            "SubSpell - Subtitle Spelling, Punctuation and Grammar Correction Tool\n\n"
            "For Bulgarian text with special support for subtitle files.\n\n"
            "© 2024 mkrastev",
        )

    def configure_prompt(self):
        """Configure the LLM prompt and generation parameters."""
        dialog = tk.Toplevel(self)
        dialog.title("Configure LLM Settings")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=self.theme["bg"])

        # Add instruction text
        instruction_frame = ttk.Frame(dialog)
        instruction_frame.pack(fill=tk.X, padx=20, pady=10)

        instructions = ttk.Label(
            instruction_frame,
            text="Configure the LLM settings for spell checking. The prompt should include:\n"
            "- Instructions for correcting spelling, punctuation, and grammar\n"
            "- Any specific rules or requirements\n"
            "- Language-specific guidelines\n"
            "- Format preservation instructions",
            wraplength=560,
            justify=tk.LEFT,
            font=("TkDefaultFont", 10),
        )
        instructions.pack(anchor=tk.W)

        ttk.Separator(dialog, orient="horizontal").pack(fill=tk.X, padx=20, pady=5)

        # Add prompt text area
        prompt_frame = ttk.Frame(dialog)
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        ttk.Label(
            prompt_frame, text="LLM Prompt:", font=("TkDefaultFont", 10, "bold")
        ).pack(anchor=tk.W)

        # Create text widget with scrollbar
        text_frame = ttk.Frame(prompt_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        prompt_text = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, width=60, height=15, font=("TkDefaultFont", 10)
        )
        prompt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add generation parameters frame
        params_frame = ttk.LabelFrame(dialog, text="Generation Parameters", padding=10)
        params_frame.pack(fill=tk.X, padx=20, pady=5)

        # Model selection
        model_frame = ttk.Frame(params_frame)
        model_frame.pack(fill=tk.X, pady=2)
        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT)
        model_var = tk.StringVar(value=self.config.get("model", "gemini-2.0-flash"))
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=model_var,
            values=[
                "gemini-2.0-flash",
                "gemini-2.0-flash-lite",
                "gemini-2.5-pro-preview-03-25",
            ],
            state="readonly",
            width=20,
        )
        model_combo.pack(side=tk.LEFT, padx=5)

        # Temperature
        temp_frame = ttk.Frame(params_frame)
        temp_frame.pack(fill=tk.X, pady=2)
        ttk.Label(temp_frame, text="Temperature:").pack(side=tk.LEFT)
        temp_var = tk.DoubleVar(value=round(self.config.get("temperature", 0.2), 2))
        temp_scale = ttk.Scale(
            temp_frame, from_=0.0, to=1.0, variable=temp_var, orient=tk.HORIZONTAL
        )
        temp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        temp_entry = ttk.Entry(temp_frame, textvariable=temp_var, width=6)
        temp_entry.pack(side=tk.LEFT, padx=5)

        # Top K
        topk_frame = ttk.Frame(params_frame)
        topk_frame.pack(fill=tk.X, pady=2)
        ttk.Label(topk_frame, text="Top K:").pack(side=tk.LEFT)
        topk_var = tk.IntVar(value=int(self.config.get("top_k", 40)))
        topk_scale = ttk.Scale(
            topk_frame, from_=1, to=100, variable=topk_var, orient=tk.HORIZONTAL
        )
        topk_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        topk_entry = ttk.Entry(topk_frame, textvariable=topk_var, width=6)
        topk_entry.pack(side=tk.LEFT, padx=5)

        # Top P
        topp_frame = ttk.Frame(params_frame)
        topp_frame.pack(fill=tk.X, pady=2)
        ttk.Label(topp_frame, text="Top P:").pack(side=tk.LEFT)
        topp_var = tk.DoubleVar(value=round(self.config.get("top_p", 0.95), 2))
        topp_scale = ttk.Scale(
            topp_frame, from_=0.0, to=1.0, variable=topp_var, orient=tk.HORIZONTAL
        )
        topp_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        topp_entry = ttk.Entry(topp_frame, textvariable=topp_var, width=6)
        topp_entry.pack(side=tk.LEFT, padx=5)

        # Add validation functions
        def validate_temperature(value):
            try:
                val = float(value)
                if 0 <= val <= 1:
                    temp_var.set(round(val, 2))  # Round the value
                    return True
                return False
            except ValueError:
                return False

        def validate_top_k(value):
            try:
                val = int(value)
                if 1 <= val <= 100:
                    topk_var.set(val)  # Ensure integer
                    return True
                return False
            except ValueError:
                return False

        def validate_top_p(value):
            try:
                val = float(value)
                if 0 <= val <= 1:
                    topp_var.set(round(val, 2))  # Round the value
                    return True
                return False
            except ValueError:
                return False

        # Add trace callbacks to update display format
        def update_temp_display(*args):
            try:
                val = temp_var.get()
                temp_var.set(round(val, 2))
            except:
                pass

        def update_topk_display(*args):
            try:
                val = topk_var.get()
                topk_var.set(int(val))
            except:
                pass

        def update_topp_display(*args):
            try:
                val = topp_var.get()
                topp_var.set(round(val, 2))
            except:
                pass

        # Register trace callbacks
        temp_var.trace_add("write", update_temp_display)
        topk_var.trace_add("write", update_topk_display)
        topp_var.trace_add("write", update_topp_display)

        # Register validation functions
        temp_validate = dialog.register(validate_temperature)
        topk_validate = dialog.register(validate_top_k)
        topp_validate = dialog.register(validate_top_p)

        # Configure entries with validation
        temp_entry.configure(validate="key", validatecommand=(temp_validate, "%P"))
        topk_entry.configure(validate="key", validatecommand=(topk_validate, "%P"))
        topp_entry.configure(validate="key", validatecommand=(topp_validate, "%P"))

        # Add tooltips for valid ranges
        def create_tooltip(widget, text):
            def show_tooltip(event):
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
                label = ttk.Label(
                    tooltip,
                    text=text,
                    background="#ffffe0",
                    relief="solid",
                    borderwidth=1,
                )
                label.pack()

                def hide_tooltip(event):
                    tooltip.destroy()

                widget.tooltip = tooltip
                widget.bind("<Leave>", hide_tooltip)

            widget.bind("<Enter>", show_tooltip)

        create_tooltip(temp_entry, "Valid range: 0.0 to 1.0")
        create_tooltip(topk_entry, "Valid range: 1 to 100")
        create_tooltip(topp_entry, "Valid range: 0.0 to 1.0")

        # Load current prompt from config
        current_prompt = self.config.get("llm_prompt", "")
        prompt_text.insert("1.0", current_prompt)

        # Add button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=15)

        def save_settings():
            new_prompt = prompt_text.get("1.0", tk.END).strip()
            if new_prompt:
                logger.info("Setting new LLM settings")
                # Save all settings to config
                self.config.set("llm_prompt", new_prompt)
                self.config.set("temperature", round(temp_var.get(), 2))
                self.config.set("top_k", int(topk_var.get()))
                self.config.set("top_p", round(topp_var.get(), 2))
                self.config.set("model", model_var.get())

                # Update environment variables
                os.environ["SUBSPELL_LLM_PROMPT"] = new_prompt
                os.environ["SUBSPELL_TEMPERATURE"] = str(round(temp_var.get(), 2))
                os.environ["SUBSPELL_TOP_K"] = str(int(topk_var.get()))
                os.environ["SUBSPELL_TOP_P"] = str(round(topp_var.get(), 2))
                os.environ["SUBSPELL_MODEL"] = model_var.get()
                
                # Reinitialize spellchecker with new settings
                self.status_var.set("Updating spellchecker with new settings...")
                dialog.configure(cursor="wait")
                button_frame.configure(cursor="wait")
                self.update_idletasks()

                save_btn.configure(state="disabled")
                cancel_btn.configure(state="disabled")

                def update_spellchecker():
                    success = False
                    error_msg = ""

                    try:
                        logger.info("Reinitializing spellchecker with new settings...")
                        self.spellchecker = None
                        success = self.initialize_spellchecker()
                        logger.info(f"Spellchecker update result: {success}")
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"Spellchecker update failed: {str(e)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")

                    self.after(0, lambda: finish_settings_update(success, error_msg))

                def finish_settings_update(success, error_msg):
                    dialog.configure(cursor="")
                    button_frame.configure(cursor="")
                    save_btn.configure(state="normal")
                    cancel_btn.configure(state="normal")

                    if success:
                        self.status_var.set("LLM settings updated successfully")
                        dialog.destroy()
                    else:
                        self.status_var.set("Failed to update LLM settings")
                        messagebox.showerror(
                            "Error",
                            f"Failed to update LLM settings:\n\n{error_msg}\n\n"
                            "See console for detailed traceback.",
                        )

                # Start the update in a separate thread
                threading.Thread(target=update_spellchecker, daemon=True).start()
            else:
                logger.warning("Empty prompt submitted")
                messagebox.showwarning("Warning", "Please enter a valid prompt.")

        save_btn = ModernButton(
            button_frame,
            text="Save",
            command=save_settings,
            style="Modern.TButton"
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ModernButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            style="Modern.TButton"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

def run_gui():
    """Run the SubSpell GUI application."""
    app = ModernSubSpellGUI()
    app.mainloop()

if __name__ == "__main__":
    run_gui()
