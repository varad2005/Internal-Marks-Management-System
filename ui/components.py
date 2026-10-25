"""
Reusable UI Components for Internal Marks Management System
K.K. Wagh Institute of Engineering Education and Research, Nashik
Department of Computer Engineering | Academic Year 2026-27
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui.theme import COLORS, FONTS

class StatCard(tk.Frame):
    """Modern KPI summary card with colored indicator and metric counter."""
    def __init__(self, parent, title, value="0", subtitle="", accent_color=COLORS["primary"], width=200):
        super().__init__(parent, bg=COLORS["bg_card"], bd=1, relief="solid", highlightthickness=0)
        self.configure(highlightbackground=COLORS["border"])
        
        # Left Accent Border
        accent = tk.Frame(self, bg=accent_color, width=5)
        accent.pack(side="left", fill="y")

        content = tk.Frame(self, bg=COLORS["bg_card"], padx=14, pady=12)
        content.pack(side="left", fill="both", expand=True)

        self.title_lbl = tk.Label(content, text=title.upper(), bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=("Segoe UI", 9, "bold"))
        self.title_lbl.pack(anchor="w")

        self.val_lbl = tk.Label(content, text=str(value), bg=COLORS["bg_card"], fg=COLORS["text_dark"], font=FONTS["metric_val"])
        self.val_lbl.pack(anchor="w", pady=(2, 0))

        if subtitle:
            self.sub_lbl = tk.Label(content, text=subtitle, bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=FONTS["caption"])
            self.sub_lbl.pack(anchor="w")
        else:
            self.sub_lbl = None

    def update_value(self, new_val, subtitle=None):
        self.val_lbl.config(text=str(new_val))
        if subtitle and self.sub_lbl:
            self.sub_lbl.config(text=subtitle)


class DataTable(tk.Frame):
    """
    Enhanced Treeview component with:
    - Custom column headers and widths
    - Alternating row zebra striping
    - Vertical and horizontal scrollbars
    - Sort-on-click functionality
    - Clean API to insert, clear, and get selected items
    """
    def __init__(self, parent, columns, show_id=False):
        super().__init__(parent, bg=COLORS["bg_main"])
        self.columns = columns
        col_keys = [c[0] for c in columns]
        
        # Container frame
        self.tree_frame = tk.Frame(self, bg=COLORS["bg_card"], bd=1, relief="solid")
        self.tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=col_keys,
            show="headings",
            selectmode="browse"
        )

        # Scrollbars
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        # Configure columns
        for col_id, col_name, width, anchor in columns:
            self.tree.heading(col_id, text=col_name, command=lambda c=col_id: self._sort_column(c, False))
            self.tree.column(col_id, width=width, minwidth=50, anchor=anchor)

        # Alternating row tag
        self.tree.tag_configure("evenrow", background=COLORS["bg_card"])
        self.tree.tag_configure("oddrow", background=COLORS["tree_alt"])

        self._sort_reverse = {}

    def set_data(self, row_dicts):
        """Populate tree with list of row dictionaries."""
        self.clear()
        col_keys = [c[0] for c in self.columns]
        for idx, row in enumerate(row_dicts):
            vals = [row.get(k, "") for k in col_keys]
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=vals, tags=(tag,))

    def clear(self):
        """Remove all rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def get_selected_item(self):
        """Return dict of selected row values or None."""
        selected = self.tree.selection()
        if not selected:
            return None
        values = self.tree.item(selected[0], "values")
        col_keys = [c[0] for c in self.columns]
        return dict(zip(col_keys, values))

    def on_select(self, callback):
        """Bind selection event."""
        self.tree.bind("<<TreeviewSelect>>", lambda e: callback(self.get_selected_item()))

    def on_double_click(self, callback):
        """Bind double click event."""
        self.tree.bind("<Double-1>", lambda e: callback(self.get_selected_item()))

    def _sort_column(self, col, reverse):
        """Sort tree content when clicking on header."""
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            # Try float/int sorting
            l.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            self.tree.move(k, "", index)
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.item(k, tags=(tag,))

        # Reverse sort next time
        self.tree.heading(col, command=lambda: self._sort_column(col, not reverse))


