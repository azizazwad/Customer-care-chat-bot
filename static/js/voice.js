// Voice dictation with the browser's Web Speech API, where it is available.

import { els } from "./dom.js";
import { showToast } from "./feedback.js";
import { getLanguage, t } from "./i18n.js";

let recognition = null;

const speechLanguage = () => (getLanguage() === "bn" ? "bn-BD" : "en-US");

export function setVoiceLanguage() {
  if (recognition) recognition.lang = speechLanguage();
}

export function initVoice(onTranscript) {
  const { voiceButton } = els;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    voiceButton.addEventListener("click", () => showToast(t("voiceUnsupported")));
    return;
  }
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = speechLanguage();
  recognition.onstart = () => {
    voiceButton.classList.add("listening");
    showToast(t("listening"));
  };
  recognition.onresult = (event) => onTranscript(event.results[0][0].transcript);
  recognition.onerror = (event) => {
    if (event.error === "not-allowed") showToast(t("voiceDenied"));
    else if (event.error !== "no-speech" && event.error !== "aborted") showToast(t("failed"));
  };
  recognition.onend = () => voiceButton.classList.remove("listening");
  voiceButton.addEventListener("click", () => {
    if (voiceButton.classList.contains("listening")) {
      recognition.stop();
      return;
    }
    try { recognition.start(); } catch { showToast(t("listening")); }
  });
}
