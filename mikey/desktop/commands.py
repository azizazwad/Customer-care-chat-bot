"""Turn what the user typed or said into a desktop command."""

from __future__ import annotations

from dataclasses import dataclass

# Speech recognition may return either Unicode spelling of য় and ড়, so phrases
# with those letters are listed twice, as \u escapes: editors can silently
# merge the two spellings if they are typed out.
TIME_PHRASES = {
    "time", "date", "what time is it", "what is the time", "what's the time",
    "tell me the time", "what is today's date", "what's today's date",
    "\u09b8\u09ae\u09af\u09bc", "\u09b8\u09ae\u09df",  # সময়
    "\u09b8\u09ae\u09af\u09bc \u09ac\u09b2\u09cb", "\u09b8\u09ae\u09df \u09ac\u09b2\u09cb",  # সময় বলো
    "তারিখ", "তারিখ বলো",
}
OPEN_WORDS = ("open", "launch", "খোলো", "খুলুন", "খুলে দাও")
# A target opens when its keyword is said on its own, or together with an open word.
LAUNCH_TARGETS = (
    ("site", "youtube", ("youtube", "ইউটিউব")),
    ("site", "google", ("google", "গুগল")),
    ("site", "github", ("github", "গিটহাব")),
    ("app", "notepad", ("notepad", "নোটপ্যাড")),
    ("app", "calculator", ("calculator", "calc", "ক্যালকুলেটর")),
    ("app", "paint", ("paint", "পেইন্ট")),
)
VOLUME_UP_PHRASES = {
    "volume up", "increase volume",
    "\u09ad\u09b2\u09bf\u0989\u09ae \u09ac\u09be\u09a1\u09bc\u09be\u0993",  # ভলিউম বাড়াও
    "\u09ad\u09b2\u09bf\u0989\u09ae \u09ac\u09be\u09dc\u09be\u0993",  # ভলিউম বাড়াও (precomposed ড়)
}
VOLUME_DOWN_PHRASES = {"volume down", "decrease volume", "ভলিউম কমাও"}
HELP_PHRASES = {"help", "commands", "সাহায্য", "কমান্ড"}


@dataclass(frozen=True)
class Command:
    action: str  # "time", "site", "app", "volume", or "help"
    target: str | int | None = None


def parse_command(text: str) -> Command | None:
    """Return the desktop command in `text`, or None to ask customer support instead."""
    value = text.casefold().strip().rstrip(" .!?")
    if value in TIME_PHRASES:
        return Command("time")
    open_intent = any(word in value for word in OPEN_WORDS)
    for action, name, keywords in LAUNCH_TARGETS:
        if (open_intent or value in keywords) and any(word in value for word in keywords):
            return Command(action, name)
    if value in VOLUME_UP_PHRASES:
        return Command("volume", 1)
    if value in VOLUME_DOWN_PHRASES:
        return Command("volume", -1)
    if value in HELP_PHRASES:
        return Command("help")
    return None
