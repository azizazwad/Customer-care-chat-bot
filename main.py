"""Mikey: bilingual English/Bangla customer-care assistant.

- Website (local): `uvicorn main:app --reload`; Vercel also loads `app` from here.
- Windows desktop assistant: `python main.py`.

The code lives in the `mikey` package: `mikey.web` (FastAPI site and API),
`mikey.desktop` (Tkinter app), and shared Groq/config modules.
"""

from mikey.web import app

__all__ = ["app"]

if __name__ == "__main__":
    from mikey.desktop import main

    main()
