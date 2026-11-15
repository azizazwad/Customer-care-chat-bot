// Safe Markdown rendering for replies, and the smooth "typing" reveal while streaming.

import { element, reducedMotion } from "./dom.js";

const canRenderMarkdown = Boolean(window.marked && window.DOMPurify);
if (canRenderMarkdown) {
  window.marked.setOptions({ gfm: true, breaks: true });
  window.DOMPurify.addHook("afterSanitizeAttributes", (node) => {
    if (node.tagName === "A") {
      node.setAttribute("target", "_blank");
      node.setAttribute("rel", "noopener noreferrer");
    }
  });
}

export function renderMarkdown(target, text) {
  if (!canRenderMarkdown) {
    target.textContent = text;
    target.style.whiteSpace = "pre-wrap";
    return;
  }
  target.innerHTML = window.DOMPurify.sanitize(window.marked.parse(text));
  target.querySelectorAll("table").forEach((table) => {
    const wrap = element("div", "table-wrap");
    table.replaceWith(wrap);
    wrap.append(table);
  });
}

// Reveals streamed text at a smooth, adaptive pace instead of in network-sized bursts.
export function createTypewriter(target, onRender) {
  let full = "";
  let shown = 0;
  let frame = 0;
  let onCaughtUp = null;

  function tick() {
    frame = 0;
    const remaining = full.length - shown;
    if (remaining > 0) {
      shown += reducedMotion.matches ? remaining : Math.max(2, Math.ceil(remaining / 14));
      renderMarkdown(target, full.slice(0, shown));
      onRender();
    }
    if (shown < full.length) frame = requestAnimationFrame(tick);
    else if (onCaughtUp) { onCaughtUp(); onCaughtUp = null; }
  }

  return {
    get text() { return full; },
    push(text) {
      full += text;
      if (!frame) frame = requestAnimationFrame(tick);
    },
    finish() {
      return new Promise((resolve) => {
        if (shown >= full.length) { resolve(); return; }
        onCaughtUp = resolve;
        if (!frame) frame = requestAnimationFrame(tick);
      });
    },
    flush() {
      cancelAnimationFrame(frame);
      frame = 0;
      if (shown < full.length) { shown = full.length; renderMarkdown(target, full); }
      if (onCaughtUp) { onCaughtUp(); onCaughtUp = null; }
    }
  };
}
