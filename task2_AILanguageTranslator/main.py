"""
AI Smart Language Translator
----------------------------
A polished CustomTkinter desktop translator with a dashboard-style layout.

Run with:
    python main.py
"""

import threading
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox

import customtkinter as ctk

from database import DatabaseManager
from export_service import ExportError, ExportService
from translator_service import TranslationError, TranslatorService
from voice_service import VoiceError, VoiceService


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "app_dark": "#101114",
    "app_light": "#F5F7FB",
    "panel_dark": "#181B22",
    "panel_light": "#FFFFFF",
    "panel_alt_dark": "#20242D",
    "panel_alt_light": "#EEF2F7",
    "muted_dark": "#9CA3AF",
    "muted_light": "#64748B",
    "text_dark": "#F8FAFC",
    "text_light": "#111827",
    "accent": "#14B8A6",
    "accent_hover": "#0F9488",
    "accent_soft_dark": "#123B3A",
    "accent_soft_light": "#DFF8F4",
    "amber": "#F59E0B",
    "rose": "#F43F5E",
    "rose_hover": "#D93654",
    "border_dark": "#2A303A",
    "border_light": "#D9E1EA",
}


def theme_value(light, dark):
    return (light, dark)


class AITranslatorApp(ctk.CTk):
    """Main desktop application window."""

    def __init__(self):
        super().__init__()

        self.title("AI Smart Language Translator")
        self.geometry("1280x820")
        self.minsize(1080, 700)
        self.configure(fg_color=theme_value(COLORS["app_light"], COLORS["app_dark"]))

        self.db = DatabaseManager()
        self.translator = TranslatorService()
        self.voice = VoiceService()

        self.dark_mode = ctk.BooleanVar(value=True)
        self.live_translate = ctk.BooleanVar(value=False)
        self.detected_lang_text = ctk.StringVar(value="Source: waiting")
        self.status_text = ctk.StringVar(value="Ready")
        self._live_translate_job = None
        self._is_translating = False

        self._build_shell()
        self._build_sidebar()
        self._build_workspace()
        self._build_history_panel()
        self.refresh_history()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_shell(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

    def _panel(self, parent, **kwargs):
        options = {
            "corner_radius": 18,
            "fg_color": theme_value(COLORS["panel_light"], COLORS["panel_dark"]),
            "border_width": 1,
            "border_color": theme_value(COLORS["border_light"], COLORS["border_dark"]),
        }
        options.update(kwargs)
        return ctk.CTkFrame(parent, **options)

    def _muted(self):
        return theme_value(COLORS["muted_light"], COLORS["muted_dark"])

    def _text_color(self):
        return theme_value(COLORS["text_light"], COLORS["text_dark"])

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=238,
            corner_radius=0,
            fg_color=theme_value("#FFFFFF", "#15171D"),
            border_width=0,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(12, weight=1)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=20, pady=(26, 18))
        brand.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            brand,
            text="AI",
            width=48,
            height=48,
            corner_radius=16,
            fg_color=COLORS["accent"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, rowspan=2, padx=(0, 12))
        ctk.CTkLabel(
            brand,
            text="Smart Translate",
            anchor="w",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(
            brand,
            text="Language workspace",
            anchor="w",
            text_color=self._muted(),
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=1, sticky="ew")

        self._sidebar_label(sidebar, "WORKSPACE", 1)
        self._sidebar_button(sidebar, "Clear text", self.clear_text_fields, 2)
        self._sidebar_button(sidebar, "Translate now", self.translate_text, 3, active=True)
        self._sidebar_button(sidebar, "Export TXT", self.export_txt, 4)
        self._sidebar_button(sidebar, "Export PDF", self.export_pdf, 5)

        self._sidebar_label(sidebar, "HISTORY", 6)
        self._sidebar_button(sidebar, "Refresh history", self.refresh_history, 7)
        self._sidebar_button(sidebar, "Clear history", self.clear_history, 8, danger=True)

        ctk.CTkFrame(
            sidebar,
            height=1,
            fg_color=theme_value(COLORS["border_light"], COLORS["border_dark"]),
        ).grid(row=9, column=0, sticky="ew", padx=20, pady=18)

        live_row = self._setting_row(sidebar, "Live translation", self.live_translate)
        live_row.grid(row=10, column=0, sticky="ew", padx=20, pady=(0, 12))

        mode_row = self._setting_row(sidebar, "Dark mode", self.dark_mode, self.toggle_appearance_mode)
        mode_row.grid(row=11, column=0, sticky="ew", padx=20, pady=(0, 12))

        tip = self._panel(sidebar, corner_radius=16, fg_color=theme_value("#F3FBFA", "#132624"), border_width=0)
        tip.grid(row=13, column=0, sticky="ew", padx=18, pady=(12, 24))
        ctk.CTkLabel(
            tip,
            text="Tip",
            text_color=COLORS["accent"],
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 2))
        ctk.CTkLabel(
            tip,
            text="Use Auto Detect for mixed-language input, then save useful results from the history panel.",
            wraplength=180,
            justify="left",
            text_color=self._muted(),
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))

    def _sidebar_label(self, parent, text, row):
        ctk.CTkLabel(
            parent,
            text=text,
            anchor="w",
            text_color=self._muted(),
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=row, column=0, sticky="ew", padx=22, pady=(12, 6))

    def _sidebar_button(self, parent, text, command, row, active=False, danger=False):
        if active:
            fg_color = COLORS["accent"]
            hover = COLORS["accent_hover"]
            text_color = "#FFFFFF"
            border_width = 0
        else:
            fg_color = "transparent"
            hover = theme_value("#EEF2F7", "#242933")
            text_color = COLORS["rose"] if danger else self._text_color()
            border_width = 0

        ctk.CTkButton(
            parent,
            text=text,
            height=40,
            anchor="w",
            corner_radius=12,
            fg_color=fg_color,
            hover_color=hover,
            text_color=text_color,
            border_width=border_width,
            font=ctk.CTkFont(size=13, weight="bold" if active else "normal"),
            command=command,
        ).grid(row=row, column=0, sticky="ew", padx=16, pady=3)

    def _setting_row(self, parent, label, variable, command=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(row, text=label, anchor="w", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, sticky="ew"
        )
        ctk.CTkSwitch(
            row,
            text="",
            width=44,
            variable=variable,
            progress_color=COLORS["accent"],
            command=command,
        ).grid(row=0, column=1, sticky="e")
        return row

    def _build_workspace(self):
        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.grid(row=0, column=1, sticky="nsew", padx=22, pady=22)
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_rowconfigure(2, weight=1)

        self._build_header(workspace)
        self._build_language_bar(workspace)
        self._build_translation_area(workspace)

    def _build_header(self, parent):
        header = self._panel(
            parent,
            corner_radius=24,
            fg_color=theme_value("#ECFFFB", "#112624"),
            border_width=0,
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        ctk.CTkLabel(
            header,
            text="Translate, speak, export",
            anchor="w",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self._text_color(),
        ).grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 4))
        ctk.CTkLabel(
            header,
            text="A focused dashboard for fast language conversion, voice input, saved history, and clean exports.",
            anchor="w",
            text_color=self._muted(),
            font=ctk.CTkFont(size=13),
        ).grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 22))

        metrics = ctk.CTkFrame(header, fg_color="transparent")
        metrics.grid(row=0, column=1, rowspan=2, sticky="e", padx=18, pady=18)
        self.history_metric = self._metric(metrics, "History", "0")
        self.history_metric.grid(row=0, column=0, padx=(0, 10))
        self.char_metric = self._metric(metrics, "Characters", "0")
        self.char_metric.grid(row=0, column=1)

    def _metric(self, parent, title, value):
        metric = ctk.CTkFrame(
            parent,
            width=112,
            height=78,
            corner_radius=18,
            fg_color=theme_value("#FFFFFF", "#182E2B"),
        )
        metric.grid_propagate(False)
        ctk.CTkLabel(
            metric,
            text=title,
            text_color=self._muted(),
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 0))
        value_label = ctk.CTkLabel(
            metric,
            text=value,
            text_color=COLORS["accent"],
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        value_label.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))
        metric.value_label = value_label
        return metric

    def _build_language_bar(self, parent):
        bar = self._panel(parent, corner_radius=18)
        bar.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        bar.grid_columnconfigure(0, weight=1)
        bar.grid_columnconfigure(2, weight=1)

        lang_names = self.translator.get_language_names(include_auto=True)
        target_names = self.translator.get_language_names(include_auto=False)
        self.source_lang_var = ctk.StringVar(value="Auto Detect")
        self.target_lang_var = ctk.StringVar(value="English")

        self.source_menu = self._language_menu(bar, lang_names, self.source_lang_var)
        self.source_menu.grid(row=0, column=0, sticky="ew", padx=(18, 8), pady=18)

        self.swap_btn = ctk.CTkButton(
            bar,
            text="Swap",
            width=88,
            height=42,
            corner_radius=14,
            fg_color=theme_value("#E7F8F5", "#153533"),
            hover_color=theme_value("#D5F1EC", "#1B4642"),
            text_color=COLORS["accent"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.swap_languages,
        )
        self.swap_btn.grid(row=0, column=1, sticky="ew", padx=6, pady=18)

        self.target_menu = self._language_menu(bar, target_names, self.target_lang_var)
        self.target_menu.grid(row=0, column=2, sticky="ew", padx=(8, 18), pady=18)

    def _language_menu(self, parent, values, variable):
        return ctk.CTkOptionMenu(
            parent,
            values=values,
            variable=variable,
            height=42,
            corner_radius=14,
            fg_color=theme_value("#F0F5FA", "#222832"),
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            text_color=self._text_color(),
            dropdown_fg_color=theme_value("#FFFFFF", "#222832"),
            dropdown_hover_color=theme_value("#E7F8F5", "#153533"),
            dropdown_text_color=self._text_color(),
            font=ctk.CTkFont(size=13),
        )

    def _build_translation_area(self, parent):
        area = ctk.CTkFrame(parent, fg_color="transparent")
        area.grid(row=2, column=0, sticky="nsew")
        area.grid_columnconfigure(0, weight=1)
        area.grid_columnconfigure(1, weight=1)
        area.grid_rowconfigure(0, weight=1)

        input_card = self._text_card(area, "Input", "Type or paste text here")
        input_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        output_card = self._text_card(area, "Translation", "Translated result")
        output_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.input_textbox = ctk.CTkTextbox(
            input_card.body,
            font=ctk.CTkFont(size=15),
            wrap="word",
            corner_radius=14,
            border_width=0,
            fg_color=theme_value("#F8FAFC", "#11141A"),
        )
        self.input_textbox.grid(row=0, column=0, sticky="nsew", padx=16, pady=(0, 14))
        self.input_textbox.bind("<KeyRelease>", self._on_input_change)

        self.output_textbox = ctk.CTkTextbox(
            output_card.body,
            font=ctk.CTkFont(size=15),
            wrap="word",
            corner_radius=14,
            border_width=0,
            state="disabled",
            fg_color=theme_value("#F8FAFC", "#11141A"),
        )
        self.output_textbox.grid(row=0, column=0, sticky="nsew", padx=16, pady=(0, 14))

        self.char_count_label = ctk.CTkLabel(
            input_card.footer,
            text="0 characters",
            text_color=self._muted(),
            font=ctk.CTkFont(size=12),
        )
        self.char_count_label.pack(side="right")

        self.mic_btn = self._compact_button(
            input_card.footer, "Voice input", self.start_voice_input, COLORS["amber"], "#D97706"
        )
        self.mic_btn.pack(side="left", padx=(0, 8))

        self.translate_btn = self._compact_button(
            input_card.footer, "Translate", self.translate_text, COLORS["accent"], COLORS["accent_hover"]
        )
        self.translate_btn.pack(side="left")

        self.speak_btn = self._outline_button(output_card.footer, "Speak", self.speak_translation)
        self.speak_btn.pack(side="left", padx=(0, 8))
        self.copy_btn = self._outline_button(output_card.footer, "Copy", self.copy_translation)
        self.copy_btn.pack(side="left")

        ctk.CTkLabel(
            output_card.footer,
            textvariable=self.detected_lang_text,
            text_color=self._muted(),
            font=ctk.CTkFont(size=12),
        ).pack(side="right")

        status_bar = self._panel(parent, corner_radius=16, fg_color=theme_value("#FFFFFF", "#15171D"))
        status_bar.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        status_bar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            status_bar,
            textvariable=self.status_text,
            text_color=self._muted(),
            anchor="w",
            font=ctk.CTkFont(size=13),
        ).grid(row=0, column=0, sticky="ew", padx=18, pady=13)

    def _text_card(self, parent, title, subtitle):
        card = self._panel(parent, corner_radius=22)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text=title,
            anchor="w",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            header,
            text=subtitle,
            anchor="w",
            text_color=self._muted(),
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, sticky="ew", pady=(2, 0))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)
        card.body = body

        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        card.footer = footer
        return card

    def _compact_button(self, parent, text, command, color, hover):
        return ctk.CTkButton(
            parent,
            text=text,
            width=116,
            height=38,
            corner_radius=13,
            fg_color=color,
            hover_color=hover,
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=command,
        )

    def _outline_button(self, parent, text, command):
        return ctk.CTkButton(
            parent,
            text=text,
            width=96,
            height=38,
            corner_radius=13,
            fg_color="transparent",
            hover_color=theme_value("#E7F8F5", "#153533"),
            border_width=1,
            border_color=COLORS["accent"],
            text_color=COLORS["accent"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=command,
        )

    def _build_history_panel(self):
        history = ctk.CTkFrame(
            self,
            width=330,
            corner_radius=0,
            fg_color=theme_value("#FFFFFF", "#15171D"),
        )
        history.grid(row=0, column=2, sticky="nsew")
        history.grid_propagate(False)
        history.grid_columnconfigure(0, weight=1)
        history.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            history,
            text="History",
            anchor="w",
            font=ctk.CTkFont(size=21, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", padx=22, pady=(28, 2))
        ctk.CTkLabel(
            history,
            text="Recent translations and reusable drafts",
            anchor="w",
            text_color=self._muted(),
            font=ctk.CTkFont(size=12),
        ).grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 14))

        self.history_scroll = ctk.CTkScrollableFrame(history, fg_color="transparent")
        self.history_scroll.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 20))
        self.history_scroll.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # UI actions
    # ------------------------------------------------------------------
    def toggle_appearance_mode(self):
        ctk.set_appearance_mode("Dark" if self.dark_mode.get() else "Light")

    def _on_input_change(self, event=None):
        text = self.input_textbox.get("1.0", "end-1c")
        count = len(text)
        self.char_count_label.configure(text=f"{count} characters")
        self.char_metric.value_label.configure(text=str(count))

        if self._live_translate_job is not None:
            self.after_cancel(self._live_translate_job)
            self._live_translate_job = None

        if self.live_translate.get() and text.strip():
            self._live_translate_job = self.after(900, self.translate_text)

    def clear_text_fields(self):
        self.input_textbox.delete("1.0", "end")
        self._set_output_text("")
        self.detected_lang_text.set("Source: waiting")
        self.status_text.set("Ready")
        self.char_count_label.configure(text="0 characters")
        self.char_metric.value_label.configure(text="0")

    def swap_languages(self):
        source_name = self.source_lang_var.get()
        target_name = self.target_lang_var.get()
        if source_name == "Auto Detect":
            messagebox.showinfo("Cannot swap", "Select a specific source language before swapping.")
            return

        self.source_lang_var.set(target_name)
        self.target_lang_var.set(source_name)

        input_text = self.input_textbox.get("1.0", "end-1c")
        output_text = self.output_textbox.get("1.0", "end-1c")
        self.input_textbox.delete("1.0", "end")
        self.input_textbox.insert("1.0", output_text)
        self._set_output_text(input_text)
        self._on_input_change()

    # ------------------------------------------------------------------
    # Translation
    # ------------------------------------------------------------------
    def translate_text(self):
        text = self.input_textbox.get("1.0", "end-1c").strip()
        if not text:
            self.status_text.set("Please enter text before translating.")
            return
        if self._is_translating:
            return

        self._is_translating = True
        self.translate_btn.configure(state="disabled", text="Translating")
        self.status_text.set("Translating...")

        source_name = self.source_lang_var.get()
        target_name = self.target_lang_var.get()
        thread = threading.Thread(
            target=self._translate_worker,
            args=(text, source_name, target_name),
            daemon=True,
        )
        thread.start()

    def _translate_worker(self, text, source_name, target_name):
        try:
            result = self.translator.translate(text, source_name, target_name)
            self.after(0, self._on_translate_success, text, result, target_name)
        except TranslationError as exc:
            self.after(0, self._on_translate_error, str(exc))
        except Exception as exc:
            self.after(0, self._on_translate_error, self._friendly_network_message(exc))

    def _on_translate_success(self, original_text, result, target_name):
        translated_text = result["translated_text"]
        detected_name = result["detected_source_name"]

        self._set_output_text(translated_text)
        self.detected_lang_text.set(f"Source: {detected_name}")
        self.status_text.set("Translation complete.")

        self.db.save_translation(original_text, translated_text, detected_name, target_name)
        self.refresh_history()

        self.translate_btn.configure(state="normal", text="Translate")
        self._is_translating = False

    def _on_translate_error(self, message):
        self.status_text.set(message)
        self.translate_btn.configure(state="normal", text="Translate")
        self._is_translating = False
        messagebox.showerror("Translation error", message)

    @staticmethod
    def _friendly_network_message(exc):
        text = str(exc).lower()
        if "connection" in text or "timed out" in text or "network" in text:
            return "No internet connection. Please check your network and try again."
        return "Something went wrong while translating. Please try again."

    def _set_output_text(self, text):
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", text)
        self.output_textbox.configure(state="disabled")

    # ------------------------------------------------------------------
    # Voice
    # ------------------------------------------------------------------
    def start_voice_input(self):
        self.mic_btn.configure(state="disabled", text="Listening")
        self.status_text.set("Listening... speak now.")
        threading.Thread(target=self._voice_input_worker, daemon=True).start()

    def _voice_input_worker(self):
        try:
            source_name = self.source_lang_var.get()
            lang_code = "en-US" if source_name == "Auto Detect" else self.translator.code_for(source_name)
            recognized_text = self.voice.listen_from_microphone(language_code=lang_code)
            self.after(0, self._on_voice_input_success, recognized_text)
        except VoiceError as exc:
            self.after(0, self._on_voice_input_error, str(exc))
        except Exception as exc:
            self.after(0, self._on_voice_input_error, f"Voice input failed: {exc}")

    def _on_voice_input_success(self, recognized_text):
        self.input_textbox.delete("1.0", "end")
        self.input_textbox.insert("1.0", recognized_text)
        self._on_input_change()
        self.mic_btn.configure(state="normal", text="Voice input")
        self.status_text.set("Voice captured successfully.")

    def _on_voice_input_error(self, message):
        self.mic_btn.configure(state="normal", text="Voice input")
        self.status_text.set(message)
        messagebox.showerror("Voice input error", message)

    def speak_translation(self):
        text = self.output_textbox.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Nothing to speak", "There is no translated text to read aloud yet.")
            return

        self.speak_btn.configure(state="disabled", text="Speaking")
        threading.Thread(target=self._speak_worker, args=(text,), daemon=True).start()

    def _speak_worker(self, text):
        try:
            self.voice.speak_text(text)
            self.after(0, lambda: self.speak_btn.configure(state="normal", text="Speak"))
        except VoiceError as exc:
            self.after(0, self._on_speak_error, str(exc))
        except Exception as exc:
            self.after(0, self._on_speak_error, f"Text-to-speech failed: {exc}")

    def _on_speak_error(self, message):
        self.speak_btn.configure(state="normal", text="Speak")
        messagebox.showerror("Text-to-speech error", message)

    # ------------------------------------------------------------------
    # Copy, history, export
    # ------------------------------------------------------------------
    def copy_translation(self):
        text = self.output_textbox.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Nothing to copy", "There is no translated text to copy yet.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status_text.set("Copied to clipboard.")

    def refresh_history(self):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        records = self.db.get_history()
        self.history_metric.value_label.configure(text=str(len(records)))

        if not records:
            empty = self._panel(
                self.history_scroll,
                corner_radius=18,
                fg_color=theme_value("#F8FAFC", "#1A1E26"),
                border_width=0,
            )
            empty.grid(row=0, column=0, sticky="ew", padx=4, pady=10)
            ctk.CTkLabel(
                empty,
                text="No translations yet",
                font=ctk.CTkFont(size=14, weight="bold"),
            ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 2))
            ctk.CTkLabel(
                empty,
                text="Your saved translations will appear here after you translate text.",
                wraplength=250,
                justify="left",
                text_color=self._muted(),
                font=ctk.CTkFont(size=12),
            ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))
            return

        for index, record in enumerate(records):
            self._render_history_entry(index, record)

    def _render_history_entry(self, row_index, record):
        entry_id, original, translated, source_lang, target_lang, timestamp = record
        card = self._panel(
            self.history_scroll,
            corner_radius=18,
            fg_color=theme_value("#F8FAFC", "#1A1E26"),
            border_width=0,
        )
        card.grid(row=row_index, column=0, sticky="ew", padx=4, pady=7)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=f"{source_lang} -> {target_lang}",
            anchor="w",
            text_color=COLORS["accent"],
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 0))
        ctk.CTkLabel(
            card,
            text=timestamp,
            anchor="w",
            text_color=self._muted(),
            font=ctk.CTkFont(size=10),
        ).grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            card,
            text=self._preview(original),
            anchor="w",
            justify="left",
            wraplength=260,
            font=ctk.CTkFont(size=12),
        ).grid(row=2, column=0, sticky="ew", padx=14)
        ctk.CTkLabel(
            card,
            text=self._preview(translated),
            anchor="w",
            justify="left",
            wraplength=260,
            text_color=self._muted(),
            font=ctk.CTkFont(size=12),
        ).grid(row=3, column=0, sticky="ew", padx=14, pady=(4, 10))

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 12))
        ctk.CTkButton(
            buttons,
            text="Reuse",
            width=78,
            height=30,
            corner_radius=10,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self._reuse_history_entry(original, source_lang, target_lang),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            buttons,
            text="Delete",
            width=78,
            height=30,
            corner_radius=10,
            fg_color="transparent",
            hover_color=theme_value("#FFE4E9", "#3A1820"),
            border_width=1,
            border_color=COLORS["rose"],
            text_color=COLORS["rose"],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self._delete_history_entry(entry_id),
        ).pack(side="left")

    @staticmethod
    def _preview(text, limit=76):
        text = " ".join(text.split())
        return text[:limit] + "..." if len(text) > limit else text

    def _reuse_history_entry(self, original_text, source_lang, target_lang):
        self.input_textbox.delete("1.0", "end")
        self.input_textbox.insert("1.0", original_text)
        self._on_input_change()

        if source_lang in self.translator.lang_name_to_code:
            self.source_lang_var.set(source_lang)
        if target_lang in self.translator.lang_name_to_code:
            self.target_lang_var.set(target_lang)
        self.status_text.set("History item loaded.")

    def _delete_history_entry(self, entry_id):
        self.db.delete_entry(entry_id)
        self.refresh_history()
        self.status_text.set("History item deleted.")

    def clear_history(self):
        confirm = messagebox.askyesno(
            "Clear history",
            "Delete all translation history? This cannot be undone.",
        )
        if confirm:
            self.db.clear_history()
            self.refresh_history()
            self.status_text.set("History cleared.")

    def _get_export_payload(self):
        original = self.input_textbox.get("1.0", "end-1c").strip()
        translated = self.output_textbox.get("1.0", "end-1c").strip()
        if not original or not translated:
            messagebox.showwarning("Nothing to export", "Translate some text before exporting.")
            return None
        return original, translated, self.source_lang_var.get(), self.target_lang_var.get()

    def export_txt(self):
        payload = self._get_export_payload()
        if not payload:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt")],
            initialfile="translation.txt",
            title="Save translation as TXT",
        )
        if not filepath:
            return
        try:
            ExportService.export_to_txt(filepath, *payload)
            self.status_text.set("TXT export saved.")
            messagebox.showinfo("Export successful", f"Translation saved to:\n{filepath}")
        except ExportError as exc:
            messagebox.showerror("Export failed", str(exc))

    def export_pdf(self):
        payload = self._get_export_payload()
        if not payload:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF File", "*.pdf")],
            initialfile="translation.pdf",
            title="Save translation as PDF",
        )
        if not filepath:
            return
        try:
            ExportService.export_to_pdf(filepath, *payload)
            self.status_text.set("PDF export saved.")
            messagebox.showinfo("Export successful", f"Translation saved to:\n{filepath}")
        except ExportError as exc:
            messagebox.showerror("Export failed", str(exc))

    def _on_close(self):
        self.destroy()


if __name__ == "__main__":
    app = AITranslatorApp()
    app.mainloop()