class SearchBar(tk.Frame):
    """Standardized search and filter bar for all management views."""
    def __init__(self, parent, placeholder="Search records...", filters=None, on_search=None, on_reset=None):
        super().__init__(parent, bg=COLORS["bg_main"], pady=6)
        self.on_search_cb = on_search
        self.on_reset_cb = on_reset
        
        # Search Entry Container
        search_box = tk.Frame(self, bg=COLORS["bg_card"], bd=1, relief="solid")
        search_box.pack(side="left", padx=(0, 10))

        tk.Label(search_box, text="🔍", bg=COLORS["bg_card"], fg=COLORS["text_muted"], font=("Segoe UI", 10)).pack(side="left", padx=6)
        
        self.search_var = tk.StringVar()
        self.entry = tk.Entry(
            search_box,
            textvariable=self.search_var,
            font=FONTS["body"],
            bg=COLORS["bg_card"],
            fg=COLORS["text_dark"],
            bd=0,
            width=28
        )
        self.entry.pack(side="left", ipady=5, padx=4)
        self.entry.bind("<Return>", lambda e: self._trigger_search())

        # Dynamic Filters (e.g., department, year, semester dropdowns)
        self.filter_vars = {}
        if filters:
            for f_key, f_label, f_options in filters:
                f_frame = tk.Frame(self, bg=COLORS["bg_main"])
                f_frame.pack(side="left", padx=6)
                
                tk.Label(f_frame, text=f"{f_label}:", bg=COLORS["bg_main"], fg=COLORS["text_muted"], font=FONTS["caption"]).pack(side="left", padx=(0, 4))
                var = tk.StringVar(value="All")
                self.filter_vars[f_key] = var
                cb = ttk.Combobox(f_frame, textvariable=var, values=["All"] + f_options, state="readonly", width=12)
                cb.pack(side="left")
                cb.bind("<<ComboboxSelected>>", lambda e: self._trigger_search())

        # Action Buttons
        btn_search = ttk.Button(self, text="Search", style="Primary.TButton", command=self._trigger_search)
        btn_search.pack(side="left", padx=6)

        btn_reset = ttk.Button(self, text="Reset", style="Secondary.TButton", command=self._trigger_reset)
        btn_reset.pack(side="left")

    def _trigger_search(self):
        if self.on_search_cb:
            keyword = self.search_var.get().strip()
            filter_vals = {k: v.get() for k, v in self.filter_vars.items()}
            self.on_search_cb(keyword, filter_vals)

    def _trigger_reset(self):
        self.search_var.set("")
        for v in self.filter_vars.values():
            v.set("All")
        if self.on_reset_cb:
            self.on_reset_cb()


