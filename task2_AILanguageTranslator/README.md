# 🌐 AI Smart Language Translator

A modern, professional desktop translation application built with **Python**, **CustomTkinter**, **SQLite**, and the **Google Translate API** (via `googletrans`). Designed to look and feel like a polished mini Google Translate desktop client — complete with voice input, text-to-speech, translation history, and document export.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## ✨ Features

| Category | Details |
|---|---|
| 🎨 **Modern UI** | Built with CustomTkinter — clean three-panel layout, custom color palette, Dark/Light mode toggle |
| 🔤 **Translation** | Large input/output text areas, source & target language dropdowns, one-click language swap |
| 🧠 **Auto-Detect** | Automatically detects and displays the source language when "Auto Detect" is selected |
| 🎤 **Voice Input** | Speak into your microphone and have it transcribed directly into the input box (SpeechRecognition) |
| 🔊 **Text-to-Speech** | Listen to the translated text read aloud (pyttsx3, fully offline) |
| 📋 **Copy to Clipboard** | One-click copy of the translated text with instant confirmation |
| 🗂️ **Translation History** | Every translation is saved to a local SQLite database with timestamps; reuse or delete entries individually |
| 📤 **Export** | Save any translation as a `.txt` file or a nicely formatted `.pdf` (ReportLab) |
| ⚡ **Live Translation** | Optional toggle to translate automatically as you type (debounced to avoid API spam) |
| 🛡️ **Error Handling** | Friendly messages for empty input, no internet connection, microphone issues, and API failures |

---

## 🖼️ Project Structure

```
ai_translator/
├── main.py                  # Application entry point + CustomTkinter GUI
├── database.py               # SQLite database manager (history CRUD)
├── translator_service.py     # Google Translate wrapper (translate + detect)
├── voice_service.py          # Speech-to-text & text-to-speech
├── export_service.py         # TXT / PDF export logic (ReportLab)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

The project follows a clean **separation of concerns**: the GUI (`main.py`) never talks to SQLite, Google Translate, or the microphone directly — it delegates to dedicated service classes (`DatabaseManager`, `TranslatorService`, `VoiceService`, `ExportService`). This makes the code easy to test, extend, and reuse.

---

## 🛠️ Requirements

- **Python 3.9 or higher**
- A working internet connection (required for translation and speech recognition, both of which call Google's services)
- A microphone (only required if you want to use Voice Input)
- **Windows users:** PyAudio installs via pip directly.
- **macOS users:** install PortAudio first: `brew install portaudio`
- **Linux users:** install these system packages first:
  ```bash
  sudo apt-get install python3-tk python3-dev portaudio19-dev espeak
  ```
  (`python3-tk` is required for CustomTkinter/Tkinter, `portaudio19-dev` for PyAudio/microphone input, and `espeak` is used by `pyttsx3` for offline text-to-speech on Linux.)

---

## 🚀 Installation & Setup

1. **Clone or download** this project folder.

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv

   # Activate it:
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

That's it — the SQLite database (`translation_history.db`) is created automatically in the project folder the first time you run the app, so there's no manual database setup required.

---

## 📖 How to Use

1. **Choose languages** — pick a source language (or leave it on "Auto Detect") and a target language from the dropdowns at the top.
2. **Enter text** — type or paste text into the left "Enter Text" box, or click **🎤 Voice Input** to speak it instead.
3. **Translate** — click **Translate ➜** (or flip on **Live Translation** in the sidebar to translate automatically as you type).
4. **Review the result** — the translated text appears on the right, along with the auto-detected source language.
5. **Take action on the result:**
   - 🔊 **Speak** — hear the translation read aloud.
   - 📋 **Copy** — copy it to your clipboard.
   - 📄 / 📕 — export it as a TXT or PDF file from the sidebar.
6. **Browse history** — every translation is automatically logged in the right-hand **Translation History** panel. Use **Reuse** to reload a past translation, **Delete** to remove a single entry, or **Clear History** in the sidebar to wipe everything.
7. **Toggle appearance** — switch between Dark and Light mode anytime using the sidebar switch.

---

## 🧩 Tech Stack

- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** — modern, themeable UI widgets on top of Tkinter
- **[googletrans](https://pypi.org/project/googletrans/)** — unofficial Google Translate API client (translation + language detection)
- **[SQLite3](https://docs.python.org/3/library/sqlite3.html)** — built into Python, used for local translation history storage
- **[SpeechRecognition](https://pypi.org/project/SpeechRecognition/)** — microphone capture + Google Web Speech API for voice input
- **[pyttsx3](https://pypi.org/project/pyttsx3/)** — fully offline text-to-speech engine
- **[ReportLab](https://www.reportlab.com/)** — PDF generation for exported translations

---

## ⚠️ Known Limitations

- `googletrans` relies on the public, unofficial Google Translate web endpoint. Google occasionally changes this endpoint, which can cause temporary translation failures upstream of this app — if that happens, an update to the `googletrans` package usually resolves it.
- Voice input requires an internet connection (it uses Google's Web Speech API under the hood via `SpeechRecognition`).
- Text-to-speech voice quality/language support depends on the voices installed on your operating system.

---

## 📌 Possible Future Enhancements

- Batch/file translation (translate entire `.docx` or `.txt` files at once)
- Favorite/starred translations
- Custom themes beyond Dark/Light
- Offline translation fallback model

---

## 📄 License

This project is open-source and free to use for educational and portfolio purposes (e.g. internship submissions, GitHub, LinkedIn).

---

**Built with Python 🐍 and a focus on clean, maintainable, production-style code.**
