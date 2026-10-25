"""
Modern Theme & UI Styling Configuration for Tkinter / ttk
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import tkinter as tk
from tkinter import ttk

# Professional Color Palette
COLORS = {
    "bg_main": "#F8FAFC",          # Slate 50
    "bg_card": "#FFFFFF",          # Pure White
    "bg_sidebar": "#0F172A",       # Slate 900 (Deep Navy)
    "bg_sidebar_hover": "#1E293B", # Slate 800
    "bg_sidebar_active": "#2563EB",# Royal Blue
    "header_bg": "#1E293B",        # Slate 800
    
    "primary": "#2563EB",          # Royal Blue
    "primary_hover": "#1D4ED8",    # Darker Blue
    "secondary": "#64748B",        # Slate 500
    "success": "#16A34A",          # Emerald 600
    "warning": "#D97706",          # Amber 600
    "danger": "#DC2626",           # Crimson Red
    "danger_hover": "#B91C1C",
    
    "text_dark": "#0F172A",        # Slate 900
    "text_muted": "#64748B",       # Slate 500
    "text_light": "#FFFFFF",       # White
    "text_sidebar": "#CBD5E1",     # Slate 300
    
    "border": "#E2E8F0",           # Slate 200
    "border_focus": "#3B82F6",     # Blue 500
    "tree_selected": "#DBEAFE",    # Light Blue
    "tree_alt": "#F1F5F9"          # Light Slate
}

FONTS = {
    "brand_title": ("Segoe UI", 13, "bold"),
    "brand_sub": ("Segoe UI", 9),
    "header_title": ("Segoe UI", 16, "bold"),
    "section_title": ("Segoe UI", 13, "bold"),
    "body": ("Segoe UI", 10),
    "body_bold": ("Segoe UI", 10, "bold"),
    "caption": ("Segoe UI", 9),
    "metric_val": ("Segoe UI", 20, "bold"),
    "metric_lbl": ("Segoe UI", 10)
}

def apply_theme(root):
    """Configure modern ttk styles across the application."""
    style = ttk.Style(root)
    
    # Use 'clam' or 'alt' as base engine for reliable multi-platform styling
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Root background
    root.configure(bg=COLORS["bg_main"])

    # Base Frame styling
    style.configure("TFrame", background=COLORS["bg_main"])
    style.configure("Card.TFrame", background=COLORS["bg_card"], relief="solid", borderwidth=1)
    style.configure("Sidebar.TFrame", background=COLORS["bg_sidebar"])
    style.configure("Header.TFrame", background=COLORS["header_bg"])

    # Labels
    style.configure("TLabel", background=COLORS["bg_main"], foreground=COLORS["text_dark"], font=FONTS["body"])
    style.configure("Card.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_dark"], font=FONTS["body"])
    style.configure("Title.TLabel", background=COLORS["bg_main"], foreground=COLORS["text_dark"], font=FONTS["header_title"])
    style.configure("SubTitle.TLabel", background=COLORS["bg_main"], foreground=COLORS["text_muted"], font=FONTS["body"])
    style.configure("HeaderTitle.TLabel", background=COLORS["header_bg"], foreground=COLORS["text_light"], font=FONTS["brand_title"])
    style.configure("HeaderSub.TLabel", background=COLORS["header_bg"], foreground="#94A3B8", font=FONTS["brand_sub"])

    # Buttons
    style.configure("Primary.TButton",
                    background=COLORS["primary"],
                    foreground=COLORS["text_light"],
                    font=FONTS["body_bold"],
                    padding=(12, 6),
                    borderwidth=0)
    style.map("Primary.TButton",
              background=[("active", COLORS["primary_hover"])])

    style.configure("Success.TButton",
                    background=COLORS["success"],
                    foreground=COLORS["text_light"],
                    font=FONTS["body_bold"],
                    padding=(12, 6),
                    borderwidth=0)

    style.configure("Danger.TButton",
                    background=COLORS["danger"],
                    foreground=COLORS["text_light"],
                    font=FONTS["body_bold"],
                    padding=(10, 5),
                    borderwidth=0)
    style.map("Danger.TButton",
              background=[("active", COLORS["danger_hover"])])

    style.configure("Secondary.TButton",
                    background="#E2E8F0",
                    foreground=COLORS["text_dark"],
                    font=FONTS["body"],
                    padding=(10, 5),
                    borderwidth=0)

    # Sidebar Navigation Buttons
    style.configure("Nav.TButton",
                    background=COLORS["bg_sidebar"],
                    foreground=COLORS["text_sidebar"],
                    font=("Segoe UI", 10),
                    anchor="w",
                    padding=(16, 10),
                    borderwidth=0)
    style.map("Nav.TButton",
              background=[("active", COLORS["bg_sidebar_hover"]), ("selected", COLORS["bg_sidebar_active"])],
              foreground=[("active", COLORS["text_light"]), ("selected", COLORS["text_light"])])

    # Treeview (DataTable)
    style.configure("Treeview",
                    background=COLORS["bg_card"],
                    foreground=COLORS["text_dark"],
                    fieldbackground=COLORS["bg_card"],
                    rowheight=28,
                    font=FONTS["body"],
                    borderwidth=1,
                    relief="solid")
    style.configure("Treeview.Heading",
                    background="#F1F5F9",
                    foreground=COLORS["text_dark"],
                    font=FONTS["body_bold"],
                    padding=(6, 6),
                    relief="flat")
    style.map("Treeview",
              background=[("selected", COLORS["tree_selected"])],
              foreground=[("selected", COLORS["primary"])])

    # Entry & Combobox
    style.configure("TEntry", padding=5, font=FONTS["body"])
    style.configure("TCombobox", padding=5, font=FONTS["body"])
    style.configure("TNotebook", background=COLORS["bg_main"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(14, 8), font=FONTS["body_bold"])

    return style
