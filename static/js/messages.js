// Building chat messages: bubbles, replies, actions, notes, and errors.

import { element, els, icon } from "./dom.js";
import { showToast } from "./feedback.js";
import { getLanguage, t } from "./i18n.js";
import { renderMarkdown } from "./markdown.js";
import { followScroll, updateJumpButton } from "./scroll.js";

export function setChatStarted(started) {
  els.welcome.hidden = started;
  els.thread.hidden = !started;
  els.mainPanel.classList.toggle("chatting", started);
  updateJumpButton();
}

export function clearMessages() {
  els.thread.replaceChildren();
  setChatStarted(false);
}

function formatTime() {
  return new Intl.DateTimeFormat(getLanguage() === "bn" ? "bn-BD" : "en", { hour: "numeric", minute: "2-digit" }).format(new Date());
}

export function createMessage(role) {
  setChatStarted(true);
  const row = element("article", `message ${role}`);
  const body = element("div", "message-body");
  const meta = element("div", "message-meta");
  const time = element("time", "", formatTime());
  const content = element("div", role === "user" ? "bubble" : "markdown");
  if (role === "assistant") {
    const avatar = element("div", "avatar");
    avatar.setAttribute("aria-hidden", "true");
    avatar.append(icon("spark"));
    meta.append(element("span", "message-name", t("botName")), time);
    row.append(avatar);
  } else {
    meta.append(time);
  }
  body.append(meta, content);
  row.append(body);
  els.thread.append(row);
  followScroll(true);
  return { row, body, content };
}

export function addGreetingIfNeeded() {
  if (els.thread.childElementCount) return;
  const greeting = createMessage("assistant");
  renderMarkdown(greeting.content, t("greeting"));
}

export function addAssistantActions(message, text) {
  const actions = element("div", "message-actions");
  const copyButton = element("button", "action-button");
  copyButton.type = "button";
  const label = element("span", "", t("copy"));
  copyButton.append(icon("copy"), label);
  copyButton.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(text);
      copyButton.classList.add("copied");
      copyButton.querySelector("use").setAttribute("href", "#i-check");
      label.textContent = t("copied");
      window.setTimeout(() => {
        copyButton.classList.remove("copied");
        copyButton.querySelector("use").setAttribute("href", "#i-copy");
        label.textContent = t("copy");
      }, 1800);
    } catch {
      showToast(t("copyFailed"));
    }
  });
  actions.append(copyButton);
  message.body.append(actions);
}

export function addNote(message, text) {
  message.body.append(element("div", "message-note", text));
}

export function showError(message, detail, onRetry) {
  const box = element("div", "message-error");
  box.setAttribute("role", "alert");
  const retryButton = element("button", "action-button");
  retryButton.type = "button";
  retryButton.append(icon("retry"), element("span", "", t("retry")));
  retryButton.addEventListener("click", onRetry);
  box.append(icon("alert"), element("span", "", detail), retryButton);
  message.body.append(box);
}

export function thinkingIndicator() {
  const wrap = element("div", "thinking");
  const dots = element("span", "thinking-dots");
  dots.append(element("i"), element("i"), element("i"));
  wrap.append(dots, element("span", "shimmer", `${t("thinking")}…`));
  return wrap;
}
