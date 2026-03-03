# -*- coding: utf-8 -*-
"""
ScreenRuler Pro - Advanced on-screen measurement tool with text annotation support
Version 2.0.0
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import math
import ctypes
import json
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageTk
import pystray
from threading import Thread

try:
    from ttkthemes import ThemedStyle
except Exception:  # pragma: no cover
    ThemedStyle = None

# --- Windows API Calls for Click-Through Support ---
def set_click_through(hwnd, enable):
    """
    Sets the window to be click-through (ignore mouse events) or not.
    WS_EX_TRANSPARENT = 0x00000020
    GWL_EXSTYLE = -20
    """
    try:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
        if enable:
            new_style = style | 0x00000020
        else:
            new_style = style & ~0x00000020
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, new_style)
        return True
    except Exception:
        return False

class ProRuler:
    def __init__(self, root):
        self.root = root
        self.root.title("ScreenRuler Pro")

        self.style = None
        self.current_theme = "arc"  # default theme
        self._init_style()
        
        # Default Configuration
        self.config = {
            "color_active": "#00FFFF",
            "color_pass": "#FF5555",
            "bg_color": "black",
            "tick_spacing": 20,
            "unit": "in",  # px, um, mm, cm, m, in
            "opacity_work": 0.95,
            "opacity_edit": 1.0,
            "show_guides": True,
            "lock_angle": None,  # None, 0 (horizontal), 90 (vertical)
            "theme": "cyan",  # cyan, green, purple, orange
            "show_fractions": False,
            "fraction_count": 4,
            "ruler_thickness": 4,
            "calibration_factor": 1.0,  # Calibration multiplier
            "show_labels": True,  # Show/hide ruler labels
            "mode": "ruler",  # ruler, fractions, angle, polygon
            "polygon_sides": 4,  # Number of sides for polygon mode
            "toolbar_visible": True,  # Show/hide toolbar
            "endpoint_style": "circle"  # none, circle, square, crosslines, arrow
        }
        
        # Themes
        self.themes = {
            "cyan": {"active": "#00FFFF", "pass": "#FF5555"},
            "green": {"active": "#00FF00", "pass": "#FF8800"},
            "purple": {"active": "#AA00FF", "pass": "#FFAA00"},
            "orange": {"active": "#FF8800", "pass": "#00FFFF"},
            "black": {"active": "#0A0A0A", "pass": "#666666"},
            "white": {"active": "#F5F5F5", "pass": "#CCCCCC"}
        }
        
        # Load saved config
        self.load_config()
        
        # Get virtual screen dimensions first (multi-monitor aware)
        self.root.update_idletasks()
        try:
            # Get virtual screen dimensions using Windows API
            SM_XVIRTUALSCREEN = 76
            SM_YVIRTUALSCREEN = 77
            SM_CXVIRTUALSCREEN = 78
            SM_CYVIRTUALSCREEN = 79
            
            self.virtual_x = int(ctypes.windll.user32.GetSystemMetrics(SM_XVIRTUALSCREEN))
            self.virtual_y = int(ctypes.windll.user32.GetSystemMetrics(SM_YVIRTUALSCREEN))
            self.virtual_w = int(ctypes.windll.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN))
            self.virtual_h = int(ctypes.windll.user32.GetSystemMetrics(SM_CYVIRTUALSCREEN))
        except Exception:
            # Fallback to single screen if Windows API fails
            self.virtual_x = 0
            self.virtual_y = 0
            self.virtual_w = int(self.root.winfo_screenwidth())
            self.virtual_h = int(self.root.winfo_screenheight())

        # Keep legacy names used across the code
        self.screen_width = self.virtual_w
        self.screen_height = self.virtual_h
        
        # State - Initialize at center of virtual screen (not absolute center)
        center_x = self.virtual_x + (self.virtual_w / 2)
        center_y = self.virtual_y + (self.virtual_h / 2)
        self.p1 = {"x": center_x - 350, "y": center_y}
        self.p2 = {"x": center_x + 350, "y": center_y}
        self.dragging = None
        self.minimized = False
        self.toolbar_minimized = False  # Track toolbar minimize state separately
        self.is_passthrough = False  # Start in Edit mode by default
        self.show_help = False
        self.show_settings = False
        self.measurement_history = []
        self.tray_icon = None
        self.control_panel = None  # Unified control panel window
        self.inline_notification = None  # Temporary notification text shown in toolbar

        # Polygon mode state
        self.polygon_points = []  # List of dicts: {"x": float, "y": float}
        self.polygon_dragging_index = None
        self.polygon_move_origin = None
        
        # Angle mode state - Initialize at center
        self.angle_center = {"x": center_x, "y": center_y}
        self.angle_arm1 = {"x": center_x - 200, "y": center_y}  # First arm endpoint
        self.angle_arm2 = {"x": center_x, "y": center_y - 200}  # Second arm endpoint
        self.angle_length = 200  # Length of each arm
        
        # Text mode state
        self.text_objects = []  # List of text objects: {"x": x, "y": y, "text": str, "width": w, "height": h, ...}
        self.text_mode_active = False
        self.text_visible = True  # Show/hide all text objects
        self.text_dragging_index = None
        self.text_resizing_index = None
        self.text_resize_handle = None  # Which corner: 'nw', 'ne', 'sw', 'se'
        self.selected_text_index = None  # Track selected text object for deletion
        self.text_input_var = tk.StringVar(value="Your text here")
        self.text_font_family = "Arial"
        self.text_font_size = 24
        self.text_bold = False
        self.text_italic = False
        self.text_underline = False
        self.text_outline = False
        
        # Toolbar state
        self.toolbar = None
        self.toolbar_frame = None
        self.toolbar_height = 90
        self.fraction_input = None
        self.polygon_input = None
        self.mode_buttons = {}
        self.menu_buttons = {}
        self.lock_status_var = tk.StringVar(value="None")
        
        # Visibility state for each mode
        self.mode_visible = {
            "ruler": True,
            "fractions": True,
            "angle": True,
            "polygon": True
        }
        
        # Initialize control variables
        self.unit_var = tk.StringVar(value=self.config["unit"])
        self.theme_var = tk.StringVar(value=self.config.get("theme", "cyan"))
        self.lock_label = None  # Will be set if created in UI
        
        # Setup Window geometry (cover the whole virtual desktop)
        self.root.geometry(f"{self.virtual_w}x{self.virtual_h}+{self.virtual_x}+{self.virtual_y}")
        
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        # Create toolbar frame first
        self.create_toolbar()
        
        # Canvas
        self.canvas = tk.Canvas(root, width=self.screen_width, height=self.screen_height,
                                bg=self.config["bg_color"], highlightthickness=0)
        self.canvas.pack()
        
        # Transparency
        self.root.wm_attributes('-transparentcolor', self.config["bg_color"])
        self.root.attributes('-alpha', self.config["opacity_edit"])  # Start with Edit mode opacity
        
        # Bind Events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
        # Keyboard Shortcuts
        self.root.bind("<space>", self.toggle_minimize)
        self.root.bind("<Escape>", self.close_app)
        self.root.bind("<p>", self.toggle_passthrough)
        self.root.bind("<P>", self.toggle_passthrough)
        self.root.bind("<r>", self.reset_ruler)
        self.root.bind("<R>", self.reset_ruler)
        self.root.bind("<h>", self.toggle_help)
        self.root.bind("<H>", self.toggle_help)
        self.root.bind("<s>", self.toggle_settings)
        self.root.bind("<S>", self.toggle_settings)
        self.root.bind("<c>", self.copy_measurement)
        self.root.bind("<C>", self.copy_measurement)
        self.root.bind("<g>", self.toggle_guides)
        self.root.bind("<G>", self.toggle_guides)
        self.root.bind("<l>", self.cycle_lock)
        self.root.bind("<L>", self.cycle_lock)
        self.root.bind("<t>", self.cycle_theme)
        self.root.bind("<T>", self.cycle_theme)
        self.root.bind("<u>", self.cycle_unit)
        self.root.bind("<U>", self.cycle_unit)
        self.root.bind("<plus>", self.increase_opacity)
        self.root.bind("<minus>", self.decrease_opacity)
        self.root.bind("<f>", self.toggle_fractions)
        self.root.bind("<F>", self.toggle_fractions)
        self.root.bind("<bracketleft>", self.decrease_fractions)
        self.root.bind("<bracketright>", self.increase_fractions)
        self.root.bind("<a>", self.show_about)
        self.root.bind("<A>", self.show_about)
        self.root.bind("<period>", self.increase_thickness)
        self.root.bind("<comma>", self.decrease_thickness)
        self.root.bind("<v>", self.toggle_labels)
        self.root.bind("<V>", self.toggle_labels)
        self.root.bind("<m>", self.cycle_mode)
        self.root.bind("<M>", self.cycle_mode)
        self.root.bind("<e>", self.cycle_endpoint_style)
        self.root.bind("<E>", self.cycle_endpoint_style)
        self.root.bind("<Delete>", self.delete_text_object)
        self.root.bind("<BackSpace>", self.delete_text_object)
        self.root.bind("<b>", self.minimize_toolbar_only)
        self.root.bind("<B>", self.minimize_toolbar_only)
        
        # Start in Edit mode by default (click-through disabled)
        hwnd = self.root.winfo_id()
        set_click_through(hwnd, False)
        
        # Setup tray icon
        self.setup_tray_icon()
        
        # Initial Draw
        self.draw()
        self.show_welcome()
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            try:
                # Create tooltip window
                tooltip = tk.Toplevel(widget)
                tooltip.wm_overrideredirect(True)
                tooltip.wm_attributes('-topmost', True)
                
                # Position tooltip below the widget
                x = widget.winfo_rootx() + widget.winfo_width() // 2
                y = widget.winfo_rooty() + widget.winfo_height() + 5
                tooltip.wm_geometry(f"+{x}+{y}")
                
                # Create label with text
                label = tk.Label(
                    tooltip,
                    text=text,
                    background="#ffffcc",
                    foreground="#000000",
                    relief=tk.SOLID,
                    borderwidth=1,
                    font=('Segoe UI', 9),
                    padx=6,
                    pady=4
                )
                label.pack()
                
                # Store tooltip reference
                widget.tooltip_window = tooltip
            except Exception:
                pass
        
        def on_leave(event):
            try:
                # Destroy tooltip window
                if hasattr(widget, 'tooltip_window'):
                    widget.tooltip_window.destroy()
                    del widget.tooltip_window
            except Exception:
                pass
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def create_toolbar(self):
        """Create toolbar UI with standard Windows title bar."""
        # Create a top-level window for toolbar
        self.toolbar = tk.Toplevel(self.root)
        self.toolbar.title("ScreenRuler Pro")
        self.toolbar.attributes('-topmost', True)
        self.toolbar.attributes('-alpha', 0.95)
        
        # Close entire app when toolbar is closed
        self.toolbar.protocol("WM_DELETE_WINDOW", self.close_app)
        
        # Position at top center of the virtual desktop (multi-monitor)
        # Compact toolbar size for better screen real estate
        toolbar_width = min(490, max(490, self.virtual_w - 100))
        toolbar_height = 128  # Reduced height since no custom title bar
        toolbar_x = int(self.virtual_x + (self.virtual_w - toolbar_width) // 2)
        toolbar_y = int(self.virtual_y + 20)
        self.toolbar.geometry(f"{toolbar_width}x{toolbar_height}+{toolbar_x}+{toolbar_y}")

        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'Icon.ico')
            if os.path.exists(icon_path):
                self.toolbar.iconbitmap(icon_path)
        except Exception:
            pass

        # Allow resizing
        self.toolbar.minsize(420, 110)
        
        # Main frame (no custom title bar needed)
        self.toolbar_frame = tk.Frame(self.toolbar, bg='#f5f6f7', relief=tk.RAISED, bd=2)
        self.toolbar_frame.pack(fill='both', expand=True)
        
        # ===== MENU BAR =====
        menubar_frame = tk.Frame(self.toolbar_frame, bg='#e7e8eb', height=28)
        menubar_frame.pack(fill='x')
        menubar_frame.pack_propagate(False)
        
        # Menu buttons
        self.menu_buttons = {}
        self.menu_buttons["File"] = self.create_menu_button(menubar_frame, "File", self.show_file_menu)
        self.menu_buttons["Edit"] = self.create_menu_button(menubar_frame, "Edit", self.show_edit_menu)
        self.menu_buttons["View"] = self.create_menu_button(menubar_frame, "View", self.show_view_menu)
        self.menu_buttons["Help"] = self.create_menu_button(menubar_frame, "Help", self.show_help_menu)
        
        # ===== TOOLBAR (ICON ROW) =====
        body_frame = tk.Frame(self.toolbar_frame, bg='#f5f6f7')
        body_frame.pack(fill='x', padx=8, pady=(6, 4))

        icon_row = tk.Frame(body_frame, bg='#f5f6f7')
        icon_row.pack(fill='x')

        self.mode_buttons = {}

        def tool_btn(text, command, is_toggle=False):
            # Square tile wrapper to enforce 1:1 aspect
            tile = tk.Frame(icon_row, bg='#d3dae3', bd=1, relief=tk.RAISED, width=38, height=38)
            tile.pack(side='left', padx=2, pady=2)
            tile.pack_propagate(False)

            btn = tk.Button(
                tile,
                text=text,
                command=command,
                font=('Segoe UI', 11, 'bold') if len(text) <= 2 else ('Segoe UI', 9, 'bold'),
                bg='#fbfbfc',
                fg='#5c616c',
                activebackground='#d3dae3',
                relief=tk.FLAT,
                bd=0,
                cursor='hand2',
                highlightthickness=0,
            )
            btn.pack(fill='both', expand=True)
            return btn

        # Mode buttons (square)
        self.mode_buttons["ruler"] = tool_btn("📏", lambda: self.toggle_mode_visibility("ruler"))
        self.create_tooltip(self.mode_buttons["ruler"], "Ruler Mode (M) - Click to toggle visibility")
        
        self.mode_buttons["fractions"] = tool_btn("¼", lambda: self.toggle_mode_visibility("fractions"))
        self.create_tooltip(self.mode_buttons["fractions"], "Fractions Mode (M) - Click to toggle visibility")
        
        self.mode_buttons["angle"] = tool_btn("∠", lambda: self.toggle_mode_visibility("angle"))
        self.create_tooltip(self.mode_buttons["angle"], "Angle Mode (M) - Click to toggle visibility")
        
        self.mode_buttons["polygon"] = tool_btn("⬟", lambda: self.toggle_mode_visibility("polygon"))
        self.create_tooltip(self.mode_buttons["polygon"], "Polygon Mode (M) - Click to toggle visibility")
        
        self.mode_buttons["text"] = tool_btn("A", lambda: self.toggle_text_mode())
        self.create_tooltip(self.mode_buttons["text"], "Text Mode - Add onscreen text")

        # Numeric box (fractions/polygon sides) styled like a tool tile
        number_tile = tk.Frame(icon_row, bg='#d3dae3', bd=1, relief=tk.RAISED, width=70, height=38)
        number_tile.pack(side='left', padx=2, pady=2)
        number_tile.pack_propagate(False)
        
        # Inner frame with white background to match other buttons
        number_inner = tk.Frame(number_tile, bg='#fbfbfc')
        number_inner.pack(fill='both', expand=True)

        self.number_label = tk.Label(number_inner, text="", font=('Segoe UI', 7, 'bold'), bg='#fbfbfc', fg='#5c616c')
        self.number_label.pack(anchor='w', padx=4, pady=(2, 0))

        self.number_input = tk.Spinbox(
            number_inner,
            from_=2,
            to=50,
            width=5,
            font=('Segoe UI', 9, 'bold'),
            justify='center',
            command=self.update_number_input,
        )
        self.number_input.pack(expand=True, fill='both')
        self.number_input.config(bg='#fbfbfc', fg='#5c616c', buttonbackground='#fbfbfc', insertbackground='#5c616c', relief=tk.FLAT)
        self.number_input.bind('<Return>', lambda e: self.update_number_input())
        self.number_input.bind('<FocusOut>', lambda e: self.update_number_input())

        # Lock button with icon showing state
        self.lock_button = tool_btn("🔓", self.cycle_lock)
        self.create_tooltip(self.lock_button, "Cycle Lock: None/Horizontal/Vertical (L)")
        
        # Unit dropdown (similar to number input)
        unit_tile = tk.Frame(icon_row, bg='#d3dae3', bd=1, relief=tk.RAISED, width=55, height=38)
        unit_tile.pack(side='left', padx=2, pady=2)
        unit_tile.pack_propagate(False)
        
        # Inner frame with white background to match other buttons
        unit_inner = tk.Frame(unit_tile, bg='#fbfbfc')
        unit_inner.pack(fill='both', expand=True)
        
        tk.Label(unit_inner, text="Unit", font=('Segoe UI', 7, 'bold'), bg='#fbfbfc', fg='#5c616c').pack(anchor='w', padx=4, pady=(2, 0))
        
        self.unit_dropdown = ttk.Combobox(
            unit_inner,
            values=['px', 'um', 'mm', 'cm', 'm', 'in'],
            width=4,
            font=('Segoe UI', 9, 'bold'),
            state='readonly',
            justify='center',
            style="Toolbar.TCombobox",
        )
        self.unit_dropdown.pack(expand=True)
        self.unit_dropdown.set(self.config.get('unit', 'px'))
        self.unit_dropdown.bind('<<ComboboxSelected>>', self.on_unit_dropdown_changed)
        
        # Edit/Work mode toggle button
        self.mode_toggle_button = tool_btn("E", self.toggle_passthrough)
        self.create_tooltip(self.mode_toggle_button, "Toggle Edit/Work Mode (P)")
        
        # Settings
        settings_btn = tool_btn("⚙", self.toggle_settings)
        self.create_tooltip(settings_btn, "Open Settings (S)")
        
        # ===== TEXT INPUT AND FORMATTING TOOLBAR (shown when text mode active) =====
        self.text_toolbar_frame = tk.Frame(body_frame, bg='#f5f6f7')
        # Initially hidden, will be packed when text mode is activated
        
        # Text input field
        text_input_frame = tk.Frame(self.text_toolbar_frame, bg='#d3dae3', bd=1, relief=tk.RAISED)
        text_input_frame.pack(fill='x', padx=2, pady=(4, 2))
        
        tk.Label(text_input_frame, text="Text:", font=('Segoe UI', 8, 'bold'), bg='#fbfbfc', fg='#5c616c').pack(side='left', padx=(4, 2))
        
        self.text_input_entry = tk.Entry(
            text_input_frame,
            textvariable=self.text_input_var,
            font=('Segoe UI', 10),
            bg='#fbfbfc',
            fg='#5c616c',
            relief=tk.FLAT,
            insertbackground='#5c616c'
        )
        self.text_input_entry.pack(side='left', fill='x', expand=True, padx=4, pady=4)
        self.text_input_entry.bind('<Return>', lambda e: self.add_text_object())
        
        add_text_btn = tk.Button(
            text_input_frame,
            text="Add",
            command=self.add_text_object,
            font=('Segoe UI', 9, 'bold'),
            bg='#5294e2',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=8,
            bd=0
        )
        add_text_btn.pack(side='right', padx=4, pady=4)
        
        # Text formatting icons row
        text_format_row = tk.Frame(self.text_toolbar_frame, bg='#f5f6f7')
        text_format_row.pack(fill='x', pady=(0, 2))
        
        def text_tool_btn(text, command, tooltip_text):
            tile = tk.Frame(text_format_row, bg='#d3dae3', bd=1, relief=tk.RAISED, width=35, height=35)
            tile.pack(side='left', padx=2, pady=2)
            tile.pack_propagate(False)
            
            btn = tk.Button(
                tile,
                text=text,
                command=command,
                font=('Segoe UI', 10, 'bold') if len(text) <= 2 else ('Segoe UI', 9, 'bold'),
                bg='#fbfbfc',
                fg='#5c616c',
                activebackground='#d3dae3',
                relief=tk.FLAT,
                bd=0,
                cursor='hand2',
                highlightthickness=0,
            )
            btn.pack(fill='both', expand=True)
            self.create_tooltip(btn, tooltip_text)
            return btn
        
        # Font size controls
        tk.Label(text_format_row, text="Size:", font=('Segoe UI', 8, 'bold'), bg='#f5f6f7', fg='#5c616c').pack(side='left', padx=(4, 2))
        
        self.font_size_spinbox = tk.Spinbox(
            text_format_row,
            from_=8,
            to=200,
            width=4,
            font=('Segoe UI', 9),
            command=self.update_text_font_size,
            bg='#fbfbfc',
            fg='#5c616c',
            buttonbackground='#fbfbfc',
            insertbackground='#5c616c',
            relief=tk.FLAT
        )
        self.font_size_spinbox.delete(0, 'end')
        self.font_size_spinbox.insert(0, str(self.text_font_size))
        self.font_size_spinbox.pack(side='left', padx=2)
        self.font_size_spinbox.bind('<Return>', lambda e: self.update_text_font_size())
        
        # Font family dropdown
        tk.Label(text_format_row, text="Font:", font=('Segoe UI', 8, 'bold'), bg='#f5f6f7', fg='#5c616c').pack(side='left', padx=(8, 2))
        
        self.font_family_dropdown = ttk.Combobox(
            text_format_row,
            values=['Arial', 'Times New Roman', 'Courier New', 'Comic Sans MS', 'Verdana', 'Georgia', 'Tahoma', 'Trebuchet MS', 'Impact', 'Calibri'],
            width=12,
            font=('Segoe UI', 9),
            state='readonly',
            style="Toolbar.TCombobox",
        )
        self.font_family_dropdown.set(self.text_font_family)
        self.font_family_dropdown.pack(side='left', padx=2)
        self.font_family_dropdown.bind('<<ComboboxSelected>>', self.update_text_font_family)
        
        # Bold, Italic, Underline buttons with styled text
        def text_style_btn(text, command, tooltip_text, font_style):
            tile = tk.Frame(text_format_row, bg='#d3dae3', bd=1, relief=tk.RAISED, width=35, height=35)
            tile.pack(side='left', padx=2, pady=2)
            tile.pack_propagate(False)
            
            btn = tk.Button(
                tile,
                text=text,
                command=command,
                font=font_style,
                bg='#fbfbfc',
                fg='#5c616c',
                activebackground='#d3dae3',
                relief=tk.FLAT,
                bd=0,
                cursor='hand2',
                highlightthickness=0,
            )
            btn.pack(fill='both', expand=True)
            self.create_tooltip(btn, tooltip_text)
            return btn
        
        self.bold_btn = text_style_btn("B", self.toggle_bold, "Bold", ('Segoe UI', 10, 'bold'))
        self.italic_btn = text_style_btn("I", self.toggle_italic, "Italic", ('Segoe UI', 10, 'italic'))
        self.underline_btn = text_style_btn("U", self.toggle_underline, "Underline", ('Segoe UI', 10, 'underline'))
        
        # Outline toggle
        self.outline_btn = text_tool_btn("□", self.toggle_outline, "Text Box Outline")
        
        # Clear text button
        self.clear_text_btn = text_tool_btn("🗑", self.clear_all_text_objects, "Clear All Text")
        
        # Show/Hide text button (eye icon)
        self.text_visibility_btn = text_tool_btn("👁", self.toggle_text_visibility, "Show/Hide Text")

        # ===== MEASUREMENT BANNER =====
        banner = tk.Frame(self.toolbar_frame, bg='#d3dae3', bd=1, relief=tk.SUNKEN)
        banner.pack(fill='both', expand=True, padx=8, pady=(0, 8))

        self.measurement_value_label = tk.Label(
            banner,
            text="—",
            font=('Segoe UI', 13, 'normal'),
            bg='#d3dae3',
            fg='#5c616c',
            anchor='center',
        )
        self.measurement_value_label.pack(fill='both', expand=True, padx=8, pady=4)

        # Initialize stateful widgets
        self.update_lock_button()
        self._sync_number_tile_for_mode()
        self._update_mode_button_highlights()
        self.update_mode_display()
        
        # Sync unit dropdown with config
        if hasattr(self, 'unit_dropdown'):
            self.unit_dropdown.set(self.config.get('unit', 'px'))
        
        # Set initial mode toggle button colors
        if hasattr(self, 'mode_toggle_button'):
            if self.is_passthrough:
                self.mode_toggle_button.config(bg='#f8d0d0', fg='#c0392b', text='W')
            else:
                self.mode_toggle_button.config(bg='#d4edda', fg='#155724', text='E')
    
    def start_move_toolbar(self, event):
        """Start moving the toolbar window"""
        self.toolbar_x = event.x
        self.toolbar_y = event.y
    
    def do_move_toolbar(self, event):
        """Move the toolbar window"""
        if not self.toolbar or not self.toolbar.winfo_exists():
            return
        try:
            deltax = event.x - self.toolbar_x
            deltay = event.y - self.toolbar_y
            x = self.toolbar.winfo_x() + deltax
            y = self.toolbar.winfo_y() + deltay
            
            # Keep the toolbar inside the virtual desktop bounds with padding
            toolbar_width = self.toolbar.winfo_width()
            toolbar_height = self.toolbar.winfo_height()
            
            max_x = int(self.virtual_x + self.virtual_w - toolbar_width)
            max_y = int(self.virtual_y + self.virtual_h - toolbar_height)
            min_x = int(self.virtual_x)
            min_y = int(self.virtual_y)
            
            x = min(max(min_x, x), max_x)
            y = min(max(min_y, y), max_y)
            
            self.toolbar.geometry(f"+{x}+{y}")
        except Exception as e:
            print(f"Warning: Could not move toolbar: {e}")

    def create_menu_button(self, parent, text, command):
        """Create a menu bar button"""
        btn = tk.Button(
            parent,
            text=text,
            font=('Segoe UI', 11, 'normal'),
            bg='#e7e8eb',
            fg='#5c616c',
            relief=tk.FLAT,
            cursor='hand2',
            command=lambda b=text: command(b),
            padx=8,
            pady=1,
            bd=0,
            activebackground='#d3dae3',
        )
        btn.pack(side='left', padx=2)
        return btn
    
    def _update_mode_button_highlights(self):
        """Highlight the active mode button in the toolbar."""
        if not getattr(self, 'mode_buttons', None):
            return

        active = self.config.get("mode", "ruler")
        for mode, btn in self.mode_buttons.items():
            # Skip text button - it's handled separately
            if mode == "text":
                continue
                
            try:
                if not btn or not btn.winfo_exists():
                    continue
                    
                # Check if this mode is visible
                is_visible = self.mode_visible.get(mode, True)
                is_active = (mode == active)
                
                if is_active and is_visible:
                    # Active and visible: blue highlight
                    btn.config(bg='#5294e2', fg='white', relief=tk.FLAT, bd=0)
                elif not is_visible:
                    # Hidden: dimmed gray
                    btn.config(bg='#d3dae3', fg='#a0a0a0', relief=tk.FLAT, bd=0)
                else:
                    # Inactive but visible: standard appearance
                    btn.config(bg='#fbfbfc', fg='#5c616c', relief=tk.FLAT, bd=0)
            except tk.TclError:
                # Widget no longer exists
                continue
            except Exception as e:
                print(f"Warning: Could not update mode button {mode}: {e}")
                continue

    def _sync_number_tile_for_mode(self):
        """Update the number tile label/range/value for fractions/polygon."""
        try:
            if not hasattr(self, 'number_label') or not hasattr(self, 'number_input'):
                return
            
            if not self.number_label.winfo_exists() or not self.number_input.winfo_exists():
                return

            mode = self.config.get("mode", "ruler")
            if mode == "fractions":
                self.number_label.config(text="Fractions")
                self.number_input.config(from_=2, to=50)
                self.number_input.delete(0, 'end')
                self.number_input.insert(0, str(self.config.get("fraction_count", 4)))
            elif mode == "polygon":
                self.number_label.config(text="Sides")
                self.number_input.config(from_=3, to=20)
                self.number_input.delete(0, 'end')
                self.number_input.insert(0, str(self.config.get("polygon_sides", 4)))
            else:
                self.number_label.config(text="")
                # Keep the control available but neutral
                self.number_input.config(from_=2, to=50)
                self.number_input.delete(0, 'end')
                self.number_input.insert(0, "")
        except tk.TclError:
            # Widget no longer exists
            pass
        except Exception as e:
            print(f"Warning: Could not sync number tile: {e}")
    
    def _popup_menu(self, menu: tk.Menu, anchor_widget: tk.Widget | None):
        """Popup menu at the bottom-left of the anchor widget."""
        try:
            if anchor_widget is not None and anchor_widget.winfo_exists():
                x = anchor_widget.winfo_rootx()
                y = anchor_widget.winfo_rooty() + anchor_widget.winfo_height()
            elif self.toolbar_frame and self.toolbar_frame.winfo_exists():
                x = self.toolbar_frame.winfo_rootx() + 10
                y = self.toolbar_frame.winfo_rooty() + 55
            else:
                # Fallback to screen center if toolbar_frame doesn't exist
                x = self.root.winfo_screenwidth() // 2
                y = self.root.winfo_screenheight() // 2
            menu.tk_popup(x, y)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass

    def _init_style(self):
        """Initialize ttk/ttkthemes style and apply default theme with toolbar tweaks."""
        try:
            if ThemedStyle:
                self.style = ThemedStyle(self.root)
                self.style.set_theme(self.current_theme)
            else:
                self.style = ttk.Style(self.root)
                try:
                    self.style.theme_use(self.current_theme)
                except Exception:
                    pass
        except Exception as e:
            print(f"Warning: Could not apply {self.current_theme} theme: {e}")
            self.style = ttk.Style(self.root)

        self._configure_toolbar_styles()

    def apply_theme(self, theme_name: str):
        """Switch ttk/ttkthemes theme at runtime."""
        prev_theme = self.current_theme
        self.current_theme = theme_name
        try:
            if hasattr(self, "style") and self.style:
                if hasattr(self.style, "set_theme"):
                    # Use getattr to avoid type checker errors with ThemedStyle
                    getattr(self.style, "set_theme")(theme_name)
                else:
                    self.style.theme_use(theme_name)
            self._configure_toolbar_styles()
            if hasattr(self, "theme_var") and self.theme_var:
                self.theme_var.set(theme_name)
        except Exception as e:
            print(f"Warning: Could not switch theme to {theme_name}: {e}")
            # Revert if failed
            self.current_theme = prev_theme
            try:
                if hasattr(self, "style") and self.style:
                    if hasattr(self.style, "set_theme"):
                        # Use getattr to avoid type checker errors with ThemedStyle
                        getattr(self.style, "set_theme")(prev_theme)
                    else:
                        self.style.theme_use(prev_theme)
                if hasattr(self, "theme_var") and self.theme_var:
                    self.theme_var.set(prev_theme)
            except Exception:
                pass

    def _configure_toolbar_styles(self):
        """Configure toolbar-specific ttk styles."""
        if not self.style:
            return
        try:
            self.style.configure(
                "Toolbar.TCombobox",
                fieldbackground="#fbfbfc",
                background="#fbfbfc",
                foreground="#5c616c",
                arrowcolor="#5c616c",
                bordercolor="#d3dae3",
            )
            self.style.map(
                "Toolbar.TCombobox",
                fieldbackground=[("readonly", "#fbfbfc")],
                foreground=[("readonly", "#5c616c")],
                background=[("readonly", "#fbfbfc")],
                bordercolor=[("readonly", "#d3dae3")],
            )
        except Exception:
            pass

    def _make_menu(self, parent):
        """Create a light-themed menu consistent with Arc theme."""
        return tk.Menu(
            parent,
            tearoff=0,
            bg="#fbfbfc",
            fg="#5c616c",
            activebackground="#5294e2",
            activeforeground="white",
            disabledforeground="#b4b8bf",
            bd=1,
            relief=tk.FLAT,
        )

    def show_file_menu(self, anchor_name=None):
        """Show File menu"""
        menu = self._make_menu(self.toolbar_frame)
        menu.add_command(label="Copy Measurements (C)", command=self.copy_measurement)
        menu.add_separator()
        menu.add_command(label="Minimize to Tray", command=self.minimize_to_tray)
        menu.add_separator()
        menu.add_command(label="Exit (Esc)", command=self.close_app)

        anchor = self.menu_buttons.get("File") if getattr(self, 'menu_buttons', None) else None
        self._popup_menu(menu, anchor)
    
    def show_edit_menu(self, anchor_name=None):
        """Show Edit menu"""
        menu = self._make_menu(self.toolbar_frame)
        
        # Mode submenu
        mode_menu = self._make_menu(menu)
        current_mode = "Work" if self.is_passthrough else "Edit"
        mode_menu.add_command(label=f"→ {current_mode}", state=tk.DISABLED)
        mode_menu.add_separator()
        mode_menu.add_command(label="Work Mode", command=lambda: self.set_passthrough_mode(True))
        mode_menu.add_command(label="Edit Mode", command=lambda: self.set_passthrough_mode(False))
        menu.add_cascade(label="Mode (P)", menu=mode_menu)
        
        # Unit submenu
        unit_menu = self._make_menu(menu)
        unit_menu.add_command(label=f"→ {self.config['unit']}", state=tk.DISABLED)
        unit_menu.add_separator()
        for unit in ['px', 'um', 'mm', 'cm', 'm', 'in']:
            unit_menu.add_command(label=unit, command=lambda u=unit: self.set_unit(u))
        menu.add_cascade(label="Unit (U)", menu=unit_menu)
        
        menu.add_command(label="Calibration", command=self.show_calibration_dialog)
        
        # Cycle Lock submenu
        lock_menu = self._make_menu(menu)
        lock_status = "None" if self.config["lock_angle"] is None else ("Horizontal" if self.config["lock_angle"] == 0 else "Vertical")
        lock_menu.add_command(label=f"→ {lock_status}", state=tk.DISABLED)
        lock_menu.add_separator()
        lock_menu.add_command(label="None", command=lambda: self.set_lock(None))
        lock_menu.add_command(label="Horizontal", command=lambda: self.set_lock(0))
        lock_menu.add_command(label="Vertical", command=lambda: self.set_lock(90))
        menu.add_cascade(label="Cycle Lock (L)", menu=lock_menu)
        
        # Theme submenu
        theme_menu = self._make_menu(menu)
        theme_menu.add_command(label=f"→ {self.config['theme'].capitalize()}", state=tk.DISABLED)
        theme_menu.add_separator()
        for theme in ['cyan', 'green', 'purple', 'orange', 'black', 'white']:
            theme_menu.add_command(label=theme.capitalize(), command=lambda t=theme: self.set_theme(t))
        menu.add_cascade(label="Cycle Themes (T)", menu=theme_menu)
        
        menu.add_command(label="Reset Ruler Position (R)", command=self.reset_ruler)
        menu.add_separator()
        menu.add_command(label="Preferences/Settings (S)", command=self.toggle_settings)
        
        anchor = self.menu_buttons.get("Edit") if getattr(self, 'menu_buttons', None) else None
        self._popup_menu(menu, anchor)
    
    def show_view_menu(self, anchor_name=None):
        """Show View menu"""
        menu = self._make_menu(self.toolbar_frame)
        
        guides_status = "✓" if self.config["show_guides"] else " "
        menu.add_command(label=f"{guides_status} Guide Lines (G)", command=self.toggle_guides)
        
        labels_status = "✓" if self.config["show_labels"] else " "
        menu.add_command(label=f"{labels_status} Ruler Labels (V)", command=self.toggle_labels)
        
        menu.add_separator()
        
        # Text mode
        text_mode_status = "✓" if self.text_mode_active else " "
        menu.add_command(label=f"{text_mode_status} Text Mode", command=self.toggle_text_mode)
        
        # Screen Text visibility (always show, regardless of whether text objects exist)
        screen_text_status = "✓" if self.text_visible else " "
        menu.add_command(label=f"{screen_text_status} Screen Text", command=self.toggle_text_visibility)
        
        # Clear text option (only show if text objects exist)
        if self.text_objects:
            menu.add_command(label="Clear All Text", command=self.clear_all_text_objects)
        
        menu.add_separator()
        
        # Ruler Ends submenu
        ends_menu = self._make_menu(menu)
        current_style = self.config.get("endpoint_style", "circle").capitalize()
        ends_menu.add_command(label=f"→ {current_style}", state=tk.DISABLED)
        ends_menu.add_separator()
        endpoint_styles = [
            ("None", "none"),
            ("Circle", "circle"),
            ("Square", "flat"),
            ("Crosslines", "crosslines"),
            ("Arrow", "arrow")
        ]
        for label, value in endpoint_styles:
            ends_menu.add_command(label=label, command=lambda v=value: self.set_endpoint_style(v))
        menu.add_cascade(label="Ruler Ends", menu=ends_menu)
        
        anchor = self.menu_buttons.get("View") if getattr(self, 'menu_buttons', None) else None
        self._popup_menu(menu, anchor)
    
    def show_help_menu(self, anchor_name=None):
        """Show Help menu"""
        menu = self._make_menu(self.toolbar_frame)
        menu.add_command(label="Help (H)", command=self.toggle_help)
        menu.add_separator()
        menu.add_command(label="About (A)", command=self.show_about)

        anchor = self.menu_buttons.get("Help") if getattr(self, 'menu_buttons', None) else None
        self._popup_menu(menu, anchor)

    def show_unit_menu(self):
        """Popup a unit selection menu (triggered by the globe button)."""
        menu = self._make_menu(self.toolbar_frame)
        menu.add_command(label=f"→ {self.config.get('unit', 'px').upper()}", state=tk.DISABLED)
        menu.add_separator()
        for unit in ['px', 'um', 'mm', 'cm', 'm', 'in']:
            menu.add_command(label=unit.upper(), command=lambda u=unit: self.set_unit(u))

        # Popup at current mouse position
        try:
            if not self.toolbar or not self.toolbar.winfo_exists():
                return
            x = self.toolbar.winfo_pointerx()
            y = self.toolbar.winfo_pointery()
            menu.tk_popup(x, y)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
    
    def set_passthrough_mode(self, enable):
        """Set passthrough mode (Work=True, Edit=False)"""
        self.is_passthrough = enable
        hwnd = self.root.winfo_id()
        set_click_through(hwnd, enable)
        
        if enable:
            self.root.attributes('-alpha', self.config["opacity_work"])
        else:
            self.root.attributes('-alpha', self.config["opacity_edit"])
        
        # Ensure windows remain visible
        self.ensure_windows_visible()
        
        self.update_mode_display()
        self.draw()
    
    def set_unit(self, unit):
        """Set measurement unit and update all related UI elements"""
        normalized = self.normalize_unit(unit)
        self.config["unit"] = normalized
        
        # Update dropdown to match
        if hasattr(self, 'unit_dropdown'):
            try:
                if self.unit_dropdown.winfo_exists():
                    self.unit_dropdown.set(normalized)
            except tk.TclError:
                pass
        
        # Update unit_var
        if self.unit_var:
            self.unit_var.set(normalized)
        
        # Update calibration unit labels if they exist
        if hasattr(self, 'calibration_unit_labels'):
            for label in self.calibration_unit_labels:
                try:
                    if label.winfo_exists():
                        label.config(text=normalized)
                except Exception:
                    pass
        
        self.save_config()
        self.draw()
    
    def set_lock(self, angle):
        """Set lock angle (None, 0=horizontal, 90=vertical)"""
        self.config["lock_angle"] = angle
        self.save_config()
        self.update_lock_button()
        self.draw()
    
    def set_theme(self, theme):
        """Set color theme"""
        self.config["theme"] = theme
        if theme in self.themes:
            self.config["color_active"] = self.themes[theme]["active"]
            self.config["color_pass"] = self.themes[theme]["pass"]
        self.save_config()
        self.draw()
    
    def set_endpoint_style(self, style):
        """Set ruler endpoint style"""
        self.config["endpoint_style"] = style
        self.save_config()
        self.draw()
    
    def on_unit_selected(self, event=None):
        """Handle unit selection from dropdown"""
        if not self.unit_var:
            return
        self.config["unit"] = self.normalize_unit(self.unit_var.get())
        self.unit_var.set(self.config["unit"])
        self.save_config()
        self.draw()
    
    def on_unit_dropdown_changed(self, event=None):
        """Handle unit dropdown selection change"""
        try:
            if hasattr(self, 'unit_dropdown'):
                selected = self.unit_dropdown.get().lower()
                self.config["unit"] = self.normalize_unit(selected)
                self.save_config()
                self.draw()
        except Exception as e:
            print(f"Warning: Could not change unit: {e}")
    
    def update_number_input(self):
        """Update fraction count or polygon sides based on current mode"""
        try:
            if not hasattr(self, 'number_input') or not self.number_input.winfo_exists():
                return
                
            value = int(self.number_input.get())
            if self.config["mode"] == "fractions":
                if 2 <= value <= 50:
                    self.config["fraction_count"] = value
                    self.save_config()
                    self.draw()
            elif self.config["mode"] == "polygon":
                if 3 <= value <= 20:
                    self.config["polygon_sides"] = value
                    self.init_polygon_with_sides(value)
                    self.save_config()
                    self.draw()
        except ValueError:
            # Invalid number input
            pass
        except tk.TclError:
            # Widget no longer exists
            pass
        except Exception as e:
            print(f"Warning: Could not update number input: {e}")
    
    def update_mode_display(self):
        """Update the mode toggle button display"""
        try:
            # Update mode toggle button with better visual feedback
            if hasattr(self, 'mode_toggle_button') and self.mode_toggle_button.winfo_exists():
                if self.is_passthrough:
                    # Work mode - light red background, bold text
                    self.mode_toggle_button.config(
                        text="W", 
                        bg='#f8d0d0',
                        fg='#c0392b',
                        font=('Segoe UI', 11, 'bold'),
                        relief=tk.SUNKEN
                    )
                else:
                    # Edit mode - light green background, bold text
                    self.mode_toggle_button.config(
                        text="E", 
                        bg='#d4edda',
                        fg='#155724',
                        font=('Segoe UI', 11, 'bold'),
                        relief=tk.RAISED
                    )
        except tk.TclError:
            # Widget no longer exists
            pass
        except Exception as e:
            print(f"Warning: Could not update mode display: {e}")
    
    def show_calibration_dialog(self):
        """Show calibration dialog - opens Settings tab with Calibration sub-tab"""
        self.open_control_panel(tab_index=0, sub_tab_index=2)
    
    def create_mode_button(self, parent, icon, mode, tooltip):
        """Create a mode selection button"""
        tile = tk.Frame(parent, bg='#dfe3e8', bd=1, relief=tk.RAISED, width=38, height=38)
        tile.pack(side='left', padx=2, pady=2)
        tile.pack_propagate(False)

        btn = tk.Button(tile, text=icon, font=('Arial', 16), bg='#4b525c', fg='#e8ecf2',
                       command=lambda: self.set_mode_from_toolbar(mode), 
                       relief=tk.FLAT, cursor='hand2', bd=0, highlightthickness=0)
        btn.pack(fill='both', expand=True)
        
        # Highlight if current mode
        if self.config["mode"] == mode:
            btn.config(bg='#4a90e2')
        
        return btn
    
    def toggle_mode_visibility(self, mode):
        """Toggle visibility of a mode - if already active, hide it; otherwise switch to it"""
        current_mode = self.config["mode"]
        
        # If clicking the currently active mode, toggle its visibility
        if current_mode == mode:
            self.mode_visible[mode] = not self.mode_visible[mode]
            if self.mode_visible[mode]:
                self.show_notification(f"{mode.capitalize()} shown")
            else:
                self.show_notification(f"{mode.capitalize()} hidden")
        else:
            # Switching to a different mode - show it and make it active
            self.mode_visible[mode] = True
            self.set_mode_from_toolbar(mode)
            self.show_notification(f"Switched to {mode.capitalize()} mode")
        
        self._update_mode_button_highlights()
        self.draw()
    
    def set_mode_from_toolbar(self, mode):
        """Set measurement mode from toolbar button"""
        # Calculate current center position before switching modes
        if self.config["mode"] == "ruler" or self.config["mode"] == "fractions":
            # Get center from ruler endpoints
            center_x = (self.p1["x"] + self.p2["x"]) / 2
            center_y = (self.p1["y"] + self.p2["y"]) / 2
        elif self.config["mode"] == "angle":
            # Get center from angle mode
            center_x = self.angle_center["x"]
            center_y = self.angle_center["y"]
        elif self.config["mode"] == "polygon" and self.polygon_points:
            # Get center from polygon
            center_x = sum(p["x"] for p in self.polygon_points) / len(self.polygon_points)
            center_y = sum(p["y"] for p in self.polygon_points) / len(self.polygon_points)
        else:
            # Default to screen center
            center_x = self.virtual_x + (self.virtual_w / 2)
            center_y = self.virtual_y + (self.virtual_h / 2)
        
        self.config["mode"] = mode
        
        # When switching to fractions mode, enable fractions
        if mode == "fractions":
            self.config["show_fractions"] = True
            # Update input label and configuration
            if hasattr(self, 'number_label'):
                self.number_label.config(text="Fractions:")
                self.number_input.config(from_=2, to=50)
                self.number_input.delete(0, 'end')
                self.number_input.insert(0, str(self.config["fraction_count"]))
            # Keep ruler at same center position
            ruler_length = math.sqrt((self.p2["x"] - self.p1["x"])**2 + (self.p2["y"] - self.p1["y"])**2)
            self.p1 = {"x": center_x - ruler_length/2, "y": center_y}
            self.p2 = {"x": center_x + ruler_length/2, "y": center_y}
        elif mode == "polygon":
            self.config["show_fractions"] = False
            # Update input label for polygon sides
            if hasattr(self, 'number_label'):
                self.number_label.config(text="Sides:")
                self.number_input.config(from_=3, to=20)
                self.number_input.delete(0, 'end')
                self.number_input.insert(0, str(self.config["polygon_sides"]))
            # Initialize polygon at preserved center position
            if not self.polygon_points:
                self.init_polygon_at_position(center_x, center_y)
            else:
                # Move existing polygon to center position
                old_center_x = sum(p["x"] for p in self.polygon_points) / len(self.polygon_points)
                old_center_y = sum(p["y"] for p in self.polygon_points) / len(self.polygon_points)
                dx = center_x - old_center_x
                dy = center_y - old_center_y
                for p in self.polygon_points:
                    p["x"] += dx
                    p["y"] += dy
        elif mode == "angle":
            self.config["show_fractions"] = False
            # Move angle mode to preserved center position
            self.angle_center = {"x": center_x, "y": center_y}
            self.angle_arm1 = {"x": center_x - 200, "y": center_y}
            self.angle_arm2 = {"x": center_x, "y": center_y - 200}
        elif mode == "ruler":
            self.config["show_fractions"] = False
            # Move ruler to preserved center position
            self.p1 = {"x": center_x - 350, "y": center_y}
            self.p2 = {"x": center_x + 350, "y": center_y}
        else:
            self.config["show_fractions"] = False
            # Hide or show number input as needed
            if hasattr(self, 'number_label'):
                if mode == "ruler" or mode == "angle":
                    # Keep the input visible but label it appropriately
                    self.number_label.config(text="Number:")
        
        # Don't reinitialize angle mode position - keep existing position
        # Angle position is already set at initialization
        
        self.save_config()
        self._sync_number_tile_for_mode()
        self._update_mode_button_highlights()
        
        # Ensure windows are visible and not minimized
        if not self.minimized:
            self.ensure_windows_visible()
        
        self.draw()
    
    def toggle_text_mode(self):
        """Toggle text mode on/off"""
        self.text_mode_active = not self.text_mode_active
        
        # Show/hide text formatting toolbar and resize window
        if self.text_mode_active:
            # Pack the text toolbar frame in the body frame
            if hasattr(self, 'text_toolbar_frame') and self.text_toolbar_frame:
                self.text_toolbar_frame.pack(fill='x', pady=(4, 0))
            # Highlight text button
            if "text" in self.mode_buttons:
                self.mode_buttons["text"].config(bg='#5294e2', fg='white')
            # Expand toolbar height to 245px
            if self.toolbar and self.toolbar.winfo_exists():
                current_width = self.toolbar.winfo_width()
                toolbar_x = self.toolbar.winfo_x()
                toolbar_y = self.toolbar.winfo_y()
                self.toolbar.geometry(f"{current_width}x245+{toolbar_x}+{toolbar_y}")
            self.show_notification("Text Mode: Active - Click 'Add' or press Enter to add text")
        else:
            if hasattr(self, 'text_toolbar_frame') and self.text_toolbar_frame:
                self.text_toolbar_frame.pack_forget()
            # Unhighlight text button
            if "text" in self.mode_buttons:
                self.mode_buttons["text"].config(bg='#fbfbfc', fg='#5c616c')
            # Restore toolbar height to 155px
            if self.toolbar and self.toolbar.winfo_exists():
                current_width = self.toolbar.winfo_width()
                toolbar_x = self.toolbar.winfo_x()
                toolbar_y = self.toolbar.winfo_y()
                self.toolbar.geometry(f"{current_width}x155+{toolbar_x}+{toolbar_y}")
            self.show_notification("Text Mode: Inactive")
        
        self.draw()
    
    def add_text_object(self):
        """Add a new text object to the screen"""
        if not self.text_mode_active:
            return
        
        text_content = self.text_input_var.get()
        if not text_content or text_content.strip() == "":
            text_content = "Your text here"
        
        # Create new text object at center of screen
        center_x = self.virtual_x + (self.virtual_w / 2)
        center_y = self.virtual_y + (self.virtual_h / 2)
        
        text_obj = {
            "x": center_x - 100,
            "y": center_y - 50,
            "width": 200,
            "height": 100,
            "text": text_content,
            "font_family": self.text_font_family,
            "font_size": self.text_font_size,
            "bold": self.text_bold,
            "italic": self.text_italic,
            "underline": self.text_underline,
            "outline": self.text_outline
        }
        
        self.text_objects.append(text_obj)
        self.draw()
        self.show_notification(f"Added text: '{text_content[:20]}...'")
    
    def update_text_font_size(self):
        """Update text font size and apply to all existing text objects"""
        try:
            self.text_font_size = int(self.font_size_spinbox.get())
            # Update all existing text objects with new font size
            for text_obj in self.text_objects:
                text_obj["font_size"] = self.text_font_size
            self.draw()
        except Exception:
            self.text_font_size = 24
            self.font_size_spinbox.delete(0, 'end')
            self.font_size_spinbox.insert(0, "24")
    
    def update_text_font_family(self, event=None):
        """Update text font family and apply to all existing text objects"""
        self.text_font_family = self.font_family_dropdown.get()
        # Update all existing text objects with new font family
        for text_obj in self.text_objects:
            text_obj["font_family"] = self.text_font_family
        self.draw()
    
    def toggle_bold(self):
        """Toggle bold text and apply to all existing text objects"""
        self.text_bold = not self.text_bold
        if self.text_bold:
            self.bold_btn.config(bg='#5294e2', fg='white')
        else:
            self.bold_btn.config(bg='#fbfbfc', fg='#5c616c')
        # Update all existing text objects with new bold setting
        for text_obj in self.text_objects:
            text_obj["bold"] = self.text_bold
        self.draw()
    
    def toggle_italic(self):
        """Toggle italic text and apply to all existing text objects"""
        self.text_italic = not self.text_italic
        if self.text_italic:
            self.italic_btn.config(bg='#5294e2', fg='white')
        else:
            self.italic_btn.config(bg='#fbfbfc', fg='#5c616c')
        # Update all existing text objects with new italic setting
        for text_obj in self.text_objects:
            text_obj["italic"] = self.text_italic
        self.draw()
    
    def toggle_underline(self):
        """Toggle underline text and apply to all existing text objects"""
        self.text_underline = not self.text_underline
        if self.text_underline:
            self.underline_btn.config(bg='#5294e2', fg='white')
        else:
            self.underline_btn.config(bg='#fbfbfc', fg='#5c616c')
        # Update all existing text objects with new underline setting
        for text_obj in self.text_objects:
            text_obj["underline"] = self.text_underline
        self.draw()
    
    def toggle_outline(self):
        """Toggle text box outline and apply to all existing text objects"""
        self.text_outline = not self.text_outline
        if self.text_outline:
            self.outline_btn.config(bg='#5294e2', fg='white')
        else:
            self.outline_btn.config(bg='#fbfbfc', fg='#5c616c')
        # Update all existing text objects with new outline setting
        for text_obj in self.text_objects:
            text_obj["outline"] = self.text_outline
        self.draw()
    
    def delete_text_object(self, event=None):
        """Delete the selected text object, or last added if none selected"""
        if self.text_objects:
            if self.selected_text_index is not None and 0 <= self.selected_text_index < len(self.text_objects):
                # Delete the selected text object
                deleted = self.text_objects.pop(self.selected_text_index)
                self.selected_text_index = None  # Clear selection
                self.draw()
                self.show_notification(f"Deleted selected text: '{deleted['text'][:20]}...'")
            else:
                # Delete the last text object if none selected
                deleted = self.text_objects.pop()
                self.draw()
                self.show_notification(f"Deleted text: '{deleted['text'][:20]}...'")
        else:
            self.show_notification("No text objects to delete")
    
    def clear_all_text_objects(self):
        """Clear all text objects"""
        if self.text_objects:
            count = len(self.text_objects)
            self.text_objects = []
            self.draw()
            self.show_notification(f"Cleared {count} text object(s)")
        else:
            self.show_notification("No text objects to clear")
    
    def toggle_text_visibility(self):
        """Toggle visibility of all text objects"""
        self.text_visible = not self.text_visible
        self.draw()
        status = "Visible" if self.text_visible else "Hidden"
        self.show_notification(f"Text: {status}")
        
        # Update eye button appearance if it exists
        if hasattr(self, 'text_visibility_btn'):
            if self.text_visible:
                self.text_visibility_btn.config(text="👁", bg='#5294e2', fg='white')
            else:
                self.text_visibility_btn.config(text="👁", bg='#fbfbfc', fg='#5c616c')
    
    def init_polygon_with_sides(self, sides):
        """Initialize polygon with specified number of sides, preserving current center position"""
        try:
            # Calculate current center position if polygon already exists
            if self.polygon_points:
                cx = sum(p["x"] for p in self.polygon_points) / len(self.polygon_points)
                cy = sum(p["y"] for p in self.polygon_points) / len(self.polygon_points)
            else:
                # Use screen center if no polygon exists yet
                cx = self.virtual_x + (self.virtual_w / 2)
                cy = self.virtual_y + (self.virtual_h / 2)
            
            radius = 150
            self.polygon_points = []
            
            for i in range(sides):
                angle = 2 * math.pi * i / sides - math.pi / 2  # Start from top
                x = cx + radius * math.cos(angle)
                y = cy + radius * math.sin(angle)
                self.polygon_points.append({"x": x, "y": y})
        except Exception as e:
            print(f"Warning: Could not initialize polygon: {e}")
            # Fallback to default 4-sided polygon
            self.init_polygon_default()
    
    def refresh_toolbar(self):
        """Refresh toolbar button states"""
        if self.toolbar and self.toolbar.winfo_exists():
            # Preserve position before recreate
            try:
                geom = self.toolbar.geometry()
            except Exception:
                geom = None
            self.toolbar.destroy()
            self.create_toolbar()
            if geom:
                try:
                    # Keep same x/y; size is managed by create_toolbar
                    if '+' in geom:
                        xy = '+' + '+'.join(geom.split('+')[1:])
                        self.toolbar.geometry(xy)
                except Exception:
                    pass
    
    def update_lock_button(self):
        """Update lock button icon and label based on lock state"""
        try:
            if hasattr(self, 'lock_button') and self.lock_button.winfo_exists():
                if self.config["lock_angle"] == 0:
                    self.lock_button.config(text="🔒H", font=('Segoe UI', 9, 'bold'))
                    self.lock_status_var.set("Horizontal")
                    if self.lock_label and self.lock_label.winfo_exists():
                        self.lock_label.config(text="Horizontal")
                elif self.config["lock_angle"] == 90:
                    self.lock_button.config(text="🔒V", font=('Segoe UI', 9, 'bold'))
                    self.lock_status_var.set("Vertical")
                    if self.lock_label and self.lock_label.winfo_exists():
                        self.lock_label.config(text="Vertical")
                else:
                    self.lock_button.config(text="🔓", font=('Segoe UI', 9, 'bold'))
                    self.lock_status_var.set("None")
                    if self.lock_label and self.lock_label.winfo_exists():
                        self.lock_label.config(text="None")
        except tk.TclError:
            # Widget no longer exists
            pass
        except Exception as e:
            print(f"Warning: Could not update lock button: {e}")

    def load_config(self):
        """Load configuration from file"""
        config_file = "ruler_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.config.update(saved)
            except Exception:
                # If config is corrupted, keep defaults and avoid crashing.
                try:
                    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
                    os.replace(config_file, f"ruler_config.bad-{ts}.json")
                except Exception:
                    pass

        # Normalize/repair config values after loading
        self.config["unit"] = self.normalize_unit(self.config.get("unit", "px"))
        if self.config.get("lock_angle") not in (None, 0, 90):
            self.config["lock_angle"] = None
        
        # Validate numeric ranges
        try:
            self.config["calibration_factor"] = float(self.config.get("calibration_factor", 1.0))
            if self.config["calibration_factor"] <= 0:
                self.config["calibration_factor"] = 1.0
        except (ValueError, TypeError):
            self.config["calibration_factor"] = 1.0
        
        # Validate opacity values
        try:
            opacity_work = float(self.config.get("opacity_work", 0.95))
            self.config["opacity_work"] = max(0.1, min(1.0, opacity_work))
        except (ValueError, TypeError):
            self.config["opacity_work"] = 0.95
        
        try:
            opacity_edit = float(self.config.get("opacity_edit", 1.0))
            self.config["opacity_edit"] = max(0.1, min(1.0, opacity_edit))
        except (ValueError, TypeError):
            self.config["opacity_edit"] = 1.0
        
        # Validate fraction_count
        try:
            fraction_count = int(self.config.get("fraction_count", 4))
            self.config["fraction_count"] = max(2, min(50, fraction_count))
        except (ValueError, TypeError):
            self.config["fraction_count"] = 4
        
        # Validate polygon_sides
        try:
            polygon_sides = int(self.config.get("polygon_sides", 4))
            self.config["polygon_sides"] = max(3, min(20, polygon_sides))
        except (ValueError, TypeError):
            self.config["polygon_sides"] = 4
        
        # Validate ruler_thickness
        try:
            ruler_thickness = int(self.config.get("ruler_thickness", 4))
            self.config["ruler_thickness"] = max(1, min(20, ruler_thickness))
        except (ValueError, TypeError):
            self.config["ruler_thickness"] = 4

    def save_config(self):
        """Save configuration to file"""
        try:
            tmp_path = "ruler_config.json.tmp"
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, "ruler_config.json")
        except Exception:
            # Avoid crashing on transient I/O issues.
            pass

    def normalize_unit(self, unit: str) -> str:
        """Normalize unit strings and keep backwards compatibility."""
        if not unit:
            return "px"
        u = str(unit).strip().lower()
        # Legacy values
        if u in ("inch", "inches"):
            return "in"
        if u in ("µm", "μm"):
            return "um"
        if u == "meter":
            return "m"
        # Canonical supported set
        if u in {"px", "um", "mm", "cm", "m", "in"}:
            return u
        return "px"

    def get_screen_dpi(self) -> float:
        """Best-effort DPI for correct unit conversions and tick spacing."""
        # Windows 10+: per-monitor DPI
        try:
            hwnd = self.root.winfo_id()
            dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
            if dpi:
                return float(dpi)
        except Exception:
            pass

        # Fallback: system DPI
        try:
            LOGPIXELSX = 88
            hdc = ctypes.windll.user32.GetDC(0)
            dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
            ctypes.windll.user32.ReleaseDC(0, hdc)
            if dpi:
                return float(dpi)
        except Exception:
            pass

        return 96.0

    def setup_tray_icon(self):
        """Setup system tray icon using Icon.ico file."""
        try:
            # Try to load the Icon.ico file
            icon_path = os.path.join(os.path.dirname(__file__), 'Icon.ico')
            
            # Check if running as a bundled executable
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # Running as compiled executable
                icon_path = os.path.join(getattr(sys, '_MEIPASS', ''), 'Icon.ico')
            
            # Load icon image
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
            else:
                # Fallback: Create icon programmatically if Icon.ico not found
                image = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
                draw = ImageDraw.Draw(image)
                # Draw a ruler icon as fallback
                draw.rectangle([15, 50, 113, 70], fill=(0, 200, 255, 255), outline=(255, 255, 255, 255), width=2)
                for x in range(20, 110, 8):
                    tick_h = 15 if (x - 20) % 32 == 0 else 10
                    draw.line([x, 48, x, 48 - tick_h], fill=(255, 255, 255, 255), width=3)

            menu = pystray.Menu(
                pystray.MenuItem('Show Ruler', self.show_from_tray),
                pystray.MenuItem('Exit', self.exit_from_tray)
            )

            self.tray_icon = pystray.Icon("ProRuler", image, "📏 ScreenRuler Pro", menu)

            Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"Could not create tray icon: {e}")

    def show_from_tray(self, icon=None, item=None):
        """Show window from tray"""
        self.root.after(0, self._show_window)

    def _show_window(self):
        """Internal method to show window"""
        self.root.deiconify()
        self.root.lift()
        if self.toolbar and self.toolbar.winfo_exists():
            self.toolbar.deiconify()
            self.toolbar.lift()
        self.minimized = False

    def exit_from_tray(self, icon=None, item=None):
        """Exit application from tray"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)

    def show_welcome(self):
        """Show welcome message"""
        # No longer showing welcome message as we have toolbar
        pass

    def show_about(self, event=None):
        """Show control panel with About tab"""
        self.open_control_panel(tab_index=2)

    def toggle_help(self, event=None):
        """Show control panel with Help tab"""
        self.open_control_panel(tab_index=1)

    def toggle_settings(self, event=None):
        """Open control panel with Settings tab"""
        self.open_control_panel(tab_index=0)

    def open_control_panel(self, tab_index=0, sub_tab_index=0):
        """Create unified control panel with Settings, Help, and About tabs"""
        # Close existing panel if open
        if self.control_panel and self.control_panel.winfo_exists():
            self.control_panel.lift()
            self.control_panel.focus_force()
            # Switch to requested tab
            if hasattr(self, 'control_notebook'):
                self.control_notebook.select(tab_index)
                # If settings tab and sub_tab_index specified, switch to that sub-tab
                if tab_index == 0 and hasattr(self, 'settings_notebook'):
                    self.settings_notebook.select(sub_tab_index)
            return
        
        self.control_panel = tk.Toplevel(self.root)
        self.control_panel.title("ScreenRuler Pro - Control Panel")
        self.control_panel.geometry("580x600")
        self.control_panel.attributes('-topmost', True)
        self.control_panel.attributes('-alpha', 0.95)
        self.control_panel.resizable(False, False)
        self.control_panel.configure(bg='#f5f6f7')
        
        # Set window icon if available
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'Icon.ico')
            if os.path.exists(icon_path):
                self.control_panel.iconbitmap(icon_path)
        except Exception:
            pass
        
        # Close panel when closed
        self.control_panel.protocol("WM_DELETE_WINDOW", self.control_panel.destroy)
        
        # Create notebook for tabs
        self.control_notebook = ttk.Notebook(self.control_panel)
        self.control_notebook.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Create all tabs in new order: Settings > Help > About
        self.create_settings_tab(self.control_notebook)
        self.create_help_tab(self.control_notebook)
        self.create_about_tab(self.control_notebook)
        
        # Select requested tab
        self.control_notebook.select(tab_index)
        
        # If settings tab and sub_tab_index specified, switch to that sub-tab
        if tab_index == 0 and sub_tab_index > 0 and hasattr(self, 'settings_notebook'):
            self.settings_notebook.select(sub_tab_index)
        
        # Footer with close button
        footer_frame = tk.Frame(self.control_panel, bg='#f5f6f7', height=60)
        footer_frame.pack(fill='x')
        footer_frame.pack_propagate(False)
        
        button_container = tk.Frame(footer_frame, bg='#f5f6f7')
        button_container.pack(expand=True)
        
        close_btn = tk.Button(button_container, text="✖  Close Panel", 
                             command=self.control_panel.destroy,
                             bg="#f46067", fg="white", 
                             font=("Segoe UI", 12, "bold"),
                             padx=50, pady=12,
                             relief=tk.FLAT,
                             cursor="hand2",
                             activebackground="#f13039",
                             activeforeground="white",
                             borderwidth=0)
        close_btn.pack()

    def create_help_tab(self, notebook):
        """Create Help tab"""
        help_frame = ttk.Frame(notebook)
        notebook.add(help_frame, text="  ❓ Help  ")
        
        # Create scrollable text widget with better styling
        scrollbar = tk.Scrollbar(help_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        help_text_widget = tk.Text(help_frame, wrap=tk.WORD, 
                                   font=("Consolas", 10),
                                   bg='white', fg='#5c616c',
                                   padx=20, pady=15,
                                   yscrollcommand=scrollbar.set,
                                   relief=tk.FLAT,
                                   selectbackground='#5294e2',
                                   selectforeground='white')
        help_text_widget.pack(fill='both', expand=True)
        scrollbar.config(command=help_text_widget.yview)
        
        help_content = """KEYBOARD SHORTCUTS
=====================================

P  - Toggle Work/Edit Mode
H  - Show Help (this window)
S  - Open Settings Tab  
A  - Open About Tab
C  - Copy Measurement to Clipboard
R  - Reset Ruler Position
M  - Cycle Mode (Ruler/Fractions/Angle)
E  - Cycle Endpoint Style
G  - Toggle Guide Lines
V  - Toggle Ruler Labels
L  - Cycle Lock (None/Horizontal/Vertical)
T  - Cycle Theme
U  - Cycle Unit (px/cm/in)
F  - Toggle Fraction Mode
[  - Decrease Fractions
]  - Increase Fractions
,  - Decrease Thickness
.  - Increase Thickness
+  - Increase Opacity
-  - Decrease Opacity
Del/Backspace - Delete Selected Text (click text first)
B  - Toggle Toolbar Visibility
Space - Minimize to Tray
Esc   - Exit Application

TEXT MODE
=====================================

  • Click text mode button (A) in toolbar
  • Enter text and click Add or press Enter
  • Click and drag text to reposition
  • Click text to select it (gold border)
  • Press Delete to remove selected text
  • Use formatting toolbar for font/style

MEASUREMENT MODES
=====================================

Ruler Mode:
  • Standard linear measurement
  • Two endpoints that can be dragged
  • Shows distance and angle

Fractions Mode:
  • Divides ruler into equal segments
  • Use [ and ] to adjust segment count
  • Useful for proportional measurements

Angle Mode:
  • Two rotating arms from center point
  • Measure angles between objects
  • Drag center to move, endpoints to rotate
  • Shows angle and arm lengths

MOUSE CONTROLS
=====================================

Edit Mode (Press P to activate):
  • Drag endpoints - Resize ruler/rotate arms
  • Drag line/center - Move entire tool
  • Drag info box - Reposition display
  • Right-click - Context menu

Work Mode (Default):
  • Click-through enabled
  • Tool visible but non-interactive

CURSOR FEEDBACK
=====================================
  • Crosshair - Over endpoints (resize/rotate)
  • 4-way Arrow - Over line/center (move)
  • Hand - Over info box (drag)

ONSCREEN TEXT ANNOTATIONS
=====================================

  • Add persistent text labels to your screen
  • Reposition by clicking and dragging
  • Select text by clicking (gold border)
  • Delete selected text with Delete key
  • Click selected text again to deselect
  • Click anywhere else to clear selection
  
  Formatting Options:
  • Change font family and size
  • Bold, Italic, Underline styles
  • Optional text box outline
  • Show/hide all text with eye button
  • Clear all text at once

ENDPOINT STYLES
=====================================

  • None - Simple line endpoints
  • Circle - Circular markers at ends
  • Square - Square markers at ends
  • Crosslines - Crosshair markers
  • Arrow - Directional arrow heads
  
  Press 'E' to cycle through styles

TOOLBAR CONTROLS
=====================================

  • 🢓 - Minimize entire app to system tray
  • ─ - Minimize toolbar only (ruler stays visible)
  • ✕ - Close application
  • Press 'B' to toggle toolbar visibility
  • Press Space to minimize to system tray

FEATURES
=====================================
  • Multiple measurement modes
  • Multiple measurement units
  • Angle measurement
  • Calibration system
  • Fraction mode
  • Onscreen text annotations
  • System tray support
  • Customizable themes
  • Real-time settings preview
  • Click-through capability
  • Toolbar minimize options
  • Text selection & deletion

CALIBRATION
=====================================
Go to Settings > Calibration tab:
  1. Measure a known object
  2. Enter the known value
  3. Click 'Calibrate from Known Value'
  4. Or manually set calibration factor

TIPS
=====================================
  • Use guide lines for alignment
  • Lock angle for straight measurements
  • Copy measurements to clipboard
  • Calibrate for accurate real-world units
  • Minimize toolbar only to keep ruler visible
  • Add text labels for reference points
  • Use angle mode for corner measurements
  • Switch modes with 'M' key
  • Cycle endpoint styles with 'E' key
"""
        
        help_text_widget.insert('1.0', help_content)

        # Add styling with tags for better readability
        help_text_widget.tag_configure("h1", font=("Segoe UI", 11, "bold"), spacing3=8, foreground="#5c616c")
        
        # Apply tag to all titles
        lines = help_content.split('\n')
        for i, line in enumerate(lines):
            if line.endswith('=='):
                help_text_widget.tag_add("h1", f"{i+1}.0", f"{i+1}.end")

        help_text_widget.config(state='disabled')  # Make read-only

    def create_settings_tab(self, notebook):
        """Create Settings tab with sub-tabs"""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="  ⚙️ Settings  ")
        
        # Create sub-notebook for settings categories with better styling
        self.settings_notebook = ttk.Notebook(settings_frame)
        self.settings_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Appearance sub-tab
        self.create_appearance_settings(self.settings_notebook)
        
        # Measurement sub-tab
        self.create_measurement_settings(self.settings_notebook)
        
        # Calibration sub-tab
        self.create_calibration_settings(self.settings_notebook)
        
        # Apply button with better styling
        button_frame = tk.Frame(settings_frame, bg='white')
        button_frame.pack(pady=15)
        
        def apply_and_save():
            self.save_config()
            parent_window = self.control_panel if self.control_panel and self.control_panel.winfo_exists() else self.root
            messagebox.showinfo("Settings Saved", 
                              "✅ All settings have been saved successfully!", 
                              parent=parent_window)
        
        tk.Button(button_frame, text="💾  Save All Settings", 
                 command=apply_and_save,
                 bg="#5294e2", fg="white", 
                 font=("Segoe UI", 11, "bold"),
                 padx=30, pady=10,
                 relief=tk.FLAT,
                 cursor="hand2",
                 activebackground="#4a85d4",
                 activeforeground="white").pack()

    def create_appearance_settings(self, notebook):
        """Create appearance settings sub-tab"""
        appearance_frame = ttk.Frame(notebook)
        notebook.add(appearance_frame, text="Appearance")
        
        # Create scrollable frame
        canvas = tk.Canvas(appearance_frame, bg='white')
        scrollbar = ttk.Scrollbar(appearance_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Theme selection
        ttk.Label(scrollable_frame, text="Theme:", font=("Arial", 10, "bold")).pack(anchor='w', padx=10, pady=(10,5))
        theme_var = tk.StringVar(value=self.config["theme"])
        
        def update_theme(t):
            theme_var.set(t)
            self.set_theme(t)
            self.draw()
            
        for theme_name in self.themes.keys():
            ttk.Radiobutton(scrollable_frame, text=theme_name.capitalize(), 
                          variable=theme_var, value=theme_name,
                          command=lambda t=theme_name: update_theme(t)).pack(anchor='w', padx=30)
        
        # Mode selection
        ttk.Label(scrollable_frame, text="Measurement Mode:", font=("Arial", 10, "bold")).pack(anchor='w', padx=10, pady=(15,5))
        mode_var = tk.StringVar(value=self.config["mode"])
        modes = [("Ruler", "ruler"), ("Fractions", "fractions"), ("Angle", "angle"), ("Polygon", "polygon")]
        
        def update_mode():
            new_mode = mode_var.get()
            self.config["mode"] = new_mode
            
            # When switching to fractions mode, enable fractions
            if new_mode == "fractions":
                self.config["show_fractions"] = True
            else:
                self.config["show_fractions"] = False # Redundant, set_mode_from_toolbar handles it
            
            # Initialize angle mode position if switching to it
            if new_mode == "angle":
                cx, cy = self.screen_width / 2, self.screen_height / 2
                self.angle_center = {"x": cx, "y": cy}
                self.angle_arm1 = {"x": cx - 200, "y": cy}
                self.angle_arm2 = {"x": cx, "y": cy - 200}
            elif new_mode == "polygon":
                self.init_polygon_default()
            self.set_mode_from_toolbar(new_mode)
            
            self.draw()
        
        for text, value in modes:
            ttk.Radiobutton(scrollable_frame, text=text, 
                          variable=mode_var, value=value,
                          command=update_mode).pack(anchor='w', padx=30)
        
        # Opacity
        ttk.Label(scrollable_frame, text="Work Mode Opacity:", font=("Arial", 10, "bold")).pack(anchor='w', padx=10, pady=(15,5))
        opacity_var = tk.DoubleVar(value=self.config["opacity_work"])
        
        def update_opacity(val):
            self.config["opacity_work"] = float(val)
            if self.is_passthrough:
                self.root.attributes('-alpha', float(val))
        
        opacity_slider = tk.Scale(scrollable_frame, from_=0.3, to=1.0, resolution=0.05,
                                 orient='horizontal', variable=opacity_var, length=450,
                                 command=update_opacity)
        opacity_slider.pack(padx=30)
        
        # Show Guides
        guides_var = tk.BooleanVar(value=self.config["show_guides"])
        
        def update_guides():
            self.config["show_guides"] = guides_var.get()
            self.draw()
        
        ttk.Checkbutton(scrollable_frame, text="Show Guide Lines",
                       variable=guides_var,
                       command=update_guides).pack(anchor='w', padx=30, pady=10)
        
        # Show Labels
        labels_var = tk.BooleanVar(value=self.config["show_labels"])
        
        def update_labels():
            self.config["show_labels"] = labels_var.get()
            self.draw()
        
        ttk.Checkbutton(scrollable_frame, text="Show Ruler Labels",
                       variable=labels_var,
                       command=update_labels).pack(anchor='w', padx=30, pady=5)
        
        # Ruler Endpoint Style
        ttk.Label(scrollable_frame, text="Ruler Endpoint Style:", font=("Arial", 10, "bold")).pack(anchor='w', padx=10, pady=(15,5))
        endpoint_var = tk.StringVar(value=self.config.get("endpoint_style", "circle"))
        endpoint_styles = [
            ("None", "none"),
            ("Circle", "circle"),
            ("Square", "flat"),
            ("Crosslines", "crosslines"),
            ("Arrow", "arrow")
        ]
        
        def update_endpoint_style():
            self.config["endpoint_style"] = endpoint_var.get()
            self.draw()
        
        for text, value in endpoint_styles:
            ttk.Radiobutton(scrollable_frame, text=text, 
                          variable=endpoint_var, value=value,
                          command=update_endpoint_style).pack(anchor='w', padx=30)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_measurement_settings(self, notebook):
        """Create measurement settings sub-tab"""
        measurement_frame = ttk.Frame(notebook)
        notebook.add(measurement_frame, text="Measurement")
        
        # Create scrollable frame
        canvas = tk.Canvas(measurement_frame, bg='white')
        scrollbar = ttk.Scrollbar(measurement_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Unit selection
        ttk.Label(scrollable_frame, text="Unit:", font=("Arial", 10, "bold")).pack(anchor='w', padx=20, pady=(15,5))
        unit_var = tk.StringVar(value=self.config["unit"])
        units = [
            ("Pixels", "px"),
            ("Micrometers (µm)", "um"),
            ("Millimeters", "mm"),
            ("Centimeters", "cm"),
            ("Meters", "m"),
            ("Inches", "in"),
        ]
        
        def update_unit():
            self.set_unit(unit_var.get())
            self.save_config()
            self.draw()
        
        for text, value in units:
            ttk.Radiobutton(scrollable_frame, text=text,
                           variable=unit_var, value=value,
                           command=update_unit).pack(anchor='w', padx=30)
        
        # Note: Measurement Box Opacity slider removed - measurements now integrated in toolbar
        
        # Tick spacing
        ttk.Label(scrollable_frame, text="Tick Spacing:", font=("Arial", 10, "bold")).pack(anchor='w', padx=20, pady=(20,5))
        tick_var = tk.IntVar(value=self.config["tick_spacing"])
        
        def update_tick(val):
            self.config["tick_spacing"] = int(float(val))
            self.draw()
        
        tick_slider = ttk.Scale(scrollable_frame, from_=10, to=50,
                               orient='horizontal', variable=tick_var, length=450,
                               command=update_tick)
        tick_slider.pack(padx=30, fill='x', expand=True)
        
        # Ruler thickness
        ttk.Label(scrollable_frame, text="Ruler Thickness:", font=("Arial", 10, "bold")).pack(anchor='w', padx=20, pady=(20,5))
        thickness_var = tk.IntVar(value=self.config["ruler_thickness"])
        
        def update_thickness(val):
            self.config["ruler_thickness"] = int(float(val))
            self.draw()
        
        thickness_slider = ttk.Scale(scrollable_frame, from_=1, to=20,
                                    orient='horizontal', variable=thickness_var, length=450,
                                    command=update_thickness)
        thickness_slider.pack(padx=30, fill='x', expand=True)
        
        # Lock angle
        ttk.Label(scrollable_frame, text="Lock Angle:", font=("Arial", 10, "bold")).pack(anchor='w', padx=20, pady=(20,5))
        current_lock = self.config.get("lock_angle")
        lock_var = tk.StringVar(value="None" if current_lock is None else str(current_lock))
        locks = [("None", "None"), ("Horizontal", "0"), ("Vertical", "90")]

        def update_lock():
            v = lock_var.get()
            self.config["lock_angle"] = None if v == "None" else int(v)
            self.save_config()
            self.update_lock_button()
            self.draw()

        for text, value in locks:
            ttk.Radiobutton(
                scrollable_frame,
                text=text,
                variable=lock_var,
                value=value,
                command=update_lock,
            ).pack(anchor='w', padx=30)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_calibration_settings(self, notebook):
        """Create calibration settings sub-tab"""
        calibration_frame = ttk.Frame(notebook)
        notebook.add(calibration_frame, text="Calibration")
        
        # Create scrollable frame
        canvas = tk.Canvas(calibration_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(calibration_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Container with reduced padding
        container = tk.Frame(scrollable_frame, bg='#f8f9fa')
        container.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Compact title section
        title_frame = tk.Frame(container, bg='white', relief=tk.FLAT)
        title_frame.pack(fill='x', pady=(0, 10))
        
        title_inner = tk.Frame(title_frame, bg='white')
        title_inner.pack(fill='x', padx=15, pady=10)
        
        title_label = tk.Label(title_inner,
                              text="🎯 Calibration",
                              font=("Segoe UI", 12, "bold"),
                              fg="#2d3436", bg='white')
        title_label.pack(anchor='w')
        
        # Current measurement display - more compact
        dist = self.get_distance()
        measure_frame = tk.Frame(title_inner, bg='#e8f4f8', relief=tk.FLAT)
        measure_frame.pack(fill='x', pady=(8, 0))
        
        current_display = tk.Label(measure_frame,
                                  text=f"📐 Current: {self.format_distance(dist)}",
                                  font=("Segoe UI", 10, "bold"),
                                  fg="#2c7a9e", bg='#e8f4f8')
        current_display.pack(padx=12, pady=8)
        
        # Method 1: Simple calibration card - more compact
        method1_card = tk.Frame(container, bg='white', relief=tk.FLAT)
        method1_card.pack(fill='x', pady=(0, 10))
        
        # Method 1 header with badge
        m1_header = tk.Frame(method1_card, bg='#d4edda')
        m1_header.pack(fill='x')
        
        m1_title_frame = tk.Frame(m1_header, bg='#d4edda')
        m1_title_frame.pack(anchor='w', padx=15, pady=8)
        
        tk.Label(m1_title_frame, text="✓", font=("Arial", 11, "bold"), 
                fg="#155724", bg='#d4edda').pack(side='left', padx=(0, 6))
        tk.Label(m1_title_frame, text="Simple Calibration",
                font=("Segoe UI", 10, "bold"),
                fg="#155724", bg='#d4edda').pack(side='left')
        tk.Label(m1_title_frame, text="RECOMMENDED",
                font=("Segoe UI", 7, "bold"),
                fg="#155724", bg='#c3e6cb',
                relief=tk.FLAT).pack(side='left', padx=8, ipadx=5, ipady=1)
        
        # Method 1 content - more compact
        m1_content = tk.Frame(method1_card, bg='white')
        m1_content.pack(fill='x', padx=15, pady=10)
        
        instructions1 = tk.Label(m1_content,
                                text="1. Measure a known object\n2. Enter the known value below\n3. Click Calibrate",
                                font=("Segoe UI", 9),
                                fg="#6c757d", bg='white',
                                justify=tk.LEFT)
        instructions1.pack(anchor='w', pady=(0, 8))
        
        # Input section with better styling
        input_container = tk.Frame(m1_content, bg='#f8f9fa', relief=tk.FLAT)
        input_container.pack(fill='x', pady=6)
        
        known_frame = tk.Frame(input_container, bg='#f8f9fa')
        known_frame.pack(padx=12, pady=10)
        
        tk.Label(known_frame, text="Known Value:", 
                font=("Segoe UI", 9, "bold"),
                fg="#495057", bg='#f8f9fa').pack(side='left', padx=(0, 6))
        
        known_var = tk.DoubleVar(value=10.0)
        known_entry = tk.Entry(known_frame, textvariable=known_var, 
                              width=10, font=("Segoe UI", 10),
                              relief=tk.FLAT, bg='white', fg='#212529',
                              highlightthickness=1, highlightcolor='#5294e2',
                              highlightbackground='#ced4da')
        known_entry.pack(side='left', padx=4, ipady=3)
        
        # Unit label that updates dynamically
        unit_label = tk.Label(known_frame, text=self.config["unit"], 
                             font=("Segoe UI", 9),
                             fg="#6c757d", bg='#f8f9fa')
        unit_label.pack(side='left', padx=(4, 6))
        
        # Store reference for updating
        if not hasattr(self, 'calibration_unit_labels'):
            self.calibration_unit_labels = []
        self.calibration_unit_labels.append(unit_label)
        
        def calibrate_simple():
            known_value = known_var.get()
            # Convert current pixel distance to currently selected unit (without calibration)
            unit = self.normalize_unit(self.config.get("unit", "px"))
            dpi = self.get_screen_dpi()
            if unit == "px":
                current_value = dist
            elif unit == "mm":
                current_value = dist / dpi * 25.4
            elif unit == "cm":
                current_value = dist / dpi * 2.54
            elif unit == "m":
                current_value = dist / dpi * 0.0254
            elif unit == "in":
                current_value = dist / dpi
            elif unit == "um":
                current_value = dist / dpi * 25400
            else:
                current_value = dist

            if current_value > 0:
                # Factor such that formatted value equals known_value in selected unit
                self.config["calibration_factor"] = known_value / current_value
                self.save_config()
                self.draw()
                current_display.config(text=f"📐 Current: {self.format_distance(dist)}")
                parent_window = self.control_panel if self.control_panel and self.control_panel.winfo_exists() else self.root
                messagebox.showinfo("Calibration", 
                                   f"Calibrated!\nFactor: {self.config['calibration_factor']:.4f}", 
                                   parent=parent_window)
        
        cal_btn = tk.Button(known_frame, text="🎯 Calibrate",
                           command=calibrate_simple,
                           bg="#28a745", fg="white", 
                           font=("Segoe UI", 9, "bold"),
                           padx=16, pady=5,
                           relief=tk.FLAT,
                           cursor="hand2",
                           activebackground="#218838",
                           borderwidth=0)
        cal_btn.pack(side='left', padx=6)
        cal_btn.bind("<Enter>", lambda e: cal_btn.config(bg="#218838"))
        cal_btn.bind("<Leave>", lambda e: cal_btn.config(bg="#28a745"))
        
        # Method 2: Manual factor card - more compact
        method2_card = tk.Frame(container, bg='white', relief=tk.FLAT)
        method2_card.pack(fill='x', pady=(0, 10))
        
        # Method 2 header
        m2_header = tk.Frame(method2_card, bg='#fff3cd')
        m2_header.pack(fill='x')
        
        m2_title_frame = tk.Frame(m2_header, bg='#fff3cd')
        m2_title_frame.pack(anchor='w', padx=15, pady=8)
        
        tk.Label(m2_title_frame, text="⚙️", font=("Arial", 11), 
                bg='#fff3cd').pack(side='left', padx=(0, 6))
        tk.Label(m2_title_frame, text="Manual Factor",
                font=("Segoe UI", 10, "bold"),
                fg="#856404", bg='#fff3cd').pack(side='left')
        tk.Label(m2_title_frame, text="ADVANCED",
                font=("Segoe UI", 7, "bold"),
                fg="#856404", bg='#ffeaa7',
                relief=tk.FLAT).pack(side='left', padx=8, ipadx=5, ipady=1)
        
        # Method 2 content
        m2_content = tk.Frame(method2_card, bg='white')
        m2_content.pack(fill='x', padx=15, pady=10)
        
        instructions2 = tk.Label(m2_content,
                                text="Directly set calibration factor (Known ÷ Displayed)",
                                font=("Segoe UI", 9),
                                fg="#6c757d", bg='white',
                                justify=tk.LEFT)
        instructions2.pack(anchor='w', pady=(0, 8))
        
        # Input section
        input_container2 = tk.Frame(m2_content, bg='#f8f9fa', relief=tk.FLAT)
        input_container2.pack(fill='x', pady=6)
        
        factor_frame = tk.Frame(input_container2, bg='#f8f9fa')
        factor_frame.pack(padx=12, pady=10)
        
        tk.Label(factor_frame, text="Factor:", 
                font=("Segoe UI", 9, "bold"),
                fg="#495057", bg='#f8f9fa').pack(side='left', padx=(0, 6))
        
        cal_var = tk.DoubleVar(value=self.config["calibration_factor"])
        cal_entry = tk.Entry(factor_frame, textvariable=cal_var, 
                            width=10, font=("Segoe UI", 10),
                            relief=tk.FLAT, bg='white', fg='#212529',
                            highlightthickness=1, highlightcolor='#5294e2',
                            highlightbackground='#ced4da')
        cal_entry.pack(side='left', padx=4, ipady=3)
        
        def apply_manual_calibration():
            self.config["calibration_factor"] = cal_var.get()
            self.draw()
            current_display.config(text=f"📐 Current: {self.format_distance(dist)}")
            parent_window = self.control_panel if self.control_panel and self.control_panel.winfo_exists() else self.root
            messagebox.showinfo("Calibration", "Manual calibration applied!", parent=parent_window)
        
        apply_btn = tk.Button(factor_frame, text="✓ Apply",
                             command=apply_manual_calibration,
                             bg="#5294e2", fg="white", 
                             font=("Segoe UI", 9, "bold"),
                             padx=16, pady=5,
                             relief=tk.FLAT,
                             cursor="hand2",
                             activebackground="#4a85d4",
                             borderwidth=0)
        apply_btn.pack(side='left', padx=6)
        apply_btn.bind("<Enter>", lambda e: apply_btn.config(bg="#4a85d4"))
        apply_btn.bind("<Leave>", lambda e: apply_btn.config(bg="#5294e2"))
        
        # Reset section - centered
        reset_card = tk.Frame(container, bg='white', relief=tk.FLAT)
        reset_card.pack(fill='x', pady=(0, 10))
        
        reset_content = tk.Frame(reset_card, bg='white')
        reset_content.pack(padx=12, pady=10)
        
        def reset_calibration():
            cal_var.set(1.0)
            self.config["calibration_factor"] = 1.0
            self.draw()
            current_display.config(text=f"📐 Current: {self.format_distance(dist)}")
            parent_window = self.control_panel if self.control_panel and self.control_panel.winfo_exists() else self.root
            messagebox.showinfo("Calibration", "Reset to default (1.0)", parent=parent_window)
        
        reset_btn = tk.Button(reset_content, text="🔄 Reset (1.0)",
                             command=reset_calibration,
                             bg="#6c757d", fg="white", 
                             font=("Segoe UI", 9, "bold"),
                             padx=18, pady=6,
                             relief=tk.FLAT,
                             cursor="hand2",
                             activebackground="#5a6268",
                             borderwidth=0)
        reset_btn.pack()
        reset_btn.bind("<Enter>", lambda e: reset_btn.config(bg="#5a6268"))
        reset_btn.bind("<Leave>", lambda e: reset_btn.config(bg="#6c757d"))
        
        # Example card - below reset
        example_card = tk.Frame(container, bg='white', relief=tk.FLAT)
        example_card.pack(fill='x', pady=(0, 5))
        
        ex_content = tk.Frame(example_card, bg='white')
        ex_content.pack(fill='x', padx=12, pady=10)
        
        tk.Label(ex_content, text="💡 Example:",
                font=("Segoe UI", 9, "bold"),
                fg="#004085", bg='white').pack(anchor='w')
        
        example_text = "Measure 10cm, shows 9.5cm\n→ Enter 10, click Calibrate\n→ Or: 10÷9.5=1.053"
        tk.Label(ex_content, text=example_text,
                font=("Segoe UI", 8), fg="#495057", bg='white',
                justify=tk.LEFT).pack(anchor='w', pady=(4, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_about_tab(self, notebook):
        """Create About tab"""
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text="  ℹ️ About  ")
        
        # Create canvas with scrollbar for scrollable content
        canvas = tk.Canvas(about_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(about_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Create centered content container
        container = tk.Frame(scrollable_frame, bg='#f8f9fa')
        container.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Main card with shadow effect
        card = tk.Frame(container, bg='white', relief=tk.FLAT, bd=0)
        card.pack(fill='both', expand=True)
        
        # Add subtle border
        border_frame = tk.Frame(card, bg='#e1e4e8', height=1)
        border_frame.pack(fill='x', side='top')
        
        # Content inside card
        content_frame = tk.Frame(card, bg='white')
        content_frame.pack(fill='both', expand=True, padx=40, pady=30)
        
        # Logo/Title with icon
        title_frame = tk.Frame(content_frame, bg='white')
        title_frame.pack(pady=(0, 8))
        
        title_label = tk.Label(title_frame, text="📏 ScreenRuler Pro",
                               font=("Segoe UI", 26, "bold"),
                               fg="#5294e2", bg='white')
        title_label.pack()
        
        # Version badge
        version_frame = tk.Frame(content_frame, bg='#e8f4f8', relief=tk.FLAT)
        version_frame.pack(pady=8)
        version_label = tk.Label(version_frame, text="Version 2.0.0",
                                font=("Segoe UI", 11, "bold"),
                                fg="#2c7a9e", bg='#e8f4f8')
        version_label.pack(padx=16, pady=6)
        
        # Separator line
        sep1 = tk.Frame(content_frame, bg='#e1e4e8', height=1)
        sep1.pack(fill='x', pady=20)
        
        # Developer section with better layout
        dev_section = tk.Frame(content_frame, bg='white')
        dev_section.pack(pady=8)
        
        dev_label = tk.Label(dev_section, text="Developed by",
                            font=("Segoe UI", 10),
                            fg="#6c757d", bg='white')
        dev_label.pack(pady=(0, 6))
        
        name_label = tk.Label(dev_section, text="Dinuka Adasooriya",
                             font=("Segoe UI", 18, "bold"),
                             fg="#2d3436", bg='white')
        name_label.pack(pady=4)
        
        # Affiliation with icon
        affil_frame = tk.Frame(dev_section, bg='white')
        affil_frame.pack(pady=8)
        
        tk.Label(affil_frame, text="🏛️", font=("Arial", 13), bg='white').pack()
        affiliation_label = tk.Label(affil_frame,
                                    text="Department of Oral Biology\nYonsei University College of Dentistry",
                                    font=("Segoe UI", 10),
                                    fg="#6c757d", bg='white',
                                    justify=tk.CENTER)
        affiliation_label.pack(pady=4)
        
        # Email with better styling
        email_container = tk.Frame(dev_section, bg='#f0f7ff', relief=tk.FLAT)
        email_container.pack(pady=12)
        
        email_inner = tk.Frame(email_container, bg='#f0f7ff')
        email_inner.pack(padx=20, pady=10)
        
        tk.Label(email_inner, text="📧", font=("Arial", 14), bg='#f0f7ff').pack(side='left', padx=6)
        email_label = tk.Label(email_inner, text="dinuka90@yuhs.ac",
                              font=("Segoe UI", 11, "underline"),
                              fg="#5294e2", bg='#f0f7ff',
                              cursor="hand2")
        email_label.pack(side='left')
        
        # Description
        sep2 = tk.Frame(content_frame, bg='#e1e4e8', height=1)
        sep2.pack(fill='x', pady=20)
        
        desc_label = tk.Label(content_frame,
                             text="Professional on-screen measurement tool\nwith advanced calibration and features",
                             font=("Segoe UI", 11),
                             fg="#6c757d", bg='white',
                             justify=tk.CENTER)
        desc_label.pack(pady=12)
        
        # License section
        sep3 = tk.Frame(content_frame, bg='#e1e4e8', height=1)
        sep3.pack(fill='x', pady=20)
        
        lic_title = tk.Label(content_frame, text="📜 License", 
                            font=("Segoe UI", 13, "bold"), 
                            fg="#2d3436", bg='white')
        lic_title.pack(pady=(4, 8))
        
        lic_text = tk.Label(
            content_frame,
            text="This program is licensed under the GNU General Public License v3.0 (GPL-3.0).\n"
                 "You are free to run, study, share, and modify the software, provided that\n"
                 "distributions of derivative works are also licensed under GPL-3.0.",
            font=("Segoe UI", 9), fg="#6c757d", bg='white', justify=tk.CENTER
        )
        lic_text.pack(pady=8)
        
        # License button with better styling
        btn_frame = tk.Frame(content_frame, bg='white')
        btn_frame.pack(pady=12)
        
        lic_btn = tk.Button(
            btn_frame,
            text="📄  View Full License",
            command=self.open_license_window,
            bg="#5294e2", fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=28, pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            activebackground="#4a85d4",
            activeforeground="white",
            borderwidth=0
        )
        lic_btn.pack()
        
        # Hover effect
        lic_btn.bind("<Enter>", lambda e: lic_btn.config(bg="#4a85d4"))
        lic_btn.bind("<Leave>", lambda e: lic_btn.config(bg="#5294e2"))
        
        # GitHub Section
        sep4 = tk.Frame(content_frame, bg='#e1e4e8', height=1)
        sep4.pack(fill='x', pady=20)
        
        github_frame = tk.Frame(content_frame, bg='white')
        github_frame.pack(pady=12)
        
        github_title = tk.Label(github_frame, text="Open Source",
                               font=("Segoe UI", 11, "bold"),
                               fg="#2d3436", bg='white')
        github_title.pack(pady=(0, 8))
        
        # GitHub button with logo
        github_btn_container = tk.Frame(github_frame, bg='#f6f8fa', relief=tk.FLAT)
        github_btn_container.pack(pady=8)
        
        github_inner = tk.Frame(github_btn_container, bg='#f6f8fa')
        github_inner.pack(padx=20, pady=12)
        
        # Try to load GitHub icon
        github_icon_label = None
        icon_loaded = False
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'GitHub_Black.ico')
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                icon_image = icon_image.resize((20, 20), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_image)
                github_icon_label = tk.Label(github_inner, image=icon_photo, bg='#f6f8fa')
                github_icon_label.image = icon_photo  # Keep reference
                github_icon_label.pack(side='left', padx=(0, 8))
                icon_loaded = True
        except Exception:
            pass
        
        # Fallback to text icon if icon couldn't be loaded
        if not icon_loaded:
            tk.Label(github_inner, text="🐙", font=("Arial", 16), bg='#f6f8fa').pack(side='left', padx=(0, 8))
        
        github_link = tk.Label(github_inner, text="View on GitHub",
                              font=("Segoe UI", 11, "underline"),
                              fg="#0366d6", bg='#f6f8fa',
                              cursor="hand2")
        github_link.pack(side='left')
        
        def open_github(event=None):
            import webbrowser
            webbrowser.open("https://github.com/Dinuka0001/ScreenRuler-Pro")
        
        github_link.bind("<Button-1>", open_github)
        if github_icon_label:
            github_icon_label.bind("<Button-1>", open_github)
        
        # Hover effects
        def on_enter(e):
            github_link.config(fg="#0256c7")
        
        def on_leave(e):
            github_link.config(fg="#0366d6")
        
        github_link.bind("<Enter>", on_enter)
        github_link.bind("<Leave>", on_leave)
        
        # Copyright
        tk.Frame(content_frame, bg='white', height=10).pack()
        copyright_label = tk.Label(content_frame,
                                  text="© 2025 All Rights Reserved",
                                  font=("Segoe UI", 9),
                                  fg="#adb5bd", bg='white')
        copyright_label.pack(pady=(8, 0))

    def open_license_window(self):
        """Open a window to display the GPL-3.0 license text.
        If a LICENSE file exists in the application directory, its contents are shown;
        otherwise, a summary and link are displayed.
        """
        win = tk.Toplevel(self.root)
        win.title("GNU GPL v3.0 License")
        win.geometry("700x600")
        win.attributes('-topmost', True)
        win.configure(bg='#f5f6f7')
        frame = tk.Frame(win, bg='#f5f6f7')
        frame.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(frame, background='#e7e8eb', troughcolor='#f5f6f7', activebackground='#5294e2')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(
            frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg='white', fg='#5c616c',
            padx=16, pady=12,
            yscrollcommand=scrollbar.set,
            relief=tk.FLAT,
        )
        text_widget.pack(fill='both', expand=True)
        scrollbar.config(command=text_widget.yview)

        license_path = os.path.join(os.path.dirname(__file__), 'LICENSE')
        content = None
        try:
            if os.path.exists(license_path):
                with open(license_path, 'r', encoding='utf-8') as f:
                    content = f.read()
        except Exception:
            content = None

        if content:
            text_widget.insert('1.0', content)
        else:
            fallback = (
                "GNU GENERAL PUBLIC LICENSE\n"
                "Version 3, 29 June 2007\n\n"
                "This program is free software: you can redistribute it and/or modify\n"
                "it under the terms of the GNU General Public License as published by\n"
                "the Free Software Foundation, either version 3 of the License, or\n"
                "(at your option) any later version.\n\n"
                "You should have received a copy of the GNU General Public License\n"
                "along with this program. If not, see https://www.gnu.org/licenses/gpl-3.0.txt\n\n"
                "Note: Place a full LICENSE file next to the application to display\n"
                "the complete license text here."
            )
            text_widget.insert('1.0', fallback)

        text_widget.config(state='disabled')

    def cycle_theme(self, event=None):
        """Cycle through themes"""
        themes = list(self.themes.keys())
        current_idx = themes.index(self.config["theme"])
        next_idx = (current_idx + 1) % len(themes)
        self.set_theme(themes[next_idx])
        self.show_notification(f"Theme: {themes[next_idx].capitalize()}")

    def cycle_unit(self, event=None):
        """Cycle through units"""
        units = ["px", "um", "mm", "cm", "m", "in"]
        unit_names = ["Pixels", "Micrometers", "Millimeters", "Centimeters", "Meters", "Inches"]
        current_unit = self.normalize_unit(self.config.get("unit", "px"))
        current_idx = units.index(current_unit) if current_unit in units else 0
        next_idx = (current_idx + 1) % len(units)
        self.config["unit"] = units[next_idx]
        self.save_config()
        if self.unit_var:
            self.unit_var.set(self.config["unit"])
        self.draw()
        self.show_notification(f"Unit: {unit_names[next_idx]}")

    def cycle_lock(self, event=None):
        """Cycle through angle locks"""
        locks = [None, 0, 90]
        current_idx = locks.index(self.config["lock_angle"])
        next_idx = (current_idx + 1) % len(locks)
        self.config["lock_angle"] = locks[next_idx]
        self.save_config()
        self.update_lock_button()
        lock_text = "None" if locks[next_idx] is None else ("Horizontal" if locks[next_idx] == 0 else "Vertical")
        self.show_notification(f"Lock: {lock_text}")
    
    def cycle_endpoint_style(self, event=None):
        """Cycle through endpoint styles"""
        styles = ["none", "circle", "flat", "crosslines", "arrow"]
        style_names = ["None", "Circle", "Square", "Crosslines", "Arrow"]
        current_style = self.config.get("endpoint_style", "circle")
        current_idx = styles.index(current_style) if current_style in styles else 1
        next_idx = (current_idx + 1) % len(styles)
        self.config["endpoint_style"] = styles[next_idx]
        self.save_config()
        self.draw()
        self.show_notification(f"Endpoint: {style_names[next_idx]}")

    def toggle_guides(self, event=None):
        """Toggle guide lines"""
        self.config["show_guides"] = not self.config["show_guides"]
        self.save_config()
        self.draw()

    def increase_opacity(self, event=None):
        """Increase opacity"""
        current = self.config["opacity_work"]
        self.config["opacity_work"] = min(1.0, current + 0.05)
        if self.is_passthrough:
            self.root.attributes('-alpha', self.config["opacity_work"])
        self.save_config()
        self.show_notification(f"Opacity: {int(self.config['opacity_work']*100)}%")

    def decrease_opacity(self, event=None):
        """Decrease opacity"""
        current = self.config["opacity_work"]
        self.config["opacity_work"] = max(0.3, current - 0.05)
        if self.is_passthrough:
            self.root.attributes('-alpha', self.config["opacity_work"])
        self.save_config()
        self.show_notification(f"Opacity: {int(self.config['opacity_work']*100)}%")

    def show_notification(self, text):
        """Show temporary notification in the toolbar measurement display."""
        # Store inline notification and update display
        self.inline_notification = text
        self.draw()
        # Clear after a short delay
        self.root.after(1800, self.clear_notification)

    def clear_notification(self):
        """Clear the inline notification and redraw."""
        if self.inline_notification is not None:
            self.inline_notification = None
            self.draw()

    def copy_measurement(self, event=None):
        """Copy current measurement to clipboard"""
        if self.config["mode"] == "angle":
            # Angle mode - copy angle and arm lengths
            cx, cy = self.angle_center["x"], self.angle_center["y"]
            ax1, ay1 = self.angle_arm1["x"], self.angle_arm1["y"]
            ax2, ay2 = self.angle_arm2["x"], self.angle_arm2["y"]
            
            dist1 = math.sqrt((ax1 - cx)**2 + (ay1 - cy)**2)
            dist2 = math.sqrt((ax2 - cx)**2 + (ay2 - cy)**2)
            
            angle1 = math.degrees(math.atan2(ay1 - cy, ax1 - cx))
            angle2 = math.degrees(math.atan2(ay2 - cy, ax2 - cx))
            
            if angle1 < 0: angle1 += 360
            if angle2 < 0: angle2 += 360
            
            angle_diff = abs(angle2 - angle1)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
            
            text = f"Angle: {angle_diff:.1f}° | Arm1: {self.format_distance(dist1)} | Arm2: {self.format_distance(dist2)}"
            
            # Add to history
            self.measurement_history.append({
                "angle": angle_diff,
                "arm1": dist1,
                "arm2": dist2,
                "unit": self.config["unit"],
                "time": datetime.now().strftime("%H:%M:%S"),
                "mode": "angle"
            })
        elif self.config["mode"] == "polygon":
            perimeter_px = self.get_polygon_perimeter_px()
            area_px2 = self.get_polygon_area_px2()
            text = f"Perimeter: {self.format_distance(perimeter_px)} | Area: {self.format_area(area_px2)}"

            self.measurement_history.append({
                "perimeter": perimeter_px,
                "area": area_px2,
                "unit": self.config["unit"],
                "time": datetime.now().strftime("%H:%M:%S"),
                "mode": "polygon"
            })
        else:
            # Normal ruler mode (or fallback)
            dist = self.get_distance()
            angle = self.get_angle()
            text = f"{self.format_distance(dist)} | {angle:.1f}°"

            self.measurement_history.append({
                "distance": dist,
                "angle": angle,
                "unit": self.config["unit"],
                "time": datetime.now().strftime("%H:%M:%S"),
                "mode": "ruler"
            })
        
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.show_notification("📋 Copied to clipboard!")

    def ensure_windows_visible(self):
        """Ensure main window and toolbar are visible and on top"""
        try:
            if not self.minimized:
                # Ensure main window is visible
                if self.root.winfo_exists():
                    self.root.deiconify()
                    self.root.lift()
                    self.root.attributes('-topmost', True)
                    
                # Ensure toolbar is visible
                if self.toolbar and self.toolbar.winfo_exists():
                    self.toolbar.deiconify()
                    self.toolbar.lift()
                    self.toolbar.attributes('-topmost', True)
        except Exception as e:
            print(f"Warning: Could not ensure window visibility: {e}")
    
    def toggle_passthrough(self, event=None):
        """Switch between Edit Mode and Work Mode"""
        self.is_passthrough = not self.is_passthrough
        hwnd = self.root.winfo_id()
        
        if self.is_passthrough:
            # Switch to Work mode
            set_click_through(hwnd, True)
            self.root.attributes('-alpha', self.config["opacity_work"])
            # Keep toolbar visible but slightly transparent in work mode
            if self.toolbar and self.toolbar.winfo_exists():
                self.toolbar.attributes('-alpha', 0.9)
        else:
            # Switch to Edit mode
            set_click_through(hwnd, False)
            self.root.attributes('-alpha', self.config["opacity_edit"])
            self.dragging = None
            # Make toolbar more visible in edit mode
            if self.toolbar and self.toolbar.winfo_exists():
                self.toolbar.attributes('-alpha', 0.95)
        
        # Ensure windows remain visible
        self.ensure_windows_visible()
        
        self.update_mode_display()
        self.draw()
    def minimize_toolbar_only(self):
        """Minimize only the toolbar to taskbar, keeping ruler visible"""
        if self.toolbar and self.toolbar.winfo_exists():
            if self.toolbar_minimized:
                # Restore toolbar from taskbar
                self.toolbar.deiconify()
                self.toolbar.lift()
                self.toolbar.attributes('-topmost', True)
                self.toolbar_minimized = False
                self.show_notification("Toolbar restored")
            else:
                # Minimize toolbar to taskbar
                self.toolbar.iconify()
                self.toolbar_minimized = True
                self.show_notification("Toolbar minimized (click taskbar to restore)")
    
    def minimize_to_tray(self):
        """Minimize entire app to system tray"""
        self.root.withdraw()
        if self.toolbar and self.toolbar.winfo_exists():
            self.toolbar.withdraw()
        self.minimized = True
        self.toolbar_minimized = False  # Reset toolbar state when minimizing to tray
        self.show_notification("Minimized to tray")
    
    def toggle_minimize(self, event=None):
        """Minimize to tray or restore window (keyboard shortcut)"""
        if self.minimized:
            self.root.deiconify()
            self.root.lift()
            if self.toolbar and self.toolbar.winfo_exists():
                self.toolbar.deiconify()
                self.toolbar.lift()
            self.minimized = False
            self.toolbar_minimized = False  # Reset toolbar state when restoring
        else:
            self.minimize_to_tray()

    def get_distance(self):
        """Calculate distance in pixels"""
        return math.sqrt((self.p2["x"] - self.p1["x"])**2 + (self.p2["y"] - self.p1["y"])**2)

    def get_polygon_perimeter_px(self):
        """Return polygon perimeter in raw pixels."""
        pts = self.polygon_points
        n = len(pts)
        if n < 2:
            return 0.0
        perim = 0.0
        for i in range(n):
            x1, y1 = pts[i]["x"], pts[i]["y"]
            x2, y2 = pts[(i + 1) % n]["x"], pts[(i + 1) % n]["y"]
            perim += math.hypot(x2 - x1, y2 - y1)
        return perim

    def get_polygon_area_px2(self):
        """Return polygon area in pixel^2 using the shoelace formula."""
        pts = self.polygon_points
        n = len(pts)
        if n < 3:
            return 0.0
        area = 0.0
        for i in range(n):
            x1, y1 = pts[i]["x"], pts[i]["y"]
            x2, y2 = pts[(i + 1) % n]["x"], pts[(i + 1) % n]["y"]
            area += x1 * y2 - x2 * y1
        return abs(area) / 2.0

    def format_distance(self, pixels):
        """Format distance based on selected unit"""
        # Apply calibration factor
        calibrated_pixels = pixels * float(self.config.get("calibration_factor", 1.0))

        unit = self.normalize_unit(self.config.get("unit", "px"))
        dpi = self.get_screen_dpi()
        if unit == "px":
            return f"{int(calibrated_pixels)} px"
        elif unit == "mm":
            mm = calibrated_pixels / dpi * 25.4
            return f"{mm:.2f} mm"
        elif unit == "cm":
            cm = calibrated_pixels / dpi * 2.54
            return f"{cm:.2f} cm"
        elif unit == "m":
            meters = calibrated_pixels / dpi * 0.0254
            return f"{meters:.4f} m"
        elif unit == "in":
            inches = calibrated_pixels / dpi
            return f"{inches:.2f} in"
        elif unit == "um":
            um = calibrated_pixels / dpi * 25400
            return f"{um:.1f} µm"
        return f"{int(calibrated_pixels)} px"

    def format_area(self, pixels_squared):
        """Format area based on selected unit squared."""
        if pixels_squared <= 0:
            return "0"

        unit = self.normalize_unit(self.config.get("unit", "px"))
        calib = float(self.config.get("calibration_factor", 1.0))
        dpi = self.get_screen_dpi()

        def px_to_unit_length(px_val: float) -> float:
            if unit == "px":
                return px_val * calib
            if unit == "mm":
                return (px_val * calib) / dpi * 25.4
            if unit == "cm":
                return (px_val * calib) / dpi * 2.54
            if unit == "m":
                return (px_val * calib) / dpi * 0.0254
            if unit == "in":
                return (px_val * calib) / dpi
            if unit == "um":
                return (px_val * calib) / dpi * 25400
            return px_val * calib

        side = math.sqrt(pixels_squared)
        unit_side = px_to_unit_length(side)
        area_unit = unit_side ** 2

        suffix = {
            "px": "px^2",
            "mm": "mm^2",
            "cm": "cm^2",
            "m": "m^2",
            "in": "in^2",
            "um": "µm^2",
        }.get(unit, "px^2")

        # Choose formatting based on magnitude
        if area_unit >= 100:
            return f"{area_unit:,.1f} {suffix}"
        if area_unit >= 1:
            return f"{area_unit:.2f} {suffix}"
        return f"{area_unit:.4f} {suffix}"

    def get_angle(self):
        """Calculate angle in degrees"""
        dx = self.p2["x"] - self.p1["x"]
        dy = self.p2["y"] - self.p1["y"]
        degrees = math.degrees(math.atan2(dy, dx))
        return degrees if degrees >= 0 else degrees + 360
    
    def get_angle_diff(self):
        """Get angle difference in angle mode"""
        cx, cy = self.angle_center["x"], self.angle_center["y"]
        ax1, ay1 = self.angle_arm1["x"], self.angle_arm1["y"]
        ax2, ay2 = self.angle_arm2["x"], self.angle_arm2["y"]
        
        angle1 = math.degrees(math.atan2(ay1 - cy, ax1 - cx))
        angle2 = math.degrees(math.atan2(ay2 - cy, ax2 - cx))
        
        # Normalize angles to 0-360
        if angle1 < 0: angle1 += 360
        if angle2 < 0: angle2 += 360
        
        # Calculate the angle between arms (always positive, acute angle preferred)
        angle_diff = abs(angle2 - angle1)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        return angle_diff

    def draw(self):
        """Main drawing function"""
        try:
            self.canvas.delete("all")
            
            if self.minimized:
                return

            # Choose color based on mode
            current_color = self.config["color_pass"] if self.is_passthrough else self.config["color_active"]

            # Draw based on selected mode and visibility
            current_mode = self.config["mode"]
            is_visible = self.mode_visible.get(current_mode, True)
            
            if is_visible:
                if current_mode == "angle":
                    self.draw_angle_mode(current_color)
                elif current_mode == "polygon":
                    self.draw_polygon_mode(current_color)
                else:
                    self.draw_ruler_mode(current_color)
            
            # Draw text objects (always visible when text mode is active or objects exist)
            self.draw_text_objects(current_color)
            
            # Update measurement display in toolbar
            self.update_measurement_display()
        except tk.TclError as e:
            # Canvas or window may have been destroyed
            print(f"Warning: Could not draw ruler: {e}")
        except Exception as e:
            print(f"Error in draw method: {e}")
            # Try to continue with basic ruler
            try:
                current_color = self.config.get("color_active", "#00FFFF")
                self.draw_ruler_mode(current_color)
            except Exception:
                pass
    
    def update_measurement_display(self):
        """Update the measurement display in the toolbar"""
        try:
            # Temporary notifications take precedence
            if self.inline_notification:
                value_text = self.inline_notification
            else:
                if self.config["mode"] == "angle":
                    angle_diff = self.get_angle_diff()
                    value_text = f"{angle_diff:.1f}°"
                elif self.config["mode"] == "polygon":
                    perimeter_px = self.get_polygon_perimeter_px()
                    area_px2 = self.get_polygon_area_px2()
                    perim_text = self.format_distance(perimeter_px)
                    area_text = self.format_area(area_px2)
                    value_text = f"P: {perim_text}, A: {area_text}"
                else:
                    dist = self.get_distance()
                    angle = self.get_angle()
                    dist_text = self.format_distance(dist)
                    value_text = f"{dist_text}, {angle:.1f}°"

            # Update measurement value label (no mode tag - it's now in the button)
            if hasattr(self, 'measurement_value_label'):
                try:
                    if self.measurement_value_label.winfo_exists():
                        self.measurement_value_label.config(text=value_text)
                        return
                except tk.TclError:
                    pass
        except Exception as e:
            print(f"Warning: Could not update measurement display: {e}")
            try:
                if hasattr(self, 'measurement_value_label') and self.measurement_value_label.winfo_exists():
                    self.measurement_value_label.config(text="—")
            except Exception:
                pass
    
    def draw_endpoint(self, x, y, current_color, size=10, angle=None):
        """Draw endpoint based on the selected style
        
        Args:
            x, y: endpoint coordinates
            current_color: color for the endpoint
            size: base size for the endpoint (default 10)
            angle: optional angle for arrow direction (in degrees)
        """
        style = self.config.get("endpoint_style", "circle")
        
        if style == "none":
            # Don't draw anything
            return
        elif style == "circle":
            # Current default - circle with outline
            r = size
            self.canvas.create_oval(x-r, y-r, x+r, y+r, 
                                   outline=current_color, width=3, 
                                   fill=self.config["bg_color"])
        elif style == "flat":
            # Square endpoint
            r = size
            self.canvas.create_rectangle(x-r, y-r, x+r, y+r, 
                                         outline=current_color, width=3, 
                                         fill=self.config["bg_color"])
        elif style == "crosslines":
            # Crosshair style
            length = size * 1.5
            self.canvas.create_line(x-length, y, x+length, y, 
                                   fill=current_color, width=2)
            self.canvas.create_line(x, y-length, x, y+length, 
                                   fill=current_color, width=2)
            # Small circle in the center
            r = size * 0.4
            self.canvas.create_oval(x-r, y-r, x+r, y+r, 
                                   outline=current_color, width=2, 
                                   fill=self.config["bg_color"])
        elif style == "arrow":
            # Arrow head pointing away from the line
            if angle is not None:
                # Convert angle to radians
                angle_rad = math.radians(angle)
                # Arrow dimensions
                arrow_length = size * 1.5
                arrow_width = size * 0.8
                
                # Calculate arrow points
                # Tip of arrow at endpoint
                tip_x, tip_y = x, y
                # Base of arrow
                base_x = x - arrow_length * math.cos(angle_rad)
                base_y = y - arrow_length * math.sin(angle_rad)
                # Perpendicular for arrow wings
                perp_x = arrow_width * math.sin(angle_rad)
                perp_y = -arrow_width * math.cos(angle_rad)
                
                # Draw filled triangle
                points = [
                    tip_x, tip_y,
                    base_x + perp_x, base_y + perp_y,
                    base_x - perp_x, base_y - perp_y
                ]
                self.canvas.create_polygon(points, 
                                          fill=current_color, 
                                          outline=current_color, 
                                          width=2)
            else:
                # Fallback to circle if no angle provided
                r = size
                self.canvas.create_oval(x-r, y-r, x+r, y+r, 
                                       outline=current_color, width=3, 
                                       fill=self.config["bg_color"])
    
    def draw_ruler_mode(self, current_color):
        """Draw ruler in normal or fraction mode"""
        x1, y1 = self.p1["x"], self.p1["y"]
        x2, y2 = self.p2["x"], self.p2["y"]
        dist = self.get_distance()

        # 1. Draw Guides (optional)
        if self.config["show_guides"]:
            self.canvas.create_line(x1, 0, x1, self.screen_height, fill="#222", dash=(4, 4))
            self.canvas.create_line(0, y1, self.screen_width, y1, fill="#222", dash=(4, 4))

        # 2. Main Line
        self.canvas.create_line(x1, y1, x2, y2, fill=current_color, width=self.config["ruler_thickness"], capstyle=tk.ROUND)
        
        # 3. Ticks
        self.draw_ticks(x1, y1, x2, y2, dist, current_color)

        # 4. Endpoints (Handles)
        # Calculate angle for arrow direction
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        # Draw endpoints with arrows pointing outward
        self.draw_endpoint(x1, y1, current_color, size=10, angle=angle + 180)
        self.draw_endpoint(x2, y2, current_color, size=10, angle=angle)

        # Measurement text is now shown in the toolbar instead of on canvas

    def draw_polygon_mode(self, current_color):
        """Draw polygon, showing perimeter and area."""
        try:
            if not self.polygon_points:
                self.init_polygon_default()

            pts = self.polygon_points
            n = len(pts)
            if n < 2:
                return

            # Draw edges
            for i in range(n):
                x1, y1 = pts[i]["x"], pts[i]["y"]
                x2, y2 = pts[(i + 1) % n]["x"], pts[(i + 1) % n]["y"]
                self.canvas.create_line(x1, y1, x2, y2, fill=current_color, width=self.config["ruler_thickness"], capstyle=tk.ROUND)

            # Vertices (handles) - draw endpoints at each vertex
            for i, p in enumerate(pts):
                # Calculate angle from this point to the next
                next_p = pts[(i + 1) % n]
                angle = math.degrees(math.atan2(next_p["y"] - p["y"], next_p["x"] - p["x"]))
                self.draw_endpoint(p["x"], p["y"], current_color, size=8, angle=angle)
        except Exception as e:
            print(f"Warning: Error drawing polygon: {e}")
    
    def draw_angle_mode(self, current_color):
        """Draw angle measurement mode with two rotating arms"""
        cx, cy = self.angle_center["x"], self.angle_center["y"]
        ax1, ay1 = self.angle_arm1["x"], self.angle_arm1["y"]
        ax2, ay2 = self.angle_arm2["x"], self.angle_arm2["y"]
        
        # Draw guide lines if enabled
        if self.config["show_guides"]:
            self.canvas.create_line(cx, 0, cx, self.screen_height, fill="#222", dash=(4, 4))
            self.canvas.create_line(0, cy, self.screen_width, cy, fill="#222", dash=(4, 4))
        
        # Draw the two arms
        self.canvas.create_line(cx, cy, ax1, ay1, fill=current_color, width=self.config["ruler_thickness"], capstyle=tk.ROUND)
        self.canvas.create_line(cx, cy, ax2, ay2, fill=current_color, width=self.config["ruler_thickness"], capstyle=tk.ROUND)
        
        # Draw ticks on both arms
        dist1 = math.sqrt((ax1 - cx)**2 + (ay1 - cy)**2)
        dist2 = math.sqrt((ax2 - cx)**2 + (ay2 - cy)**2)
        self.draw_ticks(cx, cy, ax1, ay1, dist1, current_color)
        self.draw_ticks(cx, cy, ax2, ay2, dist2, current_color)
        
        # Draw center point (larger)
        r_center = 15
        self.canvas.create_oval(cx-r_center, cy-r_center, cx+r_center, cy+r_center, 
                               outline=current_color, width=4, fill=self.config["bg_color"])
        
        # Draw arm endpoints with angle information for arrows
        angle1 = math.degrees(math.atan2(ay1 - cy, ax1 - cx))
        angle2 = math.degrees(math.atan2(ay2 - cy, ax2 - cx))
        self.draw_endpoint(ax1, ay1, current_color, size=10, angle=angle1)
        self.draw_endpoint(ax2, ay2, current_color, size=10, angle=angle2)
        
        # Draw arc to visualize angle
        # Normalize angles to 0-360
        if angle1 < 0: angle1 += 360
        if angle2 < 0: angle2 += 360
        
        # Calculate the angle between arms (always positive, acute angle preferred)
        angle_diff = abs(angle2 - angle1)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        # Draw arc
        arc_radius = 60
        arc_extent = angle2 - angle1
        if abs(arc_extent) > 180:
            if arc_extent > 0:
                arc_extent = arc_extent - 360
            else:
                arc_extent = arc_extent + 360
        
        self.canvas.create_arc(cx-arc_radius, cy-arc_radius, cx+arc_radius, cy+arc_radius,
                              start=angle1, extent=arc_extent, outline=current_color, width=2, style=tk.ARC)
        
        # Measurement text is now shown in the toolbar instead of on canvas
    
    def draw_text_objects(self, current_color):
        """Draw all text objects on canvas"""
        if not self.text_objects or not self.text_visible:
            return
        
        try:
            for i, text_obj in enumerate(self.text_objects):
                x = text_obj["x"]
                y = text_obj["y"]
                width = text_obj["width"]
                height = text_obj["height"]
                text = text_obj["text"]
                
                # Get text formatting
                font_family = text_obj.get("font_family", "Arial")
                font_size = text_obj.get("font_size", 24)
                bold = text_obj.get("bold", False)
                italic = text_obj.get("italic", False)
                underline = text_obj.get("underline", False)
                outline = text_obj.get("outline", False)
                
                # Build font tuple
                font_weight = "bold" if bold else "normal"
                font_slant = "italic" if italic else "roman"
                font_tuple = (font_family, font_size, f"{font_weight} {font_slant}")
                
                # Draw outline box if enabled
                if outline:
                    self.canvas.create_rectangle(
                        x, y, x + width, y + height,
                        outline=current_color,
                        width=2
                    )
                
                # Draw selection highlight if this text is selected
                if hasattr(self, 'selected_text_index') and self.selected_text_index == i:
                    # Draw a thick highlight border around selected text
                    self.canvas.create_rectangle(
                        x - 3, y - 3, x + width + 3, y + height + 3,
                        outline='#FFD700',  # Gold color for selection
                        width=3,
                        dash=(5, 3)  # Dashed line
                    )
                
                # Draw text centered in the box
                text_x = x + width / 2
                text_y = y + height / 2
                
                text_id = self.canvas.create_text(
                    text_x, text_y,
                    text=text,
                    fill=current_color,
                    font=font_tuple,
                    anchor='center'
                )
                
                # Apply underline if needed (tkinter canvas text doesn't support underline directly)
                if underline:
                    # Get text bounding box
                    bbox = self.canvas.bbox(text_id)
                    if bbox:
                        x1, y1, x2, y2 = bbox
                        # Draw line under text
                        self.canvas.create_line(
                            x1, y2 + 2, x2, y2 + 2,
                            fill=current_color, width=2
                        )
        except Exception as e:
            print(f"Warning: Error drawing text objects: {e}")

    def init_polygon_at_position(self, cx, cy):
        """Initialize a polygon at the specified center position."""
        try:
            w, h = 320, 200
            sides = self.config.get("polygon_sides", 4)
            
            if sides == 4:
                # Rectangle
                self.polygon_points = [
                    {"x": cx - w / 2, "y": cy - h / 2},
                    {"x": cx + w / 2, "y": cy - h / 2},
                    {"x": cx + w / 2, "y": cy + h / 2},
                    {"x": cx - w / 2, "y": cy + h / 2},
                ]
            else:
                # Regular polygon
                radius = 150
                self.polygon_points = []
                for i in range(sides):
                    angle = 2 * math.pi * i / sides - math.pi / 2
                    self.polygon_points.append({
                        "x": cx + radius * math.cos(angle),
                        "y": cy + radius * math.sin(angle)
                    })
        except Exception as e:
            print(f"Warning: Could not initialize polygon: {e}")
            # Absolute fallback
            self.polygon_points = [
                {"x": cx - 160, "y": cy - 100},
                {"x": cx + 160, "y": cy - 100},
                {"x": cx + 160, "y": cy + 100},
                {"x": cx - 160, "y": cy + 100},
            ]
    
    def init_polygon_default(self):
        """Initialize a default 4-point polygon centered on screen."""
        cx = self.virtual_x + (self.virtual_w / 2)
        cy = self.virtual_y + (self.virtual_h / 2)
        self.init_polygon_at_position(cx, cy)
    
    def get_color_with_alpha(self, hex_color):
        """Convert hex color to RGB tuple for PIL"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def apply_opacity_to_color(self, hex_color, opacity):
        """Apply opacity to a hex color. Returns a color suitable for canvas."""
        # For tkinter canvas, we'll use a darkened version when opacity is low
        # This is a workaround since tkinter doesn't support alpha directly
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Blend with black based on opacity
        r = int(r * opacity)
        g = int(g * opacity)
        b = int(b * opacity)
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_ticks(self, x1, y1, x2, y2, dist, color):
        """Draw measurement ticks with unit-aware major/minor steps"""
        if dist <= 0:
            return

        ux = (x2 - x1) / dist
        uy = (y2 - y1) / dist
        nx, ny = -uy, ux

        # Fractions mode keeps equal partitions as before
        if self.config["show_fractions"]:
            fraction_count = max(2, self.config["fraction_count"])
            # Only iterate up to fraction_count (inclusive) to avoid drawing beyond ruler end
            for i in range(fraction_count + 1):
                t = i / fraction_count
                tick_dist = t * dist
                
                # Draw tick at this fraction position
                px = x1 + ux * tick_dist
                py = y1 + uy * tick_dist
                length = 16 if i in (0, fraction_count) else 12
                self.canvas.create_line(px + nx*length, py + ny*length,
                                        px - nx*length, py - ny*length,
                                        fill=color, width=2)
                if self.config["show_labels"] and 0 < i < fraction_count:
                    label = f"{i}/{fraction_count}"
                    self.canvas.create_text(px + nx*26, py + ny*26, text=label,
                                            fill=color, font=("Arial", 8, "normal"))
            return

        # Unit-aware ticks
        unit = self.normalize_unit(self.config.get("unit", "px"))
        calib = max(1e-6, float(self.config.get("calibration_factor", 1.0)))
        dpi = self.get_screen_dpi()

        def px_per(unit_name: str) -> float:
            if unit_name == "in":
                return dpi / calib
            if unit_name == "cm":
                return (dpi / 2.54) / calib
            if unit_name == "mm":
                return (dpi / 25.4) / calib
            if unit_name == "um":
                return (dpi / 25400.0) / calib
            if unit_name == "m":
                return (dpi / 0.0254) / calib
            # px
            return 1.0  # px not adjusted by calibration for spacing

        # Determine minor step size in pixels and hierarchy
        # Initialize medium2_mult to avoid unbound variable error (only used for inches)
        medium2_mult = 0
        
        if unit == "px":
            minor_px = max(5, int(self.config.get("tick_spacing", 20)))
            # Hierarchy: minor, medium every x5, major every x10
            medium_mult, major_mult = 5, 10
            label_every = major_mult
            label_format = lambda i: f"{i*minor_px} px"
        elif unit == "in":
            base = px_per("in")
            minor_px = base / 8.0  # 1/8 inch
            # Normalize to at least 8px between ticks for readability
            min_pixels = 8.0
            if minor_px < min_pixels:
                scale = math.ceil(min_pixels / minor_px)
                minor_px *= scale
            # Mod pattern: 8 -> 1", 4 -> 1/2", 2 -> 1/4"
            medium2_mult, medium_mult, major_mult = 2, 4, 8
            label_every = major_mult
            def label_format(i):
                inches = (i * minor_px) / (px_per("in"))
                return f"{int(round(inches))} in"
        elif unit == "cm":
            base = px_per("cm")
            minor_px = base * 0.1  # 1 mm
            min_pixels = 6.0
            if minor_px < min_pixels:
                scale = math.ceil(min_pixels / minor_px)
                minor_px *= scale
            medium_mult, major_mult = 5, 10   # 0.5cm, 1cm
            label_every = major_mult
            def label_format(i):
                cm_val = (i * minor_px) / base
                return f"{int(round(cm_val))} cm"
        elif unit == "mm":
            base = px_per("mm")
            minor_px = base * 1.0  # 1 mm
            min_pixels = 6.0
            if minor_px < min_pixels:
                scale = math.ceil(min_pixels / minor_px)
                minor_px *= scale
            medium_mult, major_mult = 5, 10   # 5mm, 10mm
            label_every = major_mult
            def label_format(i):
                mm_val = (i * minor_px) / base
                return f"{int(round(mm_val))} mm"
        elif unit == "m":
            base = px_per("m")
            minor_px = base * 0.01  # 1 cm (0.01 m)
            min_pixels = 6.0
            if minor_px < min_pixels:
                scale = math.ceil(min_pixels / minor_px)
                minor_px *= scale
            medium_mult, major_mult = 5, 10   # 0.05m, 0.1m
            label_every = major_mult
            def label_format(i):
                m_val = (i * minor_px) / base
                return f"{m_val:.2f} m"
        else:  # um
            base = px_per("um")
            # Start with 100 µm minor
            minor_px = base * 100.0
            min_pixels = 6.0
            if minor_px < min_pixels:
                scale = math.ceil(min_pixels / minor_px)
                minor_px *= scale
            medium_mult, major_mult = 5, 10   # 500µm, 1000µm
            label_every = major_mult
            def label_format(i):
                um_val = (i * minor_px) / base
                return f"{int(round(um_val))} µm"

        # Draw ticks along the segment
        steps = int(dist // minor_px) + 1
        for i in range(steps + 1):
            tick_dist = i * minor_px
            # Only draw tick if it's within the ruler length
            if tick_dist > dist:
                break
                
            px = x1 + ux * tick_dist
            py = y1 + uy * tick_dist

            # Determine tick length by hierarchy
            length = 10
            if unit == "in":
                if i % major_mult == 0:
                    length = 18
                elif i % medium_mult == 0:
                    length = 14
                elif i % medium2_mult == 0:
                    length = 12
                else:
                    length = 9
            else:
                if i % major_mult == 0:
                    length = 16
                elif i % medium_mult == 0:
                    length = 12
                else:
                    length = 8

            self.canvas.create_line(px + nx*length, py + ny*length,
                                    px - nx*length, py - ny*length,
                                    fill=color, width=2)

            # Labels at major ticks
            if self.config.get("show_labels", True):
                if unit == "in":
                    if i % label_every == 0:
                        self.canvas.create_text(px + nx*28, py + ny*28, text=label_format(i),
                                                fill=color, font=("Arial", 8, "normal"))
                else:
                    if i % label_every == 0:
                        self.canvas.create_text(px + nx*26, py + ny*26, text=label_format(i),
                                                fill=color, font=("Arial", 8, "normal"))

    def on_click(self, event):
        """Handle mouse click"""
        if self.is_passthrough:
            return
        
        # Check if clicking on text objects first (priority over other modes)
        text_clicked = False
        if self.text_objects and self.text_visible:
            for i, text_obj in enumerate(self.text_objects):
                x, y = text_obj["x"], text_obj["y"]
                width, height = text_obj["width"], text_obj["height"]
                
                # Check if clicking inside text box
                if x <= event.x <= x + width and y <= event.y <= y + height:
                    # Toggle selection if clicking on already selected text
                    if self.selected_text_index == i:
                        self.selected_text_index = None  # Deselect
                        self.draw()
                        return
                    else:
                        # Select this text for moving
                        self.text_dragging_index = i
                        self.selected_text_index = i  # Mark as selected
                        self.text_drag_start = {"x": event.x, "y": event.y}
                        text_clicked = True
                        self.draw()  # Redraw to show selection
                        return
        
        # Clear text selection if clicking elsewhere
        if not text_clicked and self.selected_text_index is not None:
            self.selected_text_index = None
            self.draw()  # Redraw to clear selection highlight
        
        if self.config["mode"] == "angle":
            # Angle mode interaction
            cx, cy = self.angle_center["x"], self.angle_center["y"]
            ax1, ay1 = self.angle_arm1["x"], self.angle_arm1["y"]
            ax2, ay2 = self.angle_arm2["x"], self.angle_arm2["y"]
            
            d_center = math.hypot(event.x - cx, event.y - cy)
            d_arm1 = math.hypot(event.x - ax1, event.y - ay1)
            d_arm2 = math.hypot(event.x - ax2, event.y - ay2)
            
            if d_center < 25:
                self.dragging = "angle_center"
            elif d_arm1 < 25:
                self.dragging = "angle_arm1"
            elif d_arm2 < 25:
                self.dragging = "angle_arm2"
            else:
                # Check if clicking near either arm line
                # Check arm 1
                line_len1 = math.hypot(ax1 - cx, ay1 - cy)
                if line_len1 > 0:
                    dist_to_line1 = abs((ay1-cy)*event.x - (ax1-cx)*event.y + ax1*cy - ay1*cx) / line_len1
                    dot1 = ((event.x - cx) * (ax1 - cx) + (event.y - cy) * (ay1 - cy)) / (line_len1 * line_len1)
                    
                    if dist_to_line1 < 10 and 0 <= dot1 <= 1:
                        self.dragging = "angle_arm1"
                        return
                
                # Check arm 2
                line_len2 = math.hypot(ax2 - cx, ay2 - cy)
                if line_len2 > 0:
                    dist_to_line2 = abs((ay2-cy)*event.x - (ax2-cx)*event.y + ax2*cy - ay2*cx) / line_len2
                    dot2 = ((event.x - cx) * (ax2 - cx) + (event.y - cy) * (ay2 - cy)) / (line_len2 * line_len2)
                    
                    if dist_to_line2 < 10 and 0 <= dot2 <= 1:
                        self.dragging = "angle_arm2"
                        return
        elif self.config["mode"] == "polygon":
            # Polygon mode interaction
            if not self.polygon_points:
                self.init_polygon_default()

            # Check vertex hit
            for idx, p in enumerate(self.polygon_points):
                if math.hypot(event.x - p["x"], event.y - p["y"]) < 18:
                    self.polygon_dragging_index = idx
                    return

            # Check near edge to move whole shape
            pts = self.polygon_points
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]["x"], pts[i]["y"]
                x2, y2 = pts[(i + 1) % n]["x"], pts[(i + 1) % n]["y"]
                seg_len = math.hypot(x2 - x1, y2 - y1)
                if seg_len == 0:
                    continue
                dist_to_seg = abs((y2 - y1) * event.x - (x2 - x1) * event.y + x2 * y1 - y2 * x1) / seg_len
                dot = ((event.x - x1) * (x2 - x1) + (event.y - y1) * (y2 - y1)) / (seg_len * seg_len)
                if dist_to_seg < 12 and 0 <= dot <= 1:
                    self.polygon_move_origin = {
                        "start_x": event.x,
                        "start_y": event.y,
                        "points": [dict(p) for p in pts],
                    }
                    return
        else:
            # Normal ruler mode interaction
            d1 = math.hypot(event.x - self.p1["x"], event.y - self.p1["y"])
            d2 = math.hypot(event.x - self.p2["x"], event.y - self.p2["y"])
            
            if d1 < 25:
                self.dragging = "p1"
            elif d2 < 25:
                self.dragging = "p2"
            else:
                self.dragging = "line"
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                self.orig_p1 = dict(self.p1)
                self.orig_p2 = dict(self.p2)

    def on_drag(self, event):
        """Handle mouse drag"""
        if self.is_passthrough:
            return
        
        # Handle text object dragging
        if self.text_dragging_index is not None:
            dx = event.x - self.text_drag_start["x"]
            dy = event.y - self.text_drag_start["y"]
            self.text_objects[self.text_dragging_index]["x"] += dx
            self.text_objects[self.text_dragging_index]["y"] += dy
            self.text_drag_start = {"x": event.x, "y": event.y}
            self.draw()
            return
        
        if not self.dragging and self.polygon_dragging_index is None and self.polygon_move_origin is None:
            return
        
        if self.config["mode"] == "angle":
            # Angle mode dragging
            if self.dragging == "angle_center":
                # Move entire angle tool
                dx = event.x - self.angle_center["x"]
                dy = event.y - self.angle_center["y"]
                self.angle_center["x"] = event.x
                self.angle_center["y"] = event.y
                self.angle_arm1["x"] += dx
                self.angle_arm1["y"] += dy
                self.angle_arm2["x"] += dx
                self.angle_arm2["y"] += dy
            elif self.dragging == "angle_arm1":
                # Rotate arm 1 around center
                self.angle_arm1["x"] = event.x
                self.angle_arm1["y"] = event.y
            elif self.dragging == "angle_arm2":
                # Rotate arm 2 around center
                self.angle_arm2["x"] = event.x
                self.angle_arm2["y"] = event.y
        elif self.config["mode"] == "polygon":
            # Dragging a single vertex
            if self.polygon_dragging_index is not None:
                self.polygon_points[self.polygon_dragging_index]["x"] = event.x
                self.polygon_points[self.polygon_dragging_index]["y"] = event.y
                self.draw()
                return

            # Moving whole polygon
            if self.polygon_move_origin:
                dx = event.x - self.polygon_move_origin["start_x"]
                dy = event.y - self.polygon_move_origin["start_y"]
                new_points = []
                for p in self.polygon_move_origin["points"]:
                    new_points.append({"x": p["x"] + dx, "y": p["y"] + dy})
                self.polygon_points = new_points
                self.draw()
                return

        else:
            # Normal ruler mode dragging
            if self.dragging == "p1":
                self.p1["x"], self.p1["y"] = event.x, event.y
                if self.config["lock_angle"] == 0:  # Horizontal lock
                    self.p1["y"] = self.p2["y"]
                elif self.config["lock_angle"] == 90:  # Vertical lock
                    self.p1["x"] = self.p2["x"]
            elif self.dragging == "p2":
                self.p2["x"], self.p2["y"] = event.x, event.y
                if self.config["lock_angle"] == 0:  # Horizontal lock
                    self.p2["y"] = self.p1["y"]
                elif self.config["lock_angle"] == 90:  # Vertical lock
                    self.p2["x"] = self.p1["x"]
            else:
                dx, dy = event.x - self.drag_start_x, event.y - self.drag_start_y
                self.p1["x"] = self.orig_p1["x"] + dx
                self.p1["y"] = self.orig_p1["y"] + dy
                self.p2["x"] = self.orig_p2["x"] + dx
                self.p2["y"] = self.orig_p2["y"] + dy
        
        self.draw()

    def on_release(self, event):
        """Handle mouse release"""
        self.dragging = None
        self.polygon_dragging_index = None
        self.polygon_move_origin = None
        self.text_dragging_index = None
        self.text_resizing_index = None
        self.text_resize_handle = None

    def on_mouse_move(self, event):
        """Handle mouse movement for cursor changes"""
        if self.is_passthrough:
            return
        
        try:
            # Check if hovering over text objects first
            if self.text_objects and self.text_visible:
                for text_obj in self.text_objects:
                    x, y = text_obj["x"], text_obj["y"]
                    width, height = text_obj["width"], text_obj["height"]
                    
                    # Check if mouse is inside text box
                    if x <= event.x <= x + width and y <= event.y <= y + height:
                        self.canvas.config(cursor="fleur")
                        return
            
            if self.config["mode"] == "angle":
                # Angle mode cursor changes
                cx, cy = self.angle_center["x"], self.angle_center["y"]
                ax1, ay1 = self.angle_arm1["x"], self.angle_arm1["y"]
                ax2, ay2 = self.angle_arm2["x"], self.angle_arm2["y"]
                
                d_center = math.hypot(event.x - cx, event.y - cy)
                d_arm1 = math.hypot(event.x - ax1, event.y - ay1)
                d_arm2 = math.hypot(event.x - ax2, event.y - ay2)
                
                if d_center < 25:
                    self.canvas.config(cursor="fleur")
                elif d_arm1 < 25 or d_arm2 < 25:
                    self.canvas.config(cursor="crosshair")
                else:
                    self.canvas.config(cursor="")
            elif self.config["mode"] == "polygon":
                # Polygon mode cursor changes
                if not self.polygon_points:
                    self.init_polygon_default()

                # Over vertex
                for p in self.polygon_points:
                    if math.hypot(event.x - p["x"], event.y - p["y"]) < 18:
                        self.canvas.config(cursor="crosshair")
                        return

                # Over edge
                pts = self.polygon_points
                n = len(pts)
                for i in range(n):
                    x1, y1 = pts[i]["x"], pts[i]["y"]
                    x2, y2 = pts[(i + 1) % n]["x"], pts[(i + 1) % n]["y"]
                    seg_len = math.hypot(x2 - x1, y2 - y1)
                    if seg_len == 0:
                        continue
                    dist_to_line = abs((y2 - y1) * event.x - (x2 - x1) * event.y + x2 * y1 - y2 * x1) / seg_len
                    dot = ((event.x - x1) * (x2 - x1) + (event.y - y1) * (y2 - y1)) / (seg_len * seg_len)
                    if dist_to_line < 12 and 0 <= dot <= 1:
                        self.canvas.config(cursor="fleur")
                        return

                self.canvas.config(cursor="")

            else:
                # Normal ruler mode cursor changes
                # Check distance to endpoints
                d1 = math.hypot(event.x - self.p1["x"], event.y - self.p1["y"])
                d2 = math.hypot(event.x - self.p2["x"], event.y - self.p2["y"])
                
                # Change cursor based on position
                if d1 < 25 or d2 < 25:
                    self.canvas.config(cursor="crosshair")
                else:
                    # Check if near the line
                    x1, y1 = self.p1["x"], self.p1["y"]
                    x2, y2 = self.p2["x"], self.p2["y"]
                    
                    # Calculate distance from point to line
                    line_len = math.hypot(x2 - x1, y2 - y1)
                    if line_len > 0:
                        dist_to_line = abs((y2-y1)*event.x - (x2-x1)*event.y + x2*y1 - y2*x1) / line_len
                        # Check if point is within line segment bounds
                        dot = ((event.x - x1) * (x2 - x1) + (event.y - y1) * (y2 - y1)) / (line_len * line_len)
                        
                        if dist_to_line < 10 and 0 <= dot <= 1:
                            self.canvas.config(cursor="fleur")
                        else:
                            self.canvas.config(cursor="")
                    else:
                        self.canvas.config(cursor="")
        except tk.TclError:
            # Canvas may have been destroyed
            pass
        except Exception as e:
            print(f"Warning: Error in mouse move handler: {e}")

    def on_right_click(self, event):
        """Handle right click - show context menu"""
        if self.is_passthrough:
            return
        
        menu = self._make_menu(self.root)
        menu.add_command(label="📋 Copy Measurement (C)", command=self.copy_measurement)
        menu.add_separator()
        
        # Mode selection submenu
        mode_menu = self._make_menu(menu)
        mode_menu.add_command(label="Ruler", command=lambda: self.set_mode_from_menu("ruler"))
        mode_menu.add_command(label="Fractions", command=lambda: self.set_mode_from_menu("fractions"))
        mode_menu.add_command(label="Angle", command=lambda: self.set_mode_from_menu("angle"))
        mode_menu.add_command(label="Polygon", command=lambda: self.set_mode_from_menu("polygon"))
        menu.add_cascade(label="📋 Measurement Mode", menu=mode_menu)
        
        menu.add_separator()
        
        # Text mode options
        if self.text_mode_active or self.text_objects:
            text_menu = self._make_menu(menu)
            text_status = "✓" if self.text_mode_active else " "
            text_menu.add_command(label=f"{text_status} Text Mode", command=self.toggle_text_mode)
            if self.text_objects:
                text_menu.add_separator()
                delete_label = "Delete Selected Text (Del)" if self.selected_text_index is not None else "Delete Last Text (Del)"
                text_menu.add_command(label=delete_label, command=self.delete_text_object)
                text_menu.add_command(label="Clear All Text", command=self.clear_all_text_objects)
            menu.add_cascade(label="✏️ Text", menu=text_menu)
            menu.add_separator()
        
        # Toggle labels (V key)
        labels_status = "✓ Show" if self.config["show_labels"] else "✗ Hide"
        menu.add_command(label=f"📖 Ruler Values {labels_status} (V)", command=self.toggle_labels)
        
        menu.add_separator()
        menu.add_command(label="⚙️ Settings (S)", command=self.toggle_settings)
        menu.add_command(label="❓ Help (H)", command=self.toggle_help)
        menu.add_command(label="ℹ️ About (A)", command=self.show_about)
        menu.add_separator()
        menu.add_command(label="🔄 Reset Position (R)", command=self.reset_ruler)
        menu.add_command(label="🔻 Minimize to Tray", command=self.minimize_to_tray)
        menu.add_command(label="❌ Exit (Esc)", command=self.close_app)
        
        menu.post(event.x_root, event.y_root)

    def reset_ruler(self, event=None):
        """Reset ruler to center"""
        try:
            cx = self.virtual_x + (self.virtual_w / 2)
            cy = self.virtual_y + (self.virtual_h / 2)
            self.p1, self.p2 = {"x": cx-300, "y": cy}, {"x": cx+300, "y": cy}
            self.draw()
        except Exception as e:
            print(f"Warning: Could not reset ruler: {e}")

    def toggle_fractions(self, event=None):
        """Toggle fraction mode"""
        self.config["show_fractions"] = not self.config["show_fractions"]
        self.save_config()
        self.draw()
        status = "ON" if self.config["show_fractions"] else "OFF"
        self.show_notification(f"Fractions: {status}")

    def increase_fractions(self, event=None):
        """Increase number of fractions"""
        if self.config["fraction_count"] < 50:
            self.config["fraction_count"] += 1
            self.save_config()
            # Update toolbar spinbox if in fractions mode
            if self.config["mode"] == "fractions" and hasattr(self, 'number_input'):
                try:
                    if self.number_input.winfo_exists():
                        self.number_input.delete(0, 'end')
                        self.number_input.insert(0, str(self.config["fraction_count"]))
                except Exception:
                    pass
            self.draw()
            self.show_notification(f"Fractions: {self.config['fraction_count']}")

    def decrease_fractions(self, event=None):
        """Decrease number of fractions"""
        if self.config["fraction_count"] > 2:
            self.config["fraction_count"] -= 1
            self.save_config()
            # Update toolbar spinbox if in fractions mode
            if self.config["mode"] == "fractions" and hasattr(self, 'number_input'):
                try:
                    if self.number_input.winfo_exists():
                        self.number_input.delete(0, 'end')
                        self.number_input.insert(0, str(self.config["fraction_count"]))
                except Exception:
                    pass
            self.draw()
            self.show_notification(f"Fractions: {self.config['fraction_count']}")

    def increase_thickness(self, event=None):
        """Increase ruler thickness"""
        if self.config["ruler_thickness"] < 20:
            self.config["ruler_thickness"] += 1
            self.save_config()
            self.draw()
            self.show_notification(f"Thickness: {self.config['ruler_thickness']}px")

    def decrease_thickness(self, event=None):
        """Decrease ruler thickness"""
        if self.config["ruler_thickness"] > 1:
            self.config["ruler_thickness"] -= 1
            self.save_config()
            self.draw()
            self.show_notification(f"Thickness: {self.config['ruler_thickness']}px")

    def toggle_labels(self, event=None):
        """Toggle ruler labels/values visibility"""
        self.config["show_labels"] = not self.config["show_labels"]
        self.save_config()
        self.draw()
        status = "ON" if self.config["show_labels"] else "OFF"
        self.show_notification(f"Ruler Values: {status}")
    
    def set_mode_from_menu(self, mode):
        """Set measurement mode from menu"""
        # Ensure the mode is visible when selected from menu
        self.mode_visible[mode] = True
        self.set_mode_from_toolbar(mode)
        
        mode_name = {"ruler": "Ruler", "fractions": "Fractions", "angle": "Angle", "polygon": "Polygon"}[mode]
        self.show_notification(f"Mode: {mode_name}")
    
    def cycle_mode(self, event=None):
        """Cycle through measurement modes: ruler, fractions, angle, polygon"""
        modes = ["ruler", "fractions", "angle", "polygon"]
        current_idx = modes.index(self.config["mode"]) if self.config["mode"] in modes else 0
        next_idx = (current_idx + 1) % len(modes)
        next_mode = modes[next_idx]
        
        # Ensure the new mode is visible when cycling
        self.mode_visible[next_mode] = True
        self.set_mode_from_toolbar(next_mode)
        
        mode_name = {"ruler": "Ruler", "fractions": "Fractions", "angle": "Angle", "polygon": "Polygon"}[next_mode]
        self.show_notification(f"Mode: {mode_name}")

    def close_app(self, event=None):
        """Close application"""
        try:
            self.save_config()
            
            # Close toolbar
            if self.toolbar and self.toolbar.winfo_exists():
                try:
                    self.toolbar.destroy()
                except Exception:
                    pass
            
            # Stop tray icon
            if self.tray_icon:
                try:
                    self.tray_icon.stop()
                except Exception:
                    pass
            
            # Destroy main window
            if self.root and self.root.winfo_exists():
                self.root.destroy()
        except Exception as e:
            print(f"Error during app closure: {e}")
            # Force exit if normal cleanup fails
            try:
                self.root.quit()
            except Exception:
                import sys
                sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProRuler(root)
    root.mainloop()
