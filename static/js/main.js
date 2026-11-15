// Entry point: connects the UI modules to the page.

import { sendMessage, startNewConversation, stopReply } from "./chat.js";
import { resizeInput, updateSendButton } from "./composer.js";
import { $, els } from "./dom.js";
import { addRipple, showToast } from "./feedback.js";
import { applyTranslations, getLanguage, setLanguage, t } from "./i18n.js";
import { initMotion, setMascotHappy } from "./motion.js";
import { initScroll } from "./scroll.js";
import { isStreaming } from "./state.js";
import { currentTheme, setTheme, toggleTheme } from "./theme.js";
import { initVoice, setVoiceLanguage } from "./voice.js";

function changeLanguage(language) {
  if (language === getLanguage()) return;
  setLanguage(language);
  applyTranslations(true);
  updateSendButton();
  setVoiceLanguage();
}

els.form.addEventListener("submit", (event) => {
  event.preventDefault();
  if (isStreaming()) stopReply();
  else sendMessage(els.input.value);
});
els.input.addEventListener("input", () => {
  resizeInput();
  updateSendButton();
  setMascotHappy(els.input.value.trim().length > 0);
});
els.input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    if (!isStreaming()) els.form.requestSubmit();
  }
});
document.querySelectorAll("[data-prompt-key]").forEach((button) => {
  button.addEventListener("click", () => sendMessage(t(button.dataset.promptKey)));
});
document.querySelectorAll(".ripple-host").forEach((host) => host.addEventListener("pointerdown", addRipple));
els.langSwitch.querySelectorAll("[data-lang]").forEach((button) => {
  button.addEventListener("click", () => changeLanguage(button.dataset.lang));
});
els.themeToggle.addEventListener("click", toggleTheme);
$("#new-chat").addEventListener("click", startNewConversation);
$("#new-chat-mobile").addEventListener("click", startNewConversation);

setTheme(currentTheme());
applyTranslations();
updateSendButton();
initScroll();
initMotion();
initVoice((transcript) => {
  els.input.value = transcript;
  resizeInput();
  updateSendButton();
  els.form.requestSubmit();
});

fetch("/api/config")
  .then((response) => response.json())
  .then((config) => {
    if (config.business_name) els.businessName.textContent = config.business_name;
    if (!config.ready) showToast(t("notConfigured"));
  })
  .catch(() => showToast(t("failed")));
