// Sending messages and streaming Mikey's replies from /api/chat/stream.

import { clearInput, MAX_LENGTH, updateSendButton } from "./composer.js";
import { els, finePointer } from "./dom.js";
import { showToast } from "./feedback.js";
import { getLanguage, t } from "./i18n.js";
import { createTypewriter } from "./markdown.js";
import {
  addAssistantActions,
  addGreetingIfNeeded,
  addNote,
  clearMessages,
  createMessage,
  showError,
  thinkingIndicator
} from "./messages.js";
import { followScroll, scrollToTop } from "./scroll.js";
import { chatState, isStreaming } from "./state.js";

// Must stay within the limits in mikey/web/schemas.py.
const MAX_HISTORY_MESSAGES = 20;
const MAX_HISTORY_CONTENT = 12000;

function remember(question, reply) {
  chatState.history.push(
    { role: "user", content: question },
    { role: "assistant", content: reply.slice(0, MAX_HISTORY_CONTENT) }
  );
  chatState.history = chatState.history.slice(-MAX_HISTORY_MESSAGES);
}

export async function sendMessage(text) {
  const message = text.trim().slice(0, MAX_LENGTH);
  if (!message || isStreaming()) return;
  addGreetingIfNeeded();
  createMessage("user").content.textContent = message;
  clearInput();
  els.heroOrb.classList.remove("is-happy");
  await streamReply(message);
}

export function stopReply() {
  chatState.controller?.abort();
}

export function startNewConversation() {
  stopReply();
  chatState.history = [];
  clearMessages();
  scrollToTop();
  showToast(t("newChatDone"));
}

async function readEvents(response, onEvent) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let newline = buffer.indexOf("\n");
    while (newline >= 0) {
      const line = buffer.slice(0, newline).trim();
      buffer = buffer.slice(newline + 1);
      if (line) onEvent(JSON.parse(line));
      newline = buffer.indexOf("\n");
    }
  }
}

async function streamReply(text) {
  const message = createMessage("assistant");
  message.row.classList.add("is-streaming");
  message.content.append(thinkingIndicator());
  const writer = createTypewriter(message.content, () => followScroll());
  const controller = new AbortController();
  controller.signal.addEventListener("abort", () => writer.flush(), { once: true });
  chatState.controller = controller;
  updateSendButton();
  let finishReason = null;
  let completed = false;

  try {
    const response = await fetch("/api/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, language: getLanguage(), history: chatState.history }),
      signal: controller.signal
    });
    if (!response.ok || !response.body) {
      const data = await response.json().catch(() => ({}));
      throw new Error(typeof data.detail === "string" ? data.detail : t("failed"));
    }
    await readEvents(response, (event) => {
      if (event.type === "delta") writer.push(event.text);
      else if (event.type === "error") throw new Error(event.detail || t("failed"));
      else if (event.type === "done") { completed = true; finishReason = event.finish_reason; }
    });
    if (!completed) throw new Error(t("interrupted"));
    await writer.finish();
    // Stopped replies (including a new conversation mid-reply) never join the history.
    if (!controller.signal.aborted) remember(text, writer.text);
    if (finishReason === "length") addNote(message, t("truncated"));
  } catch (error) {
    writer.flush();
    message.content.querySelector(".thinking")?.remove();
    if (error.name === "AbortError") addNote(message, t("stopped"));
    else showError(message, error.message || t("failed"), () => {
      if (isStreaming()) return;
      message.row.remove();
      streamReply(text);
    });
  } finally {
    message.row.classList.remove("is-streaming");
    if (writer.text) {
      addAssistantActions(message, writer.text);
      els.announcer.textContent = message.content.textContent;
    }
    if (chatState.controller === controller) chatState.controller = null;
    updateSendButton();
    followScroll();
    if (finePointer.matches) els.input.focus();
  }
}