class FormModal(tk.Toplevel):
    """Standardized Modal Dialog for CRUD Insert and Update operations with pinned action buttons and scrollable fields."""
    def __init__(self, parent, title="Record Form", fields=None, initial_data=None, on_save=None, width=500, submit_text=None):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.configure(bg=COLORS["bg_main"])
        self.on_save = on_save
        self.field_inputs = {}
        self.initial_data = initial_data or {}

        fields_list = fields or []
        n_fields = len(fields_list)
        modal_w = max(int(width) if width else 500, 480)

        # Calculate responsive window height
        try:
            screen_h = parent.winfo_screenheight()
        except Exception:
            screen_h = 800
        ideal_h = 160 + n_fields * 62
        modal_h = min(ideal_h, max(520, int(screen_h * 0.82)))

        self.geometry(f"{modal_w}x{modal_h}")
        self.minsize(440, 380)
        self.resizable(True, True)

        # Center modal relative to parent
        self.update_idletasks()
        try:
            x = parent.winfo_rootx() + (parent.winfo_width() - modal_w) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - modal_h) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        # 1. Header (Pinned at Top)
        header = tk.Frame(self, bg=COLORS["header_bg"], padx=20, pady=14)
        header.pack(side="top", fill="x")
        tk.Label(header, text=title, bg=COLORS["header_bg"], fg=COLORS["text_light"], font=FONTS["brand_title"]).pack(anchor="w")

        # 2. Footer Buttons (Pinned at Bottom FIRST to ensure buttons are ALWAYS visible)
        footer = tk.Frame(self, bg=COLORS["bg_main"], padx=20, pady=12)
        footer.pack(side="bottom", fill="x")

        # Subtle divider above footer
        tk.Frame(footer, height=1, bg=COLORS["border"]).pack(fill="x", side="top", pady=(0, 10))

        btn_bar = tk.Frame(footer, bg=COLORS["bg_main"])
        btn_bar.pack(fill="x")

        if submit_text:
            btn_text = submit_text
        elif "Register" in title:
            btn_text = "Register Student"
        elif "Add" in title:
            btn_text = title
        elif "Edit" in title:
            btn_text = "Save Changes"
        else:
            btn_text = "Save Record"

        btn_cancel = ttk.Button(btn_bar, text="Cancel", style="Secondary.TButton", command=self.destroy)
        btn_cancel.pack(side="right", padx=(10, 0))

        btn_save = ttk.Button(btn_bar, text=btn_text, style="Primary.TButton", command=self._save)
        btn_save.pack(side="right")

        # 3. Middle Scrollable Container
        container = tk.Frame(self, bg=COLORS["bg_main"])
        container.pack(side="top", fill="both", expand=True)

        canvas = tk.Canvas(container, bg=COLORS["bg_main"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        body = tk.Frame(canvas, bg=COLORS["bg_main"], padx=22, pady=14)

        body_id = canvas.create_window((0, 0), window=body, anchor="nw")

        def _on_canvas_configure(event):
            canvas.itemconfig(body_id, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        def _on_body_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        body.bind("<Configure>", _on_body_configure)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mousewheel scrolling handler
        def _on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        def _bind_mousewheel(w):
            w.bind("<MouseWheel>", _on_mousewheel, add="+")
            w.bind("<Button-4>", _on_mousewheel, add="+")
            w.bind("<Button-5>", _on_mousewheel, add="+")
            for child in w.winfo_children():
                _bind_mousewheel(child)

        first_entry = None
        for f_def in fields_list:
            key = f_def["name"]
            label = f_def["label"]
            f_type = f_def.get("type", "text")
            options = f_def.get("options", [])
            required = f_def.get("required", True)
            is_readonly = f_def.get("readonly", False)

            f_row = tk.Frame(body, bg=COLORS["bg_main"])
            f_row.pack(fill="x", pady=6)

            lbl_text = f"{label} *" if required else label
            tk.Label(f_row, text=lbl_text, bg=COLORS["bg_main"], fg=COLORS["text_dark"], font=FONTS["body_bold"]).pack(anchor="w")

            val = self.initial_data.get(key, f_def.get("default", ""))

            if f_type == "combobox":
                var = tk.StringVar(value=str(val) if val != "" else (options[0] if options else ""))
                self.field_inputs[key] = var
                cb_state = "readonly" if not f_def.get("editable", False) else "normal"
                cb = ttk.Combobox(f_row, textvariable=var, values=options, state=cb_state, font=FONTS["body"])
                cb.pack(fill="x", pady=(2, 0))
                if not first_entry and cb_state != "readonly":
                    first_entry = cb
            elif f_type == "checkbox":
                var = tk.BooleanVar(value=bool(val))
                self.field_inputs[key] = var
                chk = ttk.Checkbutton(f_row, text=label, variable=var)
                chk.pack(anchor="w", pady=(2, 0))
            else:
                var = tk.StringVar(value=str(val) if val is not None else "")
                self.field_inputs[key] = var
                state = "readonly" if is_readonly else "normal"
                ent = ttk.Entry(f_row, textvariable=var, font=FONTS["body"], state=state)
                ent.pack(fill="x", pady=(2, 0))
                if not is_readonly:
                    ent.bind("<Return>", lambda e: self._save())
                    if not first_entry:
                        first_entry = ent

            if f_def.get("hint"):
                tk.Label(f_row, text=f_def["hint"], bg=COLORS["bg_main"], fg=COLORS["text_muted"], font=FONTS["caption"]).pack(anchor="w", pady=(1, 0))

        self.update_idletasks()
        _bind_mousewheel(body)
        _bind_mousewheel(canvas)

        if first_entry:
            first_entry.focus_set()

        self.bind("<Escape>", lambda e: self.destroy())

    def _save(self):
        data = {k: v.get() for k, v in self.field_inputs.items()}
        if self.on_save:
            try:
                self.on_save(data)
                self.destroy()
            except Exception as e:
                messagebox.showerror("Validation / Database Error", str(e), parent=self)
