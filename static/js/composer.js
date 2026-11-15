// The message box: auto-height, character count, and the send/stop button.

import { els } from "./dom.js";
import { t } from "./i18n.js";
import { isStreaming } from "./state.js";

export const MAX_LENGTH = 2000;

export function resizeInput() {
  els.input.style.height = "auto";
  els.input.style.height = `${Math.min(els.input.scrollHeight, 200)}px`;
}

export function updateSendButton() {
  const { input, sendButton, charCount } = els;
  const streaming = isStreaming();
  sendButton.classList.toggle("is-stop", streaming);
  sendButton.disabled = !streaming && !input.value.trim();
  const label = t(streaming ? "stop" : "send");
  sendButton.setAttribute("aria-label", label);
  sendButton.title = label;
  const remaining = MAX_LENGTH - input.value.length;
  charCount.textContent = remaining <= 300 ? String(remaining) : "";
  charCount.classList.toggle("near-limit", remaining <= 100);
}

export function clearInput() {
  els.input.value = "";
  resizeInput();
  updateSendButton();
}
