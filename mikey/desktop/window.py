"""The Tkinter window for the desktop assistant."""

from __future__ import annotations

import threading
import urllib.error
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, ttk

from ..config import read_setting
from ..groq_client import request_groq_reply
from .commands import parse_command
from .constants import (
    ACCENT,
    APP_NAME,
    BANGLA_APP_LABELS,
    BG,
    CARD,
    LANGUAGES,
    MUTED,
    PANEL,
    TEXT,
    WEBSITES,
)
from .speech import Speaker, sr, voice_input_available
from .system import (
    capture_screen_base64,
    press_volume_key,
    screen_capture_available,
    start_approved_app,
    volume_keys_available,
)


class MikeyApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1000x740")
        self.root.minsize(820, 620)
        self.root.configure(bg=BG)
        self.closing = False
        self.api_key = read_setting("GROQ_API_KEY")
        self.business_name = read_setting("BUSINESS_NAME", "our team")
        self.support_context = read_setting("SUPPORT_CONTEXT")
        self.language = tk.StringVar(value="English")
        self.status = tk.StringVar(value="Ready")
        self.recognizer = sr.Recognizer() if sr else None
        self.speaker = Speaker()
        self._listen_stop = threading.Event()
        self._listener: threading.Thread | None = None
        self.history: list[dict[str, object]] = []
        self._build()
        self._message("Mikey", self._text(
            "Welcome to Mikey Customer Care. How can I help you today?",
            "মাইকি কাস্টমার কেয়ারে স্বাগতম। আজ আপনাকে কীভাবে সাহায্য করতে পারি?",
        ))
        self._message("Mikey", self._text(
            "Ask a question below. Voice recognition and AI chat require internet.",
            "নিচে আপনার প্রশ্ন লিখুন। ভয়েস ও AI চ্যাটের জন্য ইন্টারনেট প্রয়োজন।",
        ))
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _text(self, english: str, bangla: str | None = None) -> str:
        return (bangla or english) if self.language.get() == "বাংলা" else english

    def _build(self):
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=26, pady=(22, 12))
        title_row = tk.Frame(top, bg=BG)
        title_row.pack(fill="x")
        tk.Label(title_row, text="MIKEY", fg=ACCENT, bg=BG,
                 font=("Segoe UI", 27, "bold")).pack(side="left")
        tk.Label(title_row, text="BILINGUAL CUSTOMER CARE", fg=MUTED, bg=BG,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=14, pady=(12, 0))
        tk.Label(title_row, textvariable=self.status, fg=ACCENT, bg=BG,
                 font=("Segoe UI", 10, "bold")).pack(side="right", padx=10, pady=12)
        lang_box = ttk.Combobox(title_row, textvariable=self.language,
                                values=list(LANGUAGES), state="readonly", width=12)
        lang_box.pack(side="right", padx=6)
        lang_box.bind("<<ComboboxSelected>>", self._language_changed)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=26, pady=8)
        sidebar = tk.Frame(body, bg=PANEL, width=208)
        sidebar.pack(side="left", fill="y", padx=(0, 14))
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="QUICK ACTIONS", fg=MUTED, bg=PANEL,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(18, 12))
        actions = [
            ("🎙  Start voice", "🎙  কথা শুনুন", self.toggle_voice),
            ("🕒  Time & date", "🕒  সময় ও তারিখ", self.show_time),
            ("🖥  Read my screen", "🖥  স্ক্রিন পড়ুন", self.analyze_screen),
            ("📁  Find a file", "📁  ফাইল খুঁজুন", self.find_file),
            ("🌐  Open websites", "🌐  ওয়েবসাইট খুলুন", self.open_websites),
            ("🔊  Volume up", "🔊  ভলিউম বাড়ান", lambda: self.volume(1)),
            ("🔉  Volume down", "🔉  ভলিউম কমান", lambda: self.volume(-1)),
            ("❔  Help", "❔  সাহায্য", self.help),
        ]
        self.action_buttons = []
        for en, bn, command in actions:
            btn = self._button(sidebar, en, command, left=True)
            btn.pack(fill="x", padx=10, pady=4)
            self.action_buttons.append((btn, en, bn))
        tk.Label(sidebar, text="Apps", fg=MUTED, bg=PANEL,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(18, 7))
        self.app_buttons = []
        for name in ("Notepad", "Calculator", "Paint", "File Explorer"):
            btn = self._button(sidebar, "▸  " + name, lambda n=name.lower(): self.launch_app(n), left=True)
            btn.pack(fill="x", padx=10, pady=3)
            self.app_buttons.append((btn, name))

        main = tk.Frame(body, bg=BG)
        main.pack(side="left", fill="both", expand=True)
        self.chat = tk.Text(main, wrap="word", state="disabled", bg=PANEL, fg=TEXT,
                            insertbackground=TEXT, relief="flat", borderwidth=0,
                            font=("Segoe UI", 11), padx=18, pady=18, spacing1=3, spacing3=8)
        self.chat.pack(fill="both", expand=True)
        self.chat.tag_configure("speaker", foreground=ACCENT, font=("Segoe UI", 10, "bold"))
        self.chat.tag_configure("body", foreground=TEXT)
        self.chat.tag_configure("muted", foreground=MUTED)

        input_panel = tk.Frame(main, bg=BG)
        input_panel.pack(fill="x", pady=(12, 0))
        self.entry = tk.Entry(input_panel, bg=CARD, fg=TEXT, insertbackground=TEXT,
                              relief="flat", font=("Segoe UI", 11))
        self.entry.pack(side="left", fill="x", expand=True, ipady=12)
        self.entry.bind("<Return>", lambda _e: self.submit())
        self._button(input_panel, "Send", self.submit).pack(side="left", padx=(8, 0))
        self._button(input_panel, "Ask support", self.ask_ai).pack(side="left", padx=(8, 0))
        footer = tk.Label(self.root,
                          text="AI chat is sent to Groq. Screen images are sent only when you choose Read my screen.",
                          fg=MUTED, bg=BG, font=("Segoe UI", 8))
        footer.pack(anchor="w", padx=28, pady=(0, 14))
        self.root.bind("<Control-l>", lambda _e: self.entry.focus_set())

    def _button(self, parent, label, command, left=False):
        return tk.Button(parent, text=label, command=command, bg=CARD, fg=TEXT,
                         activebackground="#243652", activeforeground="white",
                         font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                         padx=12, pady=9, borderwidth=0, anchor="w" if left else "center")

    def _language_changed(self, _event=None):
        for btn, en, bn in self.action_buttons:
            btn.configure(text=bn if self.language.get() == "বাংলা" else en)
        for btn, name in self.app_buttons:
            label = BANGLA_APP_LABELS.get(name, name)
            btn.configure(text="▸  " + (label if self.language.get() == "বাংলা" else name))
        self._message("Mikey", self._text("Language set to English.", "ভাষা বাংলা করা হয়েছে।"))

    def _message(self, speaker: str, message: str):
        if self.closing:
            return
        self.chat.configure(state="normal")
        self.chat.insert("end", speaker + "\n", "speaker")
        self.chat.insert("end", message + "\n\n", "body")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def _ui(self, fn, *args):
        if not self.closing:
            try:
                self.root.after(0, lambda: fn(*args))
            except tk.TclError:
                pass

    def _say(self, text: str):
        self.speaker.say(text, bangla=self.language.get() == "বাংলা")

    def show_time(self):
        now = datetime.now()
        text = self._text(f"It is {now:%I:%M %p} on {now:%A, %d %B %Y}.",
                          f"এখন সময় {now:%I:%M %p}, তারিখ {now:%d-%m-%Y}।")
        self._message("Mikey", text)
        self._say(text)

    def open_websites(self):
        for name, url in WEBSITES.items():
            webbrowser.open(url)
        self._message("Mikey", self._text("Opened YouTube, Google, and GitHub.", "ইউটিউব, গুগল ও গিটহাব খোলা হয়েছে।"))

    def launch_app(self, name: str):
        try:
            started = start_approved_app(name)
        except OSError as exc:
            self._message("Mikey", f"Could not open {name}: {exc}")
            return
        if not started:
            self._message("Mikey", self._text("That app is not on the approved list.", "এই অ্যাপটি অনুমোদিত তালিকায় নেই।"))
            return
        self._message("Mikey", self._text(f"Opening {name.title()}.", f"{name.title()} খোলা হচ্ছে।"))

    def volume(self, direction: int):
        if not volume_keys_available():
            self._message("Mikey", "Volume shortcuts are available on Windows.")
            return
        try:
            press_volume_key(direction)
            self._message("Mikey", self._text("Changed system volume.", "সিস্টেমের ভলিউম পরিবর্তন করা হয়েছে।"))
        except Exception as exc:
            self._message("Mikey", f"Volume control failed: {exc}")

    def find_file(self):
        path = filedialog.askopenfilename(title=self._text("Choose a file", "ফাইল নির্বাচন করুন"))
        if path:
            self._message("Mikey", self._text(f"Selected: {path}", f"নির্বাচিত ফাইল: {path}"))

    def analyze_screen(self):
        if not screen_capture_available():
            self._message("Mikey", "Screen reading needs Pillow. Install the project requirements first.")
            return
        if not self.api_key:
            self._message("Mikey", self._text("Add GROQ_API_KEY to .env to enable screen analysis.",
                                                ".env ফাইলে GROQ_API_KEY যোগ করলে স্ক্রিন বিশ্লেষণ চালু হবে।"))
            return
        try:
            data = capture_screen_base64()
        except Exception as exc:
            self._message("Mikey", f"Could not capture the screen: {exc}")
            return
        self.status.set("Analyzing screen…")
        prompt = "Describe the visible screen briefly and answer in Bengali." if self.language.get() == "বাংলা" else "Describe the visible screen briefly and point out the main content."
        threading.Thread(
            target=self._groq_request, args=(prompt, data, []), daemon=True
        ).start()

    def submit(self):
        prompt = self.entry.get().strip()
        if not prompt:
            return
        self.entry.delete(0, "end")
        self._message("You", prompt)
        self.handle_command(prompt)

    def handle_command(self, text: str):
        command = parse_command(text)
        if command is None:
            self.ask_prompt(text)
        elif command.action == "time":
            self.show_time()
        elif command.action == "site":
            self.open_site(command.target)
        elif command.action == "app":
            self.launch_app(command.target)
        elif command.action == "volume":
            self.volume(command.target)
        elif command.action == "help":
            self.help()

    def open_site(self, name: str):
        webbrowser.open(WEBSITES[name])
        self._message("Mikey", self._text(f"Opening {name.title()}.", f"{name.title()} খোলা হচ্ছে।"))

    def help(self):
        msg = ("Tell me what you need help with. You can ask about a product or service, "
               "or use the desktop shortcuts for time, apps, and volume.")
        bn = "আপনার কী সাহায্য দরকার বলুন। পণ্য বা সেবা সম্পর্কে প্রশ্ন করুন, অথবা সময়, অ্যাপ ও ভলিউমের শর্টকাট ব্যবহার করুন।"
        self._message("Mikey", self._text(msg, bn))

    def ask_ai(self):
        prompt = self.entry.get().strip()
        if not prompt:
            return
        self.entry.delete(0, "end")
        self._message("You", prompt)
        self.ask_prompt(prompt)

    def ask_prompt(self, prompt: str):
        if not self.api_key:
            self._message("Mikey", self._text(
                "AI support is not configured yet. Add GROQ_API_KEY to the .env file; desktop shortcuts still work.",
                "AI সহায়তা এখনো চালু করা হয়নি। .env ফাইলে GROQ_API_KEY যোগ করুন; ডেস্কটপ শর্টকাটগুলো কাজ করবে।",
            ))
            return
        self.status.set(self._text("Thinking…", "ভাবছি…"))
        self.history.append({"role": "user", "content": prompt})
        threading.Thread(
            target=self._groq_request,
            args=(prompt, None, self.history[-20:].copy()),
            daemon=True,
        ).start()

    def _groq_request(
        self,
        prompt: str,
        image_data: str | None,
        history: list[dict[str, object]],
    ):
        try:
            chat_history = [
                {"role": str(message["role"]), "content": str(message["content"])}
                for message in history
                if isinstance(message.get("content"), str)
            ]
            answer = request_groq_reply(
                prompt,
                chat_history,
                "bn" if self.language.get() == "বাংলা" else "en",
                image_data,
            )
            if not image_data:
                self.history.append({"role": "assistant", "content": answer})
            self._ui(self._message, "Mikey", answer)
            self._say(answer[:900])
        except urllib.error.HTTPError as exc:
            self._ui(self._message, "Mikey", f"Groq request failed ({exc.code}).")
        except Exception as exc:
            self._ui(self._message, "Mikey", f"Could not complete the Groq request: {exc}")
        finally:
            self._ui(self.status.set, "Ready")

    def toggle_voice(self):
        if self._listener and self._listener.is_alive():
            self._listen_stop.set()
            self.status.set(self._text("Stopping…", "বন্ধ হচ্ছে…"))
            return
        if not voice_input_available():
            self._message("Mikey", "Voice input is unavailable. Install the requirements and check your microphone.")
            return
        self._listen_stop.clear()
        self.status.set(self._text("Listening…", "শুনছি…"))
        self._listener = threading.Thread(target=self._listen_loop, daemon=True)
        self._listener.start()

    def _listen_loop(self):
        try:
            with sr.Microphone() as source:
                self._ui(self._message, "Mikey", self._text("Listening. Say a command.", "বলুন, আমি শুনছি।"))
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                while not self._listen_stop.is_set() and not self.closing:
                    try:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=8)
                    except sr.WaitTimeoutError:
                        continue
                    try:
                        phrase = self.recognizer.recognize_google(audio, language=LANGUAGES[self.language.get()]["speech"])
                        self._ui(self._message, "You", phrase)
                        self.root.after(0, lambda p=phrase: self.handle_command(p))
                    except sr.UnknownValueError:
                        self._ui(self._message, "Mikey", self._text("Sorry, I did not catch that.", "দুঃখিত, বুঝতে পারিনি।"))
                    except sr.RequestError as exc:
                        self._ui(self._message, "Mikey", f"Speech service error: {exc}")
                        break
        except Exception as exc:
            self._ui(self._message, "Mikey", f"Microphone error: {exc}")
        finally:
            self._ui(self.status.set, "Ready")

    def close(self):
        self.closing = True
        self._listen_stop.set()
        self.speaker.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    MikeyApp(root)
    root.mainloop()
