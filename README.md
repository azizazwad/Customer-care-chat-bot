# Mikey — English and Bangla Customer-Care Assistant

Mikey is a bilingual English/Bangla customer-care web app powered by Groq, built with FastAPI. The responsive chat UI streams replies as they are written, renders formatted answers (lists, tables, code), and supports voice dictation in compatible browsers, conversation history, dark mode, and new conversations. A Windows desktop assistant is also available with voice input, optional screen analysis, approved app shortcuts, quick website links, time/date, volume controls, and a file picker.

## Project structure

```text
main.py                  Entry point: `uvicorn main:app` (and Vercel) load the website; `python main.py` opens the desktop app
mikey/
  config.py              Paths, the .env reader, and Groq settings (models, timeouts, limits)
  prompts.py             Mikey's system prompt: persona, rules, and formatting
  groq_client.py         Groq requests: build, send with retries, stream, and explain errors
  network.py             HTTPS connections that try IPv4 first
  web/                   The website (FastAPI)
    server.py            Creates the app and serves the page and static files
    routes.py            /api/config, /api/chat, /api/chat/stream
    schemas.py           Request bodies and their limits
    errors.py            Groq failures → HTTP errors
  desktop/               The Windows desktop assistant (Tkinter)
    window.py            The window and its actions
    commands.py          Text or speech → desktop command
    system.py            Apps, volume keys, screen capture
    speech.py            Microphone input and reading replies aloud
    constants.py         Colors, languages, approved websites and apps
static/
  index.html             The chat page
  css/                   tokens, base, layout, welcome, chat, composer, effects, responsive
  js/                    ES modules; main.js wires up chat, messages, composer, markdown,
                         i18n, theme, motion, voice, scroll, feedback, state, storage, dom
  vendor/                marked (Markdown) and DOMPurify (HTML sanitizer)
```

## Run the customer-care website

Use Python 3.11 or newer. From PowerShell in the project folder:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# Create .env as shown below, then:
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open **http://127.0.0.1:8000** in your browser. When `.venv` is already set up, the short command works too:

```powershell
uvicorn main:app --reload
```

The reload server is for local development only.

## Configure customer care

Create a `.env` file beside `main.py` and set:

```powershell
GROQ_API_KEY=your_groq_key_here
BUSINESS_NAME=Your business name
SUPPORT_CONTEXT=Add verified product details, support hours, and policies here.
```

`GROQ_API_KEY` is required for AI chat. Keep `.env` private; it is ignored by Git and by Vercel uploads. `BUSINESS_NAME` and `SUPPORT_CONTEXT` are optional. The assistant is instructed not to make up prices, policies, order status, refunds, or actions, and to offer human support when it cannot verify an answer. Do not put customer secrets or sensitive personal data in the support context. Environment variables with the same names take priority over `.env`.

The app uses Groq's chat completion API. Customer-care chat uses `openai/gpt-oss-120b`. Optional desktop screen analysis uses Groq's vision-capable `qwen/qwen3.8-27b` model. These can be overridden with `GROQ_CHAT_MODEL` and `GROQ_VISION_MODEL`. Requests allow up to 120 seconds for a reply and cap generated output at 2048 tokens, which includes the model's hidden reasoning; a timeout is reported as HTTP 504.

The website uses `POST /api/chat/stream`, which streams newline-delimited JSON events (`delta`, then `done` or `error`); `POST /api/chat` returns the whole reply at once. Both take `{"message", "language", "history"}`, where `history` is up to 20 earlier `{"role", "content"}` turns.

Groq requests send their own `User-Agent`, because Groq's Cloudflare protection blocks Python's default one with **Error 1010**. They also connect over IPv4 first, since some networks drop IPv6 connections to Groq, and retry brief network failures such as a failed DNS lookup. If Error 1010 still appears, contact Groq Support with the Ray ID shown by the app.

## Deploy to Vercel

Vercel runs the website as a Python function: it loads `app` from `main.py`, installs `requirements.txt`, and serves `/static` from its CDN. The desktop assistant is not deployed (see `.vercelignore`).

1. Push the project to GitHub (`.env` and `venv/` are git-ignored), then import the repository at [vercel.com/new](https://vercel.com/new). Or run `vercel deploy` from the project folder with the [Vercel CLI](https://vercel.com/docs/cli).
2. In the Vercel project, open **Settings → Environment Variables** and add `GROQ_API_KEY`, plus `BUSINESS_NAME` and `SUPPORT_CONTEXT` if you use them.
3. Redeploy so the variables take effect.

The server keeps no conversation state between requests: the browser holds the conversation and sends recent turns with each message, which suits Vercel's serverless functions.

The chat API is public once deployed, and every message uses your Groq quota. Consider adding a rate-limiting rule in Vercel's Firewall.

## Language and privacy

- Choose **English** or **বাংলা** in the website header. Voice dictation uses the browser's Web Speech API where available; audio transcription may be handled by your browser's speech service.
- Web chat messages are sent to Groq. In the desktop app, screen content is captured and sent only when you choose **Read my screen**.
- The conversation lives only in the open browser tab; the server does not store it. Starting a new conversation or reloading the page clears it.
- Mikey does not execute arbitrary shell commands or make unattended changes to files.

## Windows desktop assistant

Run `run.bat` to set up and launch the desktop assistant. `requirements.txt` installs its speech and screen-capture packages on Windows only, so Vercel's Linux build skips them. If Windows asks for microphone access, allow it. In the desktop app choose English or বাংলা.

## Included features

- Ask customer-care questions in English or Bangla, with conversational context.
- Use browser voice dictation in supported browsers.
- Open Notepad, Calculator, Paint, and File Explorer.
- Open YouTube, Google, and GitHub.
- Read the current date/time and adjust system volume.
- Select a file with the Windows file picker.
- Ask Groq to describe a screenshot after you explicitly choose screen analysis.
